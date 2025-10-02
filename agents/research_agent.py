from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools
from agno.tools.yfinance import YFinanceTools

from config import get_google_api_key, get_tavily_api_key

GOOGLE_API_KEY = get_google_api_key(required=True)
TAVILY_API_KEY = get_tavily_api_key()

tools = [
    YFinanceTools(),
    DuckDuckGoTools(enable_news=True),
]

if TAVILY_API_KEY:
    tools.append(TavilyTools(api_key=TAVILY_API_KEY))

research_agent = Agent(
    name="Financial Research Agent",
    role="Gather essential financial data and market information",
    model=Gemini(
        id="gemini-2.0-flash-001",
        api_key=GOOGLE_API_KEY,
    ),
    tools=tools,
    instructions=[
        "You are a financial research specialist focused on essential data gathering",
        "Be efficient: gather key data in minimal tool calls",
        "Use YFinance for: price levels (1D/1W/1M/YTD), market cap, volume, P/E, EV metrics, revenue, EPS, balance sheet line items, cash flows",
        "Use DuckDuckGo for: top 3-5 recent news items only with timestamps and summary",
        "When available, use Tavily for curated analyst notes, regulatory filings, and in-depth articles",
        "Capture macro and industry context impacting the company (demand shifts, regulation, supply chain)",
        "Identify key market-moving events (last 30 days) and tag them by impact",
        "Supply data in structured bullet lists or mini tables to speed downstream analysis",
        "Prioritize quality over quantity to minimize API usage"
    ],
    markdown=True,

)
