import re
from dataclasses import dataclass
from enum import Enum

from app.services.classification_service import CATEGORY_KEYWORDS, PHRASE_HINTS


class ChatIntentType(str, Enum):
    GREETING = "GREETING"
    SMALL_TALK = "SMALL_TALK"
    SUPPORT_REQUEST = "SUPPORT_REQUEST"
    IRRELEVANT = "IRRELEVANT"
    ABUSIVE = "ABUSIVE"
    EMPTY = "EMPTY"


@dataclass(frozen=True)
class ChatIntentResult:
    intent_type: ChatIntentType
    cleaned_text: str
    confidence: float
    reason: str
    escalation_requested: bool = False


class ChatIntentService:
    GREETINGS = {
        "hi",
        "hello",
        "hey",
        "hiya",
        "good morning",
        "good afternoon",
        "good evening",
    }
    SMALL_TALK = {
        "how are you",
        "what can you do",
        "who are you",
        "thanks",
        "thank you",
        "are you a bot",
    }
    IRRELEVANT = {
        "joke",
        "weather",
        "prime minister",
        "pm of",
        "president",
        "sports",
        "movie",
        "recipe",
        "stock price",
        "capital of",
        "news",
    }
    FRUSTRATION = {
        "useless",
        "stupid",
        "terrible",
        "sucks",
        "not helpful",
        "waste of time",
        "angry",
        "frustrated",
        "connect me to human",
        "give me human",
        "give me a technician",
        "connect me to technician",
    }
    HUMAN_REQUESTS = {
        "human",
        "agent",
        "technician",
        "support person",
        "talk to someone",
        "connect me",
    }
    GENERIC_SUPPORT = {
        "not working",
        "broken",
        "issue",
        "problem",
        "error",
        "failed",
        "failing",
        "can't",
        "cannot",
        "unable",
        "blocked",
        "stuck",
        "slow",
        "locked",
        "down",
        "human support",
        "need support now",
        "it support",
        "support ticket",
    }

    def route(self, text: str) -> ChatIntentResult:
        original = text or ""
        compact = " ".join(original.strip().split())
        lower = compact.lower()
        normalized = re.sub(r"[^a-z0-9\s'-]", " ", lower)
        normalized = " ".join(normalized.split())

        if not compact:
            return ChatIntentResult(ChatIntentType.EMPTY, "", 0.99, "No user content.")

        cleaned = self._remove_leading_greeting(compact)
        cleaned_lower = cleaned.lower()
        support_score = self._support_score(normalized)
        has_support = support_score > 0
        has_frustration = any(phrase in normalized for phrase in self.FRUSTRATION)
        escalation_requested = any(phrase in normalized for phrase in self.HUMAN_REQUESTS)
        has_irrelevant_request = any(phrase in normalized for phrase in self.IRRELEVANT)
        has_problem_cue = self._has_problem_cue(normalized)

        if has_irrelevant_request and not has_problem_cue:
            return ChatIntentResult(ChatIntentType.IRRELEVANT, compact, 0.9, "Out-of-scope request.")

        if has_support and cleaned_lower:
            return ChatIntentResult(ChatIntentType.SUPPORT_REQUEST, cleaned, min(0.95, 0.55 + support_score * 0.08), "Support cues detected.", escalation_requested)

        if has_frustration or escalation_requested:
            return ChatIntentResult(ChatIntentType.ABUSIVE, cleaned or compact, 0.86, "Frustration or human handoff wording detected.", escalation_requested)

        if self._is_greeting_only(normalized):
            return ChatIntentResult(ChatIntentType.GREETING, "", 0.95, "Greeting only.")

        if any(phrase == normalized or phrase in normalized for phrase in self.SMALL_TALK):
            return ChatIntentResult(ChatIntentType.SMALL_TALK, "", 0.9, "Small talk.")

        if self._looks_random(normalized):
            return ChatIntentResult(ChatIntentType.EMPTY, "", 0.82, "Random or insufficient content.")

        return ChatIntentResult(ChatIntentType.IRRELEVANT, compact, 0.62, "No IT support signal detected.")

    def _support_score(self, normalized: str) -> int:
        score = sum(1 for phrase in self.GENERIC_SUPPORT if phrase in normalized)
        score += sum(2 for phrase in PHRASE_HINTS if phrase in normalized)
        for keywords in CATEGORY_KEYWORDS.values():
            score += sum(1 for keyword in keywords if keyword in normalized)
        return score

    def _is_greeting_only(self, normalized: str) -> bool:
        if normalized in self.GREETINGS:
            return True
        tokens = normalized.split()
        return bool(tokens) and len(tokens) <= 3 and all(token in {"hi", "hello", "hey", "there", "team"} for token in tokens)

    def _has_problem_cue(self, normalized: str) -> bool:
        return any(phrase in normalized for phrase in self.GENERIC_SUPPORT) or any(phrase in normalized for phrase in PHRASE_HINTS)

    def _remove_leading_greeting(self, text: str) -> str:
        cleaned = text.strip()
        for greeting in sorted(self.GREETINGS, key=len, reverse=True):
            pattern = re.compile(rf"^\s*{re.escape(greeting)}[\s,!.:-]+", re.IGNORECASE)
            cleaned = pattern.sub("", cleaned).strip()
        return cleaned

    def _looks_random(self, normalized: str) -> bool:
        if len(normalized) <= 4:
            return True
        tokens = normalized.split()
        if len(tokens) == 1 and not any(vowel in normalized for vowel in "aeiou"):
            return True
        return False
