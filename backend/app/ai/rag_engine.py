import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and", "or",
    "in", "on", "at", "for", "with", "by", "it", "this", "that", "what", "when",
    "how", "do", "does", "can", "i", "my", "you", "your", "we", "our",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def rank_chunks(question: str, chunks: list[dict], top_k: int = 3,
                k1: float = 1.5, b: float = 0.75) -> list[dict]:
    """Rank chunks by how well they match the question (BM25).

    Each chunk is a dict with at least: id, document_id, text.
    Returns the best matches, highest score first. Chunks with no
    matching words are left out, so an unrelated question returns [].
    """
    query_terms = tokenize(question)
    if not query_terms or not chunks:
        return []

    tokenized = [tokenize(c["text"]) for c in chunks]
    avg_len = sum(len(t) for t in tokenized) / len(tokenized) or 1.0
    n = len(chunks)

    doc_freq = Counter()
    for tokens in tokenized:
        for term in set(tokens):
            doc_freq[term] += 1

    results = []
    for chunk, tokens in zip(chunks, tokenized):
        counts = Counter(tokens)
        score = 0.0
        for term in set(query_terms):
            if term not in counts:
                continue
            idf = math.log(1 + (n - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            tf = counts[term]
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * len(tokens) / avg_len))
        if score > 0:
            results.append({**chunk, "score": round(score, 4)})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]

def best_sentences(question: str, text: str, limit: int = 2) -> str:
    """Pick the sentences in `text` that share the most words with the question."""
    terms = set(tokenize(question))
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    scored = [(len(terms & set(tokenize(s))), i, s) for i, s in enumerate(sentences)]
    scored = [item for item in scored if item[0] > 0]
    if not scored:
        return text.strip()
    top = sorted(scored, key=lambda item: (-item[0], item[1]))[:limit]
    return " ".join(s for _, _, s in sorted(top, key=lambda item: item[1]))