GUEST = {
    "first_name": "Asha",
    "last_name": "Rao",
    "email": "asha@example.com",
    "phone": "9876543210",
}


def test_create_guest(client):
    r = client.post("/guests", json=GUEST)
    assert r.status_code == 201
    assert r.json()["email"] == "asha@example.com"


def test_duplicate_email_rejected(client):
    client.post("/guests", json=GUEST)
    assert client.post("/guests", json=GUEST).status_code == 409


def test_invalid_email_rejected(client):
    r = client.post("/guests", json={**GUEST, "email": "not-an-email"})
    assert r.status_code == 422


def test_get_update_and_404(client):
    guest_id = client.post("/guests", json=GUEST).json()["id"]
    assert client.get(f"/guests/{guest_id}").status_code == 200
    assert client.get("/guests/9999").status_code == 404
    r = client.patch(f"/guests/{guest_id}", json={"first_name": "Meera"})
    assert r.status_code == 200
    assert r.json()["first_name"] == "Meera"


def test_delete_guest(client):
    guest_id = client.post("/guests", json=GUEST).json()["id"]
    assert client.delete(f"/guests/{guest_id}").status_code == 204
    assert client.get(f"/guests/{guest_id}").status_code == 404