from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

IntentType = Literal["greeting", "inquiry", "high_intent_lead"]

def classify_intent(message: str, llm: ChatGoogleGenerativeAI) -> IntentType:

    # First check keywords for high intent
    if detect_high_intent_keywords(message):
        return "high_intent_lead"
    
    
    system_prompt = """Classify as ONE word:
greeting - Hi/Hello
inquiry - Questions
high_intent_lead - Wants to try/signup/mentions channel
Reply: greeting, inquiry, or high_intent_lead"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"'{message}'")
    ]
    
    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    
    if intent not in ["greeting", "inquiry", "high_intent_lead"]:
        if "greeting" in intent:
            return "greeting"
        elif "high_intent" in intent or "high intent" in intent:
            return "high_intent_lead"
        else:
            return "inquiry"
    
    return intent


def detect_high_intent_keywords(message: str) -> bool:
    high_intent_keywords = [
        "sign up", "signup", "register", "try", "start", "interested",
        "want to", "i'd like", "i would like", "get started", "purchase",
        "buy", "subscribe", "join", "my channel", "my youtube", "my instagram",
        "for my", "i need", "ready to", "make a video", "create a video",
        "video for", "content for", "i want", "looking to"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in high_intent_keywords)
