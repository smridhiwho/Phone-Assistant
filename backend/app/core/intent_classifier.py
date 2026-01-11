import re
import logging
from typing import Dict, Any, Optional
from app.services.huggingface_service import HuggingFaceService


logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user query intent for routing."""

    INTENT_KEYWORDS = {
        "compare_phones": [
            "compare", "vs", "versus", "difference", "better",
            "which one", "between", "or"
        ],
        "explain_feature": [
            "what is", "what's", "explain", "meaning", "means",
            "how does", "why", "ois", "eis", "amoled", "oled",
            "refresh rate", "mah", "processor", "chipset"
        ],
        "get_details": [
            "tell me about", "details", "specs", "specifications",
            "more about", "info", "information"
        ],
        "filter_by_brand": [
            "samsung", "oneplus", "google", "pixel", "xiaomi",
            "redmi", "realme", "vivo", "oppo", "nothing", "iqoo",
            "poco", "motorola", "moto"
        ],
        "budget_search": [
            "under", "below", "budget", "cheap", "affordable",
            "around", "range", "less than", "within"
        ],
        "search_phones": [
            "best", "recommend", "suggest", "looking for", "need",
            "want", "find", "show", "give me", "phone", "mobile"
        ],
        "chitchat": [
            "hello", "hi", "hey", "thanks", "thank you", "bye",
            "good", "okay", "ok", "help"
        ]
    }

    PRICE_PATTERN = re.compile(
        r'(?:under|below|around|within|less than|budget of?|upto|up to)?\s*'
        r'(?:rs\.?|inr|₹)?\s*(\d[\d,]*k?)\s*'
        r'(?:rs\.?|inr|₹)?',
        re.IGNORECASE
    )

    BRAND_PATTERN = re.compile(
        r'\b(samsung|oneplus|one plus|google|pixel|xiaomi|mi|redmi|'
        r'realme|vivo|oppo|nothing|iqoo|poco|motorola|moto)\b',
        re.IGNORECASE
    )

    FEATURE_KEYWORDS = {
        "camera": ["camera", "photo", "photography", "video", "megapixel", "mp"],
        "gaming": ["gaming", "game", "gamer", "pubg", "fps"],
        "battery": ["battery", "mah", "backup", "long lasting", "endurance"],
        "fast_charging": ["fast charging", "quick charge", "turbo charge", "supercharge"],
        "display": ["display", "screen", "amoled", "oled", "120hz", "144hz"],
        "compact": ["compact", "small", "one hand", "one-hand", "lightweight"],
        "5g": ["5g", "5 g"],
        "flagship": ["flagship", "premium", "high end", "high-end", "best"]
    }

    def __init__(self, llm_service: Optional[HuggingFaceService] = None):
        self.llm_service = llm_service

    def classify(self, query: str) -> Dict[str, Any]:
        """Classify the intent of a user query."""
        logger.info("[INTENT] classify() called")
        logger.info(f"[INTENT] Query: {query}")
        query_lower = query.lower().strip()

        params = self._extract_parameters(query_lower)
        logger.info(f"[INTENT] Extracted params: {params}")

        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[intent] = score

        logger.info(f"[INTENT] Intent scores: {scores}")

        if not scores:
            intent = "search_phones"
            confidence = 0.5
            logger.info("[INTENT] No keyword matches - defaulting to search_phones")
        else:
            intent = max(scores, key=scores.get)
            max_score = scores[intent]
            confidence = min(0.5 + (max_score * 0.15), 0.95)
            logger.info(f"[INTENT] Best match: {intent} (score={max_score}, confidence={confidence})")

        if params.get("price_max") or params.get("price_min"):
            if intent not in ["compare_phones", "get_details"]:
                logger.info(f"[INTENT] Adjusting intent from {intent} to budget_search (price detected)")
                intent = "budget_search"
                confidence = max(confidence, 0.8)

        if params.get("brand") and intent == "search_phones":
            logger.info(f"[INTENT] Adjusting intent from search_phones to filter_by_brand (brand={params.get('brand')})")
            intent = "filter_by_brand"
            confidence = max(confidence, 0.75)

        result = {
            "intent": intent,
            "confidence": confidence,
            "extracted_params": params
        }
        logger.info(f"[INTENT] Final classification: {result}")
        return result

    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract parameters from query."""
        params = {}

        price_match = self.PRICE_PATTERN.search(query)
        if price_match:
            price_str = price_match.group(1).replace(",", "")
            if price_str.lower().endswith("k"):
                price = int(price_str[:-1]) * 1000
            else:
                price = int(price_str)
                if price < 1000:
                    price *= 1000

            if any(word in query for word in ["under", "below", "less than", "within", "upto", "up to"]):
                params["price_max"] = price
            elif "around" in query:
                params["price_min"] = int(price * 0.8)
                params["price_max"] = int(price * 1.2)
            else:
                params["price_max"] = price

        brand_match = self.BRAND_PATTERN.search(query)
        if brand_match:
            brand = brand_match.group(1).lower()
            # Normalize brand names
            brand_map = {
                "one plus": "OnePlus",
                "oneplus": "OnePlus",
                "mi": "Xiaomi",
                "redmi": "Xiaomi",
                "moto": "Motorola",
                "pixel": "Google"
            }
            params["brand"] = brand_map.get(brand, brand.title())

        features = []
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                features.append(feature)
        if features:
            params["features"] = features

        ram_match = re.search(r'(\d+)\s*gb\s*(?:ram)?', query, re.IGNORECASE)
        if ram_match:
            params["min_ram"] = int(ram_match.group(1))

        return params


_intent_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get intent classifier singleton."""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier
