from typing import Dict, Any, List, Optional
import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.intent_classifier import IntentClassifier, get_intent_classifier
from app.core.query_processor import QueryProcessor, get_query_processor
from app.core.response_generator import ResponseGenerator, get_response_generator
from app.core.safety_filter import SafetyFilter, get_safety_filter
from app.services.huggingface_service import HuggingFaceService, get_huggingface_service
from app.services.product_service import ProductService, get_product_service
from app.repositories.phone_repository import PhoneRepository
from app.repositories.conversation_repository import ConversationRepository
from app.models.database import Phone, QueryAnalytics
from app.models.schemas import ChatResponse, PhoneResponse

logger = logging.getLogger(__name__)


class ShoppingAgent:

    def __init__(self, db: AsyncSession, intent_classifier: Optional[IntentClassifier] = None,
                 query_processor: Optional[QueryProcessor] = None, response_generator: Optional[ResponseGenerator] = None,
                 safety_filter: Optional[SafetyFilter] = None, llm_service: Optional[HuggingFaceService] = None,
                 product_service: Optional[ProductService] = None):
        self.db = db
        self.phone_repo = PhoneRepository(db)
        self.conversation_repo = ConversationRepository(db)
        self.intent_classifier = intent_classifier or get_intent_classifier()
        self.query_processor = query_processor or get_query_processor()
        self.response_generator = response_generator or get_response_generator()
        self.safety_filter = safety_filter or get_safety_filter()
        self.llm_service = llm_service or get_huggingface_service()
        self.product_service = product_service or get_product_service()

    async def process_message(self, message: str, session_id: str, context: Optional[Dict[str, Any]] = None) -> ChatResponse:
        start_time = time.time()
        logger.info(f"[AGENT] Processing: {message[:100]}")

        safety_result = self.safety_filter.check_input(message)
        if not safety_result["is_safe"]:
            logger.warning(f"[AGENT] UNSAFE: {safety_result.get('reason')}")
            response = self.safety_filter.get_safe_response(safety_result)
            await self._log_query(message, "adversarial", 0, int((time.time() - start_time) * 1000), True)
            return ChatResponse(response=response, products=[], intent="adversarial",
                              suggestions=["Best phones under 30,000", "Compare Samsung vs OnePlus", "Explain AMOLED"], session_id=session_id)

        history = await self.conversation_repo.get_conversation_history(session_id)
        logger.info(f"[AGENT] History: {len(history)} messages")

        intent = self.intent_classifier.classify(message)
        logger.info(f"[AGENT] Intent: {intent}")

        logger.info("[AGENT] Calling HuggingFace for params...")
        llm_params = await self.llm_service.extract_search_parameters(message, intent["intent"])
        logger.info(f"[AGENT] LLM params: {llm_params}")

        if llm_params:
            intent["extracted_params"].update({k: v for k, v in llm_params.items() if v is not None})

        search_criteria = self.query_processor.process(message, intent)
        logger.info(f"[AGENT] Search criteria: {search_criteria}")

        phones = await self._get_phones_for_intent(intent, search_criteria)
        logger.info(f"[AGENT] Found {len(phones)} phones")

        if intent["intent"] == "compare_phones":
            phone_ids = self.query_processor.get_comparison_phones(message, await self.phone_repo.get_all(limit=50))
            if phone_ids:
                phones = await self.phone_repo.get_by_ids(phone_ids)

        logger.info("[AGENT] Generating response...")
        response_data = await self.response_generator.generate_response(message, intent, phones, history)

        response_text = self.safety_filter.sanitize_output(response_data["response"])

        await self.conversation_repo.add_message(session_id, "user", message, {"intent": intent["intent"]})
        await self.conversation_repo.add_message(session_id, "assistant", response_text,
                                                 {"intent": intent["intent"], "product_ids": [p.id for p in phones] if phones else []})

        await self._log_query(message, intent["intent"], len(phones), int((time.time() - start_time) * 1000), False)

        return ChatResponse(response=response_text, products=response_data.get("products", []),
                          intent=intent["intent"], suggestions=response_data.get("suggestions", []), session_id=session_id)

    async def _get_phones_for_intent(self, intent: Dict[str, Any], search_criteria: Dict[str, Any]) -> List[Phone]:
        intent_type = intent["intent"]
        filters = search_criteria.get("filters", {})
        params = intent.get("extracted_params", {})
        search_type = search_criteria.get("search_type")

        if intent_type == "filter_by_brand":
            brand = filters.get("brand") or params.get("brand")
            if brand:
                return await self.phone_repo.get_by_brand(brand)

        if intent_type == "budget_search" or filters.get("max_price"):
            max_price = filters.get("max_price", params.get("price_max", 30000))
            min_price = filters.get("min_price", params.get("price_min", 0))
            return await self.phone_repo.get_by_price_range(min_price, max_price)

        if search_type == "gaming":
            return await self.phone_repo.get_gaming_phones()
        if search_type == "camera":
            return await self.phone_repo.get_camera_phones()
        if search_type == "battery":
            return await self.phone_repo.get_battery_phones()

        features = params.get("features", [])
        return await self.phone_repo.search(
            brand=filters.get("brand") or params.get("brand"),
            min_price=filters.get("min_price") or params.get("price_min"),
            max_price=filters.get("max_price") or params.get("price_max"),
            min_ram=filters.get("min_ram") or params.get("min_ram"),
            features=features if features else filters.get("features"),
            limit=10
        )

    async def _log_query(self, query: str, intent: str, products_returned: int, response_time_ms: int, was_adversarial: bool):
        try:
            self.db.add(QueryAnalytics(query=query, intent=intent, products_returned=products_returned,
                                       response_time_ms=response_time_ms, was_adversarial=was_adversarial))
            await self.db.commit()
        except Exception as e:
            print(f"Failed to log analytics: {e}")

    async def get_phone_details(self, phone_id: int) -> Optional[PhoneResponse]:
        phone = await self.phone_repo.get_by_id(phone_id)
        return self.product_service.phone_to_response(phone) if phone else None

    async def compare_phones(self, phone_ids: List[int]) -> Dict[str, Any]:
        phones = await self.phone_repo.get_by_ids(phone_ids)
        if len(phones) < 2:
            return {"phones": [], "comparison": [], "summary": "Need at least 2 phones to compare."}
        return {
            "phones": self.product_service.phones_to_response(phones),
            "comparison": self.product_service.generate_comparison(phones),
            "summary": self.product_service.generate_comparison_summary(phones)
        }

    async def search_phones(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        filters = filters or {}
        phones = await self.phone_repo.search(
            brand=filters.get("brand"), min_price=filters.get("min_price"), max_price=filters.get("max_price"),
            min_ram=filters.get("min_ram"), min_battery=filters.get("min_battery"),
            features=filters.get("features"), search_text=query, limit=filters.get("limit", 10)
        )
        return {"products": self.product_service.phones_to_response(phones), "count": len(phones),
                "explanation": f"Found {len(phones)} phones matching your search."}
