# solvency2-ai-agent
🚀 Core Features
Automated Risk Metrics: Real-time calculation of Annualized Volatility and Value-at-Risk (VaR 95%) using historical market data.
AI-Driven Insights: Integration with Google Gemini (2.0/1.5) to generate qualitative regulatory reports and CRO executive summaries.
Interactive Visualizations: High-fidelity Plotly charts for cumulative performance tracking and risk metric benchmarking.
Smart Caching: Optimized performance and API quota management using Streamlit's @st.cache_data to ensure stability for Free Tier users.
2026 Ready: Built with the latest Streamlit syntax and updated Pandas 3.0+ compatibility (using strict .iloc indexing).
🛠️ Tech Stack
Frontend: Streamlit
Data Source: Yahoo Finance (yfinance)
Calculations: NumPy, Pandas
Visuals: Plotly
AI Engine: Google GenAI SDK (Gemini 2.0 Flash)
📋 Prerequisites
Before running the application, ensure you have:
Python 3.11+ installed.
A Google Gemini API Key (obtainable from Google AI Studio).
Internet access (for fetching real-time ticker data).
📥 Installation
Clone the repository:
code
Bash
git clone https://github.com/your-username/solvency2-ai-agent.git
cd solvency2-ai-agent
Install dependencies:
code
Bash
pip install -r requirements.txt
Run the application:
code
Bash
streamlit run App.py
🖥️ Usage Guide
Enter API Key: Paste your Gemini API Key into the sidebar input field.
Define Assets: Enter the ticker symbols for the Target Asset (e.g., SPY for S&P 500) and the Benchmark (e.g., GLD for Gold).
Select Horizon: Choose the historical period (1y, 2y, or 5y) for the risk calculation.
Run Analytics: Click the button to trigger data fetching and AI report generation.
Interpret Results:
Review the Volatility and VaR metrics in the top row.
Analyze the Performance Chart for relative growth comparisons.
Read the AI Regulatory Insight for automated stress-test suggestions and Solvency II analysis.
⚠️ Important Note on API Quotas
This app uses the Gemini Free Tier. If you encounter a 429 Resource Exhausted error:
This is a rate limit enforced by Google.
The application implements auto-caching; once a report is successfully generated, it will be stored for 1 hour to prevent further quota consumption.
Please wait 60 seconds before re-running analytics if the limit is reached.
⚖️ Disclaimer
This software is for educational and research purposes only. It does not constitute financial advice. The risk metrics and AI-generated insights are based on historical data and probabilistic models which do not guarantee future results. Users should consult with a certified actuary or financial advisor for regulatory compliance.
Developed by [Your Name/Handle]
Building the future of AI-driven Financial Risk Management.
