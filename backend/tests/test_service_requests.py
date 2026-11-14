from datetime import date, timedelta


def make_room(client, number="101"):
    r = client.post(
        "/rooms",
        json={
            "room_number": number,
            "room_type": "double",
            "floor": 1,
            "capacity": 2,
            "price_per_night": 2500,
        },
    )
    return r.json()["id"]


def make_guest(client, email="asha@example.com"):
    r = client.post(
        "/guests",
        json={"first_name": "Asha", "last_name": "Rao", "email": email},
    )
    return r.json()["id"]


def make_reservation(client, guest, room):
    start = date.today() + timedelta(days=10)
    r = client.post(
        "/reservations",
        json={
            "guest_id": guest,
            "room_id": room,
            "check_in": start.isoformat(),
            "check_out": (start + timedelta(days=2)).isoformat(),
        },
    )
    return r.json()["id"]


def body(guest, room, **extra):
    return {
        "guest_id": guest,
        "room_id": room,
        "request_type": "housekeeping",
        "description": "Please bring extra towels",
        **extra,
    }


def test_create_request_defaults(client):
    guest, room = make_guest(client), make_room(client)
    r = client.post("/service-requests/", json=body(guest, room))
    assert r.status_code == 201
    assert r.json()["status"] == "pending"
    assert r.json()["priority"] == "normal"


def test_create_request_linked_to_reservation(client):
    guest, room = make_guest(client), make_room(client)
    res_id = make_reservation(client, guest, room)
    r = client.post("/service-requests/", json=body(guest, room, reservation_id=res_id))
    assert r.status_code == 201
    assert r.json()["reservation_id"] == res_id


def test_unknown_guest_and_room(client):
    guest, room = make_guest(client), make_room(client)
    assert client.post("/service-requests/", json=body(9999, room)).status_code == 400
    assert client.post("/service-requests/", json=body(guest, 9999)).status_code == 400

def test_reservation_must_match_guest_and_room(client):
    guest = make_guest(client)
    room_a, room_b = make_room(client, "101"), make_room(client, "102")
    res_id = make_reservation(client, guest, room_a)
    r = client.post("/service-requests/", json=body(guest, room_b, reservation_id=res_id))
    assert r.status_code >= 400


def test_invalid_priority_rejected(client):
    guest, room = make_guest(client), make_room(client)
    r = client.post("/service-requests/", json=body(guest, room, priority="asap"))
    assert r.status_code == 422


def test_list_filters(client):
    guest, room = make_guest(client), make_room(client)
    client.post("/service-requests/", json=body(guest, room, priority="urgent"))
    client.post("/service-requests/", json=body(guest, room, priority="low"))
    r = client.get("/service-requests/", params={"priority": "urgent"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["priority"] == "urgent"


def test_status_flow_and_invalid_change(client):
    guest, room = make_guest(client), make_room(client)
    req_id = client.post("/service-requests/", json=body(guest, room)).json()["id"]

    r = client.patch(f"/service-requests/{req_id}/status", json={"status": "in_progress"})
    assert r.status_code == 200
    r = client.patch(f"/service-requests/{req_id}/status", json={"status": "completed"})
    assert r.json()["status"] == "completed"

    # a completed request can never be reopened
    r = client.patch(f"/service-requests/{req_id}/status", json={"status": "pending"})
    assert r.status_code >= 400


def test_update_priority_and_404(client):
    guest, room = make_guest(client), make_room(client)
    req_id = client.post("/service-requests/", json=body(guest, room)).json()["id"]
    r = client.patch(f"/service-requests/{req_id}", json={"priority": "high"})
    assert r.status_code == 200
    assert r.json()["priority"] == "high"
    assert client.get("/service-requests/9999").status_code == 404


def test_delete_request(client):
    guest, room = make_guest(client), make_room(client)
    req_id = client.post("/service-requests/", json=body(guest, room)).json()["id"]
    assert client.delete(f"/service-requests/{req_id}").status_code in (200, 204)
    assert client.get(f"/service-requests/{req_id}").status_code == 404