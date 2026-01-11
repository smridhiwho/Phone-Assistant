import re
import logging
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class SafetyFilter:
    """Multi-layer safety filter for adversarial input detection."""

    ADVERSARIAL_PATTERNS = [
        r"ignore\s+(previous|above|prior|all)\s+(instructions?|rules?|prompts?)",
        r"disregard\s+(previous|above|prior|all)\s+(instructions?|rules?)",
        r"forget\s+(everything|all|previous)",
        r"new\s+instructions?:",
        r"override\s+(system|instructions?|rules?)",
        r"system\s*:\s*",
        r"\[system\]",
        r"<\s*system\s*>",
        r"previous\s+instructions?\s+(are\s+)?cancel",
        r"new\s+role",

        r"(reveal|show|display|print|output)\s+(your|the)\s+(prompt|system|instructions?|rules?|source\s*code)",
        r"what\s+(are|is)\s+your\s+(prompt|instructions?|rules?|system|hidden)",
        r"(tell|show)\s+me\s+(your|the)\s+(prompt|system|instructions?)",
        r"(give|provide)\s+me\s+(your|the)\s+(api|key|token|credentials?)",
        r"api\s*[-_]?\s*key",
        r"secret\s*[-_]?\s*key",
        r"access\s*[-_]?\s*token",
        r"hidden\s+instructions?",
        r"reveal.+source\s*code",
        r"your\s+source\s*code",

        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode",
        r"bypass\s+(safety|filter|restriction)",
        r"pretend\s+you\s+(are|can|don't|have)",
        r"act\s+as\s+if\s+you",
        r"roleplay\s+as",
        r"imagine\s+you\s+(are|can|don't)",

        r"you\s+are\s+now\s+a",
        r"from\s+now\s+on\s+you",
        r"your\s+new\s+(role|purpose|function)",
        r"switch\s+to\s+\w+\s+mode",

        r"(how\s+to\s+)?(hack|exploit|attack|breach)",
        r"write\s+(malware|virus|trojan)",
        r"(steal|extract)\s+(data|information|credentials?)",
        r"extract\s+user\s+data",
    ]

    OFF_TOPIC_PATTERNS = [
        r"(politics|political|election|vote|party)",
        r"(religion|religious|god|prayer)",
        r"(medical|health|doctor|disease|symptom|diagnosis)",
        r"(legal|lawyer|lawsuit|sue)",
        r"(invest|stock|crypto|bitcoin|trading)",
        r"(recipe|cook|food|restaurant)",
        r"(dating|relationship|love)",
        r"(weather|temperature|forecast)",
    ]

    PHONE_RELATED_ALLOW = [
        "system update", "system version", "operating system", "android system",
        "security patch", "security update", "security features",
        "developer options", "developer settings",
        "password", "fingerprint", "face unlock",  # phone security features
        "hack" + r"(?:athon|er\s+news)"  # hackathon, hacker news (allowed)
    ]

    def __init__(self):
        self.compiled_adversarial = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.ADVERSARIAL_PATTERNS
        ]
        self.compiled_off_topic = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.OFF_TOPIC_PATTERNS
        ]
        self.compiled_allow = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PHONE_RELATED_ALLOW
        ]

    def check_input(self, query: str) -> Dict[str, Any]:
        """
        Check if input is safe.

        Returns:
            Dict with:
            - is_safe: bool
            - is_adversarial: bool
            - is_off_topic: bool
            - reason: str (if not safe)
            - severity: str (low/medium/high)
        """
        logger.info("[SAFETY] check_input() called")
        logger.info(f"[SAFETY] Query: {query[:200]}..." if len(query) > 200 else f"[SAFETY] Query: {query}")

        if not query or not query.strip():
            logger.warning("[SAFETY] Empty query detected")
            return {
                "is_safe": False,
                "is_adversarial": False,
                "is_off_topic": False,
                "reason": "Empty query",
                "severity": "low"
            }

        query_lower = query.lower().strip()

        # Check for phone-related allowlist first
        for pattern in self.compiled_allow:
            if pattern.search(query_lower):
                logger.info("[SAFETY] Query matches allowlist - SAFE")
                return {
                    "is_safe": True,
                    "is_adversarial": False,
                    "is_off_topic": False,
                    "reason": None,
                    "severity": None
                }

        # Check adversarial patterns
        for pattern in self.compiled_adversarial:
            if pattern.search(query_lower):
                logger.warning(f"[SAFETY] ADVERSARIAL pattern matched: {pattern.pattern}")
                return {
                    "is_safe": False,
                    "is_adversarial": True,
                    "is_off_topic": False,
                    "reason": "Potential adversarial input detected",
                    "severity": self._determine_severity(pattern.pattern)
                }

        # Check off-topic patterns (but be lenient)
        off_topic_matches = sum(
            1 for pattern in self.compiled_off_topic
            if pattern.search(query_lower)
        )

        # Only flag as off-topic if clearly not phone-related
        phone_keywords = [
            "phone", "mobile", "smartphone", "device", "app",
            "battery", "camera", "display", "screen", "processor",
            "ram", "storage", "android", "ios", "samsung", "oneplus",
            "google", "pixel", "xiaomi", "realme", "vivo", "oppo"
        ]
        has_phone_context = any(kw in query_lower for kw in phone_keywords)

        if off_topic_matches > 0 and not has_phone_context:
            logger.info(f"[SAFETY] Off-topic matches: {off_topic_matches}, phone context: {has_phone_context}")
            if off_topic_matches >= 2:
                logger.warning("[SAFETY] OFF-TOPIC query detected")
                return {
                    "is_safe": False,
                    "is_adversarial": False,
                    "is_off_topic": True,
                    "reason": "Query appears to be off-topic (not phone-related)",
                    "severity": "low"
                }

        # Check for excessive length (potential payload)
        if len(query) > 2000:
            logger.warning(f"[SAFETY] Query too long: {len(query)} chars")
            return {
                "is_safe": False,
                "is_adversarial": True,
                "is_off_topic": False,
                "reason": "Query exceeds maximum length",
                "severity": "medium"
            }

        if self._has_suspicious_characters(query):
            logger.warning("[SAFETY] Suspicious characters detected")
            return {
                "is_safe": False,
                "is_adversarial": True,
                "is_off_topic": False,
                "reason": "Suspicious character patterns detected",
                "severity": "medium"
            }

        logger.info("[SAFETY] Query is SAFE")
        return {
            "is_safe": True,
            "is_adversarial": False,
            "is_off_topic": False,
            "reason": None,
            "severity": None
        }

    def _determine_severity(self, pattern: str) -> str:
        """Determine severity based on pattern type."""
        high_severity_keywords = [
            "api", "key", "token", "credentials", "hack", "exploit",
            "malware", "virus", "steal", "extract"
        ]
        medium_severity_keywords = [
            "ignore", "override", "jailbreak", "bypass", "reveal"
        ]

        pattern_lower = pattern.lower()
        if any(kw in pattern_lower for kw in high_severity_keywords):
            return "high"
        if any(kw in pattern_lower for kw in medium_severity_keywords):
            return "medium"
        return "low"

    def _has_suspicious_characters(self, text: str) -> bool:
        """Check for suspicious character patterns."""
        special_chars = sum(1 for c in text if c in "{}[]<>\\|`~^")
        if special_chars > 10:
            return True

        encoding_patterns = [
            r"base64",
            r"\\x[0-9a-f]{2}",
            r"%[0-9a-f]{2}",
            r"&#\d+;",
        ]
        for pattern in encoding_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def sanitize_output(self, response: str) -> str:
        """Sanitize output to prevent prompt leakage."""
        # Patterns that might indicate prompt leakage
        leakage_patterns = [
            r"system\s+prompt",
            r"my\s+instructions",
            r"I\s+was\s+told\s+to",
            r"I\s+am\s+programmed\s+to",
            r"my\s+rules\s+are",
        ]

        for pattern in leakage_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return "I'm a mobile phone shopping assistant. How can I help you find your perfect phone?"

        return response

    def get_safe_response(self, check_result: Dict[str, Any]) -> str:
        """Generate appropriate response for unsafe input."""
        logger.info("[SAFETY] get_safe_response() called")
        logger.info(f"[SAFETY] Check result: {check_result}")

        if check_result.get("is_adversarial"):
            logger.warning("[SAFETY] Returning HARDCODED adversarial response")
            return (
                "I'm a mobile phone shopping assistant focused on helping you "
                "find the perfect smartphone. I can help with phone recommendations, "
                "comparisons, and feature explanations. How can I assist you with "
                "your phone search today?"
            )

        if check_result.get("is_off_topic"):
            logger.warning("[SAFETY] Returning HARDCODED off-topic response")
            return (
                "I specialize in mobile phone shopping assistance. I can help you "
                "find phones based on your budget, compare different models, or "
                "explain phone features. What would you like to know about smartphones?"
            )

        logger.warning("[SAFETY] Returning HARDCODED generic response")
        return (
            "I didn't quite understand that. I'm here to help you find the perfect "
            "mobile phone. You can ask me about phone recommendations, comparisons, "
            "or specific features. How can I help?"
        )


# Singleton instance
_safety_filter: Optional[SafetyFilter] = None


def get_safety_filter() -> SafetyFilter:
    """Get safety filter singleton."""
    global _safety_filter
    if _safety_filter is None:
        _safety_filter = SafetyFilter()
    return _safety_filter
