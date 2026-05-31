from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_marketing_agent.crews.factory import task_from_config
from content_marketing_agent.crews.llm import default_llm


@CrewBase
class ProductionCrew:
    """Drafts blog, email, social, ad, landing-page, and case-study content."""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config: Any = "config/agents.yaml"
    tasks_config: Any = "config/tasks.yaml"

    @agent
    def blog_writer(self) -> Agent:
        return Agent(config=self.agents_config["blog_writer"], llm=default_llm())

    @agent
    def email_copywriter(self) -> Agent:
        return Agent(config=self.agents_config["email_copywriter"], llm=default_llm())

    @agent
    def social_copywriter(self) -> Agent:
        return Agent(config=self.agents_config["social_copywriter"], llm=default_llm())

    @agent
    def conversion_copywriter(self) -> Agent:
        return Agent(config=self.agents_config["conversion_copywriter"], llm=default_llm())

    @task
    def blog_draft_task(self) -> Task:
        return task_from_config(self.tasks_config["blog_draft_task"])

    @task
    def email_draft_task(self) -> Task:
        return task_from_config(self.tasks_config["email_draft_task"])

    @task
    def social_batch_task(self) -> Task:
        return task_from_config(self.tasks_config["social_batch_task"])

    @task
    def conversion_assets_task(self) -> Task:
        return task_from_config(self.tasks_config["conversion_assets_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
