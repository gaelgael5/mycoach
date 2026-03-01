"""Program, Session, Exercise schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel


# --- Exercise ---
class ExerciseCreate(BaseModel):
    name: str
    sets: int | None = None
    reps: str | None = None
    weight: float | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    order: int = 0

class ExerciseUpdate(BaseModel):
    name: str | None = None
    sets: int | None = None
    reps: str | None = None
    weight: float | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    order: int | None = None

class ExerciseRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    name: str
    sets: int | None = None
    reps: str | None = None
    weight: float | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    order: int
    created_at: datetime
    model_config = {"from_attributes": True}


# --- Session ---
class SessionCreate(BaseModel):
    day_number: int
    name: str
    notes: str | None = None

class SessionUpdate(BaseModel):
    day_number: int | None = None
    name: str | None = None
    notes: str | None = None

class SessionRead(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    day_number: int
    name: str
    notes: str | None = None
    created_at: datetime
    exercises: list[ExerciseRead] = []
    model_config = {"from_attributes": True}

class SessionReadBrief(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    day_number: int
    name: str
    notes: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


# --- Program ---
class ProgramCreate(BaseModel):
    name: str
    description: str | None = None
    duration_weeks: int | None = None

class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_weeks: int | None = None

class ProgramRead(BaseModel):
    id: uuid.UUID
    coach_id: uuid.UUID
    name: str
    description: str | None = None
    duration_weeks: int | None = None
    is_template: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ProgramReadDetail(ProgramRead):
    sessions: list[SessionRead] = []

class ProgramAssign(BaseModel):
    client_ids: list[uuid.UUID]

class ProgramAssignmentRead(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    client_id: uuid.UUID
    assigned_at: datetime
    model_config = {"from_attributes": True}
