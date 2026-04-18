from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse


ActionType = Literal["link", "internal_route", "trigger"]


@dataclass(frozen=True)
class ChatAction:
    label: str
    type: ActionType
    url: str | None = None
    route: str | None = None
    trigger: str | None = None

    def to_dict(self) -> dict:
        payload = {"label": self.label, "type": self.type}
        if self.url:
            payload["url"] = self.url
        if self.route:
            payload["route"] = self.route
        if self.trigger:
            payload["trigger"] = self.trigger
        return payload


class ActionRegistry:
    """Predefined safe actions that can be attached to assistant messages."""

    ALLOWED_HOSTS = {"company.com", "mail.company.com"}
    ALLOWED_TRIGGERS = {"request_human_support"}
    MAX_ACTIONS = 3

    RESET_PASSWORD = ChatAction("Reset Password", "link", url="https://company.com/reset-password")
    MFA_HELP = ChatAction("Unlock Account / MFA Help", "link", url="https://company.com/account-help")
    VPN_SETUP = ChatAction("Open VPN Setup", "link", url="https://company.com/vpn-guide")
    VPN_DOWNLOAD = ChatAction("Download VPN Client", "link", url="https://company.com/vpn-download")
    NETWORK_TROUBLESHOOTER = ChatAction("Open Network Troubleshooter", "link", url="https://company.com/network-troubleshooter")
    WEBMAIL = ChatAction("Open Webmail", "link", url="https://mail.company.com")
    SYSTEM_HELP = ChatAction("Restart/System Help Guide", "link", url="https://company.com/system-help")
    COMPANY_TOOLS = ChatAction("Open Internal Company Tools", "link", url="https://company.com/tools")
    PRINTER_SETUP = ChatAction("Printer Setup Guide", "link", url="https://company.com/printer-setup")
    BROWSER_FIX = ChatAction("Browser Fix Guide", "link", url="https://company.com/browser-cache")

    CATEGORY_ACTIONS: dict[str, tuple[ChatAction, ...]] = {
        "PASSWORD": (RESET_PASSWORD, MFA_HELP),
        "ACCESS": (MFA_HELP, COMPANY_TOOLS),
        "VPN": (VPN_SETUP, VPN_DOWNLOAD),
        "WIFI": (NETWORK_TROUBLESHOOTER,),
        "NETWORK": (NETWORK_TROUBLESHOOTER,),
        "EMAIL": (WEBMAIL,),
        "DEVICE_PERFORMANCE": (SYSTEM_HELP,),
        "SOFTWARE": (COMPANY_TOOLS,),
        "BROWSER": (BROWSER_FIX,),
        "PRINTER": (PRINTER_SETUP,),
    }

    def actions_for_category(self, category: str | None, *, confidence: float, has_support_path: bool = True) -> list[dict]:
        if not has_support_path or confidence < 0.45:
            return []
        actions = self.CATEGORY_ACTIONS.get((category or "GENERAL").upper(), ())
        return self.validate_many([action.to_dict() for action in actions[: self.MAX_ACTIONS]])

    def escalation_actions(self, ticket_id: int | None = None) -> list[dict]:
        route = f"/user/tickets/{ticket_id}" if ticket_id else "/user/tickets"
        return self.validate_many(
            [
                {
                    "label": "Connect to Technician",
                    "type": "internal_route",
                    "route": route,
                }
            ]
        )

    def validate_many(self, actions: list[dict]) -> list[dict]:
        validated: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for action in actions:
            clean = self.validate(action)
            if not clean:
                continue
            identity = (clean["label"], clean.get("url") or clean.get("route") or clean.get("trigger") or "")
            if identity in seen:
                continue
            seen.add(identity)
            validated.append(clean)
            if len(validated) >= self.MAX_ACTIONS:
                break
        return validated

    def validate(self, action: dict) -> dict | None:
        label = str(action.get("label") or "").strip()
        action_type = str(action.get("type") or "").strip()
        if not label or len(label) > 80 or action_type not in {"link", "internal_route", "trigger"}:
            return None

        if action_type == "link":
            url = str(action.get("url") or "").strip()
            if not self._is_allowed_url(url):
                return None
            return {"label": label, "type": action_type, "url": url}

        if action_type == "internal_route":
            route = str(action.get("route") or "").strip()
            if not self._is_allowed_route(route):
                return None
            return {"label": label, "type": action_type, "route": route}

        trigger = str(action.get("trigger") or "").strip()
        if trigger not in self.ALLOWED_TRIGGERS:
            return None
        return {"label": label, "type": action_type, "trigger": trigger}

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in self.ALLOWED_HOSTS:
            return False
        return bool(parsed.path or parsed.hostname == "mail.company.com")

    def _is_allowed_route(self, route: str) -> bool:
        return route.startswith("/user/tickets") and "//" not in route and ".." not in route
