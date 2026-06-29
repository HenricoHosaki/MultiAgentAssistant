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


class SacFlow(Flow[SacState]):

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
        result = triage_agent.kickoff(
            self.state.question,
            response_format=TriageResult,
        )
        self.state.intent = result.pydantic.intent
        self.state.confidence = result.pydantic.confidence

    @router(triage)
    def route(self):
        return self.state.intent

    @listen("products")
    def handle_products(self):
        result = ProductsCrew().crew().kickoff(inputs={"question": self.state.question})
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source

    @listen("delivery")
    def handle_delivery(self):
        result = DeliveryCrew().crew().kickoff(inputs={"question": self.state.question})
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source

    @listen("payments")
    def handle_payments(self):
        result = PaymentsCrew().crew().kickoff(inputs={"question": self.state.question})
        self.state.answer = result.pydantic.answer
        self.state.found_answer = result.pydantic.found_answer
        self.state.source = result.pydantic.source

    @listen("other")
    def handle_other(self):
        self.state.answer = (
            "I'm sorry, I can only help with questions about products, delivery, or payments."
        )

    @listen(or_(handle_products, handle_delivery, handle_payments))
    def check_escalation(self):
        low_confidence = self.state.confidence < 0.6
        no_answer = not self.state.found_answer

        if low_confidence or no_answer:
            reason = "low_confidence" if low_confidence else "no_answer_found"
            open_ticket(self.state.question, reason=reason)
            self.state.answer = (
                "I wasn't able to fully resolve your question, so I've forwarded it to "
                "a human agent who will follow up with you shortly."
            )