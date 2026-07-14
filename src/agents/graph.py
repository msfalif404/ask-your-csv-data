from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.nodes import (
    AskDataState, route_intent_node, select_schema_node, 
    answer_planner_node, visualization_planner_node,
    executor_node, analyzer_node, cache_check_node
)

def route_after_cache(state: AskDataState):
    if state.get("is_cache_hit"):
        return "executor"
    return "router"

def route_after_selector(state: AskDataState):
    if state["intent"] == "visualization":
        return "visualization_planner"
    return "answer_planner"

def route_after_executor(state: AskDataState):
    return "analyzer"

def route_after_router(state: AskDataState):
    if state["intent"] == "out_of_domain":
        return "__end__"
    return "selector"

def build_ask_data_graph(memory_saver=None):
    workflow = StateGraph(AskDataState)
    
    workflow.add_node("cache_check", cache_check_node)
    workflow.add_node("router", route_intent_node)
    workflow.add_node("selector", select_schema_node)
    workflow.add_node("answer_planner", answer_planner_node)
    workflow.add_node("visualization_planner", visualization_planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("analyzer", analyzer_node)
    
    workflow.set_entry_point("cache_check")
    
    workflow.add_conditional_edges(
        "cache_check",
        route_after_cache,
        {
            "executor": "executor",
            "router": "router"
        }
    )
    
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "selector": "selector",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "selector",
        route_after_selector,
        {
            "visualization_planner": "visualization_planner",
            "answer_planner": "answer_planner"
        }
    )
    
    workflow.add_edge("visualization_planner", "executor")
    workflow.add_edge("answer_planner", "executor")
    
    workflow.add_conditional_edges(
        "executor",
        route_after_executor,
        {
            "analyzer": "analyzer",
            "__end__": END
        }
    )
    
    workflow.add_edge("analyzer", END)
    
    if memory_saver is None:
        memory_saver = MemorySaver()
        
    return workflow.compile(checkpointer=memory_saver)
