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
    GENERIC_OPTION_LABELS = {"yes", "no", "not sure"}
    BOOLEAN_FIELDS = {
        "account_locked",
        "cache_cleared",
        "internet_working",
        "mfa_available",
        "mfa_prompt",
        "other_devices_working",
        "other_users_affected",
        "reset_attempted",
        "restart_done",
        "webmail_works",
    }
    MULTI_SELECT_FIELDS = {"business_impact"}

    CATEGORY_ISSUE_QUESTIONS: dict[str, dict] = {
        "VPN": {
            "type": "question",
            "question": "What is happening with the VPN?",
            "field": "vpn_issue_type",
            "input_type": "single_select",
            "source": "rule_based",
            "options": [
                {"label": "Cannot connect", "value": "cannot_connect"},
                {"label": "Connected but no internet", "value": "connected_no_internet"},
                {"label": "Slow connection", "value": "slow_connection"},
                {"label": "Disconnecting frequently", "value": "disconnecting"},
                {"label": "Other", "value": "other", "requires_text": True},
            ],
        },
        "WIFI": {
            "type": "question",
            "question": "What WiFi problem are you seeing?",
            "field": "wifi_issue_type",
            "input_type": "single_select",
            "source": "rule_based",
            "options": [
                {"label": "No networks visible", "value": "no_networks_visible"},
                {"label": "Connected but no internet", "value": "connected_no_internet"},
                {"label": "Slow internet", "value": "slow_internet"},
                {"label": "Frequent disconnect", "value": "frequent_disconnect"},
                {"label": "Other", "value": "other", "requires_text": True},
            ],
        },
        "PASSWORD": {
            "type": "question",
            "question": "What password or sign-in problem are you seeing?",
            "field": "password_issue_type",
            "input_type": "single_select",
            "source": "rule_based",
            "options": [
                {"label": "Forgot password", "value": "forgot_password"},
                {"label": "Account locked", "value": "account_locked"},
                {"label": "Incorrect password error", "value": "incorrect_password"},
                {"label": "MFA issue", "value": "mfa_issue"},
                {"label": "Other", "value": "other", "requires_text": True},
            ],
        },
    }

    SERVICE_OPTIONS = [
        {"label": "Email (Outlook/Gmail)", "value": "email"},
        {"label": "VPN", "value": "vpn"},
        {"label": "Company Portal", "value": "company_portal"},
        {"label": "Internal Tool", "value": "internal_tool"},
        {"label": "HR System", "value": "hr_system"},
        {"label": "Other", "value": "other", "requires_text": True},
    ]

    CATEGORY_FIELD_OPTIONS: dict[tuple[str, str], list[dict]] = {
        ("ACCESS", "affected_app"): SERVICE_OPTIONS,
        ("ACCESS", "application"): SERVICE_OPTIONS,
        ("GENERAL", "affected_app"): [
            {"label": "Company Portal", "value": "company_portal"},
            {"label": "Email", "value": "email"},
            {"label": "VPN", "value": "vpn"},
            {"label": "WiFi or network", "value": "network"},
            {"label": "Laptop or device", "value": "device"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        ("DEVICE_PERFORMANCE", "affected_app"): [
            {"label": "Whole device", "value": "whole_device"},
            {"label": "Browser", "value": "browser"},
            {"label": "Email / Outlook", "value": "email"},
            {"label": "Teams or meeting app", "value": "meeting_app"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        ("SOFTWARE", "affected_app"): [
            {"label": "Microsoft Teams", "value": "teams"},
            {"label": "Zoom", "value": "zoom"},
            {"label": "Slack", "value": "slack"},
            {"label": "Office app", "value": "office_app"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        ("BROWSER", "affected_site"): [
            {"label": "Company Portal", "value": "company_portal"},
            {"label": "HR System", "value": "hr_system"},
            {"label": "Payroll", "value": "payroll"},
            {"label": "Intranet", "value": "intranet"},
            {"label": "External website", "value": "external_site"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
    }

    FIELD_OPTIONS: dict[str, list[dict]] = {
        "application": SERVICE_OPTIONS,
        "affected_app": SERVICE_OPTIONS,
        "account_locked": [
            {"label": "Yes - account locked", "value": "yes"},
            {"label": "No - different error", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "reset_attempted": [
            {"label": "Yes - reset already tried", "value": "yes"},
            {"label": "No - not tried yet", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "mfa_available": [
            {"label": "Yes - I can access MFA", "value": "yes"},
            {"label": "No - MFA unavailable", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "mfa_prompt": [
            {"label": "Yes - prompt appears", "value": "yes"},
            {"label": "No - no prompt", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "internet_working": [
            {"label": "Yes - normal websites work", "value": "yes"},
            {"label": "No - internet is down", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
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
            {"label": "I am not sure", "value": "unknown"},
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
            {"label": "I am not sure", "value": "unknown"},
        ],
        "other_users_affected": [
            {"label": "Yes - others affected", "value": "yes"},
            {"label": "No - only me", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
        ],
        "other_devices_working": [
            {"label": "Yes - other devices work", "value": "yes"},
            {"label": "No - other devices also fail", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "restart_done": [
            {"label": "Yes - restarted already", "value": "yes"},
            {"label": "No - not yet", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
        ],
        "cache_cleared": [
            {"label": "Yes - tried private window/cache clear", "value": "yes"},
            {"label": "No - not yet", "value": "no"},
            {"label": "I am not sure", "value": "unknown"},
        ],
        "browser": [
            {"label": "Chrome", "value": "chrome"},
            {"label": "Edge", "value": "edge"},
            {"label": "Firefox", "value": "firefox"},
            {"label": "Safari", "value": "safari"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "network_name": [
            {"label": "Company WiFi", "value": "company_wifi"},
            {"label": "Guest WiFi", "value": "guest_wifi"},
            {"label": "Home WiFi", "value": "home_wifi"},
            {"label": "Public WiFi", "value": "public_wifi"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "network_connection": [
            {"label": "Office network", "value": "office_network"},
            {"label": "VPN", "value": "vpn"},
            {"label": "Home WiFi", "value": "home_wifi"},
            {"label": "Mobile hotspot", "value": "hotspot"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
        "business_impact": [
            {"label": "Blocking my work", "value": "blocking_work"},
            {"label": "Affecting multiple people", "value": "multiple_users"},
            {"label": "Security concern", "value": "security"},
            {"label": "Minor inconvenience", "value": "minor"},
            {"label": "Other", "value": "other", "requires_text": True},
        ],
    }

    def build(
        self,
        *,
        fields: tuple[DiagnosticField, ...],
        missing_fields: list[str],
        questions: list[str],
        category: str | None = None,
    ) -> list[dict]:
        category_key = (category or "GENERAL").upper()
        field_by_key = {field.key: field for field in fields}
        structured_questions: list[dict] = []
        used_fields: set[str] = set()

        category_question = self.CATEGORY_ISSUE_QUESTIONS.get(category_key)
        if category_question and self._validate_question(category_question, category_key):
            structured_questions.append(category_question)
            used_fields.add(str(category_question["field"]))

        for question in questions:
            field_key = self._field_for_question(question, fields, missing_fields)
            if not field_key or field_key in used_fields:
                continue
            used_fields.add(field_key)
            field = field_by_key.get(field_key)
            options = self._options_for_field(field_key, category_key)
            candidate = {
                "type": "question",
                "question": question,
                "field": field.key if field else field_key,
                "input_type": "multi_select" if field_key in self.MULTI_SELECT_FIELDS else "single_select",
                "options": options,
                "source": "rule_based",
            }
            if not self._validate_question(candidate, category_key):
                continue

            structured_questions.append(candidate)
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

    def _options_for_field(self, field_key: str, category: str) -> list[dict]:
        return self.CATEGORY_FIELD_OPTIONS.get((category, field_key)) or self.FIELD_OPTIONS.get(field_key, [])

    def _validate_question(self, question: dict, category: str) -> bool:
        text = str(question.get("question") or "").strip()
        field_key = str(question.get("field") or "").strip()
        input_type = question.get("input_type")
        raw_options = question.get("options")
        if not text or not field_key or input_type not in {"single_select", "multi_select"} or not isinstance(raw_options, list):
            return False

        options = [option for option in raw_options if isinstance(option, dict) and str(option.get("label") or "").strip() and str(option.get("value") or "").strip()]
        non_other_options = [option for option in options if str(option.get("value")).lower() != "other"]
        if len(non_other_options) < 3:
            return False

        labels = {str(option["label"]).strip().lower() for option in non_other_options}
        values = {str(option["value"]).strip().lower() for option in non_other_options}
        is_boolean = self._is_boolean_question(text, field_key)

        if labels & self.GENERIC_OPTION_LABELS and not is_boolean:
            return False
        if {"yes", "no"}.issubset(values) and not is_boolean:
            return False
        if field_key in {"affected_app", "application", "affected_site"} and values & {"yes", "no", "unknown"}:
            return False
        if field_key.endswith("_issue_type") and values & {"yes", "no", "unknown"}:
            return False
        if category == "ACCESS" and field_key in {"affected_app", "application"}:
            return {"email", "vpn", "company_portal", "internal_tool", "hr_system"}.intersection(values) != set()
        return True

    def _is_boolean_question(self, question: str, field_key: str) -> bool:
        if field_key in self.BOOLEAN_FIELDS:
            return True
        lower = question.lower().strip()
        return lower.startswith(("are ", "can ", "did ", "do ", "does ", "have ", "has ", "is ", "was ", "were "))
