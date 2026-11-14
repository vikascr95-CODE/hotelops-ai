from app.ai.rag_engine import rank_chunks

CHUNKS = [
    {"id": 1, "document_id": 1, "text": "Check-in time is 2 PM. Check-out time is 11 AM."},
    {"id": 2, "document_id": 1, "text": "Breakfast is served from 7 AM to 10 AM in the dining hall."},
    {"id": 3, "document_id": 1, "text": "Pets are not allowed in any room. Service animals are welcome."},
]


def test_finds_the_right_chunk():
    result = rank_chunks("What time is check-out?", CHUNKS)
    assert result[0]["id"] == 1


def test_breakfast_question():
    result = rank_chunks("When is breakfast served?", CHUNKS)
    assert result[0]["id"] == 2


def test_unrelated_question_returns_nothing():
    assert rank_chunks("How do I reach the airport by helicopter?", CHUNKS) == []


def test_top_k_limit():
    assert len(rank_chunks("room", CHUNKS, top_k=1)) <= 1


def test_empty_inputs():
    assert rank_chunks("", CHUNKS) == []
    assert rank_chunks("check-out", []) == []