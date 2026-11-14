def make_room(client):
    r = client.post(
        "/rooms",
        json={
            "room_number": "101",
            "room_type": "double",
            "floor": 1,
            "capacity": 2,
            "price_per_night": 2500,
        },
    )
    return r.json()["id"]


def make_guest(client):
    r = client.post(
        "/guests",
        json={"first_name": "Asha", "last_name": "Rao", "email": "asha@example.com"},
    )
    return r.json()["id"]


def make_request(client, description, priority="normal"):
    guest, room = make_guest(client), make_room(client)
    r = client.post(
        "/service-requests/",
        json={
            "guest_id": guest,
            "room_id": room,
            "request_type": "other",
            "description": description,
            "priority": priority,
        },
    )
    return r.json()["id"]


def test_predict_suggests_without_changing_anything(client):
    r = client.post("/triage/predict", json={"description": "The tap is leaking water"})
    assert r.status_code == 200
    assert r.json()["category"] == "maintenance"
    assert r.json()["team"] == "Maintenance team"


def test_predict_rejects_too_short_text(client):
    assert client.post("/triage/predict", json={"description": "x"}).status_code == 422


def test_apply_sets_category_and_raises_priority(client):
    req_id = make_request(client, "The air conditioner is not working", priority="low")
    r = client.post(f"/triage/service-requests/{req_id}/apply")
    assert r.status_code == 200
    body = r.json()
    assert body["applied"] is True
    assert body["service_request"]["request_type"] == "maintenance"
    assert body["service_request"]["priority"] == "high"


def test_apply_never_lowers_priority(client):
    req_id = make_request(client, "Please bring extra towels", priority="urgent")
    body = client.post(f"/triage/service-requests/{req_id}/apply").json()
    assert body["service_request"]["priority"] == "urgent"
    assert body["service_request"]["request_type"] == "housekeeping"


def test_apply_skips_low_confidence_requests(client):
    req_id = make_request(client, "blah qwerty zzz")
    body = client.post(f"/triage/service-requests/{req_id}/apply").json()
    assert body["applied"] is False
    assert body["service_request"]["request_type"] == "other"


def test_apply_skips_closed_requests(client):
    req_id = make_request(client, "The air conditioner is not working")
    client.patch(f"/service-requests/{req_id}/status", json={"status": "in_progress"})
    client.patch(f"/service-requests/{req_id}/status", json={"status": "completed"})
    body = client.post(f"/triage/service-requests/{req_id}/apply").json()
    assert body["applied"] is False


def test_apply_unknown_request_returns_404(client):
    assert client.post("/triage/service-requests/9999/apply").status_code == 404