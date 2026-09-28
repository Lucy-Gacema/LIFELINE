import uuid
from typing import Optional, List, Literal, Any
from pydantic import BaseModel


class AssistantMessageIn(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    input_mode: Literal["text", "voice"] = "text"
   
    confirm_action_id: Optional[str] = None
    confirmed: Optional[bool] = None


class ProposedAction(BaseModel):
    action_id: str
    tool_name: str
    risk_level: Literal["low", "medium", "high"]
    arguments: dict
    summary: str 

class AssistantMessageOut(BaseModel):
    conversation_id: str
    reply_text: str
    speak_text: Optional[str] = None  
    proposed_action: Optional[ProposedAction] = None
    data: Optional[Any] = None  
    requires_clarification: bool = False
    clarification_options: Optional[List[dict]] = None
