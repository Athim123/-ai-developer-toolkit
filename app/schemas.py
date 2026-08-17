from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Projects ---
class ProjectCreate(BaseModel):
    name: str


class ProjectOut(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Prompts ---
class PromptCreate(BaseModel):
    project_id: str
    name: str
    template: str


class PromptOut(BaseModel):
    id: str
    project_id: str
    name: str
    template: str
    version: int
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Runs ---
class RunCreate(BaseModel):
    project_id: str
    workflow: str = Field(..., description="Workflow name, e.g. 'code_assist'")
    input: dict[str, Any]
    model: Optional[str] = None
    tools: list[str] = Field(default_factory=list)
    prompt_id: Optional[str] = None


class RunOut(BaseModel):
    run_id: str
    status: str
    trace_url: str


class RunDetail(BaseModel):
    id: str
    project_id: str
    workflow_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    input_payload: dict
    output_payload: Optional[dict]
    latency_ms: Optional[float]

    class Config:
        from_attributes = True


# --- Tools ---
class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolExecuteResponse(BaseModel):
    tool_name: str
    result: Any
    success: bool


# --- Evaluation ---
class EvaluateRequest(BaseModel):
    run_id: str
    criteria: list[str] = Field(
        default_factory=lambda: ["correctness", "relevance", "safety"]
    )


class EvaluateResponse(BaseModel):
    run_id: str
    scores: dict[str, float]
    rationale: str


# --- Retrieval ---
class RetrievalQuery(BaseModel):
    project_id: str
    query: str
    top_k: int = 5


class RetrievalResult(BaseModel):
    document_id: str
    title: str
    snippet: str
    score: float


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]


# --- Errors ---
class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
