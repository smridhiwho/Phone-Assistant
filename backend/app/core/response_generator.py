from typing import List, Dict, Any, Optional
import json
import logging

from app.models.database import Phone
from app.services.huggingface_service import HuggingFaceService, get_huggingface_service
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)


class ResponseGenerator:

    def __init__(self, llm_service: Optional[HuggingFaceService] = None, product_service: Optional[ProductService] = None):
        self.llm_service = llm_service or get_huggingface_service()
        self.product_service = product_service or ProductService()

    async def generate_response(self, query: str, intent: Dict[str, Any], phones: List[Phone], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        intent_type = intent.get("intent", "search_phones")
        logger.info(f"[RESPONSE_GEN] Intent: {intent_type}, Query: {query[:50]}..., Phones: {len(phones)}")

        if intent_type == "adversarial":
            logger.info("[RESPONSE_GEN] HARDCODED refusal")
            return self._generate_refusal_response()

        if intent_type == "chitchat":
            logger.info("[RESPONSE_GEN] LLM chitchat")
            return await self._generate_llm_chitchat_response(query, conversation_history)

        if intent_type == "explain_feature":
            logger.info("[RESPONSE_GEN] LLM feature explanation")
            return await self._generate_llm_feature_explanation(query)

        if intent_type == "compare_phones":
            logger.info("[RESPONSE_GEN] LLM comparison")
            return await self._generate_llm_comparison_response(query, phones)

        if intent_type == "get_details" and phones:
            logger.info("[RESPONSE_GEN] LLM details")
            return await self._generate_llm_details_response(query, phones[0])

        logger.info("[RESPONSE_GEN] LLM search")
        return await self._generate_llm_search_response(query, intent, phones)

    def _generate_refusal_response(self) -> Dict[str, Any]:
        return {
            "response": "I'm a mobile phone shopping assistant. I can help you find, compare, and learn about smartphones. Please ask me about phones, their features, or help finding the right device for you.",
            "products": [],
            "intent": "adversarial",
            "suggestions": ["What's the best phone under 30,000?", "Compare Samsung S24 vs OnePlus 12", "Best camera phones in 2024"]
        }

    def _generate_chitchat_response(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        if any(word in query_lower for word in ["hello", "hi", "hey"]):
            response = "Hello! I'm your mobile phone shopping assistant. What are you looking for?"
        elif any(word in query_lower for word in ["thanks", "thank"]):
            response = "You're welcome! Anything else about mobile phones?"
        elif "help" in query_lower:
            response = "I can help with: finding phones, comparing models, explaining features. What would you like?"
        else:
            response = "I'm here to help you find the perfect smartphone! What are you looking for?"
        return {"response": response, "products": [], "intent": "chitchat", "suggestions": ["Best phones under 25,000", "Show me flagship phones", "Best camera phones"]}

    def _generate_feature_explanation(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        explanations = {
            "ois": "OIS (Optical Image Stabilization) uses mechanical movement to counteract camera shake for sharper photos.",
            "eis": "EIS (Electronic Image Stabilization) uses software to stabilize video by cropping and adjusting frames.",
            "amoled": "AMOLED displays offer vibrant colors, deep blacks, and better power efficiency than LCD.",
            "oled": "OLED displays produce their own light, enabling thinner screens and perfect blacks.",
            "refresh rate": "Refresh rate (Hz) indicates how often the display updates. Higher = smoother scrolling.",
            "mah": "mAh measures battery capacity. Higher mAh = longer battery life.",
            "5g": "5G offers faster speeds and lower latency than 4G. Coverage varies by region.",
            "ip68": "IP68 means dust-tight and waterproof (1.5m for 30 minutes).",
            "wireless charging": "Charge your phone by placing it on a compatible pad. Speeds vary from 5W to 50W+."
        }
        response = next((exp for term, exp in explanations.items() if term in query_lower),
                       "I can explain OIS, AMOLED, refresh rate, mAh, 5G, IP68, and more. Which feature?")
        return {"response": response, "products": [], "intent": "explain_feature", "suggestions": ["What is AMOLED?", "Explain refresh rate", "What does IP68 mean?"]}

    def _generate_comparison_response(self, phones: List[Phone]) -> Dict[str, Any]:
        if len(phones) < 2:
            return {"response": "Please specify at least two phones to compare.", "products": [], "intent": "compare_phones", "suggestions": ["Compare Samsung S24 vs OnePlus 12"]}
        summary = self.product_service.generate_comparison_summary(phones)
        phone_responses = self.product_service.phones_to_response(phones)
        phone_names = [f"{p.brand} {p.model}" for p in phones]
        return {"response": f"Comparison of {', '.join(phone_names)}:\n\n{summary}", "products": phone_responses, "intent": "compare_phones", "suggestions": ["Which has better camera?", "Which is better value?"]}

    def _generate_details_response(self, phone: Phone) -> Dict[str, Any]:
        phone_response = self.product_service.phone_to_response(phone)
        features_text = ""
        if phone.features:
            try:
                features = json.loads(phone.features) if isinstance(phone.features, str) else phone.features
                features_text = ", ".join(features[:5])
            except: pass
        response = f"{phone.brand} {phone.model}: {phone.price_inr:,} | {phone.display_size}\" {phone.display_type} {phone.refresh_rate}Hz | {phone.processor} | {phone.ram_gb}GB RAM | {phone.battery_mah}mAh | {features_text}"
        return {"response": response, "products": [phone_response], "intent": "get_details", "suggestions": [f"Compare {phone.model} with alternatives"]}

    def _generate_search_response(self, query: str, intent: Dict[str, Any], phones: List[Phone]) -> Dict[str, Any]:
        params = intent.get("extracted_params", {})
        intent_type = intent.get("intent", "search_phones")
        if not phones:
            return {"response": "No phones found matching your criteria.", "products": [], "intent": intent_type, "suggestions": ["Show phones under 30,000"]}
        phone_responses = self.product_service.phones_to_response(phones)
        top_phones = phones[:3]
        phone_list = "\n".join([f"- {p.brand} {p.model}: {p.price_inr:,} - {p.highlights or ''}" for p in top_phones])
        return {"response": f"Found {len(phones)} phones:\n{phone_list}", "products": phone_responses, "intent": intent_type, "suggestions": self._generate_follow_up_suggestions(intent_type, params)}

    def _generate_follow_up_suggestions(self, intent_type: str, params: Dict[str, Any]) -> List[str]:
        if intent_type == "budget_search":
            return ["Show phones with better cameras", "Which has best battery?", "Compare top 2"]
        elif intent_type == "filter_by_brand":
            brand = params.get("brand", "")
            return [f"Flagship {brand} phone?", f"Budget {brand} under 25,000", "Compare with competitors"]
        return ["Tell me more about first option", "Compare top recommendations", "Filter by price"]

    async def _generate_llm_chitchat_response(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        prompt = f"""[INST] <<SYS>>
You are a friendly mobile phone shopping assistant. Keep responses concise (2-3 sentences).
<</SYS>>
User: {query} [/INST]"""
        try:
            response = await self.llm_service.generate(prompt, max_tokens=200, temperature=0.7)
            logger.info(f"[RESPONSE_GEN] LLM response: {response[:100]}...")
            return {"response": response, "products": [], "intent": "chitchat", "suggestions": ["Best phones under 25,000", "Show flagship phones", "Best camera phones"]}
        except Exception as e:
            logger.error(f"[RESPONSE_GEN] LLM failed: {e}")
            return self._generate_chitchat_response(query)

    async def _generate_llm_feature_explanation(self, query: str) -> Dict[str, Any]:
        prompt = f"""[INST] <<SYS>>
You are a mobile phone expert. Explain features concisely (3-4 sentences).
<</SYS>>
User asks: {query}
Explain: [/INST]"""
        try:
            response = await self.llm_service.generate(prompt, max_tokens=300, temperature=0.5)
            logger.info(f"[RESPONSE_GEN] LLM response: {response[:100]}...")
            return {"response": response, "products": [], "intent": "explain_feature", "suggestions": ["What is AMOLED?", "Explain refresh rate", "What does IP68 mean?"]}
        except Exception as e:
            logger.error(f"[RESPONSE_GEN] LLM failed: {e}")
            return self._generate_feature_explanation(query)

    async def _generate_llm_comparison_response(self, query: str, phones: List[Phone]) -> Dict[str, Any]:
        if len(phones) < 2:
            return {"response": "Please specify at least two phones to compare.", "products": [], "intent": "compare_phones", "suggestions": ["Compare Samsung S24 vs OnePlus 12"]}

        specs = "\n".join([f"{p.brand} {p.model}: {p.price_inr:,} | {p.processor} | {p.ram_gb}GB | {p.battery_mah}mAh | {p.rear_camera}" for p in phones[:3]])
        phone_names = [f"{p.brand} {p.model}" for p in phones[:3]]

        prompt = f"""[INST] <<SYS>>
Compare these phones objectively. Be concise (4-5 sentences).
<</SYS>>
Compare: {', '.join(phone_names)}
Specs:
{specs}
[/INST]"""
        try:
            response = await self.llm_service.generate(prompt, max_tokens=500, temperature=0.5)
            logger.info(f"[RESPONSE_GEN] LLM response: {response[:100]}...")
            return {"response": response, "products": self.product_service.phones_to_response(phones), "intent": "compare_phones", "suggestions": ["Which has better camera?", "Which is better value?"]}
        except Exception as e:
            logger.error(f"[RESPONSE_GEN] LLM failed: {e}")
            return self._generate_comparison_response(phones)

    async def _generate_llm_details_response(self, query: str, phone: Phone) -> Dict[str, Any]:
        features_text = ""
        if phone.features:
            try:
                features = json.loads(phone.features) if isinstance(phone.features, str) else phone.features
                features_text = ", ".join(features[:5])
            except: pass

        phone_info = f"{phone.brand} {phone.model}: {phone.price_inr:,} | {phone.display_size}\" {phone.display_type} {phone.refresh_rate}Hz | {phone.processor} | {phone.ram_gb}GB/{phone.storage_gb}GB | {phone.rear_camera} | {phone.battery_mah}mAh | {features_text}"

        prompt = f"""[INST] <<SYS>>
Present phone details helpfully. Highlight strengths. Be concise (4-5 sentences).
<</SYS>>
User: {query}
Phone: {phone_info}
[/INST]"""
        try:
            response = await self.llm_service.generate(prompt, max_tokens=400, temperature=0.6)
            logger.info(f"[RESPONSE_GEN] LLM response: {response[:100]}...")
            return {"response": response, "products": [self.product_service.phone_to_response(phone)], "intent": "get_details", "suggestions": [f"Compare {phone.model} with alternatives"]}
        except Exception as e:
            logger.error(f"[RESPONSE_GEN] LLM failed: {e}")
            return self._generate_details_response(phone)

    async def _generate_llm_search_response(self, query: str, intent: Dict[str, Any], phones: List[Phone]) -> Dict[str, Any]:
        params = intent.get("extracted_params", {})
        intent_type = intent.get("intent", "search_phones")

        if not phones:
            return {"response": "No phones found matching your criteria.", "products": [], "intent": intent_type, "suggestions": ["Show phones under 30,000"]}

        phones_text = "\n".join([f"- {p.brand} {p.model}: {p.price_inr:,} - {p.highlights or ''}" for p in phones[:5]])
        context = ", ".join([f"budget {params.get('price_max')}" if params.get("price_max") else "", params.get("brand", ""), ", ".join(params.get("features", [])[:2])]).strip(", ")

        prompt = f"""[INST] <<SYS>>
Present search results helpfully. Be concise (3-4 sentences).
<</SYS>>
Query: {query}
Context: {context or 'general search'}
Found {len(phones)} phones:
{phones_text}
[/INST]"""
        try:
            response = await self.llm_service.generate(prompt, max_tokens=400, temperature=0.6)
            logger.info(f"[RESPONSE_GEN] LLM response: {response[:100]}...")
            return {"response": response, "products": self.product_service.phones_to_response(phones), "intent": intent_type, "suggestions": self._generate_follow_up_suggestions(intent_type, params)}
        except Exception as e:
            logger.error(f"[RESPONSE_GEN] LLM failed: {e}")
            return self._generate_search_response(query, intent, phones)


_response_generator: Optional[ResponseGenerator] = None

def get_response_generator() -> ResponseGenerator:
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator
