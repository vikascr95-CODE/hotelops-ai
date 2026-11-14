"""Triage agent for service requests.

Two small scikit-learn models read the request text:
  * one predicts the category (housekeeping, maintenance, ...)
  * one predicts the priority (low, normal, high, urgent)

Safety rules run on top of the models. If the text mentions an emergency
(fire, smoke, gas, medical trouble...), the rules force category "safety"
and priority "urgent", whatever the models say. If the model is not
confident, the result is flagged for a human to review.
"""

import re
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from app.ai.triage_data import TRAINING_DATA

TEAMS = {
    "housekeeping": "Housekeeping team",
    "maintenance": "Maintenance team",
    "room_service": "Kitchen and room service",
    "front_desk": "Front desk",
    "safety": "Security and emergency response",
}

PRIORITY_ORDER = ["low", "normal", "high", "urgent"]

# If the best category guess is below this probability, a human should check it.
MIN_CONFIDENCE = 0.40

EMERGENCY_PATTERNS = [
    r"\bfire\b", r"\bsmoke\b", r"\bgas leak\b", r"\bsmell(?:s|ing)? gas\b",
    r"\bflood(?:ing|ed)?\b", r"\bsparks?\b", r"\bambulance\b", r"\bdoctor\b",
    r"\bmedical\b", r"\bchest pain\b", r"\bunconscious\b", r"\bbleeding\b",
    r"\blocked in\b", r"\bstuck (?:in|with)\b", r"\bsuspicious\b",
    r"\bemergency\b", r"\bheart attack\b", r"\bnot breathing\b",
]


def _train(label_position: int):
    texts = [row[0] for row in TRAINING_DATA]
    labels = [row[label_position] for row in TRAINING_DATA]
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), lowercase=True),
        LogisticRegression(C=20, max_iter=1000),
    )
    model.fit(texts, labels)
    return model


@lru_cache(maxsize=1)
def get_models():
    """Train both models once, on first use. The data is tiny, so it takes milliseconds."""
    return _train(1), _train(2)


def find_emergency_words(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for pattern in EMERGENCY_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            found.append(match.group(0))
    return found


def triage(text: str) -> dict:
    text = " ".join(text.split())
    category_model, priority_model = get_models()

    probabilities = category_model.predict_proba([text])[0]
    best = probabilities.argmax()
    category = str(category_model.classes_[best])
    confidence = float(probabilities[best])
    priority = str(priority_model.predict([text])[0])
    reasons = [f"Model predicted category '{category}' ({confidence:.0%} confident)"]

    emergency_words = find_emergency_words(text)
    if emergency_words:
        category, priority, confidence = "safety", "urgent", 1.0
        reasons = [f"Safety rule triggered by: {', '.join(emergency_words)}"]

    return {
        "category": category,
        "priority": priority,
        "team": TEAMS[category],
        "confidence": round(confidence, 3),
        "needs_review": confidence < MIN_CONFIDENCE,
        "reasons": reasons,
    }