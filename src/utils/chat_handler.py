import streamlit as st
import pandas as pd
import uuid
from src.agents.graph import build_ask_data_graph
from src.utils.query_engine import execute_query, render_visualization
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "memory_saver" not in st.session_state:
        st.session_state.memory_saver = MemorySaver()

def render_chat_history():
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if "text" in msg and msg["text"]:
                st.markdown(msg["text"])
            if "dataframe" in msg:
                st.dataframe(msg["dataframe"])
            if "figure" in msg:
                st.plotly_chart(msg["figure"], key=f"hist_fig_{i}")
            if "schema" in msg and "raw_df" in msg:
                with st.expander("🔍 Audit Trail (LLM Query Plan vs Actual Data)"):
                    st.markdown("**1. Gen AI Query Plan (DSL Schema)**")
                    st.json(msg["schema"])
                    st.markdown("**2. Actual Computed Data (Pandas)**")
                    st.dataframe(msg["raw_df"])
                    st.info("💡 Arsitektur *Text-to-DSL* menjamin bahwa AI tidak menghitung angka sendiri. Angka mutlak dihitung oleh Pandas berdasarkan skema kueri di atas, lalu dinarasikan oleh AI untuk mencegah halusinasi matematika.")

def process_graph_response(prompt: str, df: pd.DataFrame):
    graph = build_ask_data_graph(st.session_state.memory_saver)
    
    result_state = graph.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": "session_1"}}
    )
    
    schema = result_state.get("dsl_schema")
    intent = result_state.get("intent")
    analysis_text = result_state.get("analysis_text")
    
    if intent == "out_of_domain":
        error_msg = "Maaf, pertanyaan Anda di luar konteks database penjualan kami (Out of Domain Guardrail). Silakan tanyakan hal yang relevan dengan data bisnis."
        st.warning(error_msg)
        st.session_state.messages.append({"role": "assistant", "text": error_msg})
        return

    if not schema:
        error_msg = "Maaf, agen gagal memproses pertanyaan Anda."
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "text": error_msg})
        return
        
    df_result = execute_query(df, schema)
    final_text = analysis_text if analysis_text else (schema.insight_text if intent == "visualization" else schema.response_template)
    
    is_cache_hit = result_state.get("is_cache_hit", False)
    if is_cache_hit:
        final_text = f"⚡ **[Hit from Semantic Cache]**\n\n" + final_text
        
    st.markdown(final_text)
    
    if intent == "visualization":
        fig = render_visualization(df_result, schema)
        if fig:
            st.plotly_chart(fig, key=f"new_fig_{uuid.uuid4().hex}")
            msg_data = {"role": "assistant", "text": final_text, "figure": fig, "schema": schema.model_dump(), "raw_df": df_result}
        else:
            st.warning("Gagal merender grafik. Pastikan kolom valid.")
            st.dataframe(df_result)
            msg_data = {"role": "assistant", "text": final_text, "dataframe": df_result, "schema": schema.model_dump(), "raw_df": df_result}
    else:
        st.dataframe(df_result)
        msg_data = {"role": "assistant", "text": final_text, "dataframe": df_result, "schema": schema.model_dump(), "raw_df": df_result}
        
    # Audit Trail Expander
    with st.expander("🔍 Audit Trail (LLM Query Plan vs Actual Data)"):
        st.markdown("**1. Gen AI Query Plan (DSL Schema)**")
        st.json(schema.model_dump())
        st.markdown("**2. Actual Computed Data (Pandas)**")
        st.dataframe(df_result)
        st.info("💡 Arsitektur *Text-to-DSL* menjamin bahwa AI tidak menghitung angka sendiri. Angka mutlak dihitung oleh Pandas berdasarkan skema kueri di atas, lalu dinarasikan oleh AI untuk mencegah halusinasi matematika.")
        
    st.session_state.messages.append(msg_data)
