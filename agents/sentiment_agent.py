from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools

from config import get_google_api_key, get_tavily_api_key

GOOGLE_API_KEY = get_google_api_key(required=True)
TAVILY_API_KEY = get_tavily_api_key()

tools = [DuckDuckGoTools(enable_news=True)]

if TAVILY_API_KEY:
    tools.append(TavilyTools(api_key=TAVILY_API_KEY))

sentiment_agent = Agent(
    name="Market Sentiment Analyst",
    role="Analyze market sentiment and news impact",
    model=Gemini(
        id="gemini-2.0-flash-001",
        api_key=GOOGLE_API_KEY,
    ),
    tools=tools,
    instructions=[
        "You are a market sentiment and news analysis expert",
        "Use DuckDuckGo efficiently - search once with focused queries",
        "Leverage Tavily (when available) for deeper analyst commentary and curated articles",
        "Classify sentiment as: Very Positive, Positive, Neutral, Negative, Very Negative",
        "Quantify analyst consensus (buy/hold/sell counts, average target vs current price) when available",
        "Identify 3-4 key themes from recent news and social chatter with sentiment score estimates",
        "Assess potential stock price impact for each theme: High, Medium, or Low, and note time horizon",
        "Look for: product launches, earnings, guidance changes, regulatory issues, macro catalysts",
        "Supply concise bullet points and mini table summaries with source excerpts or timestamps",
        "Focus on last 30 days (and flag older but still impactful items)",
        "Be succinct yet information-dense"
    ],
    markdown=True,
)
