from tool import market_research_tool, community_sentiment_tool, technical_feasibility_tool

class StartupValidatorAgent:
    """Orchestrates LLM reasoning + tools."""
    def __init__(self):
        self.history = []

    def validate(self, idea: str) -> str:
        self.history.append(f"User Idea: {idea}")

        # Market Research
        market = market_research_tool(idea)
        self.history.append(market)

        # Community Sentiment
        sentiment = community_sentiment_tool(idea)
        self.history.append(sentiment)

        # Technical Feasibility
        tech = technical_feasibility_tool(idea)
        self.history.append(tech)

        # Combine into report
        report = f"--- Startup Validation Report ---\n"
        report += f"Idea: {idea}\n\n"
        report += f"{market}\n\n"
        report += f"{sentiment}\n\n"
        report += f"{tech}\n"
        return report
