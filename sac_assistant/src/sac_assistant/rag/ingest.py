from pathlib import Path
import sys
import chromadb
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

KNOWLEDGE_ROOT = Path(__file__).parent.parent.parent.parent / "knowledge"

MIN_BODY_CHARS = 20

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
chroma_client = chromadb.PersistentClient(path=str(Path(__file__).parent / "chroma_db"))


def _has_content(section: str) -> bool:
    parts = section.split("\n", 1)
    body = parts[1].strip() if len(parts) > 1 else ""
    return len(body) >= MIN_BODY_CHARS


def ingest(domain: str):
    knowledge_dir = KNOWLEDGE_ROOT / domain
    md_files = list(knowledge_dir.glob("*.md"))

    collection = chroma_client.get_or_create_collection(name=domain)
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")
        sections = text.split("## ")
        for section in sections:
            section = section.strip()
            if not section or not _has_content(section):
                continue
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=section,
            )
            embedding = result.embeddings[0].values
            print(f"[{domain}] Generated embedding with {len(embedding)} dimensions")
            collection.add(
                ids=[f"{file_path.stem}-{len(collection.get()['ids'])}"],
                embeddings=[embedding],
                documents=[section],
                metadatas=[{"source": file_path.name}],
            )


if __name__ == "__main__":
    domains = sys.argv[1:] or ["products", "delivery", "payments"]
    for domain in domains:
        ingest(domain)