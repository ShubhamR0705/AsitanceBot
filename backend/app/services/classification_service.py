import re
from dataclasses import dataclass


CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "VPN": {"vpn", "vpm", "anyconnect", "globalprotect", "forticlient", "gateway", "mfa", "tunnel", "company apps", "internal apps"},
    "PASSWORD": {"password", "passwrd", "pwd", "reset", "forgot", "credentials"},
    "ACCESS": {"access", "permission", "permissions", "locked", "unlock", "login", "signin", "sign", "sso", "mfa", "authenticator", "payroll", "hr portal", "portal", "403", "forbidden"},
    "WIFI": {"wifi", "wi-fi", "wireless", "ssid", "router", "access point"},
    "NETWORK": {"network", "internet", "ethernet", "lan", "dns", "dhcp", "intranet", "websites", "connection"},
    "EMAIL": {"email", "outlook", "outlok", "mail", "office mail", "mailbox", "calendar", "attachment", "sync", "syncng", "send", "stuck"},
    "DEVICE_PERFORMANCE": {"slow", "performance", "laptop", "device", "freeze", "freezing", "hang", "hangs", "lag", "memory", "cpu", "disk"},
    "SOFTWARE": {"software", "install", "installation", "update", "license", "licence", "application", "app", "teams", "zoom", "slack", "crash", "crashing"},
    "BROWSER": {"browser", "chrome", "edge", "firefox", "safari", "cache", "cookies", "website", "web page", "page"},
    "PRINTER": {"printer", "printing", "print", "scanner", "scan", "paper", "toner", "queue"},
}

PHRASE_HINTS: dict[str, str] = {
    "password not taking": "PASSWORD",
    "cant login": "PASSWORD",
    "can't login": "PASSWORD",
    "cannot login": "PASSWORD",
    "login issue": "ACCESS",
    "log in": "ACCESS",
    "logging in": "ACCESS",
    "sign in": "ACCESS",
    "signing in": "ACCESS",
    "office login": "PASSWORD",
    "account locked": "PASSWORD",
    "forgot password": "PASSWORD",
    "reset link": "PASSWORD",
    "password reset": "PASSWORD",
    "mfa code": "ACCESS",
    "mfa prompt": "ACCESS",
    "authenticator": "ACCESS",
    "access denied": "ACCESS",
    "permission denied": "ACCESS",
    "payroll access": "ACCESS",
    "mail stuck": "EMAIL",
    "office mail": "EMAIL",
    "not syncing": "EMAIL",
    "not syncng": "EMAIL",
    "company apps are not opening": "VPN",
    "internal apps": "VPN",
    "vpn conection": "VPN",
    "vpn connection": "VPN",
    "laptop hangs": "DEVICE_PERFORMANCE",
    "system slow": "DEVICE_PERFORMANCE",
    "app crashed": "SOFTWARE",
    "application crashed": "SOFTWARE",
    "software install": "SOFTWARE",
    "browser not loading": "BROWSER",
    "website not opening": "BROWSER",
    "printer offline": "PRINTER",
    "print queue": "PRINTER",
    "ethernet not working": "NETWORK",
    "dns issue": "NETWORK",
}


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    confidence: float
    matched_keywords: list[str]


class ClassificationService:
    def classify(self, text: str) -> ClassificationResult:
        lower_text = text.lower()
        words = set(re.findall(r"[a-z0-9-]+", lower_text))
        scores: list[tuple[str, int, list[str]]] = []

        for category, keywords in CATEGORY_KEYWORDS.items():
            matched = sorted(keyword for keyword in keywords if keyword in words or keyword in lower_text)
            phrase_hits = [phrase for phrase, phrase_category in PHRASE_HINTS.items() if phrase_category == category and phrase in lower_text]
            all_matches = sorted(set(matched + phrase_hits))
            scores.append((category, len(matched) + len(phrase_hits) * 2, all_matches))

        best_category, best_score, matched_keywords = max(scores, key=lambda item: item[1])
        if best_score == 0:
            return ClassificationResult(category="GENERAL", confidence=0.25, matched_keywords=[])

        if best_category == "ACCESS" and "vpn" in lower_text and not any(
            term in lower_text
            for term in ["access", "account", "login", "log in", "logging in", "password", "portal", "sign in", "signin", "sso"]
        ):
            vpn_score = next((score for category, score, _ in scores if category == "VPN"), 0)
            if vpn_score > 0:
                vpn_matches = next((matches for category, _, matches in scores if category == "VPN"), ["vpn"])
                return ClassificationResult(category="VPN", confidence=min(0.95, 0.55 + vpn_score * 0.15), matched_keywords=vpn_matches)

        confidence = min(0.95, 0.45 + best_score * 0.15)
        return ClassificationResult(category=best_category, confidence=confidence, matched_keywords=matched_keywords)
