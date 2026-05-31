from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_marketing_agent.crews.factory import task_from_config
from content_marketing_agent.crews.llm import default_llm, review_llm


@CrewBase
class AnalyticsCrew:
    """Turns platform metrics into baseline comparison and recommendations."""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config: Any = "config/agents.yaml"
    tasks_config: Any = "config/tasks.yaml"

    @agent
    def performance_analyst(self) -> Agent:
        return Agent(config=self.agents_config["performance_analyst"], llm=default_llm())

    @agent
    def baseline_analyst(self) -> Agent:
        return Agent(config=self.agents_config["baseline_analyst"], llm=default_llm())

    @agent
    def insights_writer(self) -> Agent:
        return Agent(config=self.agents_config["insights_writer"], llm=review_llm())

    @task
    def performance_snapshot_task(self) -> Task:
        return task_from_config(self.tasks_config["performance_snapshot_task"])

    @task
    def baseline_comparison_task(self) -> Task:
        return task_from_config(self.tasks_config["baseline_comparison_task"])

    @task
    def monthly_report_task(self) -> Task:
        return task_from_config(self.tasks_config["monthly_report_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
