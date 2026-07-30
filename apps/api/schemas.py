"""HTTP request and response models for the API service."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    goal: str = Field(min_length=8, max_length=4000)


class ArtifactResponse(BaseModel):
    id: UUID
    kind: str
    storage_path: str
    content_type: str
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class StepResponse(BaseModel):
    id: UUID
    role: str
    status: str
    position: int
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: UUID
    goal: str
    status: str
    error_message: str | None
    final_report: str | None
    created_at: datetime
    updated_at: datetime
    steps: list[StepResponse] = Field(default_factory=list)
    artifacts: list[ArtifactResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class JobSummaryResponse(BaseModel):
    id: UUID
    goal: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
