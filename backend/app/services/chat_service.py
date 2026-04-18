from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, ConversationStage, ConversationStatus, Message, MessageSender
from app.models.message_feedback import MessageFeedback
from app.models.ticket import Ticket
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.services.action_registry import ActionRegistry
from app.services.approval_workflow_service import ApprovalWorkflowService
from app.services.chat_intent_service import ChatIntentResult, ChatIntentService, ChatIntentType
from app.services.classification_service import ClassificationService
from app.services.escalation_service import EscalationService
from app.services.issue_understanding_service import IssueUnderstanding, IssueUnderstandingService
from app.services.kb_retrieval_service import KBRetrievalService
from app.services.openai_response_service import GeneratedSupportResponse, OpenAIResponseService
from app.services.triage_service import TriageAction, TriageDecision, TriageService


@dataclass
class ChatResult:
    conversation: Conversation
    assistant_message: Message
    category: str
    kb_titles: list[str]
    escalated: bool = False
    ticket: Ticket | None = None


@dataclass
class FeedbackResult:
    conversation: Conversation
    assistant_message: Message | None
    escalated: bool
    ticket: Ticket | None = None


class ChatService:
    def __init__(
        self,
        db: Session,
        response_generator: OpenAIResponseService | None = None,
        understanding_service: IssueUnderstandingService | None = None,
    ):
        self.db = db
        self.conversations = ConversationRepository(db)
        self.classifier = ClassificationService()
        self.kb = KBRetrievalService(db)
        self.escalation = EscalationService(db)
        self.response_generator = response_generator or OpenAIResponseService()
        self.understanding_service = understanding_service or IssueUnderstandingService()
        self.intent_router = ChatIntentService()
        self.triage = TriageService()
        self.actions = ActionRegistry()
        self.approvals = ApprovalWorkflowService(db)

    def create_conversation(self, user: User) -> Conversation:
        return self.conversations.create(user.id)

    def list_user_conversations(self, user: User) -> list[Conversation]:
        return self.conversations.list_for_user(user.id)

    def get_user_conversation(self, user: User, conversation_id: int) -> Conversation | None:
        conversation = self.conversations.get(conversation_id)
        if conversation is None or conversation.user_id != user.id:
            return None
        return conversation

    def submit_message(self, user: User, conversation_id: int, content: str, structured_response: dict | None = None) -> ChatResult:
        conversation = self.get_user_conversation(user, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")
        if conversation.status != ConversationStatus.ACTIVE:
            raise ValueError("Conversation is not active")

        normalized_structured_response = self._normalize_structured_response(structured_response)
        user_content = content.strip() or self._structured_response_content(normalized_structured_response)
        user_message_meta = {"structured_response": normalized_structured_response, "input_source": "guided_option"} if normalized_structured_response else None
        self.conversations.add_message(conversation, MessageSender.USER, user_content, meta=user_message_meta)
        conversation = self.conversations.get(conversation.id) or conversation

        if normalized_structured_response:
            conversation = self.conversations.update_state(
                conversation,
                collected_context=self._merge_structured_response(
                    conversation.collected_context or {},
                    normalized_structured_response,
                ),
            )
            conversation = self.conversations.get(conversation.id) or conversation
            intent = ChatIntentResult(
                intent_type=ChatIntentType.SUPPORT_REQUEST,
                cleaned_text=user_content,
                confidence=0.95,
                reason="Structured guided answer selected.",
            )
        else:
            intent = self.intent_router.route(user_content)

        if intent.intent_type != ChatIntentType.SUPPORT_REQUEST:
            handled = self._handle_non_support_intent(conversation, intent)
            if handled:
                return handled

        support_text = self._structured_support_text(conversation, user_content, normalized_structured_response) if normalized_structured_response else intent.cleaned_text or user_content
        classification = self.classifier.classify(support_text)
        understanding = self.understanding_service.understand(
            issue_text=support_text,
            conversation_history=self._conversation_history(conversation),
            existing_context=conversation.collected_context or {},
            deterministic_classification=classification,
        )
        category = self._select_category(conversation, classification.category, understanding)
        triage_decision = self.triage.decide(
            conversation=conversation,
            issue_text=support_text,
            category=category,
            classification=classification,
            understanding=understanding,
        )
        conversation = self.conversations.update_state(
            conversation,
            category=category,
            triage_stage=triage_decision.stage,
            collected_context=triage_decision.collected_context,
            last_triage=triage_decision.to_meta(),
        )

        if self.approvals.is_software_install_request(support_text, triage_decision.collected_context):
            ticket = self.approvals.create_install_request(
                user=user,
                conversation=conversation,
                text=support_text,
                context=triage_decision.collected_context,
                triage=triage_decision.to_meta(),
            )
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.ESCALATED,
                triage_stage=ConversationStage.ESCALATED,
                escalation_summary=(
                    f"Software installation approval request for {ticket.requested_software}. "
                    f"Approval status: {ticket.approval_status.value}."
                ),
            )
            actions = self.actions.escalation_actions(ticket.id)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                (
                    f"I created software installation request ticket #{ticket.id} for {ticket.requested_software}. "
                    "It is pending admin approval before a technician proceeds."
                ),
                meta={
                    "ticket_id": ticket.id,
                    "request_type": ticket.request_type.value,
                    "approval_required": ticket.approval_required,
                    "approval_status": ticket.approval_status.value,
                    "requested_software": ticket.requested_software,
                    "actions": actions,
                    **triage_decision.to_meta(),
                },
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return ChatResult(
                conversation=conversation,
                assistant_message=assistant_message,
                category="SOFTWARE",
                kb_titles=[],
                escalated=True,
                ticket=ticket,
            )

        if triage_decision.action == TriageAction.ASK_CLARIFYING_QUESTIONS:
            structured_questions = self.triage.guided_questions.sanitize_all(triage_decision.structured_questions, category)
            question_meta = self._structured_question_meta(structured_questions)
            triage_meta = triage_decision.to_meta()
            triage_meta["structured_questions"] = structured_questions
            actions = self._support_actions(category, triage_decision.confidence, has_support_path=True)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                self._build_clarifying_content(category, triage_decision, structured_questions),
                meta={
                    "category": category,
                    "confidence": triage_decision.confidence,
                    "classification_source": understanding.source,
                    "issue_summary": understanding.short_issue_summary,
                    "matched_keywords": classification.matched_keywords,
                    "intent_type": intent.intent_type.value,
                    "intent_confidence": intent.confidence,
                    "actions": actions,
                    **triage_meta,
                    **question_meta,
                },
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return ChatResult(
                conversation=conversation,
                assistant_message=assistant_message,
                category=category,
                kb_titles=[],
            )

        if triage_decision.action == TriageAction.ESCALATE:
            summary = self._build_escalation_summary(conversation, triage_decision)
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.ESCALATED,
                triage_stage=ConversationStage.ESCALATED,
                escalation_summary=summary,
            )
            conversation = self.conversations.get(conversation.id) or conversation
            ticket = self.escalation.escalate(conversation, summary=summary)
            actions = self.actions.escalation_actions(ticket.id)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                (
                    "I escalated this directly because it may need human review. "
                    f"Your ticket is #{ticket.id}; the technician will receive the details collected so far."
                ),
                meta={
                    "ticket_id": ticket.id,
                    "escalated": True,
                    "actions": actions,
                    "intent_type": intent.intent_type.value,
                    "intent_confidence": intent.confidence,
                    **triage_decision.to_meta(),
                },
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return ChatResult(
                conversation=conversation,
                assistant_message=assistant_message,
                category=category,
                kb_titles=[],
                escalated=True,
                ticket=ticket,
            )

        retrieval_query = self._build_retrieval_query(support_text, understanding, triage_decision.collected_context)
        entries = self.kb.retrieve(
            retrieval_query,
            category,
            limit=3,
            secondary_category=understanding.secondary_category,
            exclude_ids=self._shown_kb_entry_ids(conversation),
        )
        self.kb.track_usage(entries)
        similar_issue = self._similar_issue(user, category, conversation.id)
        generated_response = self._generate_response(
            issue_text=retrieval_query,
            category=category,
            entries=entries,
            attempt=conversation.failure_count + 1,
            collected_context=triage_decision.collected_context,
            triage_reason=triage_decision.reason,
            is_retry=False,
        )
        assistant_text = generated_response.content or self._build_assistant_response(category, entries, conversation.failure_count + 1)
        actions = self._support_actions(category, triage_decision.confidence, has_support_path=bool(entries))
        if similar_issue:
            assistant_text = (
                f"You had a similar {category.replace('_', ' ').lower()} issue in ticket #{similar_issue.id}. "
                "I will use the current details first, but that history is available if this needs a technician.\n\n"
                f"{assistant_text}"
            )
        assistant_message = self.conversations.add_message(
            conversation,
            MessageSender.ASSISTANT,
            assistant_text,
            meta={
                "category": category,
                "confidence": triage_decision.confidence,
                "classification_source": understanding.source,
                "issue_summary": understanding.short_issue_summary,
                "matched_keywords": classification.matched_keywords,
                "intent_type": intent.intent_type.value,
                "intent_confidence": intent.confidence,
                "kb_entry_ids": [entry.id for entry in entries],
                "kb_titles": [entry.title for entry in entries],
                "attempt": conversation.failure_count + 1,
                "response_source": generated_response.source,
                "response_error": generated_response.error,
                "similar_ticket_id": similar_issue.id if similar_issue else None,
                "actions": actions,
                **triage_decision.to_meta(),
            },
        )
        conversation = self.conversations.get(conversation.id) or conversation
        return ChatResult(
            conversation=conversation,
            assistant_message=assistant_message,
            category=category,
            kb_titles=[entry.title for entry in entries],
        )

    def record_feedback(self, user: User, conversation_id: int, resolved: bool) -> FeedbackResult:
        conversation = self.get_user_conversation(user, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")
        if conversation.status != ConversationStatus.ACTIVE:
            return FeedbackResult(
                conversation=conversation,
                assistant_message=None,
                escalated=conversation.status == ConversationStatus.ESCALATED,
                ticket=conversation.ticket,
            )

        if resolved:
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.RESOLVED,
                triage_stage=ConversationStage.RESOLVED,
            )
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                "Marked as resolved. I saved the conversation so you can review it later.",
                meta={"resolution": "USER_CONFIRMED"},
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return FeedbackResult(conversation=conversation, assistant_message=assistant_message, escalated=False)

        if conversation.triage_stage == ConversationStage.CLARIFYING:
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                "I still need the clarifying details above before I can give a useful fix. Reply with whatever you know, even partial answers.",
                meta={"triage_action": TriageAction.ASK_CLARIFYING_QUESTIONS.value, "triage_stage": ConversationStage.CLARIFYING.value},
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return FeedbackResult(conversation=conversation, assistant_message=assistant_message, escalated=False)

        failure_count = conversation.failure_count + 1
        conversation = self.conversations.update_state(conversation, failure_count=failure_count)

        if failure_count >= 2:
            summary = self._build_escalation_summary(conversation)
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.ESCALATED,
                triage_stage=ConversationStage.ESCALATED,
                escalation_summary=summary,
            )
            conversation = self.conversations.get(conversation.id) or conversation
            ticket = self.escalation.escalate(conversation, summary=summary)
            actions = self.actions.escalation_actions(ticket.id)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                (
                    "I escalated this to a technician because the guided fixes did not resolve it. "
                    f"Your ticket is #{ticket.id}; a support agent can now review the full conversation."
                ),
                meta={"ticket_id": ticket.id, "escalated": True, "actions": actions},
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return FeedbackResult(conversation=conversation, assistant_message=assistant_message, escalated=True, ticket=ticket)

        last_user_issue = self._latest_user_issue(conversation)
        shown_ids = self._shown_kb_entry_ids(conversation)
        entries = self.kb.retrieve(
            last_user_issue,
            conversation.category or "GENERAL",
            limit=3,
            secondary_category=(conversation.last_triage or {}).get("secondary_category"),
            exclude_ids=shown_ids,
        )
        if not entries:
            summary = self._build_escalation_summary(conversation)
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.ESCALATED,
                triage_stage=ConversationStage.ESCALATED,
                escalation_summary=summary,
            )
            conversation = self.conversations.get(conversation.id) or conversation
            ticket = self.escalation.escalate(conversation, summary=summary)
            actions = self.actions.escalation_actions(ticket.id)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                (
                    "I do not have a meaningfully different approved fix to try next, so I escalated this to a technician. "
                    f"Your ticket is #{ticket.id}."
                ),
                meta={"ticket_id": ticket.id, "escalated": True, "escalation_reason": "no_alternate_kb", "actions": actions},
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return FeedbackResult(conversation=conversation, assistant_message=assistant_message, escalated=True, ticket=ticket)
        self.kb.track_usage(entries)
        generated_response = self._generate_response(
            issue_text=last_user_issue,
            category=conversation.category or "GENERAL",
            entries=entries,
            attempt=failure_count + 1,
            collected_context=conversation.collected_context or {},
            triage_reason="One more targeted troubleshooting attempt before escalation.",
            is_retry=True,
        )
        conversation = self.conversations.update_state(conversation, triage_stage=ConversationStage.WAITING_FOR_FEEDBACK)
        assistant_message = self.conversations.add_message(
            conversation,
            MessageSender.ASSISTANT,
            generated_response.content or self._build_retry_response(conversation.category or "GENERAL", entries),
            meta={
                "category": conversation.category,
                "kb_entry_ids": [entry.id for entry in entries],
                "kb_titles": [entry.title for entry in entries],
                "attempt": failure_count + 1,
                "failure_state": "user_marked_not_resolved",
                "response_source": generated_response.source,
                "response_error": generated_response.error,
                "actions": self._support_actions(conversation.category or "GENERAL", 0.9, has_support_path=bool(entries)),
            },
        )
        conversation = self.conversations.get(conversation.id) or conversation
        return FeedbackResult(conversation=conversation, assistant_message=assistant_message, escalated=False)

    def _handle_non_support_intent(self, conversation: Conversation, intent: ChatIntentResult) -> ChatResult | None:
        meta = {
            "intent_type": intent.intent_type.value,
            "intent_confidence": intent.confidence,
            "intent_reason": intent.reason,
            "support_response": False,
        }
        if intent.intent_type == ChatIntentType.ABUSIVE and intent.escalation_requested and self._has_support_context(conversation):
            summary = self._build_escalation_summary(conversation)
            conversation = self.conversations.update_state(
                conversation,
                status=ConversationStatus.ESCALATED,
                triage_stage=ConversationStage.ESCALATED,
                escalation_summary=summary,
            )
            conversation = self.conversations.get(conversation.id) or conversation
            ticket = self.escalation.escalate(conversation, summary=summary)
            actions = self.actions.escalation_actions(ticket.id)
            assistant_message = self.conversations.add_message(
                conversation,
                MessageSender.ASSISTANT,
                (
                    "I understand this is frustrating. I escalated the issue to a technician with the context collected so far. "
                    f"Your ticket is #{ticket.id}."
                ),
                meta={**meta, "ticket_id": ticket.id, "escalated": True, "actions": actions},
            )
            conversation = self.conversations.get(conversation.id) or conversation
            return ChatResult(conversation=conversation, assistant_message=assistant_message, category=conversation.category or "GENERAL", kb_titles=[], escalated=True, ticket=ticket)

        response_by_intent = {
            ChatIntentType.GREETING: "Hi. Tell me what IT issue you are facing, including the app, device, and any exact error message.",
            ChatIntentType.SMALL_TALK: "I can help with IT support issues like VPN, WiFi, email, access, software, browser, printer, and device problems. What is not working?",
            ChatIntentType.IRRELEVANT: "I am focused on IT support here, so I cannot help with that request. Tell me the device, app, or service that is having a problem.",
            ChatIntentType.EMPTY: "I did not get enough detail to troubleshoot yet. Please describe the IT issue, the affected app or device, and any error message.",
            ChatIntentType.ABUSIVE: "I understand this is frustrating. Share the IT issue in one sentence and I can troubleshoot it or escalate it with useful context.",
        }
        assistant_message = self.conversations.add_message(
            conversation,
            MessageSender.ASSISTANT,
            response_by_intent[intent.intent_type],
            meta=meta,
        )
        conversation = self.conversations.get(conversation.id) or conversation
        return ChatResult(conversation=conversation, assistant_message=assistant_message, category=conversation.category or "GENERAL", kb_titles=[])

    def record_message_feedback(self, user: User, message_id: int, helpful: bool, note: str | None = None) -> MessageFeedback:
        message = self.db.get(Message, message_id)
        if message is None or message.sender != MessageSender.ASSISTANT:
            raise ValueError("Assistant message not found")
        conversation = self.get_user_conversation(user, message.conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")

        feedback = MessageFeedback(
            message_id=message.id,
            conversation_id=conversation.id,
            user_id=user.id,
            helpful=helpful,
            note=note,
        )
        meta = dict(message.meta or {})
        meta["helpful_feedback"] = helpful
        message.meta = meta
        self.db.add(feedback)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def _normalize_structured_response(self, structured_response: dict | None) -> dict | None:
        if not structured_response:
            return None
        field = str(structured_response.get("field") or "").strip()
        raw_value = structured_response.get("value")
        if not field or raw_value in (None, "", []):
            return None
        value: str | list[str]
        if isinstance(raw_value, list):
            value = [str(item).strip() for item in raw_value if str(item).strip()]
            if not value:
                return None
        else:
            value = str(raw_value).strip()
        return {
            "field": field,
            "value": value,
            "label": str(structured_response.get("label") or self._stringify_structured_value(value)).strip(),
            "input_type": structured_response.get("input_type") or "single_select",
            "question": structured_response.get("question"),
        }

    def _merge_structured_response(self, context: dict, structured_response: dict) -> dict:
        merged = dict(context)
        field = structured_response["field"]
        value = structured_response["value"]
        merged[field] = value
        structured_inputs = dict(merged.get("structured_inputs") or {})
        structured_inputs[field] = value
        merged["structured_inputs"] = structured_inputs

        if field == "account_locked" and value == "yes":
            merged["error_type"] = "account_locked"
        if field == "password_issue_type":
            merged["error_type"] = value
            if value == "account_locked":
                merged["account_locked"] = "yes"
            if value == "mfa_issue":
                merged["mfa_available"] = "no"
        if field in {"vpn_issue_type", "wifi_issue_type"}:
            merged["issue_type"] = value
            if value == "connected_no_internet":
                merged.setdefault("internet_working", "no")
        if field == "mfa_prompt" and value == "no":
            merged["mfa_available"] = "no"
        if field == "internet_working" and value == "no":
            merged["business_impact"] = merged.get("business_impact") or "network unavailable"
        return merged

    def _structured_response_content(self, structured_response: dict | None) -> str:
        if not structured_response:
            return ""
        question = structured_response.get("question")
        label = structured_response.get("label") or self._stringify_structured_value(structured_response.get("value"))
        if question:
            return f"{question}\nAnswer: {label}"
        return f"{structured_response.get('field', 'Answer')}: {label}"

    def _structured_support_text(self, conversation: Conversation, user_content: str, structured_response: dict | None) -> str:
        if not structured_response:
            return user_content
        prior_issue = self._latest_user_issue(conversation)
        field = structured_response["field"]
        value = self._stringify_structured_value(structured_response["value"])
        return (
            f"{prior_issue}\n"
            f"Structured answer: {field} = {value}\n"
            f"Current answer: {user_content}"
        )

    def _structured_question_meta(self, structured_questions: list[dict]) -> dict:
        if not structured_questions:
            return {}
        primary = structured_questions[0]
        return {
            "type": "question",
            "question": primary.get("question"),
            "field": primary.get("field"),
            "input_type": primary.get("input_type"),
            "options": primary.get("options"),
            "structured_questions": structured_questions,
        }

    def _build_clarifying_content(self, category: str, triage_decision: TriageDecision, structured_questions: list[dict] | None = None) -> str:
        questions = structured_questions if structured_questions is not None else triage_decision.structured_questions
        if questions:
            label = category.replace("_", " ").title()
            if len(questions) == 1:
                return str(questions[0]["question"])
            return f"I categorized this as {label}. Answer these quick checks so I can suggest the right fix."
        return self.triage.build_clarifying_response(category, triage_decision.questions)

    def _stringify_structured_value(self, value: Any) -> str:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)

    def _latest_user_issue(self, conversation: Conversation) -> str:
        for message in reversed(conversation.messages):
            if message.sender == MessageSender.USER and not (message.meta or {}).get("structured_response"):
                return message.content
        return conversation.category or "GENERAL"

    def _conversation_history(self, conversation: Conversation) -> str:
        return "\n".join(f"{message.sender.value}: {message.content}" for message in conversation.messages[-8:])

    def _select_category(self, conversation: Conversation, deterministic_category: str, understanding: IssueUnderstanding) -> str:
        if conversation.category and conversation.category != "GENERAL":
            return conversation.category
        if understanding.confidence_score >= 0.45:
            return understanding.primary_category
        return deterministic_category

    def _build_retrieval_query(self, user_text: str, understanding: IssueUnderstanding, collected_context: dict) -> str:
        context_text = " ".join(str(value) for value in collected_context.values() if value)
        secondary = f" {understanding.secondary_category}" if understanding.secondary_category else ""
        return f"{user_text}\n{understanding.short_issue_summary}{secondary}\n{context_text}"

    def _shown_kb_entry_ids(self, conversation: Conversation) -> set[int]:
        shown: set[int] = set()
        for message in conversation.messages:
            if not message.meta:
                continue
            for entry_id in message.meta.get("kb_entry_ids", []) or []:
                try:
                    shown.add(int(entry_id))
                except (TypeError, ValueError):
                    continue
        return shown

    def _has_support_context(self, conversation: Conversation) -> bool:
        if conversation.category and conversation.category != "GENERAL":
            return True
        if conversation.collected_context:
            return True
        return any(bool((message.meta or {}).get("kb_entry_ids")) for message in conversation.messages)

    def _similar_issue(self, user: User, category: str, current_conversation_id: int) -> Ticket | None:
        if category == "GENERAL":
            return None
        return self.db.scalar(
            select(Ticket)
            .where(Ticket.user_id == user.id, Ticket.category == category, Ticket.conversation_id != current_conversation_id)
            .order_by(Ticket.updated_at.desc())
            .limit(1)
        )

    def _generate_response(
        self,
        *,
        issue_text: str,
        category: str,
        entries: list,
        attempt: int,
        collected_context: dict | None = None,
        triage_reason: str | None = None,
        is_retry: bool,
    ) -> GeneratedSupportResponse:
        return self.response_generator.generate_support_response(
            issue_text=issue_text,
            category=category,
            entries=entries,
            attempt=attempt,
            collected_context=collected_context or {},
            triage_reason=triage_reason,
            is_retry=is_retry,
        )

    def _support_actions(self, category: str | None, confidence: float, *, has_support_path: bool) -> list[dict]:
        return self.actions.actions_for_category(category, confidence=confidence, has_support_path=has_support_path)

    def _build_escalation_summary(self, conversation: Conversation, triage_decision: TriageDecision | None = None) -> str:
        context = triage_decision.collected_context if triage_decision else dict(conversation.collected_context or {})
        history = "\n".join(f"{message.sender.value}: {message.content}" for message in conversation.messages)
        generated = self.response_generator.generate_escalation_summary(
            category=conversation.category or "GENERAL",
            collected_context=context,
            conversation_history=history,
            failure_count=conversation.failure_count,
        )
        if generated.content:
            return generated.content

        collected = "\n".join(f"- {key.replace('_', ' ').title()}: {value}" for key, value in context.items()) or "- No structured details collected."
        missing_fields = []
        if triage_decision:
            missing_fields = triage_decision.missing_fields
        elif conversation.last_triage:
            missing_fields = conversation.last_triage.get("missing_fields", [])
        missing = "\n".join(f"- {field.replace('_', ' ').title()}" for field in missing_fields) or "- None identified."
        return (
            f"Technician handoff summary\n"
            f"Category: {conversation.category or 'GENERAL'}\n"
            f"Unresolved attempts: {conversation.failure_count}\n\n"
            f"Facts collected:\n{collected}\n\n"
            f"Missing information:\n{missing}\n\n"
            f"Suggested next action: Review the conversation, validate the likely root cause, and continue from the steps already attempted."
        )

    def _build_assistant_response(self, category: str, entries: list, attempt: int) -> str:
        label = category.replace("_", " ").title()
        intro = f"I categorized this as {label}. Try these steps:"
        steps = "\n\n".join(f"{index}. {entry.title}: {entry.content}" for index, entry in enumerate(entries, start=1))
        close = "After trying this, choose Resolved or Not Resolved so I can continue the workflow."
        return f"{intro}\n\n{steps}\n\n{close}"

    def _build_retry_response(self, category: str, entries: list) -> str:
        label = category.replace("_", " ").title()
        steps = "\n\n".join(f"{index}. {entry.title}: {entry.content}" for index, entry in enumerate(entries, start=1))
        return (
            f"Thanks for confirming. Here is one more guided attempt for {label} before escalation:\n\n"
            f"{steps}\n\n"
            "If this still does not resolve the issue, choose Not Resolved and I will escalate it automatically."
        )
