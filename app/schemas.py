from pydantic import BaseModel, Field, EmailStr, UUID4, field_validator, ConfigDict
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
    id: UUID4
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
    id: UUID4
    roomId: UUID4
    daysOfWeek: List[int]
    startTime: time
    endTime: time

    model_config = ConfigDict(from_attributes=True)

class SlotResponse(BaseModel):
    id: UUID4
    roomId: UUID4
    start: datetime
    end: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    slotId: UUID4
    createConferenceLink: bool = False

class BookingResponse(BaseModel):
    id: UUID4
    slotId: UUID4
    userId: UUID4
    status: str
    conferenceLink: Optional[str] = None
    createdAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)