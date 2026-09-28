from typing import Any, List, Optional
from pydantic import BaseModel


class SyncOperationIn(BaseModel):
    device_id: str
    idempotency_key: str
    operation_type: str 
    payload: dict
    client_timestamp: Optional[str] = None


class SyncPushRequest(BaseModel):
    operations: List[SyncOperationIn]


class SyncOperationResult(BaseModel):
    idempotency_key: str
    status: str 
    server_id: Optional[str] = None
    error_message: Optional[str] = None


class SyncPushResponse(BaseModel):
    results: List[SyncOperationResult]


class SyncPullResponse(BaseModel):
    
    server_time: str
    products_updated_since: List[dict] = []
    settings: dict = {}
