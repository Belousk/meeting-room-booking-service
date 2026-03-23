from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import rooms, schedules, slots, bookings
from app.auth import create_access_token
from app.schemas import DummyLoginRequest, Token
from app.config import settings
from app.database import engine
from app.models import Base
from app.services.slot_generator import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц (в продакшене использовать миграции)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Запуск фонового генератора слотов
    start_scheduler()
    yield
    # Остановка при завершении
    stop_scheduler()

app = FastAPI(title="Room Booking Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"])

app.include_router(rooms.router)
app.include_router(schedules.router)
app.include_router(slots.router)
app.include_router(bookings.router)

@app.get("/_info")
async def info():
    return {"status": "ok"}

@app.post("/dummyLogin", response_model=Token)
async def dummy_login(data: DummyLoginRequest):
    if data.role == "admin":
        user_id = settings.ADMIN_UUID
    else:
        user_id = settings.USER_UUID
    token = create_access_token(data={"user_id": str(user_id), "role": data.role.value})
    return {"token": token}