ROOM = {
    "room_number": "101",
    "room_type": "double",
    "floor": 1,
    "capacity": 2,
    "price_per_night": 2500,
}


def test_create_room(client):
    r = client.post("/rooms", json=ROOM)
    assert r.status_code == 201
    body = r.json()
    assert body["room_number"] == "101"
    assert body["status"] == "available"
    assert body["is_active"] is True


def test_duplicate_room_number_rejected(client):
    client.post("/rooms", json=ROOM)
    r = client.post("/rooms", json=ROOM)
    assert r.status_code == 409


def test_invalid_price_rejected(client):
    r = client.post("/rooms", json={**ROOM, "price_per_night": -5})
    assert r.status_code == 422


def test_list_and_pagination(client):
    for n in range(1, 6):
        client.post("/rooms", json={**ROOM, "room_number": str(100 + n)})
    r = client.get("/rooms", params={"skip": 1, "limit": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_room_and_404(client):
    room_id = client.post("/rooms", json=ROOM).json()["id"]
    assert client.get(f"/rooms/{room_id}").status_code == 200
    assert client.get("/rooms/9999").status_code == 404


def test_update_room(client):
    room_id = client.post("/rooms", json=ROOM).json()["id"]
    r = client.patch(f"/rooms/{room_id}", json={"price_per_night": 3000})
    assert r.status_code == 200
    assert float(r.json()["price_per_night"]) == 3000


def test_delete_is_soft(client):
    room_id = client.post("/rooms", json=ROOM).json()["id"]
    assert client.delete(f"/rooms/{room_id}").status_code == 204
    assert client.get("/rooms").json() == []
    inactive = client.get("/rooms", params={"include_inactive": True}).json()
    assert len(inactive) == 1