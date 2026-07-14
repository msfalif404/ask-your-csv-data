from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph.message import add_messages
from src.prompts.manager import PromptManager
from src.models.router import IntentRouterSchema
from src.models.selector import ColumnSelectorSchema
from src.models.visualization import VisualizationSchema
from src.models.query import DataQuerySchema
from src.utils.schema_catalog import get_all_columns_with_descriptions, build_schema_context
from src.utils.query_engine import execute_query
from src.utils.data_loader import get_data_path, load_data
from typing_extensions import TypedDict, Annotated
from typing import Optional, Any
from config.settings import OPENAI_API_KEY
import pandas as pd
from src.utils.semantic_cache import semantic_cache

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
llm_analyzer = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY)
prompt_manager = PromptManager()

class AskDataState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[str]
    selected_columns: Optional[list[str]]
    dsl_schema: Optional[Any]
    data_markdown: Optional[str]
    analysis_text: Optional[str]
    is_cache_hit: Optional[bool]

def cache_check_node(state: AskDataState):
    query = state["messages"][-1].content
    cached = semantic_cache.check_cache(query)
    
    if cached:
        return {
            "intent": cached["intent"],
            "dsl_schema": cached["dsl_schema"],
            "is_cache_hit": True
        }
    return {"is_cache_hit": False}

def route_intent_node(state: AskDataState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_manager.router_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    chain = prompt | llm.with_structured_output(IntentRouterSchema)
    result = chain.invoke({"messages": state["messages"]})
    return {"intent": result.intent}

def select_schema_node(state: AskDataState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_manager.schema_selector_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    chain = prompt | llm.with_structured_output(ColumnSelectorSchema)
    result = chain.invoke({
        "messages": state["messages"],
        "available_columns": get_all_columns_with_descriptions()
    })
    return {"selected_columns": result.selected_columns}

def _invoke_planner(state: AskDataState, prompt_template: str, schema_class):
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        MessagesPlaceholder(variable_name="messages")
    ])
    chain = prompt | llm.with_structured_output(schema_class)
    result = chain.invoke({
        "messages": state["messages"],
        "schema_context": build_schema_context(state["selected_columns"])
    })
    
    query = state["messages"][-1].content
    semantic_cache.add_to_cache(query, state["intent"], result.model_dump())
    
    return {"dsl_schema": result}

def answer_planner_node(state: AskDataState):
    return _invoke_planner(state, prompt_manager.answer_planner_prompt, DataQuerySchema)

def visualization_planner_node(state: AskDataState):
    return _invoke_planner(state, prompt_manager.visualization_planner_prompt, VisualizationSchema)

def executor_node(state: AskDataState):
    try:
        file_path = get_data_path()
        df = load_data(file_path)
        schema = state.get("dsl_schema")
        
        if df is not None and not df.empty and schema:
            df_result = execute_query(df, schema)
            markdown_table = df_result.head(20).to_markdown()
            return {"data_markdown": markdown_table}
    except Exception as e:
        return {"data_markdown": f"Error calculating data: {str(e)}"}
        
    return {"data_markdown": "Data is empty or query is invalid."}

def analyzer_node(state: AskDataState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_manager.analyzer_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    chain = prompt | llm_analyzer
    result = chain.invoke({
        "messages": state["messages"],
        "data_markdown": state.get("data_markdown", "No data.")
    })
    
    return {"analysis_text": result.content, "messages": [AIMessage(content=result.content)]}
