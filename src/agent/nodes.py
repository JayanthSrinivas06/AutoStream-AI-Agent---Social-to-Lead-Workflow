from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agent.state import AgentState
from utils.intent import classify_intent
from rag.retriever import get_retriever
from tools.lead_capture import mock_lead_capture, validate_lead_data


def classify_intent_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    messages = state["messages"]
    if not messages:
        return {"intent": "greeting"}
    
    # If we're already in high-intent mode and haven't captured lead yet, stay in high-intent
    from tools.lead_capture import validate_lead_data
    if state.get("intent") == "high_intent_lead" and not state.get("lead_captured", False):
        validation = validate_lead_data(
            state.get("user_name"),
            state.get("user_email"),
            state.get("user_platform")
        )
        if not validation["is_complete"]:
            return {"intent": "high_intent_lead"}
    
    last_message = messages[-1]
    user_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    intent = classify_intent(user_text, llm)
    
    return {"intent": intent}


def rag_retrieval_node(state: AgentState) -> Dict[str, Any]:
    messages = state["messages"]
    if not messages:
        return {"context": ""}
    
    last_message = messages[-1]
    query = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    retriever = get_retriever()
    context = retriever.get_context(query)
    
    return {"context": context}


def generate_response_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    intent = state.get("intent", "inquiry")
    context = state.get("context", "")
    messages = state["messages"]
    
    last_message = messages[-1]
    user_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    if intent == "greeting":
        system_prompt = "AutoStream AI. Greet, ask how to help. Brief."
    
    elif intent == "inquiry":
        system_prompt = f"""Answer using:
{context}
Concise, max 60 words."""
    
    else:
        validation = validate_lead_data(
            state.get("user_name"),
            state.get("user_email"),
            state.get("user_platform")
        )
        
        if not validation["is_complete"]:
            missing = validation["missing_fields"]
            if "name" in missing:
                system_prompt = "Ask name. Friendly."
            elif "email" in missing:
                system_prompt = f"Name: {state.get('user_name')}. Ask email."
            else:
                system_prompt = f"Have {state.get('user_name')}, {state.get('user_email')}. Ask platform."
        else:
            system_prompt = "Confirm setup. Thank them."
    
    # Build prompt with minimal conversation history
    prompt_messages = [SystemMessage(content=system_prompt)]
    
    # Add only last 2 messages for context (optimized for token efficiency)
    recent_messages = messages[-2:] if len(messages) > 2 else messages
    for msg in recent_messages:
        if isinstance(msg, (HumanMessage, AIMessage)):
            prompt_messages.append(msg)
    
    response = llm.invoke(prompt_messages)
    ai_message = AIMessage(content=response.content)
    
    # Append to existing messages, don't replace
    return {"messages": state["messages"] + [ai_message]}


def extract_info_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    messages = state["messages"]
    if len(messages) < 2:
        return {}
    
    last_message = messages[-1]
    user_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    updates = {}
    
    validation = validate_lead_data(
        state.get("user_name"),
        state.get("user_email"),
        state.get("user_platform")
    )
    
    if not validation["is_complete"]:
        missing = validation["missing_fields"]
        
        if "name" in missing:
            extract_prompt = f"""Extract name from: "{user_text}"
Respond with name only or "NONE"."""
            
            response = llm.invoke([HumanMessage(content=extract_prompt)])
            extracted = response.content.strip()
            if extracted != "NONE" and len(extracted) > 0 and len(extracted) < 50:
                updates["user_name"] = extracted
        
        elif "email" in missing:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_text)
            if emails:
                updates["user_email"] = emails[0]
        
        elif "platform" in missing:
            # Check the entire conversation for platform mentions
            platforms = ["youtube", "instagram", "tiktok", "facebook", "twitter", "linkedin", "twitch"]
            
            # Check all user messages for platform keywords
            for msg in messages:
                if hasattr(msg, 'content'):
                    msg_lower = msg.content.lower()
                    for platform in platforms:
                        if platform in msg_lower:
                            updates["user_platform"] = platform.capitalize()
                            break
                if "user_platform" in updates:
                    break
            
            # If still not found, try LLM extraction on current message
            if "user_platform" not in updates:
                extract_prompt = f"""Extract platform from: "{user_text}"
YouTube/Instagram/TikTok/Facebook/Twitter/LinkedIn/Twitch
Platform name only or "NONE"."""
                
                response = llm.invoke([HumanMessage(content=extract_prompt)])
                extracted = response.content.strip()
                if extracted != "NONE":
                    updates["user_platform"] = extracted
    
    return updates


def lead_capture_node(state: AgentState) -> Dict[str, Any]:
    validation = validate_lead_data(
        state.get("user_name"),
        state.get("user_email"),
        state.get("user_platform")
    )
    
    if validation["is_complete"] and not state.get("lead_captured", False):
        result = mock_lead_capture(
            state["user_name"],
            state["user_email"],
            state["user_platform"]
        )
        
        return {"lead_captured": True}
    
    return {}


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "inquiry")
    
    if intent == "greeting":
        return "respond"
    elif intent == "inquiry":
        return "retrieve"
    else:  # high_intent_lead
        return "extract_info"


def route_after_extraction(state: AgentState) -> str:
    validation = validate_lead_data(
        state.get("user_name"),
        state.get("user_email"),
        state.get("user_platform")
    )
    
    if validation["is_complete"]:
        return "capture_lead"
    else:
        return "respond"
