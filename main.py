import streamlit as st
import pandas as pd
from src.utils.data_loader import get_data_path, load_data
from src.utils.visualization import render_kpi_cards, render_charts
from src.utils.ui import setup_page_config, apply_custom_css
from src.utils.chat_handler import initialize_chat_session, render_chat_history, process_graph_response

@st.cache_data
def get_cached_data() -> pd.DataFrame:
    file_path = get_data_path()
    dataframe = load_data(file_path)
    if dataframe is None:
        return pd.DataFrame()
    return dataframe

def render_insights_page():
    st.title("Superstore Business Insights")
    st.markdown("Dashboard showing the results of Exploratory Data Analysis.")
    
    dataframe = get_cached_data()
    
    if dataframe.empty:
        st.warning("Data is empty or not found. Please check the dataset file.")
        return
        
    render_kpi_cards(dataframe)
    st.write("---")
    render_charts(dataframe)
    
    with st.expander("View Raw Data"):
        st.dataframe(dataframe.head(100), width=True)

def _handle_user_prompt(prompt: str):
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Agen sedang berpikir dan menyusun data..."):
            try:
                dataframe = get_cached_data()
                process_graph_response(prompt, dataframe)
            except Exception as error:
                error_msg = f"Terjadi kesalahan saat memproses data: {str(error)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "text": error_msg})

def render_chat_page():
    st.title("Chat with Data")
    
    initialize_chat_session()
    render_chat_history()
                
    if prompt := st.chat_input("Tanyakan sesuatu... (Misal: Tampilkan grafik bar total profit per kategori)"):
        _handle_user_prompt(prompt)

def main():
    setup_page_config()
    apply_custom_css()
    
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Select Menu:", ("Business Insights", "Chat with Data"))
    
    if menu == "Business Insights":
        render_insights_page()
    elif menu == "Chat with Data":
        render_chat_page()

if __name__ == "__main__":
    main()
