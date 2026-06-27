from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from sac_assistant.tools.knowledge_search_tool import DeliveryKnowledgeSearchTool


@CrewBase
class DeliveryCrew():
    """Delivery specialist crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def delivery_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['delivery_specialist'],  # type: ignore[index]
            tools=[DeliveryKnowledgeSearchTool()],
            verbose=True
        )

    @task
    def answer_delivery_question(self) -> Task:
        return Task(
            config=self.tasks_config['answer_delivery_question'],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
