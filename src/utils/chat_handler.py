import streamlit as st
import pandas as pd
import uuid
from src.agents.graph import build_ask_data_graph
from src.utils.query_engine import execute_query
from src.utils.chart_builder import render_visualization
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "memory_saver" not in st.session_state:
        st.session_state.memory_saver = MemorySaver()

def render_chat_history():
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if "text" in message and message["text"]:
                st.markdown(message["text"])
            if "dataframe" in message:
                st.dataframe(message["dataframe"])
            if "figure" in message:
                st.plotly_chart(message["figure"], key=f"hist_fig_{i}")
            if "schema" in message and "raw_df" in message:
                _render_audit_trail(message["schema"], message["raw_df"])

def _render_audit_trail(schema: dict, dataframe: pd.DataFrame):
    with st.expander("🔍 Audit Trail (LLM Query Plan vs Actual Data)"):
        st.markdown("**1. Gen AI Query Plan (DSL Schema)**")
        st.json(schema)
        st.markdown("**2. Actual Computed Data (Pandas)**")
        st.dataframe(dataframe)
        st.info("💡 Arsitektur *Text-to-DSL* menjamin bahwa AI tidak menghitung angka sendiri. Angka mutlak dihitung oleh Pandas berdasarkan skema kueri di atas, lalu dinarasikan oleh AI untuk mencegah halusinasi matematika.")

def _invoke_agent_graph(prompt: str) -> dict:
    graph = build_ask_data_graph(st.session_state.memory_saver)
    return graph.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": "session_1"}}
    )

def _handle_agent_error(error_message: str):
    st.error(error_message)
    st.session_state.messages.append({"role": "assistant", "text": error_message})

def _handle_visualization_response(schema, df_result, final_text):
    message_data = {"role": "assistant", "text": final_text, "schema": schema.model_dump(), "raw_df": df_result}
    figure = render_visualization(df_result, schema)
    if figure:
        st.plotly_chart(figure, key=f"new_fig_{uuid.uuid4().hex}")
        message_data["figure"] = figure
    else:
        st.warning("Gagal merender grafik. Pastikan kolom valid.")
        st.dataframe(df_result)
        message_data["dataframe"] = df_result
    return message_data

def _handle_tabular_response(schema, df_result, final_text):
    message_data = {"role": "assistant", "text": final_text, "schema": schema.model_dump(), "raw_df": df_result}
    st.dataframe(df_result)
    message_data["dataframe"] = df_result
    return message_data

def process_graph_response(prompt: str, dataframe: pd.DataFrame):
    result_state = _invoke_agent_graph(prompt)
    
    schema = result_state.get("dsl_schema")
    intent = result_state.get("intent")
    analysis_text = result_state.get("analysis_text")
    
    if intent == "out_of_domain":
        warning_msg = "Maaf, pertanyaan Anda di luar konteks database penjualan kami (Out of Domain Guardrail). Silakan tanyakan hal yang relevan dengan data bisnis."
        st.warning(warning_msg)
        st.session_state.messages.append({"role": "assistant", "text": warning_msg})
        return

    if not schema:
        _handle_agent_error("Maaf, agen gagal memproses pertanyaan Anda.")
        return
        
    df_result = execute_query(dataframe, schema)
    
    final_text = analysis_text if analysis_text else (getattr(schema, "insight_text", "") if intent == "visualization" else getattr(schema, "response_template", "Analisis berhasil."))
    
    if result_state.get("is_cache_hit", False):
        final_text = f"⚡ **[Hit from Semantic Cache]**\n\n" + final_text
        
    st.markdown(final_text)
    
    if intent == "visualization":
        message_data = _handle_visualization_response(schema, df_result, final_text)
    else:
        message_data = _handle_tabular_response(schema, df_result, final_text)
        
    _render_audit_trail(schema.model_dump(), df_result)
    st.session_state.messages.append(message_data)
