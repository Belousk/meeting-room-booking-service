import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
import uuid
from app.services.room_service import RoomService
from app.services.schedule_service import ScheduleService
from app.services.slot_service import SlotService
from app.services.booking_service import BookingService
from app.schemas import RoomCreate, ScheduleCreate, BookingCreate

@pytest.mark.asyncio
async def test_room_service_create_room():
    db_mock = AsyncMock()
    service = RoomService(db_mock)
    room_data = RoomCreate(name="Test Room")
    await service.create_room(room_data)
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_schedule_service_create_schedule():
    db_mock = AsyncMock()
    service = ScheduleService(db_mock)
    room_id = uuid.uuid4()
    schedule_data = ScheduleCreate(daysOfWeek=[1,2], startTime="09:00", endTime="17:00")
    await service.create_schedule(room_id, schedule_data)
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_slot_service_get_available_slots():
    db_mock = AsyncMock()
    # Настраиваем мок для execute: он должен возвращать объект с методом scalars()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db_mock.execute = AsyncMock(return_value=mock_result)
    service = SlotService(db_mock)
    slots = await service.get_available_slots(uuid.uuid4(), datetime.now(timezone.utc).date())
    assert slots == []

@pytest.mark.asyncio
async def test_booking_service_create_booking_success():
    db_mock = AsyncMock()
    slot_id = uuid.uuid4()
    user_id = uuid.uuid4()
    slot_mock = MagicMock()
    # Используем timezone-aware datetime
    slot_mock.start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    slot_mock.room_id = uuid.uuid4()
    slot_mock.id = slot_id
    db_mock.get = AsyncMock(return_value=slot_mock)
    service = BookingService(db_mock)
    booking_data = BookingCreate(slotId=slot_id)
    booking = await service.create_booking(user_id, booking_data)
    assert booking.user_id == user_id
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_booking_service_create_booking_past_slot():
    db_mock = AsyncMock()
    slot_mock = MagicMock()
    slot_mock.start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    db_mock.get = AsyncMock(return_value=slot_mock)
    service = BookingService(db_mock)
    with pytest.raises(ValueError, match="Cannot book past slot"):
        await service.create_booking(uuid.uuid4(), BookingCreate(slotId=uuid.uuid4()))

@pytest.mark.asyncio
async def test_booking_service_cancel_booking():
    db_mock = AsyncMock()
    booking_mock = MagicMock()
    booking_mock.id = uuid.uuid4()
    booking_mock.user_id = uuid.uuid4()
    booking_mock.status = "active"
    db_mock.get = AsyncMock(return_value=booking_mock)
    service = BookingService(db_mock)
    cancelled = await service.cancel_booking(booking_mock.id, booking_mock.user_id)
    assert cancelled.status == "cancelled"
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()