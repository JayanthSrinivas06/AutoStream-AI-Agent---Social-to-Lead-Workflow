from typing import TypedDict, Optional, List


class AgentState(TypedDict):
    messages: List
    intent: Optional[str]
    user_name: Optional[str]
    user_email: Optional[str]
    user_platform: Optional[str]
    lead_captured: bool
    context: Optional[str]
