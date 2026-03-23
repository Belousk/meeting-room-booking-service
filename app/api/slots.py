from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import SlotResponse
from app.services.slot_service import SlotService
from app.services.room_service import RoomService
from app.dependencies import get_current_user
import uuid
from datetime import date, datetime, timezone

router = APIRouter(prefix="/rooms/{roomId}/slots", tags=["Slots"])

@router.get("/list")
async def list_available_slots(
    roomId: uuid.UUID,
    date: date = Query(..., description="Date in YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    room_service = RoomService(db)
    room = await room_service.get_room_by_id(roomId)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    slot_service = SlotService(db)
    if not await slot_service.room_has_schedule(roomId):
        return {"slots": []}
    
    slots = await slot_service.get_available_slots(roomId, date)
    return {"slots": [SlotResponse.model_validate(s).model_dump() for s in slots]}
