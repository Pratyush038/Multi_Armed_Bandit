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
    download_and_prepare_data
)
import time

# Page config
st.set_page_config(
    page_title="Thompson Sampling Stock Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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
        color: #3b82f6;
    }
    
    .status-text.success {
        color: #10b981;
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
    }
    /* Metric container hover effect */
    [data-testid="metric-container"]:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        transform: scale(1.02) !important;
    }

    /* Metric label (e.g., "Mean Total Return") */
    [data-testid="metric-container"] .css-1ht1j8u {
        font-size: 1.25rem !important;  /* Adjusted for better layout */
        font-weight: 700 !important;
        color: #bae6fd !important;
    }

    /* Metric value (e.g., 14.29%) */
    [data-testid="metric-container"] .css-1dp5vir {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #f0f9ff !important;
    }

    /* Metric delta (e.g., ±2.35%) */
    [data-testid="metric-container"] .css-1b4bkrp {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #7dd3fc !important;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(to right, #8b5cf6, #ec4899) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(236, 72, 153, 0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }

    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 25px rgba(236, 72, 153, 0.4) !important;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar section spacing */
    .sidebar-section {
        margin-bottom: 2rem !important;
    }
    
    /* Chart styling */
    .stPlotlyChart, .js-plotly-plot {
        background: transparent !important;
    }
    
    /* Text color fixes */
    .content-container p, .content-container div, .portfolio-section p, .portfolio-section div {
        color: #e2e8f0;
    }
    
    /* Ensure all text is visible */
    * {
        word-wrap: break-word;
        word-break: break-word;
        white-space: normal;
    }
</style>
""", unsafe_allow_html=True)

# Title with animation
st.markdown("""
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #93c5fd; /* optional: a bit lighter than title */
        }
    </style>

    <h1 class="main-title">Thompson Sampling Stock Trader</h1>
    <h1 class="subtitle">Optimal Stock Trading Strategy Using Thompson Sampling in the Context of Multi-Armed Bandits</h1>
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
st.sidebar.markdown("**Number of Simulations**")
num_simulations = st.sidebar.slider("", 10, 500, 100, label_visibility="collapsed")

st.sidebar.markdown("**Random Seed**")
seed = st.sidebar.number_input("", value=42, label_visibility="collapsed")

st.sidebar.markdown("**Start Date**")
start_date = st.sidebar.date_input("", datetime.today() - timedelta(days=365), label_visibility="collapsed")

st.sidebar.markdown("**End Date**")
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
    
    st.metric("Mean Total Return", f"{mean_ret1:.2f}%", f"±{std_ret1:.2f}%")
    st.metric("Mean Sharpe Ratio", f"{mean_shp1:.2f}", f"±{std_shp1:.2f}")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portfolio-section">
        <h3>Top Performers Portfolio</h3>
    """, unsafe_allow_html=True)
    
    st.metric("Mean Total Return", f"{mean_ret2:.2f}%", f"±{std_ret2:.2f}%")
    st.metric("Mean Sharpe Ratio", f"{mean_shp2:.2f}", f"±{std_shp2:.2f}")
    
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