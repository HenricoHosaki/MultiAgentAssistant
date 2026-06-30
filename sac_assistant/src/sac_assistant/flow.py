from typing import Literal

from crewai import Agent
from crewai.flow.flow import Flow, listen, or_, router, start
from pydantic import BaseModel

from sac_assistant.crews.products_crew.products_crew import ProductsCrew
from sac_assistant.crews.delivery_crew.delivery_crew import DeliveryCrew
from sac_assistant.crews.payments_crew.payments_crew import PaymentsCrew
from sac_assistant.guardrails.input_guardrail import check_input
from sac_assistant.tools.ticket_tool import open_ticket

class TriageResult(BaseModel):
    intent: Literal["products", "delivery", "payments", "other"]
    confidence: float


class SacState(BaseModel):
    question: str = ""
    blocked: bool = False
    block_reason: str = ""
    intent: str = ""
    confidence: float = 0.0
    found_answer: bool = True
    source: str = ""
    answer: str = ""
    system_error: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class SacFlow(Flow[SacState]):

    def _add_usage(self, usage) -> None:
        if usage is None:
            return
        if isinstance(usage, dict):
            self.state.prompt_tokens += usage.get("prompt_tokens", 0)
            self.state.completion_tokens += usage.get("completion_tokens", 0)
            self.state.total_tokens += usage.get("total_tokens", 0)
        else:
            self.state.prompt_tokens += usage.prompt_tokens
            self.state.completion_tokens += usage.completion_tokens
            self.state.total_tokens += usage.total_tokens

    @start()
    def guardrail_check(self):
        passed, reason = check_input(self.state.question)
        self.state.blocked = not passed
        self.state.block_reason = reason

    @router(guardrail_check)
    def route_guardrail(self):
        return "blocked" if self.state.blocked else "allowed"

    @listen("blocked")
    def handle_blocked(self):
        self.state.answer = (
            "Não posso processar essa solicitação. Evite compartilhar dados sensíveis "
            "como CPF ou número de cartão, e reformule sua pergunta."
        )

    @listen("allowed")
    def triage(self):
        triage_agent = Agent(
            role="Customer Question Triage Specialist",
            goal="Classify the customer's question into the correct support category",
            backstory=(
                "You read customer support questions and decide which specialist team "
                "should handle them: products, delivery, payments, or other if it doesn't "
                "fit any of those categories. You only classify, you never answer the question."
            ),
        )
        try:
            result = triage_agent.kickoff(
                self.state.question,
                response_format=TriageResult,
            )
        except Exception:
            self.state.intent = "other"
            self.state.system_error = True
            return

        self.state.intent = result.pydantic.intent
        self.state.confidence = result.pydantic.confidence
        self._add_usage(result.usage_metrics)

    @router(triage)
    def route(self):
        return self.state.intent

    @listen("products")
    def handle_products(self):
        try:
            result = ProductsCrew().crew().kickoff(inputs={"question": self.state.question})
        except Exception:
            self.state.found_answer = False
            self.state.system_error = True
            return
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source
        self._add_usage(result.token_usage)

    @listen("delivery")
    def handle_delivery(self):
        try:
            result = DeliveryCrew().crew().kickoff(inputs={"question": self.state.question})
        except Exception:
            self.state.found_answer = False
            self.state.system_error = True
            return
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source
        self._add_usage(result.token_usage)

    @listen("payments")
    def handle_payments(self):
        try:
            result = PaymentsCrew().crew().kickoff(inputs={"question": self.state.question})
        except Exception:
            self.state.found_answer = False
            self.state.system_error = True
            return
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source
        self._add_usage(result.token_usage)

    @listen("other")
    def handle_other(self):
        if self.state.system_error:
            open_ticket(self.state.question, reason="system_error")
            self.state.answer = (
                "We're experiencing a technical issue right now, so I've forwarded your "
                "question to a human agent who will follow up with you shortly."
            )
            return

        self.state.answer = (
            "I'm sorry, I can only help with questions about products, delivery, or payments."
        )

    @listen(or_(handle_products, handle_delivery, handle_payments))
    def check_escalation(self):
        low_confidence = self.state.confidence < 0.6
        no_answer = not self.state.found_answer

        if low_confidence or no_answer:
            if self.state.system_error:
                reason = "system_error"
            elif low_confidence:
                reason = "low_confidence"
            else:
                reason = "no_answer_found"
            open_ticket(self.state.question, reason=reason)
            self.state.answer = (
                "I wasn't able to fully resolve your question, so I've forwarded it to "
                "a human agent who will follow up with you shortly."
            )
