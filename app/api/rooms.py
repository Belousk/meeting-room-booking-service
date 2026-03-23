from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RoomCreate, RoomResponse
from app.services.room_service import RoomService
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/list")
async def list_rooms(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = RoomService(db)
    rooms = await service.get_all_rooms()
    return {"rooms": [RoomResponse.model_validate(r).model_dump() for r in rooms]}

@router.post("/create", status_code=201)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin)
):
    service = RoomService(db)
    room = await service.create_room(room_data)
    return {"room": RoomResponse.model_validate(room).model_dump()}