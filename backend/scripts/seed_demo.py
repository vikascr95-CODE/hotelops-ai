"""Fill the HotelOps AI database with demo data.

Run from the backend folder, with the virtual environment active:
    python scripts/seed_demo.py

It talks to the app directly (no server or network needed) and writes to
your real database. Safe to run twice: existing rooms and guests are
reused, and overlapping bookings are skipped.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def create_or_find(path: str, body: dict, key: str) -> int:
    r = client.post(path, json=body)
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        for item in client.get(path, params={"limit": 100}).json():
            if item[key] == body[key]:
                return item["id"]
    raise SystemExit(f"{path} failed: {r.status_code} {r.text}")


ROOMS = [
    ("201", "single", 2, 1, 1800),
    ("202", "double", 2, 2, 2500),
    ("203", "double", 2, 2, 2600),
    ("204", "suite", 2, 4, 5200),
    ("205", "single", 2, 1, 1900),
]
GUESTS = [
    ("Asha", "Rao", "asha.rao@example.com"),
    ("Ravi", "Kumar", "ravi.kumar@example.com"),
    ("Meera", "Shetty", "meera.shetty@example.com"),
    ("Arjun", "Nair", "arjun.nair@example.com"),
]

room_ids = [
    create_or_find(
        "/rooms",
        {
            "room_number": number,
            "room_type": room_type,
            "floor": floor,
            "capacity": capacity,
            "price_per_night": price,
        },
        "room_number",
    )
    for number, room_type, floor, capacity, price in ROOMS
]
print("rooms ready:", len(room_ids))

guest_ids = [
    create_or_find(
        "/guests",
        {"first_name": first, "last_name": last, "email": email},
        "email",
    )
    for first, last, email in GUESTS
]
print("guests ready:", len(guest_ids))

today = date.today()
for guest, room, start, end in [(0, 0, 1, 3), (1, 1, 2, 5), (2, 3, 1, 4)]:
    r = client.post(
        "/reservations",
        json={
            "guest_id": guest_ids[guest],
            "room_id": room_ids[room],
            "check_in": (today + timedelta(days=start)).isoformat(),
            "check_out": (today + timedelta(days=end)).isoformat(),
        },
    )
    print("reservation:", r.status_code)

# Requests start as type "other" with a plain priority, so clicking
# "AI triage" on the dashboard visibly changes them.
REQUESTS = [
    ("Please bring two extra towels and a blanket", "normal"),
    ("The air conditioner is not cooling and the room is very hot", "low"),
    ("I would like to order dinner to the room at 8 PM", "normal"),
    ("Need a taxi to the airport tomorrow at 6 AM", "normal"),
    ("There is smoke coming from the bathroom", "normal"),
    ("The wifi keeps disconnecting in my room", "low"),
    ("The room has not been cleaned today", "normal"),
    ("Could you please help me with something", "low"),
]
for i, (text, priority) in enumerate(REQUESTS):
    r = client.post(
        "/service-requests/",
        json={
            "guest_id": guest_ids[i % len(guest_ids)],
            "room_id": room_ids[i % len(room_ids)],
            "request_type": "other",
            "description": text,
            "priority": priority,
        },
    )
    print("service request:", r.status_code)

print("Done. Start the server and open http://127.0.0.1:8000/dashboard/")