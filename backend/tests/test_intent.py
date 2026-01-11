"""Tests for the intent classifier."""

import pytest
from app.core.intent_classifier import IntentClassifier, get_intent_classifier


class TestIntentClassifier:
    """Tests for IntentClassifier class."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    QUERY_TEST_CASES = [
        # Search queries
        ("Best camera phone under 30,000", "budget_search"),
        ("Show me flagship phones", "search_phones"),
        ("I need a good phone for gaming", "search_phones"),

        # Budget queries
        ("Phones under Rs 20000", "budget_search"),
        ("Budget smartphones around 15k", "budget_search"),
        ("Affordable phones below 25000", "budget_search"),

        # Brand queries
        ("Show me Samsung phones", "filter_by_brand"),
        ("OnePlus phones under 40k", "budget_search"),  # Has price constraint, prioritizes budget
        ("Google Pixel options", "filter_by_brand"),

        # Comparison queries
        ("Compare Samsung S24 vs OnePlus 12", "compare_phones"),
        ("Which is better Pixel 8 or iPhone 15?", "compare_phones"),
        ("Difference between Xiaomi 14 and OnePlus 12", "compare_phones"),

        # Feature explanation queries
        ("What is AMOLED display?", "explain_feature"),
        ("Explain OIS in cameras", "explain_feature"),
        ("What does mAh mean?", "explain_feature"),

        # Chitchat
        ("Hello", "chitchat"),
        ("Thanks for the help", "chitchat"),
        ("Hi there", "chitchat"),
    ]

    @pytest.mark.parametrize("query,expected_intent", QUERY_TEST_CASES)
    def test_intent_classification(self, classifier, query, expected_intent):
        """Test that queries are classified correctly."""
        result = classifier.classify(query)
        assert result["intent"] == expected_intent, \
            f"Query '{query}' should have intent '{expected_intent}', got '{result['intent']}'"
        assert 0 <= result["confidence"] <= 1

    def test_price_extraction(self, classifier):
        """Test price extraction from queries."""
        test_cases = [
            ("under 30000", 30000),
            ("below Rs 25k", 25000),
            ("around 50000", None),  # "around" creates a range
            ("budget of 20k", 20000),
            ("less than 15000", 15000),
        ]

        for query, expected_max in test_cases:
            result = classifier.classify(query)
            params = result["extracted_params"]

            if expected_max:
                assert "price_max" in params, f"Should extract price from: {query}"
                assert params["price_max"] == expected_max, \
                    f"Expected max price {expected_max}, got {params.get('price_max')}"

    def test_brand_extraction(self, classifier):
        """Test brand extraction from queries."""
        test_cases = [
            ("Samsung phones", "Samsung"),
            ("Show me OnePlus options", "OnePlus"),
            ("Google Pixel phones", "Google"),
            ("Xiaomi under 20k", "Xiaomi"),
            ("Redmi phones", "Xiaomi"),  # Redmi should map to Xiaomi
        ]

        for query, expected_brand in test_cases:
            result = classifier.classify(query)
            params = result["extracted_params"]

            assert "brand" in params, f"Should extract brand from: {query}"
            assert params["brand"] == expected_brand, \
                f"Expected brand '{expected_brand}', got '{params.get('brand')}'"

    def test_feature_extraction(self, classifier):
        """Test feature extraction from queries."""
        test_cases = [
            ("best camera phone", ["camera"]),
            ("gaming phone with good battery", ["gaming", "battery"]),
            ("compact phone with 5G", ["compact", "5g"]),
            ("flagship with fast charging", ["flagship", "fast_charging"]),
        ]

        for query, expected_features in test_cases:
            result = classifier.classify(query)
            params = result["extracted_params"]

            if expected_features:
                assert "features" in params, f"Should extract features from: {query}"
                for feature in expected_features:
                    assert feature in params["features"], \
                        f"Expected feature '{feature}' in: {query}"

    def test_ram_extraction(self, classifier):
        """Test RAM extraction from queries."""
        result = classifier.classify("Phone with 8GB RAM")
        params = result["extracted_params"]

        assert "min_ram" in params
        assert params["min_ram"] == 8

    def test_combined_extraction(self, classifier):
        """Test extraction of multiple parameters."""
        query = "Samsung phone under 30000 with good camera"
        result = classifier.classify(query)
        params = result["extracted_params"]

        assert params.get("brand") == "Samsung"
        assert params.get("price_max") == 30000
        assert "camera" in params.get("features", [])

    def test_confidence_levels(self, classifier):
        """Test that confidence levels are reasonable."""
        # Clear intent should have high confidence
        result = classifier.classify("Compare Samsung S24 vs OnePlus 12")
        assert result["confidence"] >= 0.6

        # Ambiguous query should have lower confidence
        result = classifier.classify("phone")
        assert result["confidence"] < 0.8


class TestIntentClassifierSingleton:
    """Test intent classifier singleton."""

    def test_singleton_instance(self):
        """Test that get_intent_classifier returns same instance."""
        classifier1 = get_intent_classifier()
        classifier2 = get_intent_classifier()
        assert classifier1 is classifier2
