from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Slot, Booking, Schedule, Room
from datetime import datetime, date, timezone
import uuid

class SlotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slots(self, room_id: uuid.UUID, date: date) -> list[Slot]:
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc)  
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59, tzinfo=timezone.utc) 
        now_utc = datetime.now(timezone.utc)                                                    

        stmt = select(Slot).outerjoin(
            Booking, and_(Slot.id == Booking.slot_id, Booking.status == "active")
        ).where(
            Slot.room_id == room_id,
            Slot.start_time >= start_of_day,
            Slot.start_time <= end_of_day,
            Slot.start_time > now_utc,
            Booking.id.is_(None)
        ).order_by(Slot.start_time)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_slot_by_id(self, slot_id: uuid.UUID) -> Slot | None:
        return await self.db.get(Slot, slot_id)

    async def room_has_schedule(self, room_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(Schedule).where(Schedule.room_id == room_id))
        return result.scalar_one_or_none() is not None