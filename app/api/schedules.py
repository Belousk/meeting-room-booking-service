from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ScheduleCreate, ScheduleResponse
from app.services.schedule_service import ScheduleService
from app.dependencies import require_admin
import uuid

router = APIRouter(prefix="/rooms/{roomId}/schedule", tags=["Schedules"])

@router.post("/create", status_code=201)
async def create_schedule(
    roomId: uuid.UUID,
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin)
):
    service = ScheduleService(db)
    if not await service.room_exists(roomId):
        raise HTTPException(status_code=404, detail="Room not found")
    existing = await service.get_schedule_by_room(roomId)
    if existing:
        raise HTTPException(status_code=409, detail="Schedule already exists")
    schedule = await service.create_schedule(roomId, schedule_data)
    return {"schedule": ScheduleResponse.model_validate(schedule).model_dump()}