from typing import Dict, Any, List, Optional
from app.models.database import Phone


class QueryProcessor:
    """Processes queries and extracts search parameters."""

    def process(
        self,
        query: str,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process query based on classified intent."""
        intent_type = intent.get("intent", "search_phones")
        params = intent.get("extracted_params", {})

        search_criteria = {
            "query": query,
            "intent": intent_type,
            "filters": {}
        }

        if params.get("price_max"):
            search_criteria["filters"]["max_price"] = params["price_max"]
        if params.get("price_min"):
            search_criteria["filters"]["min_price"] = params["price_min"]

        if params.get("brand"):
            search_criteria["filters"]["brand"] = params["brand"]

        if params.get("min_ram"):
            search_criteria["filters"]["min_ram"] = params["min_ram"]

        features = params.get("features", [])
        if features:
            search_criteria["filters"]["features"] = features

            if "camera" in features:
                search_criteria["search_type"] = "camera"
            elif "gaming" in features:
                search_criteria["search_type"] = "gaming"
            elif "battery" in features:
                search_criteria["search_type"] = "battery"
            elif "compact" in features:
                search_criteria["search_type"] = "compact"

        return search_criteria

    def extract_phone_ids(self, query: str, phones: List[Phone]) -> List[int]:
        """Extract phone IDs mentioned in query."""
        query_lower = query.lower()
        mentioned_ids = []

        for phone in phones:
            phone_name = f"{phone.brand} {phone.model}".lower()
            model_only = phone.model.lower()

            if phone_name in query_lower or model_only in query_lower:
                mentioned_ids.append(phone.id)

        return mentioned_ids

    def get_comparison_phones(
        self,
        query: str,
        available_phones: List[Phone]
    ) -> List[int]:
        """Identify phones to compare from query."""
        mentioned = self.extract_phone_ids(query, available_phones)
        if len(mentioned) >= 2:
            return mentioned[:4]  # Max 4 for comparison

        if mentioned:
            target = next(p for p in available_phones if p.id == mentioned[0])
            similar = self._find_similar_phones(target, available_phones)
            return [target.id] + [p.id for p in similar[:2]]

        return []

    def _find_similar_phones(
        self,
        target: Phone,
        phones: List[Phone],
        count: int = 2
    ) -> List[Phone]:
        """Find phones similar to target by price range."""
        price_range = 0.25  # 25% price difference
        min_price = target.price_inr * (1 - price_range)
        max_price = target.price_inr * (1 + price_range)

        similar = [
            p for p in phones
            if p.id != target.id
            and min_price <= p.price_inr <= max_price
        ]

        similar.sort(key=lambda p: abs(p.price_inr - target.price_inr))
        return similar[:count]

_query_processor: Optional[QueryProcessor] = None


def get_query_processor() -> QueryProcessor:
    """Get query processor singleton."""
    global _query_processor
    if _query_processor is None:
        _query_processor = QueryProcessor()
    return _query_processor
