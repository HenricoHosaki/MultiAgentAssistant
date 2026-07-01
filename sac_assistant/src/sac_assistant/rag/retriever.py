from pathlib import Path
import chromadb
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
chroma_client = chromadb.PersistentClient(path=str(Path(__file__).parent / "chroma_db"))

MAX_DISTANCE = 0.85


def retrieve(
    query: str,
    collection_name: str,
    n_results: int = 3,
    max_distance: float = MAX_DISTANCE,
):
    collection = chroma_client.get_or_create_collection(name=collection_name)

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
    )
    query_embedding = result.embeddings[0].values

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    kept_docs, kept_metas, kept_dists = [], [], []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist < max_distance:
            kept_docs.append(doc)
            kept_metas.append(meta)
            kept_dists.append(dist)

    return {
        "documents": [kept_docs],
        "metadatas": [kept_metas],
        "distances": [kept_dists],
    }


if __name__ == "__main__":
    resposta = retrieve("Is the backpack waterproof?", collection_name="products")
    print(resposta)