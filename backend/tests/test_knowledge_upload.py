import pytest


@pytest.fixture(autouse=True)
def temp_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.document_service.UPLOAD_DIR", tmp_path)


def upload(client, name, data, content_type="text/plain"):
    return client.post("/knowledge/upload", files={"file": (name, data, content_type)})


def test_upload_text_file(client):
    r = upload(client, "policy.txt", b"Check-out time is 11 AM.")
    assert r.status_code == 201
    assert r.json()["original_filename"] == "policy.txt"


def test_wrong_file_type_rejected(client):
    assert upload(client, "virus.exe", b"data").status_code == 400


def test_empty_file_rejected(client):
    assert upload(client, "empty.txt", b"").status_code == 400


def test_non_utf8_text_rejected(client):
    assert upload(client, "bad.txt", b"\xff\xfe\x00bad").status_code == 422


def test_corrupted_pdf_rejected(client):
    r = upload(client, "broken.pdf", b"this is not a pdf", "application/pdf")
    assert r.status_code == 422