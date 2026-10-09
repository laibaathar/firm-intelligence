"""
One chroma collection per chunking strategy ... so that strategies can be compared side by side

Each collection remembers a "fingerprint" of the chunks and the embedding model the built it.
If either changes, the collection is rebuilt from scratch.
"""

import hashlib
import chromadb

import chunking
import knowledge
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

ALL_DOCUMENTS = DOCUMENTS + CORPUS_DOCUMENTS
BATCH_SIZE =128 #Voyages own guidance: batch documents to stay well inside rate limits
chroma = chromadb.PersistentClient(path="./chroma_store")

def collection_name(strategy: str) -> str:
    return f"chunks_{strategy}"

def collection_for(strategy: str):
    return chroma.get_or_create_collection(
        name = collection_name(strategy), configuration ={"hnsw": {"space": "cosine"}}
    )

def embed_batched(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    """ Embed any number of texts in batches. Return all vectors and the total token count."""
    vectors: list[list[float]] = []
    tokens = 0

    for start in range(0, len(texts), BATCH_SIZE):
        batch_vectors, batch_tokens = knowledge.embed_texts(texts[start:start + BATCH_SIZE], input_type=input_type)
        vectors.extend(batch_vectors)
        tokens += batch_tokens
    return vectors, tokens

# the fingerprint changes if the text, the model or the order changes... and stays put of nothing does
def fingerprint(chunks: list[dict]) -> str: 
    # SHA-256 - a recipe that turns any text into a fixed-length code (64 chars)
    digest = hashlib.sha256(knowledge.EMBED_MODEL.encode())
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[:16]

def build(strategy: str, force: bool = False) -> dict:
    """Make sure the strategys collection matches the current corpur, chunker and model."""
    """Answers one question is the index i already have still correct?"""

    #Part1
    chunks = chunking.chunk_corpus(ALL_DOCUMENTS, strategy)
    fp = fingerprint(chunks)
    col = collection_for(strategy)
    stored = col.get(limit=1, include=["metadatas"])["metadatas"]
    if not force and col.count() == len(chunks) and stored and stored[0].get("fingerprint") == fp:
        return {"strategy": strategy, "chunks": len(chunks), "embedding_tokens": 0, "rebuilt": False}

    #part 2 - the rebuild
    try:
        chroma.delete_collection(collection_name(strategy))
    except Exception:
        pass

    col  = collection_for(strategy)
    vectors, tokens = embed_batched([c["text"] for c in chunks], input_type="document")
    col.upsert(
        ids = [c["id"] for c in chunks],
        embeddings = vectors,
        documents = [c["text"] for c in chunks],
        metadatas = [{"doc_id": c["doc_id"], "title": c["title"], "fingerprint": fp} for c in chunks],

    )
    return {"strategy": strategy, "chunks": len(chunks), "embedding_tokens": tokens, "rebuilt": True}

