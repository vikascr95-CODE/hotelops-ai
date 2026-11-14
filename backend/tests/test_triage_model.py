import pytest

from app.ai.triage import MIN_CONFIDENCE, TEAMS, find_emergency_words, triage

# Phrases the model has never seen in training.
HELD_OUT = [
    ("The AC in my room is broken and it is very hot", "maintenance"),
    ("Could someone bring me two more bath towels", "housekeeping"),
    ("I'd like to have dinner sent upstairs", "room_service"),
    ("Can I check out at 3 pm instead", "front_desk"),
    ("The wifi is not connecting", "maintenance"),
    ("Extra pillow please", "housekeeping"),
    ("Send me a sandwich and juice", "room_service"),
    ("Need a cab to the railway station", "front_desk"),
]


@pytest.mark.parametrize("text, expected", HELD_OUT)
def test_category_on_unseen_phrases(text, expected):
    assert triage(text)["category"] == expected


def test_overall_accuracy_on_unseen_phrases():
    correct = sum(triage(t)["category"] == c for t, c in HELD_OUT)
    assert correct / len(HELD_OUT) >= 0.85


@pytest.mark.parametrize(
    "text",
    [
        "I can see smoke in the hallway",
        "My husband is unconscious",
        "There is a fire near the stairs",
        "Please call an ambulance",
    ],
)
def test_emergencies_are_always_urgent_safety(text):
    result = triage(text)
    assert result["category"] == "safety"
    assert result["priority"] == "urgent"
    assert result["needs_review"] is False
    assert result["team"] == TEAMS["safety"]


def test_gibberish_is_flagged_for_human_review():
    result = triage("blah qwerty zzz")
    assert result["needs_review"] is True
    assert result["confidence"] < MIN_CONFIDENCE


def test_result_has_team_and_reason():
    result = triage("The tap is leaking")
    assert result["team"] in TEAMS.values()
    assert result["reasons"]


def test_emergency_word_finder():
    assert set(find_emergency_words("There is SMOKE and a fire")) == {"smoke", "fire"}
    assert find_emergency_words("Please bring towels") == []