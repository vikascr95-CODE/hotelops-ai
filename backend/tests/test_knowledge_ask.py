from app.database.connection import get_db
from app.models.document import Document, DocumentChunk
from main import app


def seed_policy(client):
    db = next(app.dependency_overrides[get_db]())
    doc = Document(
        filename="stored.txt",
        original_filename="hotel_policy.txt",
        content_type="text/plain",
        file_size=100,
        extracted_text="policy",
    )
    doc.chunks = [
        DocumentChunk(
            chunk_index=0,
            content="Check-in time is 2 PM. Check-out time is 11 AM.",
        ),
        DocumentChunk(
            chunk_index=1,
            content="Breakfast is served from 7 AM to 10 AM in the dining hall.",
        ),
    ]
    db.add(doc)
    db.commit()
    db.close()


def test_answers_from_document(client):
    seed_policy(client)
    r = client.post("/knowledge/ask", json={"question": "What time is check-out?"})
    assert r.status_code == 200
    body = r.json()
    assert body["grounded"] is True
    assert "11 AM" in body["answer"]
    assert body["sources"][0]["document"] == "hotel_policy.txt"


def test_unrelated_question_is_not_grounded(client):
    seed_policy(client)
    r = client.post("/knowledge/ask", json={"question": "Do you offer helicopter rides?"})
    assert r.status_code == 200
    assert r.json()["grounded"] is False
    assert r.json()["sources"] == []


def test_no_documents_uploaded(client):
    r = client.post("/knowledge/ask", json={"question": "What time is breakfast?"})
    assert r.json()["grounded"] is False


def test_question_too_short_rejected(client):
    r = client.post("/knowledge/ask", json={"question": "hi"})
    assert r.status_code == 422