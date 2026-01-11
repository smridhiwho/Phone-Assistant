import json
import re
import logging
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class HuggingFaceService:

    def __init__(self):
        self.model_name = settings.hf_model_name
        self.use_inference_api = settings.use_inference_api
        self.client: Optional[InferenceClient] = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return

        logger.info("=" * 50)
        logger.info(f"[HUGGINGFACE] Initializing with model: {self.model_name}")

        if self.use_inference_api:
            hf_token = settings.hf_token
            if hf_token:
                logger.info(f"[HUGGINGFACE] Token: {hf_token[:10]}...{hf_token[-5:]}")
                self.client = InferenceClient(model=self.model_name, token=hf_token)
            else:
                logger.warning("[HUGGINGFACE] No token - using free API")
                self.client = InferenceClient(model=self.model_name)
            logger.info("[HUGGINGFACE] Client initialized")
        else:
            logger.warning("[HUGGINGFACE] Inference API disabled!")

        self._initialized = True
        logger.info("=" * 50)

    async def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        logger.info("*" * 50)
        logger.info("[HUGGINGFACE] generate() called")
        logger.info(f"[HUGGINGFACE] Prompt: {prompt[:200]}...")

        self.initialize()

        if not self.client:
            logger.error("[HUGGINGFACE] CLIENT IS NONE!")
            raise RuntimeError("HuggingFace client not initialized")

        messages = [{"role": "user", "content": prompt}]

        try:
            logger.info(f"[HUGGINGFACE] >>> MAKING API CALL to {self.model_name} <<<")
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            logger.info("[HUGGINGFACE] >>> API RESPONSE RECEIVED <<<")
            logger.info(f"[HUGGINGFACE] Response: {str(content)[:300]}...")
            logger.info("*" * 50)
            return content.strip()
        except Exception as e:
            logger.error(f"[HUGGINGFACE] API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    async def generate_chat(self, messages: list, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        logger.info("*" * 50)
        logger.info(f"[HUGGINGFACE] generate_chat() - {len(messages)} messages")

        self.initialize()

        if not self.client:
            logger.error("[HUGGINGFACE] CLIENT IS NONE!")
            raise RuntimeError("HuggingFace client not initialized")

        try:
            logger.info(f"[HUGGINGFACE] >>> MAKING CHAT API CALL to {self.model_name} <<<")
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            logger.info("[HUGGINGFACE] >>> CHAT RESPONSE RECEIVED <<<")
            logger.info(f"[HUGGINGFACE] Response: {str(content)[:300]}...")
            logger.info("*" * 50)
            return content
        except Exception as e:
            logger.error(f"[HUGGINGFACE] CHAT ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    async def extract_search_parameters(self, query: str, intent: str) -> Dict[str, Any]:
        logger.info(f"[HUGGINGFACE] extract_search_parameters() - Query: {query}, Intent: {intent}")

        prompt = f"""Extract search parameters from this mobile phone query.

Query: "{query}"
Intent: {intent}

Extract JSON: {{"features": [], "price_min": null, "price_max": null, "brand": null, "min_ram": null, "search_text": null}}

Return ONLY valid JSON."""

        try:
            response = await self.generate(prompt, max_tokens=300, temperature=0.3)
            logger.info(f"[HUGGINGFACE] Raw response: {response}")
            params = self._parse_json_response(response)
            result = {
                "features": params.get("features", []),
                "price_min": params.get("price_min"),
                "price_max": params.get("price_max"),
                "brand": params.get("brand"),
                "min_ram": params.get("min_ram"),
                "search_text": params.get("search_text")
            }
            logger.info(f"[HUGGINGFACE] Extracted params: {result}")
            return result
        except Exception as e:
            logger.error(f"[HUGGINGFACE] Parameter extraction FAILED: {e}", exc_info=True)
            raise

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            return {"intent": "search_phones", "confidence": 0.5, "extracted_params": {}}

    @property
    def is_available(self) -> bool:
        self.initialize()
        return self.client is not None


_huggingface_service: Optional[HuggingFaceService] = None


def get_huggingface_service() -> HuggingFaceService:
    global _huggingface_service
    if _huggingface_service is None:
        _huggingface_service = HuggingFaceService()
    return _huggingface_service
