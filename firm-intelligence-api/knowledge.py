"""Embedding and retrival mechanics... nothing in here will know about FastAPI"""
import math
import os
import voyageai
from documents import DOCUMENTS

EMBED_MODEL = "voyage-3-lite"
#EMBED_MODEL = "voyage-4-lite" (replace above one with below model if it ask for adding payment method)

voyage = voyageai.Client(
    api_key = os.environ["VOYAGE_API_KEY"],
    max_retries=3,
    timeout=3
)
#the in-memory index... a list of dicts (exact like FIRM last week.)

INDEX: list[dict] = []

def embed_texts(texts: list[str], input_type: str) -> tuple[list[list[float]]]:
    #embed a batch
     #input_type: tells voyage whether these are docs or a query
    result = voyage.embed(texts=texts, model=EMBED_MODEL, input_type=input_type)

    #returns the vectors and token count (can see cost)
    return result.embeddings, result.total_tokens


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """How close are two vectors in direction, ignoring their length
    1.0 means identical direction
    0.0 means unrelated
    -1.0 means opposite """
    dot = sum(x * y for x, y in zip(a,b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

def build_index() -> int:
    """Embed every document once and hold the vectors in memory"""
    INDEX.clear()
    texts = [doc["body"] for doc in DOCUMENTS]

    vectors, tokens = embed_texts(texts, input_type = "document")
    for doc , vector in zip(DOCUMENTS, vectors):
        INDEX.append({
            "id": doc["id"],
            "title": doc["title"],
            "text": doc["body"],
            "vector": vector
        })

    return tokens

def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question ... then score it against everything in the index """
    if not INDEX:
        raise RuntimeError("Index isx Empty - call build_index() first")
    query_vectors, _ = embed_texts([question], input_type="query")
    query_vectors = query_vectors[0]

    scored = [
        {
            "id": entry["id"],
            "title": entry["title"],
            "text": entry["text"],
            "score": cosine_similarity(query_vectors, entry["vector"])
        }
        for entry in INDEX
    ]

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]
