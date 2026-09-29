#embed texts .... is imported, not rewritten
#the embedding provider has not changed... only where the vectors get stored

import chromadb
from documents import DOCUMENTS
from knowledge import embed_texts

chroma = chromadb.PersistentClient(path="./chroma_store")
collection = chroma.get_or_create_collection(
    name= "firm_documents",
    # HNSW (hierachchial Navigable Small World) is a graph based index used in vector databased to perform fast and appropriate nearest neighbour search in high dimensional data
    configuration={"hnsw": {"space": "cosine"}},
)

def count() -> int:
    return collection.count()

def build_index() -> int:
    """Embed every document and hand the vectors to chroma."""
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors, tokens = embed_texts(texts, input_type="document")

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]}for doc in DOCUMENTS],
    )
    return tokens


def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and let chroma do the storage."""
    query_vectors, _ =  embed_texts([question], input_type="query")

    result = collection.query(query_embeddings=query_vectors, n_results=top_k)
    return [
        {
            "id": doc_id,
            "title": metadata["title"],
            "text": text,

            #chroma will give us back distance... lower is closer...
            #We will do (1- distance) in order to flip from return distance, to similarity

            "score": 1- distance
        }
        for doc_id, text, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],

        )
    ]

#things to note from our switch to chroma
#embed_texts is imported not rewritten ...embedding provided has not changed only the storage has 
#configuration=........ -> not optional, we are choosing something different from Chromas default
#Chroma return distance, we return similarity
 #in chroma, lower is better
 #higher was better for ours.... (1 - distance) converts
# upsert instead of add => add falls on an id that already exists, upsert overwrites


