"""Multi-agent investment analysis CLI entry point."""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from agno.exceptions import ModelProviderError
from agno.models.google import Gemini
from agno.team import Team

from agents.analysis_agent import analysis_agent
from agents.report_agent import report_agent
from agents.research_agent import research_agent
from agents.sentiment_agent import sentiment_agent
from pdf_generator import generate_pdf_report
from config import get_google_api_key


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------
GOOGLE_API_KEY = get_google_api_key(required=True)


# ---------------------------------------------------------------------------
# Team factory
# ---------------------------------------------------------------------------

def _create_investment_team() -> Team:
    """Return a fresh configured Team instance for each run."""

    return Team(
        name="Investment Analysis Team",
        members=[
            research_agent,
            analysis_agent,
            sentiment_agent,
            report_agent,
        ],
        model=Gemini(
            id="gemini-2.0-flash-001",
            api_key=GOOGLE_API_KEY,
        ),
        instructions=[
            "You are a coordinated investment analysis team.",
            "Work together efficiently to produce comprehensive investment reports.",
            "Be concise to minimize API calls.",
            "Research Agent: Gather essential financial data first.",
            "Sentiment Agent: Provide succinct sentiment insights.",
            "Analysis Agent: Perform focused quantitative assessment.",
            "Report Agent: Deliver polished and professional reports.",
            "Ensure data flows cleanly between agents and avoid duplication.",
            "Return ONLY the final investor-ready report in Markdown.",
        ],
        markdown=True,
    )


TEAM_PROMPT_TEMPLATE = """
Conduct a comprehensive investment analysis for {ticker} ({company_name}).

TEAM COORDINATION INSTRUCTIONS:

1. RESEARCH AGENT
   - Gather current fundamentals and price performance.
    - Summarize recent filings, earnings, and company developments.
    - Capture industry landscape trends, regulatory updates, and competitive positioning.
    - Provide bullet-pointed data that downstream agents can reference.
    - Surface quantitative metrics: revenue/EPS growth (YoY & QoQ), gross/operating margins, FCF, leverage, liquidity, capital allocation moves.
    - Pull market data: price change (1D/1W/1M/YTD), beta, 52-week range, volume trends, short interest if notable.

2. SENTIMENT AGENT
   - Evaluate news sentiment and analyst outlook.
   - Flag major positive or negative narratives across markets and social media.
   - Highlight short- versus long-term sentiment differentials.
    - Quantify consensus rating distribution, price targets, and notable analyst moves when available.

3. ANALYSIS AGENT
   - Build on the collected data to assess financial health.
    - Provide valuation and growth commentary with explicit metrics (P/E, EV/EBITDA, P/S, PEG, dividend yield, etc.).
    - Include ratio analysis (ROIC, ROE, debt/EBITDA, interest coverage) and compare against industry benchmarks where possible.
   - Document key risks, catalysts, and SWOT elements.
    - Develop scenario analysis (bull/base/bear) with assumption deltas.

4. REPORT AGENT
   - Produce the final investor-ready report with sections:
       • Executive Summary with rating (Strong Buy / Buy / Hold / Sell)
       • Company Overview and recent developments
         • Financial Performance (include KPIs table with YoY/QoQ deltas)
         • Technical & Market Analysis (price action, momentum, volatility, support/resistance)
         • Valuation Overview (table of multiples vs industry and vs history)
         • Market & Sentiment Analysis (top news drivers, analyst consensus, social sentiment)
         • Catalysts & Strategic Initiatives
         • Risk Matrix (likelihood vs impact) & Mitigations
         • Scenario Outlook (bull/base/bear with target prices & key drivers)
         • Final Recommendation & Rationale with actionability (entry range, stop-loss, time horizon)
         • Sources / Data provenance notes

COORDINATION REQUIREMENTS:
- Each agent must build upon previous findings and reference them explicitly.
- Avoid redundant re-statements; cite specific figures and sources where possible.
- Provide a cohesive recommendation that integrates qualitative and quantitative inputs.
- DO NOT include meta-discussion, delegations, or coordination logs in the final output.

RETURN FORMAT:
- Only the final Markdown report.
- Start directly with the Executive Summary headline (e.g., "## Executive Summary").
- Use Markdown tables or bullet lists where clarity improves.
"""


COORDINATION_KEYPHRASES = [
    "i will delegate",
    "delegate this task",
    "has completed",
    "handover",
    "i have reviewed",
    "as requested",
    "workflow",
]


def _strip_coordination_messages(report: str) -> str:
    """Remove agent coordination chatter if accidentally returned."""

    lowered = report.lower()
    if not any(marker in lowered for marker in COORDINATION_KEYPHRASES):
        return report

    lines = report.splitlines()
    start_index = 0
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        header = stripped.lower()
        if header.startswith("## executive summary") or header.startswith("# executive summary"):
            start_index = idx
            break
        if header.startswith("## investment") or header.startswith("# investment"):
            start_index = idx
            break
        if header.startswith("## overview") or header.startswith("# overview"):
            start_index = idx
            break
        if stripped.startswith("# ") or stripped.startswith("## "):
            start_index = idx
            break

    return "\n".join(lines[start_index:]) if start_index else report


# ---------------------------------------------------------------------------
# Core execution helpers
# ---------------------------------------------------------------------------


def generate_investment_report_with_team(
    ticker: str,
    company_name: Optional[str] = None,
    save_to_file: bool = True,
) -> Dict[str, Any]:
    """Run the multi-agent workflow and optionally persist artifacts."""

    ticker = ticker.upper().strip()
    company_name = company_name or "Company name to be determined"

    print(f"\n🚀 Launching multi-agent analysis for {ticker} ({company_name})\n")

    prompt = TEAM_PROMPT_TEMPLATE.format(ticker=ticker, company_name=company_name)
    team = _create_investment_team()

    max_attempts = 3
    base_delay = 15

    result_content: Optional[str] = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = team.run(prompt)
            result_content = getattr(result, "content", str(result))
            print("✅ Team collaboration complete\n")
            break
        except ModelProviderError as exc:  # Agno wraps provider errors here
            message = str(exc)
            print(f"⚠️  Provider error (attempt {attempt}/{max_attempts}): {message}")

            network_error = any(
                keyword in message.lower()
                for keyword in [
                    "getaddrinfo failed",
                    "connection refused",
                    "failed to establish",
                    "network is unreachable",
                    "timed out",
                ]
            )

            retryable_error = any(
                keyword in message.lower()
                for keyword in ["429", "resource_exhausted", "503", "unavailable", "rate limit"]
            )

            if network_error:
                if attempt == max_attempts:
                    raise ConnectionError(
                        "Network connection error while reaching Gemini API. "
                        "Check connectivity, firewall, or VPN settings."
                    ) from exc

                wait_seconds = 30
                print(f"   Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
                continue

            if retryable_error and attempt < max_attempts:
                wait_seconds = base_delay * (2 ** (attempt - 1))
                print(f"   Hit provider limits; waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)
                continue

            raise
        except Exception as exc:  # pragma: no cover - catch-all for robustness
            print(f"❌ Unexpected error: {exc}")
            raise

    if not result_content:
        raise RuntimeError("Analysis failed: no content returned from team run.")

    preview = result_content.replace("\n", " ")[:180]
    print(f"📄 Content preview: {preview}...")

    clean_report = _strip_coordination_messages(result_content)

    markdown_path: Optional[str] = None
    pdf_path: Optional[str] = None

    if save_to_file:
        os.makedirs("reports/output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        markdown_path = f"reports/output/{ticker}_team_report_{timestamp}.md"
        with open(markdown_path, "w", encoding="utf-8") as handle:
            handle.write(f"# Team Investment Analysis Report: {ticker}\n")
            handle.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            handle.write("---\n\n")
            handle.write(clean_report)

        print(f"💾 Markdown report saved to {markdown_path}")

        try:
            print("🖨️  Rendering PDF...")
            pdf_path = generate_pdf_report(ticker, company_name, clean_report)
            print(f"✅ PDF saved to {pdf_path}")
        except Exception as exc:  # pragma: no cover - PDF errors are non-fatal
            print(f"⚠️  PDF generation failed: {exc}")

    return {
        "ticker": ticker,
        "company_name": company_name,
        "report_markdown": clean_report,
        "markdown_path": markdown_path,
        "pdf_path": pdf_path,
        "timestamp": datetime.now().isoformat(),
    }



