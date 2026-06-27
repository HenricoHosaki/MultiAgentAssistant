from pathlib import Path
import chromadb
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
chroma_client = chromadb.PersistentClient(path=str(Path(__file__).parent / "chroma_db"))


def retrieve(query: str, collection_name: str, n_results: int = 3):
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
    return results


if __name__ == "__main__":
    resposta = retrieve("Is the backpack waterproof?", collection_name="products")
    print(resposta)