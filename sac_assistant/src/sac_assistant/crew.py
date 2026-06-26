from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from sac_assistant.tools.knowledge_search_tool import ProductKnowledgeSearchTool


@CrewBase
class SacAssistant():
    """SacAssistant crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def products_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['products_specialist'],  # type: ignore[index]
            tools=[ProductKnowledgeSearchTool()],
            verbose=True
        )

    @task
    def answer_product_question(self) -> Task:
        return Task(
            config=self.tasks_config['answer_product_question'],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SacAssistant crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )