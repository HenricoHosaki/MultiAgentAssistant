from pathlib import Path
import chromadb
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge" / "products"

md_files = list(KNOWLEDGE_DIR.glob("*.md"))

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
chroma_client = chromadb.PersistentClient(path=str(Path(__file__).parent / "chroma_db"))
collection = chroma_client.get_or_create_collection(name="products")
collection.delete(ids=collection.get()["ids"])

for file_path in md_files:
    text = file_path.read_text(encoding="utf-8")
    sections = text.split("## ")
    for section in sections:
        section = section.strip()
        if not section:
            continue
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=section,
        )
        embedding = result.embeddings[0].values
        print(f"Generated embedding with {len(embedding)} dimensions")
        collection.add(
            ids=[f"{file_path.stem}-{len(collection.get()['ids'])}"],
            embeddings=[embedding],
            documents=[section],
            metadatas=[{"source": file_path.name}],
        )