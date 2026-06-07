"""VC-style snapshot agent using pydantic-ai : maps price vs 50-day MA, news, risk, and recommendation.

Gemini runs through pydantic-ai's ``google-gla`` provider (Google Generative Language API).
Set ``GOOGLE_API_KEY`` from Google AI Studio; optional ``PYDANTIC_AI_MODEL`` overrides the full ``provider:model`` id.
"""

from __future__ import annotations

import functools
import os
from typing import Literal

import yfinance as yf
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

RiskLevel = Literal["Low", "Medium", "High"]
NewsSentiment = Literal["Positive", "Neutral", "Negative"]


class VCAssessment(BaseModel):
    """Model output from the VC analyst agent."""

    risk_assessment: RiskLevel = Field(
        ...,
        description="Qualitative risk given the ticker’s price versus its 50-day moving average.",
    )
    recommendation: str = Field(
        ...,
        description="Actionable stance (e.g. accumulate, hold, trim) justified by MA50 positioning and news.",
    )
    news_sentiment: NewsSentiment = Field(
        ...,
        description="Overall tilt of recent news toward the stock outlook.",
    )
    key_headlines: list[str] = Field(
        ...,
        description="Up to five notable headlines or snippets from news search and catalyst context.",
    )


def sma_50(ticker: str) -> float:
    """50-day simple moving average of adjusted close using recent history."""
    symbol = ticker.strip().upper()
    hist = yf.Ticker(symbol).history(period="6mo")
    if hist is None or len(hist) < 50:
        raise ValueError(
            f"Need at least 50 trading sessions of history for {symbol!r}; got {0 if hist is None else len(hist)}."
        )
    return float(hist["Close"].rolling(50).mean().iloc[-1])


# ``google-gla`` = Gemini developer API (uses ``GOOGLE_API_KEY``), not Vertex.
DEFAULT_MODEL = os.getenv("PYDANTIC_AI_MODEL", "google-gla:gemini-2.5-flash")

_AGENT_INSTRUCTIONS = (
    "You are a concise venture-style public-equity analyst. "
    "The user supplies a ticker, current price, the 50-day simple moving average (SMA50), "
    "and whether price is above or below SMA50—these facts are authoritative for technical context. "
    "You MUST call search_news with the same ticker before giving any final recommendation. "
    "Use those headlines to surface upcoming catalysts (for example earnings dates such as May 20) "
    "and strategic items (for example partnerships such as IREN) when they appear in results; "
    "weigh them alongside MA50 when judging risk and stance. "
    "Set risk_assessment to Low when the setup is orderly (typically price at or above SMA50 "
    "without implying extreme overstretch unless justified), Medium when mixed or marginal, "
    "and High when price is materially below SMA50 or the setup implies elevated drawdown risk. "
    "Set news_sentiment to Positive, Neutral, or Negative based on the searched headlines and catalyst tone. "
    "Populate key_headlines with up to five concise strings derived from search_news (and authoritative facts). "
    "The recommendation MUST align with SMA50 and incorporate material news or catalyst risk: "
    "favor constructive stance when above, defensive or wait-and-see when below unless news overrides clearly. "
    "One short sentence for recommendation."
)


def _register_news_tool(agent: Agent[None, VCAssessment]) -> None:
    """Attach DuckDuckGo news search to the agent instance."""

    @agent.tool
    def search_news(ctx: RunContext[None], ticker: str) -> str:
        """Return the top five headline lines from a DuckDuckGo text search for recent stock news."""
        sym = ticker.strip().upper()
        query = f"{sym} stock news May 2026"
        try:
            rows = DDGS().text(query, max_results=5)
        except Exception as e:
            return f"News search failed: {e}"
        lines: list[str] = []
        for row in (rows or [])[:5]:
            title = (row.get("title") or "").strip()
            if title:
                lines.append(title)
        return "\n".join(lines) if lines else "No headlines returned."


@functools.cache
def get_vc_agent(model: str | None = None) -> Agent[None, VCAssessment]:
    """Return a cached pydantic-ai ``Agent``. Lazy so importing this module works without API keys.

    Default configuration uses Gemini with :class:`GoogleProvider` and ``GOOGLE_API_KEY``.
    """
    resolved = DEFAULT_MODEL if model is None else model
    if resolved.startswith("google-gla:"):
        gemini_name = resolved.split(":", maxsplit=1)[1]
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set; it is required for Gemini via the google-gla provider."
            )
        provider = GoogleProvider(api_key=api_key)
        agent: Agent[None, VCAssessment] = Agent(
            GoogleModel(gemini_name, provider=provider),
            output_type=VCAssessment,
            instructions=_AGENT_INSTRUCTIONS,
        )
    else:
        agent = Agent(resolved, output_type=VCAssessment, instructions=_AGENT_INSTRUCTIONS)
    _register_news_tool(agent)
    return agent


def build_price_vs_ma_prompt(
    ticker: str,
    price: float,
    *,
    ma50: float | None = None,
) -> str:
    """Compose the user message with computed MA context."""
    ma = sma_50(ticker) if ma50 is None else ma50
    position = "above" if price >= ma else "below"
    pct = (price / ma - 1.0) * 100.0
    return (
        f"Ticker: {ticker.strip().upper()}\n"
        f"Current price: {price:.4f}\n"
        f"50-day SMA: {ma:.4f}\n"
        f"Price is {position} the 50-day SMA (≈ {pct:+.2f}% vs SMA).\n"
        "Call search_news with this ticker first, then return risk_assessment, recommendation, "
        "news_sentiment, and key_headlines."
    )


async def assess_risk(ticker: str, price: float, *, model: str | None = None) -> VCAssessment:
    """Run the agent asynchronously (fetches SMA50 from yfinance)."""
    prompt = build_price_vs_ma_prompt(ticker, price)
    result = await get_vc_agent(model).run(prompt)
    return result.output


def assess_risk_sync(ticker: str, price: float, *, model: str | None = None) -> VCAssessment:
    """Synchronous helper; same semantics as ``assess_risk``."""
    prompt = build_price_vs_ma_prompt(ticker, price)
    result = get_vc_agent(model).run_sync(prompt)
    return result.output


if __name__ == "__main__":
    demo_ticker = "NVDA"
    stock = yf.Ticker(demo_ticker)
    demo_price = float(stock.fast_info["last_price"])
    out = assess_risk_sync(demo_ticker, demo_price)
    print(out.model_dump_json(indent=2))
import yfinance as yf

def get_market_data(ticker_symbol):
    # Ensure Indian stocks have the correct suffix
    if ticker_symbol == "RIL" or ticker_symbol == "RELIANCE":
        ticker_symbol = "RELIANCE.NS"
    
    ticker = yf.Ticker(ticker_symbol)
    
    try:
        # Use the high-level 'dividends' property instead of '_dividends'
        divs = ticker.dividends
        
        # Use 'fast_info' for the price (more reliable in 2026 versions)
        price = ticker.fast_info['last_price']
        
        return price, divs
    except Exception as e:
        print(f"Error fetching {ticker_symbol}: {e}")
        return None, None

price, dividends = get_market_data("RELIANCE.NS")
print(f"Current Price: {price}")
