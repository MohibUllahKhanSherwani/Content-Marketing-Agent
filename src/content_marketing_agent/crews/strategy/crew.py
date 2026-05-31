from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_marketing_agent.crews.factory import task_from_config
from content_marketing_agent.crews.llm import default_llm


@CrewBase
class StrategyCrew:
    """Creates campaign strategy, topic clusters, and calendar direction."""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config: Any = "config/agents.yaml"
    tasks_config: Any = "config/tasks.yaml"

    @agent
    def market_researcher(self) -> Agent:
        return Agent(config=self.agents_config["market_researcher"], llm=default_llm())

    @agent
    def seo_aeo_strategist(self) -> Agent:
        return Agent(config=self.agents_config["seo_aeo_strategist"], llm=default_llm())

    @agent
    def campaign_planner(self) -> Agent:
        return Agent(config=self.agents_config["campaign_planner"], llm=default_llm())

    @task
    def market_research_task(self) -> Task:
        return task_from_config(self.tasks_config["market_research_task"])

    @task
    def seo_aeo_task(self) -> Task:
        return task_from_config(self.tasks_config["seo_aeo_task"])

    @task
    def campaign_plan_task(self) -> Task:
        return task_from_config(self.tasks_config["campaign_plan_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
