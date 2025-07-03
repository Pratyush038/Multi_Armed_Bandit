import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
from datetime import datetime, timedelta
from thompson_trader import (
    ThompsonSamplingStockTrader,
    portfolio1,
    portfolio2,
    run_multiple_simulations,
    download_and_prepare_data,
    get_sector_allocation,
    get_portfolio_sectors,
    calculate_buy_and_hold_performance,
    calculate_random_selection_performance,
    calculate_risk_metrics,
    calculate_portfolio_risk_metrics
)
import time

def format_delta(delta):
    if delta is None or delta == "":
        return ""
    delta = str(delta)
    delta = delta.replace("↑", "▲").replace("↓", "▼")
    return delta

# Page config
st.set_page_config(
    page_title="Thompson Sampling Stock Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Sidebar with matching dark-purple gradient and highlight tone */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(6, 182, 212, 0.15), rgba(139, 92, 246, 0.15)) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
        box-shadow: 2px 0 10px rgba(139, 92, 246, 0.05) !important;
    }


    /* Apply to entire page, including block-container */
    html, body, .main, .block-container {
        height: auto !important;
        background-color: #000 !important;
        background-image: radial-gradient(circle, grey 0.4px, transparent 0.2px) !important;
        background-size: 20px 20px !important;
        background-repeat: repeat !important;
    }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Sora:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-weight: 700;
        font-size: 3.5rem !important;
        margin-bottom: 2rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
            
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.3)); }
        to { filter: drop-shadow(0 0 30px rgba(59, 130, 246, 0.6)); }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(145deg, rgba(20, 25, 40, 0.95), rgba(35, 45, 65, 0.95)) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(124, 58, 237, 0.4) !important;
        box-shadow: 10px 0 30px rgba(124, 58, 237, 0.15) !important;
        padding: 1.5rem !important;
    }
    .css-1d391kg h1, 
    .css-1d391kg h2, 
    .css-1d391kg h3 {
        background: linear-gradient(to right, #a78bfa, #9333ea) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        text-align: center !important;
        margin: 1rem !important;
        
    }
    /* Main content containers */           
    .content-container {
        background: radial-gradient(circle at center, rgba(59, 130, 246, 0.3), #0f172a 85%);
        color: #bae6fd;
        box-shadow: 0 20px 50px rgba(14, 165, 233, 0.2), 0 0 30px rgba(59, 130, 246, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        border: 1px solid rgba(14, 165, 233, 0.2);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    .content-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.08), transparent);
        z-index: 2;
        transition: left 0.8s ease;
        pointer-events: none;
    }
    .content-container:hover {
        background: linear-gradient(145deg, #1f2937 0%, #374151 100%);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 30px 80px rgba(99, 102, 241, 0.35);
        transform: scale(1.015);
    }
    .content-container:hover::before {
        left: 100%;
    }
    .content-container h2,
    .content-container h3,
    .portfolio-header h3 {
        background: linear-gradient(135deg, #22d3ee, #06b6d4) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-fill-color: transparent !important;
        text-align: center !important;
    }

        
    /* Portfolio sections */
    .portfolio-section {
        background: radial-gradient(circle at center, rgba(59, 130, 246, 0.25), #0f172a 85%);
        color: #e2e8f0;
        border: 1px solid rgba(14, 165, 233, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 20px 50px rgba(14, 165, 233, 0.2), 0 0 30px rgba(59, 130, 246, 0.15);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        z-index: 0;
    }

    .portfolio-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.08), transparent);
        z-index: 2;
        transition: left 0.8s ease;
        pointer-events: none;
    }

    .portfolio-section:hover {
        background: linear-gradient(145deg, #1f2937 0%, #374151 100%);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 30px 80px rgba(99, 102, 241, 0.35);
        transform: scale(1.015);
    }

    .portfolio-section:hover::before {
        left: 100%;
    }

    .portfolio-section h2,
    .portfolio-section h3,
    .portfolio-section p {
        color: #bae6fd;
        text-align: center;
    }

    
    /* Status containers */
    .status-container {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        animation: slideUp 0.6s ease-out;
    }
    .container-wrapper {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .status-container.loading {
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .status-container.success {
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .status-container.warning {
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(59, 130, 246, 0.2);
        border-left: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .status-text {
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .status-text.loading {
        color: #fff;
    }
    
    .status-text.success {
        color: #fff;
    }
    
    .status-text.warning {
        color: #f59e0b;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        margin: 0.5rem 0 !important;
        text-align: center !important;
        align-items: center !important;
        justify-content: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Metric container hover effect */
    [data-testid="metric-container"]:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        transform: scale(1.02) !important;
    }

    /* Fix Streamlit metric label and value colors for dark background */
    [data-testid="metric-container"] label, 
    [data-testid="metric-container"] .css-1ht1j8u, /* metric label */
    [data-testid="metric-container"] .css-1dp5vir /* metric value */
    {
        color: #fff !important;
        text-shadow: 0 1px 4px #000a;
        text-align: center !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    [data-testid="metric-container"] .css-1dp5vir {
        color: #f0f9ff !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] .css-1b4bkrp {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #16a34a !important;
        text-align: center !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Sidebar text color fixes (reverted to light gray for visibility) */
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg label, .css-1d391kg strong {
        color: #e2e8f0 !important;
    }
    
    /* Streamlit widget text colors */
    .stSlider, .stNumberInput, .stDateInput {
        color: #bae6fd !important;
    }
    
    /* Text area and input styling */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        color: #bae6fd !important;
    }
    
    /* Success and error message styling */
    .stSuccess, .stError {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        color: #bae6fd !important;
    }
    
    /* Ensure all text is visible */
    * {
        word-wrap: break-word;
        word-break: break-word;
        white-space: normal;
    }
    /* ENFORCE green color for metric delta (arrow and ±xx%) everywhere */
    html body [data-testid="metric-container"] .css-1b4bkrp, 
    html body [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #16a34a !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    /* Replace Streamlit metric delta arrow with triangle */
    [data-testid="stMetricDelta"] span {
        font-family: inherit !important;
    }
    [data-testid="stMetricDelta"] span:before {
        content: '' !important;
    }
    [data-testid="stMetricDelta"] span:after {
        content: '' !important;
    }
    [data-testid="stMetricDelta"][data-testid*="positive"] span:before {
        content: '▲ ' !important;
        color: #16a34a !important;
        font-size: 1.1em !important;
        font-weight: 700 !important;
        vertical-align: middle !important;
    }
    [data-testid="stMetricDelta"][data-testid*="negative"] span:before {
        content: '▼ ' !important;
        color: #ef4444 !important;
        font-size: 1.1em !important;
        font-weight: 700 !important;
        vertical-align: middle !important;
    }
    /* Make the delta value itself match the triangle color */
    [data-testid="stMetricDelta"][data-testid*="positive"] span {
        color: #16a34a !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"][data-testid*="negative"] span {
        color: #ef4444 !important;
        font-weight: 700 !important;
    }
    /* Hide the default Streamlit arrow (works for most Streamlit versions) */
    [data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    .subtitle {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #93c5fd; /* optional: a bit lighter than title */
        }
    /* Center all section headers and portfolio section titles */
    .content-container h2,
    .content-container h3,
    .portfolio-section h3,
    .portfolio-section h2 {
        text-align: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;  /* violet-500 to pink-500 */
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        margin-top: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(236, 72, 153, 0.4) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed, #db2777) !important;  /* darker violet-pink */
        box-shadow: 0 6px 18px rgba(236, 72, 153, 0.6) !important;
        transform: scale(1.02) !important;
    }

    /* Modal styling */
    #info-modal-overlay {backdrop-filter: blur(2px);}
    #info-modal-content {max-width: 420px !important; width: 92vw !important; max-height: 70vh !important; overflow-y: auto !important;}
    .stCloseModalBtn button {
        position: absolute;
        top: 1rem;
        right: 1.1rem;
        background: none !important;
        border: none !important;
        color: #bae6fd !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        z-index: 2;
        width: 2.5rem !important;
        height: 2.5rem !important;
        line-height: 2rem !important;
        border-radius: 50% !important;
        transition: color 0.2s, background 0.2s;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .stCloseModalBtn button:hover {
        color: #38bdf8 !important;
        background: rgba(56,189,248,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# Title with info button and modal logic
if 'show_info_details' not in st.session_state:
    st.session_state['show_info_details'] = False

# Info button logic
if 'show_info_details' not in st.session_state:
    st.session_state['show_info_details'] = False

col_title, col_info = st.columns([0.95, 0.05])
with col_title:
    st.markdown("""
        <h1 class="main-title" style="margin-bottom: 0; text-align: center;">
            Thompson Sampling Stock Trader
        </h1>
        <h1 class="subtitle">Optimal Stock Trading Strategy Using Thompson Sampling in the Context of Multi-Armed Bandits</h1>
    """, unsafe_allow_html=True)

with st.expander("What do these terms mean?", expanded=False):
    st.markdown("""
    <div style="color: #bae6fd; font-size: 1.1rem;">
    <h3 style="color: #38bdf8;">Multi-Armed Bandit</h3>
    <p>
    The <b>Multi-Armed Bandit</b> problem is a classic scenario in probability and machine learning. Imagine a row of slot machines ("one-armed bandits"), each with an unknown payout. The challenge is to find the best strategy to maximize your total reward over time by balancing <b>exploration</b> (trying different machines) and <b>exploitation</b> (sticking with the best one found so far).
    </p>
    <h3 style="color: #38bdf8;">Thompson Sampling</h3>
    <p>
    <b>Thompson Sampling</b> is a Bayesian algorithm for solving the Multi-Armed Bandit problem. It models the uncertainty of each option's reward and randomly samples from these models to decide which to try next. Over time, it naturally balances exploration and exploitation, focusing more on the best-performing options.
    </p>
    <h3 style="color: #38bdf8;">Total Return</h3>
    <p>
    <b>Total Return</b> is the overall percentage gain or loss of a portfolio over a period, including all price changes and dividends. It is calculated as:<br>
    <code>Total Return = (Final Value / Initial Value - 1) × 100%</code>
    </p>
    <h3 style="color: #38bdf8;">Sharpe Ratio</h3>
    <p>
    The <b>Sharpe Ratio</b> measures risk-adjusted return. It is the average return earned in excess of the risk-free rate per unit of volatility (standard deviation). Higher Sharpe ratios indicate better risk-adjusted performance.<br>
    <code>Sharpe Ratio = (Mean Portfolio Return) / (Portfolio Standard Deviation)</code>
    </p>
    <h3 style="color: #38bdf8;">Other Terms</h3>
    <ul>
    <li><b>Buy & Hold:</b> A strategy where you simply buy a portfolio and hold it for the entire period, without trading.</li>
    <li><b>Simulations:</b> Running the strategy multiple times to estimate average performance and variability.</li>
    <li><b>Confidence Band:</b> The shaded area around a line in a chart, showing the range of possible outcomes (e.g., ±1 standard deviation).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Simulation Settings Sidebar Header (Bright Purple Style)
st.sidebar.markdown("""
<div style='
    background: transparent;
    padding: 1rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    text-align: center;
'>
    <h2 style='
        margin: 0;
        font-size: 1.5rem;
        font-family: Inter, sans-serif !important;
        letter-spacing: 1.5px !important;
        background: linear-gradient(90deg, #38bdf8, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;   
    '>Simulation Settings</h2>

</div>
""", unsafe_allow_html=True)

# Sidebar widgets
st.sidebar.markdown("""
<div style="color: #bae6fd; font-weight: 600; margin-bottom: 0.5rem;">
    <strong>Number of Simulations</strong>
</div>
""", unsafe_allow_html=True)
num_simulations = st.sidebar.slider("", 10, 500, 100, label_visibility="collapsed")

st.sidebar.markdown("""
<div style="color: #bae6fd; font-weight: 600; margin-bottom: 0.5rem;">
    <strong>Random Seed</strong>
</div>
""", unsafe_allow_html=True)
seed = st.sidebar.number_input("", value=42, label_visibility="collapsed")

st.sidebar.markdown("""
<div style="color: #bae6fd; font-weight: 600; margin-bottom: 0.5rem;">
    <strong>Start Date</strong>
</div>
""", unsafe_allow_html=True)
start_date = st.sidebar.date_input("", datetime.today() - timedelta(days=365), label_visibility="collapsed")

st.sidebar.markdown("""
<div style="color: #bae6fd; font-weight: 600; margin-bottom: 0.5rem;">
    <strong>End Date</strong>
</div>
""", unsafe_allow_html=True)
end_date = st.sidebar.date_input("", datetime.today(), label_visibility="collapsed")

# Reset Button
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
if st.sidebar.button("Rerun Simulations"):
    st.session_state.simulations_run = False
    st.session_state.data_loaded = False
    st.rerun()
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Cache stock data
@st.cache_data(show_spinner=False)
def get_stock_data(portfolio, start, end):
    return download_and_prepare_data(portfolio, start, end)

# Create loading state management
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'simulations_run' not in st.session_state:
    st.session_state.simulations_run = False

# Loading data with custom spinner
if not st.session_state.data_loaded:
    st.markdown("""
    <div class="status-container loading">
        <div class="loading-spinner"></div>
        <div class="status-text loading">Downloading stock data...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulate loading time for better UX
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    
    # Download data
    data1, stats1 = get_stock_data(portfolio1, start_date, end_date)
    data2, stats2 = get_stock_data(portfolio2, start_date, end_date)
    
    progress_bar.empty()
    st.session_state.data_loaded = True
    st.session_state.data1 = data1
    st.session_state.stats1 = stats1
    st.session_state.data2 = data2
    st.session_state.stats2 = stats2
    
    # Success message
    st.markdown("""
    <div class="status-container success">
        <div class="status-text success">✓ Stock data loaded successfully!</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
    st.rerun()

else:
    data1, stats1 = st.session_state.data1, st.session_state.stats1
    data2, stats2 = st.session_state.data2, st.session_state.stats2

# Filter portfolios to only valid symbols
valid_symbols1 = [s for s in portfolio1 if s in stats1.index]
valid_symbols2 = [s for s in portfolio2 if s in stats2.index]

# Optional: Warn if any stocks are missing
removed1 = set(portfolio1) - set(valid_symbols1)
removed2 = set(portfolio2) - set(valid_symbols2)

if removed1:
    st.markdown(f"""
    <div class="status-container warning">
        <div class="status-text warning">⚠ Large-cap stocks removed due to missing data: {', '.join(removed1)}</div>
    </div>
    """, unsafe_allow_html=True)

if removed2:
    st.markdown(f"""
    <div class="status-container warning">
        <div class="status-text warning">⚠ Top Performers removed due to missing data: {', '.join(removed2)}</div>
    </div>
    """, unsafe_allow_html=True)

# Run simulations with loading state
if not st.session_state.simulations_run:
    st.markdown("""
    <div class="status-container loading">
        <div class="loading-spinner"></div>
        <div class="status-text loading">Running simulations...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar for simulations
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)
        if i < 50:
            status_text.text(f"Running Portfolio 1 simulations... {i*2}%")
        else:
            status_text.text(f"Running Portfolio 2 simulations... {(i-50)*2}%")
    
    # Run actual simulations
    avg1, std1, mean_ret1, std_ret1, mean_shp1, std_shp1, selections1 = run_multiple_simulations(
        ThompsonSamplingStockTrader, portfolio1, data1, stats1, num_simulations, seed
    )
    avg2, std2, mean_ret2, std_ret2, mean_shp2, std_shp2, selections2 = run_multiple_simulations(
        ThompsonSamplingStockTrader, portfolio2, data2, stats2, num_simulations, seed
    )
    
    progress_bar.empty()
    status_text.empty()
    
    # Store results
    st.session_state.simulations_run = True
    st.session_state.results = {
        'avg1': avg1, 'std1': std1, 'mean_ret1': mean_ret1, 'std_ret1': std_ret1,
        'mean_shp1': mean_shp1, 'std_shp1': std_shp1, 'selections1': selections1,
        'avg2': avg2, 'std2': std2, 'mean_ret2': mean_ret2, 'std_ret2': std_ret2,
        'mean_shp2': mean_shp2, 'std_shp2': std_shp2, 'selections2': selections2
    }
    
    # Success message
    st.markdown("""
    <div class="status-container success">
        <div class="status-text success">✓ Simulations completed successfully!</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
    st.rerun()

else:
    results = st.session_state.results
    avg1, std1, mean_ret1, std_ret1, mean_shp1, std_shp1, selections1 = (
        results['avg1'], results['std1'], results['mean_ret1'], results['std_ret1'],
        results['mean_shp1'], results['std_shp1'], results['selections1']
    )
    avg2, std2, mean_ret2, std_ret2, mean_shp2, std_shp2, selections2 = (
        results['avg2'], results['std2'], results['mean_ret2'], results['std_ret2'],
        results['mean_shp2'], results['std_shp2'], results['selections2']
    )

# Results container with proper nesting
st.markdown("""
<div class="content-container">
    <h2>Simulation Results</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Large-cap Portfolio</h3>
    """, unsafe_allow_html=True)
    
    st.metric("Mean Total Return", f"{mean_ret1:.2f}%", format_delta(f"±{std_ret1:.2f}%"))
    st.metric("Mean Sharpe Ratio", f"{mean_shp1:.2f}", format_delta(f"±{std_shp1:.2f}"))
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Top Performers Portfolio</h3>
    """, unsafe_allow_html=True)
    
    st.metric("Mean Total Return", f"{mean_ret2:.2f}%", format_delta(f"±{std_ret2:.2f}%"))
    st.metric("Mean Sharpe Ratio", f"{mean_shp2:.2f}", format_delta(f"±{std_shp2:.2f}"))
    
    st.markdown("</div>", unsafe_allow_html=True)

# Chart container with proper nesting
st.markdown("""
<div class="content-container">
    <h2>Portfolio Value Over Time</h2>
""", unsafe_allow_html=True)

df_plot = pd.DataFrame({
    'Day': np.arange(len(avg1)),
    'Large-cap (mean)': avg1,
    'Top Performers (mean)': avg2,
    'Large-cap (low)': avg1 - std1,
    'Large-cap (high)': avg1 + std1,
    'Top Performers (low)': avg2 - std2,
    'Top Performers (high)': avg2 + std2
})

# Enhanced Altair chart with better colors
line_chart = alt.Chart(df_plot.reset_index()).transform_fold(
    ['Large-cap (mean)', 'Top Performers (mean)'],
    as_=['Portfolio', 'Value']
).mark_line(strokeWidth=3).encode(
    x=alt.X('Day:Q', title='Trading Day', axis=alt.Axis(labelColor='white', titleColor='white')),
    y=alt.Y('Value:Q', title='Portfolio Value (Rs.)', axis=alt.Axis(labelColor='white', titleColor='white')),
    color=alt.Color('Portfolio:N',
                    scale=alt.Scale(
                        domain=['Large-cap (mean)', 'Top Performers (mean)'],
                        range=['#38bdf8', '#a78bfa'])),
    tooltip=['Day:Q', 'Portfolio:N', 'Value:Q']
)

band1 = alt.Chart(df_plot).mark_area(opacity=0.12, color='#38bdf8').encode(
    x='Day:Q',
    y='Large-cap (low):Q',
    y2='Large-cap (high):Q'
)

band2 = alt.Chart(df_plot).mark_area(opacity=0.12, color='#a78bfa').encode(
    x='Day:Q',
    y='Top Performers (low):Q',
    y2='Top Performers (high):Q'
)

# 🛠 Apply config to the final chart object, not individual layers
chart = (line_chart + band1 + band2).interactive().resolve_scale(
    color='independent'
).configure_axis(
    grid=True,
    gridColor='rgba(255, 255, 255, 0.1)',  # subtle white grid lines
    gridDash=[2, 2],                       # dashed grid for minimal distraction
    labelColor='white',
    titleColor='white'
).configure_view(
    stroke=None
)


st.altair_chart(chart, use_container_width=True)


st.markdown("</div>", unsafe_allow_html=True)

# Selection frequency visualization with proper nesting
st.markdown("""
<div class="content-container">
    <h2>Most Frequently Selected Stocks</h2>
""", unsafe_allow_html=True)

# Count selections
sel_count1 = pd.Series(selections1).value_counts().sort_values(ascending=False)
sel_count2 = pd.Series(selections2).value_counts().sort_values(ascending=False)
# Top 10
top1 = sel_count1.head(10).reset_index()
top1.columns = ['Stock', 'Count']
top2 = sel_count2.head(10).reset_index()
top2.columns = ['Stock', 'Count']

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Large-cap Portfolio</h3>
    """, unsafe_allow_html=True)
    
    bar1 = alt.Chart(top1).mark_bar(color='#3b82f6').encode(
        x=alt.X('Count:Q', title='Selection Count'),
        y=alt.Y('Stock:N', sort='-x', title='Stock Symbol'),
        tooltip=['Stock:N', 'Count:Q']
    ).configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        labelColor='white',
        titleColor='white'
    ).configure_view(
        stroke=None
    )
    
    st.altair_chart(bar1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Top Performers Portfolio</h3>
    """, unsafe_allow_html=True)
    
    bar2 = alt.Chart(top2).mark_bar(color='#8b5cf6').encode(
        x=alt.X('Count:Q', title='Selection Count'),
        y=alt.Y('Stock:N', sort='-x', title='Stock Symbol'),
        tooltip=['Stock:N', 'Count:Q']
    ).configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        labelColor='white',
        titleColor='white'
    ).configure_view(
        stroke=None
    )
    
    st.altair_chart(bar2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Sector Allocation Analysis
st.markdown("""
<div class="content-container">
    <h2>Sector-wise Allocation Analysis</h2>
</div>
""", unsafe_allow_html=True)

# Calculate sector allocations
sector_alloc1 = get_sector_allocation(selections1, valid_symbols1)
sector_alloc2 = get_sector_allocation(selections2, valid_symbols2)

# Convert to DataFrame for Altair
sector_df1 = pd.DataFrame(list(sector_alloc1.items()), columns=['Sector', 'Allocation'])
sector_df2 = pd.DataFrame(list(sector_alloc2.items()), columns=['Sector', 'Allocation'])

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Large-cap Portfolio - Sector Allocation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not sector_df1.empty:
        pie1 = alt.Chart(sector_df1).mark_arc().encode(
            theta=alt.Theta('Allocation:Q', type='quantitative'),
            color=alt.Color('Sector:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Sector:N', alt.Tooltip('Allocation:Q', format='.1f')]
        ).configure_view(
            stroke=None
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )
        
        st.altair_chart(pie1, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #bae6fd; opacity: 0.8;">
            <p>No sector data available for this portfolio</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Top Performers Portfolio - Sector Allocation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not sector_df2.empty:
        pie2 = alt.Chart(sector_df2).mark_arc().encode(
            theta=alt.Theta('Allocation:Q', type='quantitative'),
            color=alt.Color('Sector:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Sector:N', alt.Tooltip('Allocation:Q', format='.1f')]
        ).configure_view(
            stroke=None
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        )
        
        st.altair_chart(pie2, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #bae6fd; opacity: 0.8;">
            <p>No sector data available for this portfolio</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Benchmark Comparison Section
st.markdown("""
<div class="content-container">
    <h2>Strategy Comparison</h2>
    <p style="color: #bae6fd; font-size: 1.1rem; margin-bottom: 2rem;">
        Compare Thompson Sampling performance against traditional strategies
    </p>
</div>
""", unsafe_allow_html=True)

# Calculate benchmark performances
bh_values1, bh_return1, bh_sharpe1 = calculate_buy_and_hold_performance(valid_symbols1, data1)
bh_values2, bh_return2, bh_sharpe2 = calculate_buy_and_hold_performance(valid_symbols2, data2)

rs_values1, rs_return1, rs_sharpe1 = calculate_random_selection_performance(valid_symbols1, data1, seed=seed)
rs_values2, rs_return2, rs_sharpe2 = calculate_random_selection_performance(valid_symbols2, data2, seed=seed)

# Benchmark comparison charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Large-cap Portfolio - Strategy Comparison</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create comparison DataFrame
    df_bench1 = pd.DataFrame({
        'Day': np.arange(len(avg1)),
        'Thompson Sampling': avg1,
        'Buy & Hold': bh_values1,
        'Random Selection': rs_values1
    })
    
    # Create comparison chart
    bench_chart1 = alt.Chart(df_bench1).transform_fold(
        ['Thompson Sampling', 'Buy & Hold', 'Random Selection'],
        as_=['Strategy', 'Value']
    ).mark_line(strokeWidth=2).encode(
        x=alt.X('Day:Q', title='Trading Day', axis=alt.Axis(labelColor='white', titleColor='white')),
        y=alt.Y('Value:Q', title='Portfolio Value (Rs.)', axis=alt.Axis(labelColor='white', titleColor='white')),
        color=alt.Color('Strategy:N',
                        scale=alt.Scale(
                            domain=['Thompson Sampling', 'Buy & Hold', 'Random Selection'],
                            range=['#38bdf8', '#10b981', '#f59e0b'])),
        tooltip=['Day:Q', 'Strategy:N', 'Value:Q']
    ).configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        gridDash=[2, 2],
        labelColor='white',
        titleColor='white'
    ).configure_view(stroke=None)
    
    st.altair_chart(bench_chart1, use_container_width=True)
    
    # Strategy metrics
    col1a, col1b, col1c = st.columns(3)
    with col1a:
        st.metric("TS Return", f"{mean_ret1:.2f}%", format_delta(f"±{std_ret1:.2f}%"))
    with col1b:
        st.metric("Buy & Hold", f"{bh_return1:.2f}%", "")
    with col1c:
        st.metric("Random", f"{rs_return1:.2f}%", "")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Top Performers Portfolio - Strategy Comparison</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create comparison DataFrame
    df_bench2 = pd.DataFrame({
        'Day': np.arange(len(avg2)),
        'Thompson Sampling': avg2,
        'Buy & Hold': bh_values2,
        'Random Selection': rs_values2
    })
    
    # Create comparison chart
    bench_chart2 = alt.Chart(df_bench2).transform_fold(
        ['Thompson Sampling', 'Buy & Hold', 'Random Selection'],
        as_=['Strategy', 'Value']
    ).mark_line(strokeWidth=2).encode(
        x=alt.X('Day:Q', title='Trading Day', axis=alt.Axis(labelColor='white', titleColor='white')),
        y=alt.Y('Value:Q', title='Portfolio Value (Rs.)', axis=alt.Axis(labelColor='white', titleColor='white')),
        color=alt.Color('Strategy:N',
                        scale=alt.Scale(
                            domain=['Thompson Sampling', 'Buy & Hold', 'Random Selection'],
                            range=['#a78bfa', '#10b981', '#f59e0b'])),
        tooltip=['Day:Q', 'Strategy:N', 'Value:Q']
    ).configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        gridDash=[2, 2],
        labelColor='white',
        titleColor='white'
    ).configure_view(stroke=None)
    
    st.altair_chart(bench_chart2, use_container_width=True)
    
    # Strategy metrics
    col2a, col2b, col2c = st.columns(3)
    with col2a:
        st.metric("TS Return", f"{mean_ret2:.2f}%", format_delta(f"±{std_ret2:.2f}%"))
    with col2b:
        st.metric("Buy & Hold", f"{bh_return2:.2f}%", "")
    with col2c:
        st.metric("Random", f"{rs_return2:.2f}%", "")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Risk Metrics Dashboard
st.markdown("""
<div class="content-container">
    <h2>Risk Analysis Dashboard</h2>
    <p style="color: #bae6fd; font-size: 1.1rem; margin-bottom: 2rem;">
        Comprehensive risk assessment and performance metrics
    </p>
</div>
""", unsafe_allow_html=True)

# Calculate risk metrics for both portfolios
if st.session_state.simulations_run:
    # Get all portfolio values from simulations
    all_portfolios1 = []
    all_portfolios2 = []
    
    for i in range(num_simulations):
        if seed is not None:
            np.random.seed(seed + i)
        
        trader1 = ThompsonSamplingStockTrader(valid_symbols1, data1, stats1)
        trader1.run()
        all_portfolios1.append(trader1.portfolio_values)
        
        trader2 = ThompsonSamplingStockTrader(valid_symbols2, data2, stats2)
        trader2.run()
        all_portfolios2.append(trader2.portfolio_values)
    
    # Calculate risk metrics
    risk_mean1, risk_std1 = calculate_portfolio_risk_metrics(all_portfolios1)
    risk_mean2, risk_std2 = calculate_portfolio_risk_metrics(all_portfolios2)
    
    # Risk metrics display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="portfolio-section">
            <h3>Large-cap Portfolio - Risk Metrics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk metrics in a grid
        col1a, col1b = st.columns(2)
        with col1a:
            st.metric("Max Drawdown", f"{risk_mean1['max_drawdown']:.2f}%", format_delta(f"±{risk_std1['max_drawdown']:.2f}%"))
            st.metric("Volatility", f"{risk_mean1['volatility']:.2f}%", format_delta(f"±{risk_std1['volatility']:.2f}%"))
            st.metric("VaR (95%)", f"{risk_mean1['var_95']:.2f}%", format_delta(f"±{risk_std1['var_95']:.2f}%"))
        
        with col1b:
            st.metric("CVaR (95%)", f"{risk_mean1['cvar_95']:.2f}%", format_delta(f"±{risk_std1['cvar_95']:.2f}%"))
            st.metric("Calmar Ratio", f"{risk_mean1['calmar_ratio']:.2f}", format_delta(f"±{risk_std1['calmar_ratio']:.2f}"))
            st.metric("Sharpe Ratio", f"{mean_shp1:.2f}", format_delta(f"±{std_shp1:.2f}"))
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="portfolio-section">
            <h3>Top Performers Portfolio - Risk Metrics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk metrics in a grid
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("Max Drawdown", f"{risk_mean2['max_drawdown']:.2f}%", format_delta(f"±{risk_std2['max_drawdown']:.2f}%"))
            st.metric("Volatility", f"{risk_mean2['volatility']:.2f}%", format_delta(f"±{risk_std2['volatility']:.2f}%"))
            st.metric("VaR (95%)", f"{risk_mean2['var_95']:.2f}%", format_delta(f"±{risk_std2['var_95']:.2f}%"))
        
        with col2b:
            st.metric("CVaR (95%)", f"{risk_mean2['cvar_95']:.2f}%", format_delta(f"±{risk_std2['cvar_95']:.2f}%"))
            st.metric("Calmar Ratio", f"{risk_mean2['calmar_ratio']:.2f}", format_delta(f"±{risk_std2['calmar_ratio']:.2f}"))
            st.metric("Sharpe Ratio", f"{mean_shp2:.2f}", format_delta(f"±{std_shp2:.2f}"))
        
        st.markdown("</div>", unsafe_allow_html=True)

# Risk metrics explanation
st.markdown("""
<div class="content-container">
    <h3>Risk Metrics Explanation</h3>
    <div style="text-align: left; color: #bae6fd;">
        <p><strong>Maximum Drawdown:</strong> Largest peak-to-trough decline in portfolio value</p>
        <p><strong>Volatility:</strong> Annualized standard deviation of daily returns</p>
        <p><strong>VaR (95%):</strong> Value at Risk - maximum expected loss with 95% confidence</p>
        <p><strong>CVaR (95%):</strong> Conditional VaR - average loss beyond VaR threshold</p>
        <p><strong>Calmar Ratio:</strong> Annualized return divided by maximum drawdown</p>
        <p><strong>Sharpe Ratio:</strong> Risk-adjusted return measure</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Custom Portfolio Testing Section
st.markdown("""
<div class="content-container">
    <h2>Test Your Own Portfolio</h2>
    <p style="color: #bae6fd; font-size: 1.1rem; margin-bottom: 2rem;">
        Enter your own stock symbols and compare Thompson Sampling performance with your actual returns
    </p>
</div>
""", unsafe_allow_html=True)

# Custom Portfolio Input Section
st.markdown("""
<div style="margin-bottom: 1rem;">
    <p style="color: #bae6fd; font-size: 1rem; margin-bottom: 0.5rem; font-weight:700;">
        Enter Stock Symbols (comma-separated):
    </p>
    <p style="color: #bae6fd; font-size: 0.9rem; margin-bottom: 1rem; opacity: 0.8;">
        Example: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS
    </p>
</div>
""", unsafe_allow_html=True)

custom_symbols_input = st.text_area(
    "Stock Symbols",
    value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, LT.NS, PIDILITIND.NS, CDSL.NS, AFFLE.NS, TATAELXSI.NS",
    height=70,
    label_visibility="collapsed",
    placeholder="Enter stock symbols separated by commas..."
)

st.markdown("""
<div style="margin-bottom: 1rem;">
    <p style="color: #bae6fd; font-size: 1rem; margin-bottom: 0.5rem; font-weight:700;">
        Note:
    </p>
    <p style="color: #bae6fd; font-size: 0.9rem; margin-bottom: 1rem; opacity: 0.8;">
        We will compare your portfolio's real buy-and-hold return with Thompson Sampling.
    </p>
</div>
""", unsafe_allow_html=True)

if st.button("Run Your Portfolio Analysis", key="custom_analysis"):
    if custom_symbols_input.strip():
        # Parse symbols
        custom_symbols = [s.strip() for s in custom_symbols_input.split(',') if s.strip()]
        
    
        if len(custom_symbols) > 0:
            st.markdown("""
            <div class="status-container loading">
                <div class="loading-spinner"></div>
                <div class="status-text loading">Analyzing your portfolio...</div>
            </div>
            """, unsafe_allow_html=True)
            try:
                custom_data, custom_stats = get_stock_data(custom_symbols, start_date, end_date)
                valid_custom_symbols = [s for s in custom_symbols if s in custom_stats.index]
                if len(valid_custom_symbols) > 0:
                    avg_custom, std_custom, mean_ret_custom, std_ret_custom, mean_shp_custom, std_shp_custom, selections_custom = run_multiple_simulations(
                        ThompsonSamplingStockTrader, valid_custom_symbols, custom_data, custom_stats, num_simulations, seed
                    )
                    # Calculate buy-and-hold return for custom portfolio
                    bh_values_custom, bh_return_custom, bh_sharpe_custom = calculate_buy_and_hold_performance(valid_custom_symbols, custom_data)
                    st.session_state.custom_results = {
                        'avg': avg_custom, 'std': std_custom, 'mean_ret': mean_ret_custom, 'std_ret': std_ret_custom,
                        'mean_shp': mean_shp_custom, 'std_shp': std_shp_custom, 'selections': selections_custom,
                        'symbols': valid_custom_symbols, 'bh_return': bh_return_custom, 'bh_sharpe': bh_sharpe_custom,
                        'bh_values': bh_values_custom
                    }
                    st.success("Your portfolio analysis completed!")
                    st.rerun()
                else:
                    st.error("No valid stock symbols found. Please check your input.")
            except Exception as e:
                st.error(f"Error analyzing portfolio: {str(e)}")
        else:
            st.error("Please enter at least one stock symbol.")
    else:
        st.error("Please enter stock symbols.")

# Display custom portfolio results if available
if 'custom_results' in st.session_state:
    custom_results = st.session_state.custom_results
    st.markdown("""
    <div class="content-container">
        <h2>Your Portfolio Results</h2>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="portfolio-section">
            <h3>Thompson Sampling Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Mean Total Return", f"{custom_results['mean_ret']:.2f}%", format_delta(f"±{custom_results['std_ret']:.2f}%"))
        st.metric("Mean Sharpe Ratio", f"{custom_results['mean_shp']:.2f}", format_delta(f"±{custom_results['std_shp']:.2f}"))
        st.metric("Stocks Analyzed", len(custom_results['symbols']), "")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="portfolio-section">
            <h3>Buy & Hold Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Total Return", f"{custom_results['bh_return']:.2f}%")
        delta_value = custom_results['bh_return'] - custom_results['mean_ret']
        if delta_value > 0:
            st.markdown(
                f'<span style="color:#16a34a; font-size:1rem; font-weight:700; margin-top:-0.5rem; display:block;">Better ({delta_value:.2f}%)</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<span style="color:#ef4444; font-size:1rem; font-weight:700; margin-top:-0.5rem; display:block;">Worse ({delta_value:.2f}%)</span>',
                unsafe_allow_html=True
            )
        st.metric("Sharpe Ratio", f"{custom_results['bh_sharpe']:.2f}")
        st.metric("Simulations Run", num_simulations, "")
        st.markdown("</div>", unsafe_allow_html=True)

    
    # Custom portfolio performance chart
    st.markdown("""
    <div class="content-container">
        <h2>Your Portfolio Performance</h2>
    </div>
    """, unsafe_allow_html=True)
    
    df_custom_plot = pd.DataFrame({
        'Day': np.arange(len(custom_results['avg'])),
        'Thompson Sampling': custom_results['avg'],
        'Lower Bound': custom_results['avg'] - custom_results['std'],
        'Upper Bound': custom_results['avg'] + custom_results['std'],
        'Buy & Hold': custom_results.get('bh_values', custom_results['avg'])
    })
    
    # Create chart with existing styling
    custom_line_chart = alt.Chart(df_custom_plot).transform_fold(
        ['Thompson Sampling', 'Buy & Hold'],
        as_=['Strategy', 'Value']
    ).mark_line(strokeWidth=3).encode(
        x=alt.X('Day:Q', title='Trading Day', axis=alt.Axis(labelColor='white', titleColor='white')),
        y=alt.Y('Value:Q', title='Portfolio Value (Rs.)', axis=alt.Axis(labelColor='white', titleColor='white')),
        color=alt.Color('Strategy:N',
                        scale=alt.Scale(
                            domain=['Thompson Sampling', 'Buy & Hold'],
                            range=['#10b981', '#f59e0b'])),
        tooltip=['Day:Q', 'Strategy:N', 'Value:Q']
    )
    
    custom_band = alt.Chart(df_custom_plot).mark_area(opacity=0.12, color='#10b981').encode(
        x='Day:Q',
        y='Lower Bound:Q',
        y2='Upper Bound:Q'
    )
    
    custom_chart = (custom_line_chart + custom_band).interactive().configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        gridDash=[2, 2],
        labelColor='white',
        titleColor='white'
    ).configure_view(stroke=None)
    
    st.altair_chart(custom_chart, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Custom portfolio stock selections
    st.markdown("""
    <div class="content-container">
        <h2>Most Selected Stocks in Your Portfolio</h2>
    </div>
    """, unsafe_allow_html=True)
    
    sel_count_custom = pd.Series(custom_results['selections']).value_counts().sort_values(ascending=False)
    top_custom = sel_count_custom.head(10).reset_index()
    top_custom.columns = ['Stock', 'Count']
    
    custom_bar = alt.Chart(top_custom).mark_bar(color='#10b981').encode(
        x=alt.X('Count:Q', title='Selection Count'),
        y=alt.Y('Stock:N', sort='-x', title='Stock Symbol'),
        tooltip=['Stock:N', 'Count:Q']
    ).configure_axis(
        grid=True,
        gridColor='rgba(255, 255, 255, 0.1)',
        labelColor='white',
        titleColor='white'
    ).configure_view(stroke=None)
    
    st.altair_chart(custom_bar, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Custom portfolio sector allocation
    if len(custom_results['symbols']) > 0:
        st.markdown("""
        <div class="content-container">
            <h2>Sector Allocation in Your Portfolio</h2>
        </div>
        """, unsafe_allow_html=True)
        
        sector_alloc_custom = get_sector_allocation(custom_results['selections'], custom_results['symbols'])
        sector_df_custom = pd.DataFrame(list(sector_alloc_custom.items()), columns=['Sector', 'Allocation'])
        
        if not sector_df_custom.empty:
            custom_pie = alt.Chart(sector_df_custom).mark_arc().encode(
                theta=alt.Theta('Allocation:Q', type='quantitative'),
                color=alt.Color('Sector:N', scale=alt.Scale(scheme='category10')),
                tooltip=['Sector:N', alt.Tooltip('Allocation:Q', format='.1f')]
            ).configure_view(
                stroke=None
            ).configure_axis(
                labelColor='white',
                titleColor='white'
            )
            
            st.altair_chart(custom_pie, use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #bae6fd; opacity: 0.8;">
                <p>No sector data available for this portfolio</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="content-container" style="margin-top: 3rem; text-align: center; padding: 1rem;">
    <p style="margin: 0.5rem 0; color: #bae6fd; font-size: 0.9rem;">
        Designed & Developed with ❤️ by <strong>Pratyush</strong>
    </p>
    <p style="margin: 0.2rem 0;">
        <a href="https://github.com/Pratyush038" target="_blank" style="margin: 0 12px;">
            <img src="https://img.icons8.com/ios-filled/50/ffffff/github.png" alt="GitHub" width="26" style="vertical-align: middle;"/>
        </a>
        <a href="https://www.linkedin.com/in/pratyushbidare/" target="_blank" style="margin: 0 12px;">
            <img src="https://img.icons8.com/ios-filled/50/ffffff/linkedin.png" alt="LinkedIn" width="26" style="vertical-align: middle;"/>
        </a>
    </p>
</div>
""", unsafe_allow_html=True)