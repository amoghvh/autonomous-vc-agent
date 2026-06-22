 Autonomous VC Analyst Agent

Deterministic Math + Stochastic Reasoning. An AI-driven investment researcher that synthesizes live market data with real-time news catalysts to generate professional-grade VC memos.
 
The Problem: 

Traditional stock screeners provide data but lack context. Chatbots provide context but lack accuracy. This agent bridges the gap by using a "Researcher-in-the-Loop" architecture: it doesn't just chat about stocks; it performs verifiable research before forming a thesis.
 
Core Intelligence


    Orchestration: Built with Pydantic-AI for type-safe, structured agentic workflows.

    Model: Powered by Google Gemini 3 Flash (and 2.5 Flash) for high-speed reasoning.

    Agency: The agent autonomously decides when to use the DuckDuckGo Search Tool to investigate earnings calls, partnerships (e.g., IREN), and market catalysts.

    Technical Logic: Integrated with yfinance to pull live market pricing and calculate 50-day Simple Moving Averages (SMA50).

 Deliverables:

The agent produces a Structured Investment Memo (PDF) featuring:

    Market Snapshot: Price vs. SMA50 position.

    Sentiment Analysis: AI-distilled mood from top 5 global news headlines.

    Risk Assessment: Color-coded risk levels (Low/Medium/High) based on technical and fundamental convergence.

    Actionable Recommendation: Concise, justified investment stances.

Tech Stack

    Language: Python 3.14+

    AI Framework: Pydantic-AI (Agentic Orchestration)

    LLM: Gemini API (Google Generative AI)

    Data: Yahoo Finance (yfinance), DuckDuckGo Search (DDGS)

    UI: Streamlit

    PDF Engine: fpdf2

 Quick Start
1. Prerequisites:

Ensure you have a Google AI Studio API Key. Set it in your environment:
Bash

export GOOGLE_API_KEY='your_api_key_here'

2. Installation:
Bash

# Clone the repository
git clone https://github.com/amoghvh/autonomous-vc-agent.git
cd autonomous-vc-agent

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


3. Run the Dashboard
Bash

streamlit run app.py

 Market Compatibility

The agent is market-agnostic. It supports global tickers including:

    US Markets: NVDA, TSLA, AAPL

    Indian Markets: RELIANCE.NS, TATAELXSI.NS, HDFCBANK.NS

 Contact & Collaboration

I am an AI Engineer focused on building autonomous agentic systems that solve real-world financial and data problems.

    Developer: Amogh Hosamani

    Email: amoghv.hosamani@gmail.com

    GitHub: @amoghvh
