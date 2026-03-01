"""Tracking schemas."""
import uuid
from datetime import datetime, date
from pydantic import BaseModel


class SessionLogCreate(BaseModel):
    client_id: uuid.UUID
    completed: bool = True
    actual_weights: dict | None = None
    notes: str | None = None

class SessionLogRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    client_id: uuid.UUID
    completed: bool
    actual_weights: dict | None = None
    notes: str | None = None
    logged_at: datetime
    model_config = {"from_attributes": True}

class MetricCreate(BaseModel):
    client_id: uuid.UUID
    date: date
    metric_type: str
    value: float
    unit: str | None = None
    notes: str | None = None

class MetricRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    date: date
    metric_type: str
    value: float
    unit: str | None = None
    notes: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}

class DashboardResponse(BaseModel):
    total_sessions_logged: int
    completed_sessions: int
    completion_rate: float
    latest_metrics: dict[str, float]
