from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Room
from app.schemas import RoomCreate
import uuid

class RoomService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_room(self, room_data: RoomCreate) -> Room:
        room = Room(**room_data.model_dump())
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_all_rooms(self) -> list[Room]:
        result = await self.db.execute(select(Room))
        return result.scalars().all()

    async def get_room_by_id(self, room_id: uuid.UUID) -> Room | None:
        return await self.db.get(Room, room_id)