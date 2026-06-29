from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from sac_assistant.tools.knowledge_search_tool import PaymentKnowledgeSearchTool
from sac_assistant.tools.payment_tool import InvoiceLookupTool
from sac_assistant.schemas.specialist_answer import SpecialistAnswer

@CrewBase
class PaymentsCrew():
    """Payments specialist crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def payment_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['payment_specialist'],  # type: ignore[index]
            tools=[PaymentKnowledgeSearchTool(), InvoiceLookupTool()],
            verbose=True
        )

    @task
    def answer_payment_question(self) -> Task:
        return Task(
            config=self.tasks_config['answer_payment_question'],  # type: ignore[index]
            output_pydantic=SpecialistAnswer,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
