from pydantic import BaseModel


class SyncOperationIn(BaseModel):
    device_id: str
    idempotency_key: str
    operation_type: str
    payload: dict
    client_timestamp: str | None = None


class SyncPushRequest(BaseModel):
    operations: list[SyncOperationIn]


class SyncOperationResult(BaseModel):
    idempotency_key: str
    status: str
    server_id: str | None = None
    error_message: str | None = None


class SyncPushResponse(BaseModel):
    results: list[SyncOperationResult]


class SyncPullResponse(BaseModel):
    server_time: str
    products_updated_since: list[dict] = []
    settings: dict = {}
