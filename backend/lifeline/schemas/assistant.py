from typing import Any, Literal

from pydantic import BaseModel


class AssistantMessageIn(BaseModel):
    conversation_id: str | None = None
    message: str
    input_mode: Literal["text", "voice"] = "text"

    confirm_action_id: str | None = None
    confirmed: bool | None = None


class ProposedAction(BaseModel):
    action_id: str
    tool_name: str
    risk_level: Literal["low", "medium", "high"]
    arguments: dict
    summary: str


class AssistantMessageOut(BaseModel):
    conversation_id: str
    reply_text: str
    speak_text: str | None = None
    proposed_action: ProposedAction | None = None
    data: Any | None = None
    requires_clarification: bool = False
    clarification_options: list[dict] | None = None
