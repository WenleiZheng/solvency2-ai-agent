import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google import genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Solvency II AI Risk Agent", layout="wide")

# --- UI HEADER ---
st.title("🛡️ Solvency II Financial Risk Analytics Platform")
st.markdown("""
*Automated Risk Monitoring & AI-Driven Regulatory Insights (2026 Edition)*
""")

# --- SIDEBAR / SETTINGS ---
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
target_ticker = st.sidebar.text_input("Target Asset (e.g., ^GSPC)", value="SPY")
benchmark_ticker = st.sidebar.text_input("Benchmark Asset (e.g., GLD)", value="GLD")
time_period = st.sidebar.selectbox("Period", ["1y", "2y", "5y"])

# --- CORE LOGIC: RISK CALCULATION ---
@st.cache_data(ttl=3600)
def get_metrics(ticker, period):
    try:
        # Fetching data
        data = yf.download(ticker, period=period, progress=False)
        
        # Check if data is empty (handles rate limits or invalid tickers)
        if data.empty or len(data) < 10:
            return None
        
        # Extract Close prices
        df = data['Close']
        
        # Ensure it is a Series (Pandas 3.0+ handling)
        if isinstance(df, pd.DataFrame): 
            df = df.iloc[:, 0]
            
        returns = df.pct_change().dropna()
        
        if returns.empty:
            return None

        vol = returns.std() * np.sqrt(252)
        var_95 = np.percentile(returns, 5)
        
        return {
            "ticker": ticker, 
            "vol": float(vol), 
            "var": float(var_95), 
            "prices": df, 
            "returns": returns
        }
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

# --- CORE LOGIC: AI AGENT ---
def get_ai_insight(target_m, bench_m, key):
    client = genai.Client(api_key=key)
    prompt = f"""
    You are a Solvency II Risk Expert. 
    Analyze the following data for a portfolio:
    Target Asset ({target_m['ticker']}): Volatility {target_m['vol']:.2%}, VaR (95%) {target_m['var']:.2%}
    Benchmark Asset ({bench_m['ticker']}): Volatility {bench_m['vol']:.2%}, VaR (95%) {bench_m['var']:.2%}
    
    Task:
    1. Compare the risk profiles under Solvency II Market Risk framework.
    2. Suggest specific Stress Test scenarios (e.g., Interest Rate shocks or Equity Drawdowns).
    3. Provide a 50-word executive summary for the CRO.
    Write the report in professional English.
    """
    try:
        # Primary model choice
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        return response.text
    except Exception:
        # Fallback to alternative model
        try:
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            return response.text
        except Exception as e:
            return f"AI Generation Error: {str(e)}"

# --- EXECUTION ---
if st.sidebar.button("Run Analytics") and api_key:
    with st.spinner("Fetching market data and generating AI report..."):
        # 1. Fetch Data
        t_metrics = get_metrics(target_ticker, time_period)
        b_metrics = get_metrics(benchmark_ticker, time_period)
        
        if t_metrics and b_metrics:
            # 2. Display Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"{target_ticker} Volatility", f"{t_metrics['vol']:.2%}")
            col2.metric(f"{target_ticker} VaR (95%)", f"{t_metrics['var']:.2%}")
            col3.metric(f"{benchmark_ticker} Volatility", f"{b_metrics['vol']:.2%}")
            col4.metric(f"{benchmark_ticker} VaR (95%)", f"{b_metrics['var']:.2%}")

            # 3. Horizontal Comparison Charts
            fig = make_subplots(
                rows=2, cols=1, 
                subplot_titles=("Relative Performance (Indexed to 100)", "Risk Metric Comparison (Vol vs VaR)"),
                vertical_spacing=0.2
            )

            # Plot 1: Cumulative Performance (Using .iloc[0] for Pandas 3.0 compatibility)
            t_base = t_metrics['prices'].iloc[0]
            b_base = b_metrics['prices'].iloc[0]
            
            fig.add_trace(go.Scatter(
                x=t_metrics['prices'].index, 
                y=(t_metrics['prices'] / t_base * 100), 
                name=target_ticker
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=b_metrics['prices'].index, 
                y=(b_metrics['prices'] / b_base * 100), 
                name=benchmark_ticker
            ), row=1, col=1)

            # Plot 2: Bar Chart Comparison
            fig.add_trace(go.Bar(
                name='Annualized Volatility', 
                x=[target_ticker, benchmark_ticker], 
                y=[t_metrics['vol'], b_metrics['vol']]
            ), row=2, col=1)
            
            fig.add_trace(go.Bar(
                name='VaR (95%) Confidence', 
                x=[target_ticker, benchmark_ticker], 
                y=[abs(t_metrics['var']), abs(b_metrics['var'])]
            ), row=2, col=1)
            
            fig.update_layout(height=800, template="plotly_white", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # 4. AI Insight Section
            st.subheader("🤖 AI Regulatory Insight (Solvency II Expert)")
            ai_report = get_ai_insight(t_metrics, b_metrics, api_key)
            st.info(ai_report)
        else:
            st.error("Failed to retrieve data. This could be due to API rate limits (Yahoo Finance) or an invalid ticker symbol. Please try again in a few minutes.")

else:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    else:
        st.info("Click 'Run Analytics' to start the Solvency II risk assessment.")
