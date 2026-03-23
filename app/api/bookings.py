from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import BookingCreate, BookingResponse
from app.services.booking_service import BookingService
from app.dependencies import require_user, require_admin, get_current_user
import uuid

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/create", status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user)
):
    service = BookingService(db)
    try:
        booking = await service.create_booking(user["id"], booking_data)
    except ValueError as e:
        if str(e) == "Slot not found":
            raise HTTPException(status_code=404, detail="Slot not found")
        elif str(e) == "Cannot book past slot":
            raise HTTPException(status_code=400, detail="Cannot book past slot")
        elif str(e) == "Slot already booked":
            raise HTTPException(status_code=409, detail="Slot already booked")
        raise
    return {"booking": BookingResponse.model_validate(booking).model_dump()}

@router.get("/list")
async def list_all_bookings(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin)
):
    service = BookingService(db)
    bookings, total = await service.get_all_bookings(page, pageSize)
    return {
        "bookings": [BookingResponse.model_validate(b).model_dump() for b in bookings],
        "pagination": {"page": page, "pageSize": pageSize, "total": total}
    }

@router.get("/my")
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user)
):
    service = BookingService(db)
    bookings = await service.get_user_bookings(user["id"])
    return {"bookings": [BookingResponse.model_validate(b).model_dump() for b in bookings]}

@router.post("/{bookingId}/cancel")
async def cancel_booking(
    bookingId: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user)
):
    service = BookingService(db)
    try:
        booking = await service.cancel_booking(bookingId, user["id"])
    except ValueError as e:
        if str(e) == "Booking not found":
            raise HTTPException(status_code=404, detail="Booking not found")
        raise
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"booking": BookingResponse.model_validate(booking).model_dump()}