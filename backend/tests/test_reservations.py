from datetime import date, timedelta


def make_room(client, number="101", price=2500):
    r = client.post(
        "/rooms",
        json={
            "room_number": number,
            "room_type": "double",
            "floor": 1,
            "capacity": 2,
            "price_per_night": price,
        },
    )
    return r.json()["id"]


def make_guest(client, email="asha@example.com"):
    r = client.post(
        "/guests",
        json={"first_name": "Asha", "last_name": "Rao", "email": email},
    )
    return r.json()["id"]


def day(offset):
    """A date `offset` days from today, as text like 2026-11-20."""
    return (date.today() + timedelta(days=offset)).isoformat()


def book(client, guest_id, room_id, start, end):
    return client.post(
        "/reservations",
        json={
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in": day(start),
            "check_out": day(end),
        },
    )


def test_booking_and_price(client):
    guest, room = make_guest(client), make_room(client)
    r = book(client, guest, room, 10, 13)  # 3 nights
    assert r.status_code == 201
    assert float(r.json()["total_price"]) == 7500
    assert r.json()["status"] == "confirmed"


def test_overlap_rejected(client):
    guest, room = make_guest(client), make_room(client)
    book(client, guest, room, 10, 13)
    assert book(client, guest, room, 12, 15).status_code == 409


def test_back_to_back_allowed(client):
    guest, room = make_guest(client), make_room(client)
    book(client, guest, room, 10, 13)
    assert book(client, guest, room, 13, 15).status_code == 201


def test_cancelled_booking_frees_the_room(client):
    guest, room = make_guest(client), make_room(client)
    res_id = book(client, guest, room, 10, 13).json()["id"]
    client.patch(f"/reservations/{res_id}/status", json={"status": "cancelled"})
    assert book(client, guest, room, 10, 13).status_code == 201


def test_past_checkin_rejected(client):
    guest, room = make_guest(client), make_room(client)
    assert book(client, guest, room, -3, 2).status_code == 400


def test_checkout_before_checkin_rejected(client):
    guest, room = make_guest(client), make_room(client)
    assert book(client, guest, room, 10, 8).status_code == 422


def test_unknown_guest_and_room(client):
    guest, room = make_guest(client), make_room(client)
    assert book(client, 9999, room, 10, 12).status_code == 404
    assert book(client, guest, 9999, 10, 12).status_code == 404


def test_status_flow_updates_room(client):
    guest, room = make_guest(client), make_room(client)
    res_id = book(client, guest, room, 10, 12).json()["id"]

    client.patch(f"/reservations/{res_id}/status", json={"status": "checked_in"})
    assert client.get(f"/rooms/{room}").json()["status"] == "occupied"

    client.patch(f"/reservations/{res_id}/status", json={"status": "checked_out"})
    assert client.get(f"/rooms/{room}").json()["status"] == "cleaning"


def test_invalid_status_change_rejected(client):
    guest, room = make_guest(client), make_room(client)
    res_id = book(client, guest, room, 10, 12).json()["id"]
    client.patch(f"/reservations/{res_id}/status", json={"status": "cancelled"})
    r = client.patch(f"/reservations/{res_id}/status", json={"status": "checked_in"})
    assert r.status_code == 409


def test_availability(client):
    guest = make_guest(client)
    room_a, room_b = make_room(client, "101"), make_room(client, "102")
    book(client, guest, room_a, 10, 13)
    r = client.get(
        "/reservations/availability",
        params={"check_in": day(11), "check_out": day(12)},
    )
    numbers = [room["room_number"] for room in r.json()]
    assert numbers == ["102"]