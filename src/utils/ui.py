import streamlit as st

def setup_page_config():
    st.set_page_config(
        page_title="Superstore Data Insights",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    st.markdown("""
    <style>
        .metric-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #333;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #4CAF50;
        }
        .metric-label {
            font-size: 14px;
            color: #B0BEC5;
        }
    </style>
    """, unsafe_allow_html=True)
