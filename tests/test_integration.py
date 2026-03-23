import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from app.services.slot_generator import generate_all_slots

@pytest.mark.asyncio
async def test_admin_creates_room_and_schedule_user_books(client: AsyncClient, db_setup):
    # 1. Admin login
    resp = await client.post("/dummyLogin", json={"role": "admin"})
    assert resp.status_code == 200
    admin_token = resp.json()["token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create room
    room_resp = await client.post("/rooms/create", json={"name": "Test Room"}, headers=headers_admin)
    assert room_resp.status_code == 201
    room_id = room_resp.json()["room"]["id"]

    # 3. Create schedule
    schedule_data = {
        "daysOfWeek": [1,2,3,4,5],
        "startTime": "09:00",
        "endTime": "17:00"
    }
    schedule_resp = await client.post(f"/rooms/{room_id}/schedule/create", json=schedule_data, headers=headers_admin)
    assert schedule_resp.status_code == 201

    # 4. Generate slots (force)
    await generate_all_slots()

    # 5. User login
    user_resp = await client.post("/dummyLogin", json={"role": "user"})
    assert user_resp.status_code == 200
    user_token = user_resp.json()["token"]
    headers_user = {"Authorization": f"Bearer {user_token}"}

    # 6. Get available slots for tomorrow
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
    slots_resp = await client.get(f"/rooms/{room_id}/slots/list", params={"date": tomorrow.isoformat()}, headers=headers_user)
    assert slots_resp.status_code == 200
    slots = slots_resp.json()["slots"]
    if not slots:
        pytest.skip("No slots available for tomorrow")
    slot_id = slots[0]["id"]

    # 7. Create booking
    book_resp = await client.post("/bookings/create", json={"slotId": slot_id}, headers=headers_user)
    assert book_resp.status_code == 201
    booking_id = book_resp.json()["booking"]["id"]

    # 8. Verify slot is no longer available
    slots_after = await client.get(f"/rooms/{room_id}/slots/list", params={"date": tomorrow.isoformat()}, headers=headers_user)
    assert slot_id not in [s["id"] for s in slots_after.json()["slots"]]

    # 9. Cancel booking
    cancel_resp = await client.post(f"/bookings/{booking_id}/cancel", headers=headers_user)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["booking"]["status"] == "cancelled"

    # 10. Idempotent cancel
    cancel_resp2 = await client.post(f"/bookings/{booking_id}/cancel", headers=headers_user)
    assert cancel_resp2.status_code == 200
    assert cancel_resp2.json()["booking"]["status"] == "cancelled"