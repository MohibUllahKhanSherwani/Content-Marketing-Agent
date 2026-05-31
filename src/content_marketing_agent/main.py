from content_marketing_agent.flows.monthly import MonthlyContentFlow


def kickoff():
    return MonthlyContentFlow().kickoff()


def plot():
    return MonthlyContentFlow().plot()


if __name__ == "__main__":
    kickoff()

