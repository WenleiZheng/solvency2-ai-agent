# solvency2-ai-agent
# 🛡️ Solvency II AI Risk Agent (2026 Edition)

An automated financial risk monitoring platform designed for risk managers and actuaries. This agent-driven application combines real-time market analytics with generative AI to provide regulatory insights and stress-testing scenarios under the Solvency II Market Risk framework.

## 🚀 Core Features

- **Automated Risk Metrics**: Real-time calculation of Annualized Volatility and Value-at-Risk (VaR 95%) using historical market data.
- **AI-Driven Insights**: Integration with Google Gemini AI to generate qualitative regulatory reports and CRO executive summaries.
- **Interactive Visualizations**: High-fidelity Plotly charts for cumulative performance tracking and risk metric benchmarking.
- **Smart Caching**: Optimized performance and API quota management using Streamlit's cache system to ensure stability.
- **2026 Ready**: Built with the latest Streamlit syntax and updated Pandas 3.0+ compatibility (using strict .iloc indexing).

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Source**: Yahoo Finance (yfinance)
- **Calculations**: NumPy, Pandas 3.0
- **Visuals**: Plotly
- **AI Engine**: Google GenAI SDK (Gemini 2.0/1.5 Flash)

## 📋 Prerequisites

Before running the application, ensure you have:
1. Python 3.11 or higher installed.
2. A Google Gemini API Key from Google AI Studio.
3. Internet access for fetching real-time market data.

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/solvency2-ai-agent.git
   cd solvency2-ai-agent
   
