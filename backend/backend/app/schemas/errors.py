from typing import Any, Optional

from pydantic import BaseModel, Field


class ApiErrorSchema(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Any] = Field(default=None, description="Optional extra context, never a stack trace")
