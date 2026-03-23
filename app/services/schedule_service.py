from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Schedule, Room
from app.schemas import ScheduleCreate
import uuid

class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_schedule(self, room_id: uuid.UUID, schedule_data: ScheduleCreate) -> Schedule:
        schedule = Schedule(
            room_id=room_id,
            days_of_week=schedule_data.daysOfWeek,
            start_time=schedule_data.startTime,
            end_time=schedule_data.endTime
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def get_schedule_by_room(self, room_id: uuid.UUID) -> Schedule | None:
        result = await self.db.execute(select(Schedule).where(Schedule.room_id == room_id))
        return result.scalar_one_or_none()

    async def room_exists(self, room_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none() is not None