import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google import genai
import os

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
target_ticker = st.sidebar.text_input("Target Asset (e.g., SPY)", value="SPY")
benchmark_ticker = st.sidebar.text_input("Benchmark Asset (e.g., GLD)", value="GLD")
time_period = st.sidebar.selectbox("Period", ["1y", "2y", "5y"])

# --- CORE LOGIC: RISK CALCULATION ---
@st.cache_data(ttl=3600)
def get_metrics(ticker, period):
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or len(data) < 10:
            return None
        
        df = data['Close']
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
            "prices": df
        }
    except Exception as e:
        st.error(f"Data Fetch Error ({ticker}): {str(e)}")
        return None

# --- CORE LOGIC: AI AGENT ---
def get_ai_insight(target_m, bench_m, key):
    try:
        # Initialize the GenAI client
        client = genai.Client(api_key=key)
        
        prompt = f"""
        You are a Solvency II Risk Expert. 
        Analyze the following data:
        Target ({target_m['ticker']}): Volatility {target_m['vol']:.2%}, VaR (95%) {target_m['var']:.2%}
        Benchmark ({bench_m['ticker']}): Volatility {bench_m['vol']:.2%}, VaR (95%) {bench_m['var']:.2%}
        
        Task:
        1. Compare profiles under Solvency II framework.
        2. Suggest Stress Test scenarios.
        3. 50-word executive summary for CRO.
        """
        
        # Try the most efficient model for 2026
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # Return the error message so we can diagnose
        return f"⚠️ AI Error: {str(e)}"

# --- EXECUTION ---
if st.sidebar.button("Run Analytics") and api_key:
    with st.spinner("Processing Financial Risk Models..."):
        # 1. Fetch Data
        t_metrics = get_metrics(target_ticker, time_period)
        b_metrics = get_metrics(benchmark_ticker, time_period)
        
        if t_metrics and b_metrics:
            # 2. Display Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"{target_ticker} Vol", f"{t_metrics['vol']:.2%}")
            col2.metric(f"{target_ticker} VaR", f"{t_metrics['var']:.2%}")
            col3.metric(f"{benchmark_ticker} Vol", f"{b_metrics['vol']:.2%}")
            col4.metric(f"{benchmark_ticker} VaR", f"{b_metrics['var']:.2%}")

            # 3. Charts
            fig = make_subplots(
                rows=2, cols=1, 
                subplot_titles=("Indexed Performance (Base 100)", "Risk Metric Comparison"),
                vertical_spacing=0.2
            )

            # Performance Plot
            t_base = t_metrics['prices'].iloc[0]
            b_base = b_metrics['prices'].iloc[0]
            fig.add_trace(go.Scatter(x=t_metrics['prices'].index, y=(t_metrics['prices']/t_base*100), name=target_ticker), row=1, col=1)
            fig.add_trace(go.Scatter(x=b_metrics['prices'].index, y=(b_metrics['prices']/b_base*100), name=benchmark_ticker), row=1, col=1)

            # Bar Plot
            fig.add_trace(go.Bar(name='Volatility', x=[target_ticker, benchmark_ticker], y=[t_metrics['vol'], b_metrics['vol']]), row=2, col=1)
            fig.add_trace(go.Bar(name='VaR (95%)', x=[target_ticker, benchmark_ticker], y=[abs(t_metrics['var']), abs(b_metrics['var'])]), row=2, col=1)
            
            fig.update_layout(height=700, template="plotly_white")
            # FIXED: Updated for Streamlit 2026 syntax
            st.plotly_chart(fig, width="stretch")

            # 4. AI Insight Section
            st.subheader("🤖 AI Regulatory Insight")
            ai_report = get_ai_insight(t_metrics, b_metrics, api_key)
            
            # If the report starts with ⚠️, it means an error occurred
            if "⚠️" in ai_report:
                st.error(ai_report)
            else:
                st.info(ai_report)
        else:
            st.error("Data source unavailable. Please check tickers or API limits.")
else:
    if not api_key:
        st.warning("Please enter your Gemini API Key to unlock AI insights.")
