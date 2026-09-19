from fastapi import HTTPException, status

class EntityNotFoundException(HTTPException):

    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} record matching ID '{identifier}' could not be located in the database."
        )

class DatabaseOperationException(HTTPException):
    def __init__(self, action: str, entity_name: str, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to {action} {entity_name}. Reason: {reason}"
        )