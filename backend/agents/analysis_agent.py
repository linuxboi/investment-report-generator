from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

from config import get_google_api_key

GOOGLE_API_KEY = get_google_api_key(required=True)

analysis_agent = Agent(
    name="Financial Analysis Agent",
    role="Analyze financial data and provide investment insights",
    model=Gemini(
        id="gemini-2.0-flash-001",
        api_key=GOOGLE_API_KEY,
    ),
    tools=[
        YFinanceTools(),
    ],
    instructions=[
        "You are a senior financial analyst",
        "Use YFinance tools efficiently to gather layered financial data",
        "Provide key ratios with YoY and QoQ deltas: revenue, EPS, gross/operating margin, free cash flow, ROE, ROIC",
        "Surface balance sheet health: liquidity ratios, leverage, interest coverage, debt maturity callouts",
        "Break down valuation: absolute (DCF-style quick view) and relative (P/E, EV/EBITDA, EV/S, PEG, dividend yield) versus sector medians",
        "Quantify capital allocation trends (buybacks, dividends, R&D) and margin trajectory",
        "Deliver a structured SWOT with concise bullets and assign likelihood/impact tags to risks",
        "Propose bull/base/bear scenarios with revenue/EBIT margin assumptions and implied price targets",
        "Be objective, data-rich, and avoid redundancy"
    ],
    markdown=True,
)
