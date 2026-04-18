from app.services.diagnostic_playbooks import DiagnosticField


class GuidedQuestionService:
    GENERIC_QUESTIONS = {
        "device_type": "Which device are you using, such as laptop, phone, or desktop?",
        "device_os": "Which operating system are you using, such as Windows or macOS?",
        "application": "Which application or company service is affected?",
        "affected_app": "Which application or company service is affected?",
        "error_message": "What exact error message do you see?",
        "business_impact": "Is this blocking your work or affecting multiple people?",
        "urgency": "How urgent is this for your work today?",
    }
    DEFAULT_OPTIONS = [
        {"label": "Yes", "value": "yes"},
        {"label": "No", "value": "no"},
        {"label": "Not sure", "value": "unknown"},
        {"label": "Other", "value": "other", "requires_text": True},
    ]

    FIELD_OPTIONS: dict[str, list[dict]] = {
        "account_locked": [
            {"label": "Yes - account locked", "value": "yes"},
            {"label": "No - different error", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "mfa_available": [
            {"label": "Yes - I can access MFA", "value": "yes"},
            {"label": "No - MFA unavailable", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "mfa_prompt": [
            {"label": "Yes - prompt appears", "value": "yes"},
            {"label": "No - no prompt", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "internet_working": [
            {"label": "Yes - normal websites work", "value": "yes"},
            {"label": "No - internet is down", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "device_os": [
            {"label": "Windows laptop", "value": "windows"},
            {"label": "macOS", "value": "macos"},
            {"label": "Ubuntu/Linux", "value": "linux"},
            {"label": "Mobile device", "value": "mobile"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "device_type": [
            {"label": "Laptop", "value": "laptop"},
            {"label": "Desktop", "value": "desktop"},
            {"label": "Phone or tablet", "value": "mobile"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "webmail_works": [
            {"label": "Yes - webmail works", "value": "yes"},
            {"label": "No - webmail also fails", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "email_client": [
            {"label": "Outlook", "value": "outlook"},
            {"label": "Webmail", "value": "webmail"},
            {"label": "Apple Mail", "value": "apple_mail"},
            {"label": "Gmail", "value": "gmail"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "send_receive_scope": [
            {"label": "Sending", "value": "sending"},
            {"label": "Receiving", "value": "receiving"},
            {"label": "Sync/calendar", "value": "sync"},
            {"label": "Attachments", "value": "attachments"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "connection_type": [
            {"label": "WiFi", "value": "wifi"},
            {"label": "Ethernet", "value": "ethernet"},
            {"label": "VPN", "value": "vpn"},
            {"label": "Mobile hotspot", "value": "hotspot"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "scope": [
            {"label": "All websites are down", "value": "all_sites"},
            {"label": "Only company/internal services", "value": "company_services"},
            {"label": "Only one app or site", "value": "single_service"},
            {"label": "Not sure", "value": "unknown"},
        ],
        "other_users_affected": [
            {"label": "Yes - others affected", "value": "yes"},
            {"label": "No - only me", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
        ],
        "restart_done": [
            {"label": "Yes - restarted already", "value": "yes"},
            {"label": "No - not yet", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
        ],
        "cache_cleared": [
            {"label": "Yes - tried private window/cache clear", "value": "yes"},
            {"label": "No - not yet", "value": "no"},
            {"label": "Not sure", "value": "unknown"},
        ],
        "business_impact": [
            {"label": "Blocking my work", "value": "blocking_work"},
            {"label": "Affecting multiple people", "value": "multiple_users"},
            {"label": "Security concern", "value": "security"},
            {"label": "Minor inconvenience", "value": "minor"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
    }
    MULTI_SELECT_FIELDS = {"business_impact"}

    def build(
        self,
        *,
        fields: tuple[DiagnosticField, ...],
        missing_fields: list[str],
        questions: list[str],
    ) -> list[dict]:
        field_by_key = {field.key: field for field in fields}
        structured_questions: list[dict] = []
        used_fields: set[str] = set()

        for question in questions:
            field_key = self._field_for_question(question, fields, missing_fields)
            if not field_key or field_key in used_fields:
                continue
            used_fields.add(field_key)
            field = field_by_key.get(field_key)

            structured_questions.append(
                {
                    "type": "question",
                    "question": question,
                    "field": field_key,
                    "input_type": "multi_select" if field_key in self.MULTI_SELECT_FIELDS else "single_select",
                    "options": self.FIELD_OPTIONS.get(field_key, self.DEFAULT_OPTIONS),
                }
            )
            if len(structured_questions) >= 3:
                break

        return structured_questions

    def _field_for_question(self, question: str, fields: tuple[DiagnosticField, ...], missing_fields: list[str]) -> str | None:
        for field in fields:
            if field.key in missing_fields and field.question == question:
                return field.key
        for field_key in missing_fields:
            if self.GENERIC_QUESTIONS.get(field_key) == question:
                return field_key
        return None

    def _generic_question(self, field_key: str) -> str:
        return self.GENERIC_QUESTIONS.get(field_key, f"What should I know about {field_key.replace('_', ' ')}?")
