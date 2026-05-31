from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_marketing_agent.crews.factory import task_from_config
from content_marketing_agent.crews.llm import review_llm


@CrewBase
class QualityCrew:
    """Reviews drafted content before the human approval gate."""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config: Any = "config/agents.yaml"
    tasks_config: Any = "config/tasks.yaml"

    @agent
    def managing_editor(self) -> Agent:
        return Agent(config=self.agents_config["managing_editor"], llm=review_llm())

    @agent
    def brand_voice_reviewer(self) -> Agent:
        return Agent(config=self.agents_config["brand_voice_reviewer"], llm=review_llm())

    @agent
    def seo_conversion_reviewer(self) -> Agent:
        return Agent(config=self.agents_config["seo_conversion_reviewer"], llm=review_llm())

    @task
    def editorial_review_task(self) -> Task:
        return task_from_config(self.tasks_config["editorial_review_task"])

    @task
    def brand_voice_task(self) -> Task:
        return task_from_config(self.tasks_config["brand_voice_task"])

    @task
    def seo_conversion_task(self) -> Task:
        return task_from_config(self.tasks_config["seo_conversion_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
