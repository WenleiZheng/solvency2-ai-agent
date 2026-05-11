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

# --- CORE LOGIC: AI AGENT (REPLACED WITH CACHED VERSION) ---
@st.cache_data(ttl=3600)
def get_ai_insight(t_ticker, t_vol, t_var, b_ticker, b_vol, b_var, key):
    """
    Analyzes risk data using Gemini 2.0. 
    Results are cached to prevent '429 Resource Exhausted' errors.
    """
    try:
        client = genai.Client(api_key=key)
        
        prompt = f"""
        You are a Solvency II Risk Expert. 
        Analyze the following data:
        Target ({t_ticker}): Volatility {t_vol:.2%}, VaR (95%) {t_var:.2%}
        Benchmark ({b_ticker}): Volatility {b_vol:.2%}, VaR (95%) {b_var:.2%}
        
        Task:
        1. Compare profiles under Solvency II framework.
        2. Suggest Stress Test scenarios.
        3. 50-word executive summary for CRO.
        Write in professional English.
        """
        
        # Using 2.0-flash which was confirmed to exist in your environment
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "⚠️ **QUOTA EXCEEDED**: You are using a Free Tier API Key. Please wait 60 seconds. Caching is enabled, so once loaded, this won't happen again for these assets."
        elif "404" in error_msg:
            return "⚠️ **MODEL NOT FOUND**: Gemini 2.0-flash is currently unavailable in your region via API."
        else:
            return f"⚠️ **AI ERROR**: {error_msg}"

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
            # Using 2026 Streamlit syntax
            st.plotly_chart(fig, width="stretch")

            # 4. AI Insight Section (MODIFIED TO PASS INDIVIDUAL VALUES)
            st.subheader("🤖 AI Regulatory Insight")
            
            ai_report = get_ai_insight(
                t_metrics['ticker'], 
                t_metrics['vol'], 
                t_metrics['var'],
                b_metrics['ticker'], 
                b_metrics['vol'], 
                b_metrics['var'],
                api_key
            )
            
            if "⚠️" in ai_report:
                st.warning(ai_report)
            else:
                st.info(ai_report)
        else:
            st.error("Data source unavailable. Please check tickers or API limits.")
else:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to unlock AI insights.")
    else:
        st.info("Click 'Run Analytics' to generate the risk report.")
