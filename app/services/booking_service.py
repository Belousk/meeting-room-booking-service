from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from app.models import Booking, Slot
from app.schemas import BookingCreate
import uuid
from datetime import datetime, timezone

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(self, user_id: uuid.UUID, booking_data: BookingCreate) -> Booking:
        slot = await self.db.get(Slot, booking_data.slotId)
        if not slot:
            raise ValueError("Slot not found")
        if slot.start_time < datetime.now(timezone.utc):
            raise ValueError("Cannot book past slot")

        conference_link = None
        if booking_data.createConferenceLink:
            conference_link = f"https://meet.example.com/room-{slot.room_id}-{slot.id}"

        booking = Booking(
            slot_id=booking_data.slotId,
            user_id=user_id,
            status="active",
            conference_link=conference_link
        )
        self.db.add(booking)
        try:
            await self.db.commit()
            await self.db.refresh(booking)
            return booking
        except IntegrityError as e:
            await self.db.rollback()
            if "unique_active_booking" in str(e):
                raise ValueError("Slot already booked")
            raise

    async def get_all_bookings(self, page: int, page_size: int) -> tuple[list[Booking], int]:
        offset = (page - 1) * page_size
        total = await self.db.execute(select(func.count()).select_from(Booking))
        total_count = total.scalar()
        result = await self.db.execute(select(Booking).offset(offset).limit(page_size))
        return result.scalars().all(), total_count

    async def get_user_bookings(self, user_id: uuid.UUID) -> list[Booking]:
        now = datetime.now(timezone.utc) 
        stmt = select(Booking).join(Slot).where(
            Booking.user_id == user_id,
            Slot.start_time >= now
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def cancel_booking(self, booking_id: uuid.UUID, user_id: uuid.UUID) -> Booking:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        if booking.user_id != user_id:
            raise PermissionError("Cannot cancel another user's booking")
        if booking.status != "cancelled":
            booking.status = "cancelled"
            await self.db.commit()
            await self.db.refresh(booking)
        return booking