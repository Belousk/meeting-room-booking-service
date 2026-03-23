from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime, time
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"

class DummyLoginRequest(BaseModel):
    role: Role

class Token(BaseModel):
    token: str

class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: Optional[int] = None

class RoomResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    capacity: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ScheduleCreate(BaseModel):
    daysOfWeek: List[int] = Field(..., alias="daysOfWeek")
    startTime: time = Field(..., alias="startTime")
    endTime: time = Field(..., alias="endTime")

    @field_validator("daysOfWeek")
    def validate_days(cls, v):
        if not v:
            raise ValueError("daysOfWeek cannot be empty")
        for d in v:
            if d < 1 or d > 7:
                raise ValueError("days must be 1-7")
        if len(set(v)) != len(v):
            raise ValueError("days must be unique")
        return sorted(v)

class ScheduleResponse(BaseModel):
    id: UUID
    roomId: UUID = Field(..., alias="room_id")
    daysOfWeek: List[int] = Field(..., alias="days_of_week")
    startTime: time = Field(..., alias="start_time")
    endTime: time = Field(..., alias="end_time")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SlotResponse(BaseModel):
    id: UUID
    roomId: UUID = Field(..., alias="room_id")
    start: datetime = Field(..., alias="start_time")
    end: datetime = Field(..., alias="end_time")

    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    slotId: UUID
    createConferenceLink: bool = False

class BookingResponse(BaseModel):
    id: UUID
    slotId: UUID = Field(..., alias="slot_id")
    userId: UUID = Field(..., alias="user_id")
    status: str
    conferenceLink: Optional[str] = Field(None, alias="conference_link")
    createdAt: Optional[datetime] = Field(None, alias="created_at")

    model_config = ConfigDict(from_attributes=True)