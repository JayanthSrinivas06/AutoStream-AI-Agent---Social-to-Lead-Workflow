import os
from typing import Dict, Any
from functools import partial

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.state import AgentState
from agent.nodes import (
    classify_intent_node,
    rag_retrieval_node,
    generate_response_node,
    extract_info_node,
    lead_capture_node,
    route_by_intent,
    route_after_extraction
)


def create_agent_graph(gemini_api_key: str = None, model_name: str = None):
    if gemini_api_key is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
    if model_name is None:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    llm = ChatGoogleGenerativeAI(
        google_api_key=gemini_api_key,
        model=model_name,
        temperature=0.7,
        max_output_tokens=300
    )
    
    classify_with_llm = partial(classify_intent_node, llm=llm)
    generate_with_llm = partial(generate_response_node, llm=llm)
    extract_with_llm = partial(extract_info_node, llm=llm)
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("classify_intent", classify_with_llm)
    workflow.add_node("retrieve", rag_retrieval_node)
    workflow.add_node("extract_info", extract_with_llm)
    workflow.add_node("respond", generate_with_llm)
    workflow.add_node("capture_lead", lead_capture_node)
    
    workflow.set_entry_point("classify_intent")
    
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "respond": "respond",
            "retrieve": "retrieve",
            "extract_info": "extract_info"
        }
    )
    
    workflow.add_edge("retrieve", "respond")
    
    workflow.add_conditional_edges(
        "extract_info",
        route_after_extraction,
        {
            "capture_lead": "capture_lead",
            "respond": "respond"
        }
    )
    
    workflow.add_edge("capture_lead", "respond")
    workflow.add_edge("respond", END)
    
    app = workflow.compile()
    
    return app


_agent_app = None

def get_agent(gemini_api_key: str = None, model_name: str = None):
    global _agent_app
    if _agent_app is None:
        _agent_app = create_agent_graph(gemini_api_key, model_name)
    return _agent_app
