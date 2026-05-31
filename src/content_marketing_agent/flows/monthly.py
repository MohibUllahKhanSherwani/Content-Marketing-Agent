from crewai.flow import Flow, listen, start
from pydantic import BaseModel, Field


class MonthlyContentState(BaseModel):
    client_name: str = "Demo Agency Client"
    objective: str = "Generate a monthly multi-channel content plan"
    produced_items: list[str] = Field(default_factory=list)
    analytics_report: str = ""


class MonthlyContentFlow(Flow[MonthlyContentState]):
    """Top-level monthly workflow placeholder.

    The source package is scaffolded first; concrete Crew kickoff calls will be
    wired here once the crew prompts and persistence layer are implemented.
    """

    @start()
    def prepare_campaign(self) -> str:
        return self.state.objective

    @listen(prepare_campaign)
    def produce_content(self, objective: str) -> list[str]:
        self.state.produced_items = [
            f"Blog plan for: {objective}",
            f"Email campaign for: {objective}",
            f"Social post batch for: {objective}",
        ]
        return self.state.produced_items

    @listen(produce_content)
    def summarize(self, produced_items: list[str]) -> str:
        self.state.analytics_report = (
            f"Prepared {len(produced_items)} demo content items for review."
        )
        return self.state.analytics_report
