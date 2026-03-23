from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models import Room, Schedule, Slot
from app.config import settings
import uuid
from datetime import datetime, timedelta, timezone
import asyncio

scheduler = AsyncIOScheduler()
engine = None
AsyncSessionLocal = None

def init_db():
    global engine, AsyncSessionLocal
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def generate_slots_for_room(room_id, schedule):
    today = datetime.now(timezone.utc).date()   
    for i in range(1, 31):
        target_date = today + timedelta(days=i)
        day_of_week = target_date.isoweekday()
        if day_of_week not in schedule.days_of_week:
            continue
        start_dt = datetime.combine(target_date, schedule.start_time, tzinfo=timezone.utc)   
        end_dt = datetime.combine(target_date, schedule.end_time, tzinfo=timezone.utc)       
        current = start_dt
        slots_to_insert = []
        while current < end_dt:
            slot_end = current + timedelta(minutes=30)
            slots_to_insert.append({
                "id": uuid.uuid4(),
                "room_id": room_id,
                "start_time": current,
                "end_time": slot_end
            })
            current = slot_end
        async with AsyncSessionLocal() as session:
            for slot in slots_to_insert:
                existing = await session.execute(
                    select(Slot).where(Slot.room_id == room_id, Slot.start_time == slot["start_time"])
                )
                if not existing.scalar_one_or_none():
                    session.add(Slot(**slot))
            await session.commit()

async def generate_all_slots():
    async with AsyncSessionLocal() as session:
        stmt = select(Room.id, Schedule).join(Schedule, Room.id == Schedule.room_id)
        result = await session.execute(stmt)
        rows = result.all()
        for room_id, schedule in rows:
            await generate_slots_for_room(room_id, schedule)

async def job():
    print("Running slot generation job...")
    await generate_all_slots()
    print("Slot generation completed.")

def start_scheduler():
    init_db()
    loop = asyncio.get_event_loop()
    loop.create_task(job())
    scheduler.add_job(job, CronTrigger(hour=0, minute=0, timezone="UTC"))
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()