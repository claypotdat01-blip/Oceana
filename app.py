import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="LAUTAN — Ocean Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# DESIGN SYSTEM — Fun yet Professional
# =========================================
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #EAF2F8; /* Softer, water-like blue background */
    color: #152C40;
}
[data-testid="stSidebar"] {
    background: #0F2537 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #E0EAF5 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #48CAE4 !important; /* Brighter teal accent */
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #48CAE4 !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #183A55 !important;
    border: 1px solid #2B577D !important;
    color: #E0EAF5 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stRadio > div > label {
    color: #E0EAF5 !important;
}

/* Fun & Professional Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0077B6 0%, #0096C7 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border-radius: 50px !important; /* Pill shape for a friendlier look */
    transition: all 0.3s ease !important;
    padding: 12px 24px !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 10px rgba(0, 119, 182, 0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 119, 182, 0.35) !important;
    background: linear-gradient(135deg, #023E8A 0%, #0077B6 100%) !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    border-top: 4px solid #00B4D8; /* Vibrant accent line */
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    color: #0077B6 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #03045E !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-bottom: 2px solid #E0EAF5 !important;
    border-radius: 12px 12px 0 0 !important;
    gap: 8px;
    padding: 8px 16px 0;
}
.stTabs [data-baseweb="tab"] {
