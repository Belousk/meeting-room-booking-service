import pytest
from httpx import AsyncClient
from app.main import app
from app.database import engine, Base, AsyncSessionLocal
from app.models import User
from app.config import settings
import uuid

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def db_setup():
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Добавляем тестовых пользователей (admin и user с фиксированными UUID)
    async with AsyncSessionLocal() as session:
        admin = User(
            id=uuid.UUID(settings.ADMIN_UUID),
            email="admin@example.com",
            role="admin",
            password_hash=None
        )
        user = User(
            id=uuid.UUID(settings.USER_UUID),
            email="user@example.com",
            role="user",
            password_hash=None
        )
        session.add_all([admin, user])
        await session.commit()

    yield

    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)