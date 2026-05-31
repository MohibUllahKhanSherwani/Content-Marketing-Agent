from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_marketing_agent.crews.factory import task_from_config
from content_marketing_agent.crews.llm import default_llm


@CrewBase
class DistributionCrew:
    """Prepares approved content for platform connectors."""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config: Any = "config/agents.yaml"
    tasks_config: Any = "config/tasks.yaml"

    @agent
    def calendar_scheduler(self) -> Agent:
        return Agent(config=self.agents_config["calendar_scheduler"], llm=default_llm())

    @agent
    def connector_operator(self) -> Agent:
        return Agent(config=self.agents_config["connector_operator"], llm=default_llm())

    @agent
    def publication_auditor(self) -> Agent:
        return Agent(config=self.agents_config["publication_auditor"], llm=default_llm())

    @task
    def scheduling_task(self) -> Task:
        return task_from_config(self.tasks_config["scheduling_task"])

    @task
    def connector_preparation_task(self) -> Task:
        return task_from_config(self.tasks_config["connector_preparation_task"])

    @task
    def publication_audit_task(self) -> Task:
        return task_from_config(self.tasks_config["publication_audit_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
