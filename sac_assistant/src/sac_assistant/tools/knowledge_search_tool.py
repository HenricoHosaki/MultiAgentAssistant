from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sac_assistant.rag.retriever import retrieve


class ProductKnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="The customer's question about products to search the knowledge base for.")


class ProductKnowledgeSearchTool(BaseTool):
    name: str = "Product Knowledge Search"
    description: str = (
        "Searches the product knowledge base (catalog, warranty, usage and care) "
        "for information relevant to a customer's question about products. "
        "Returns relevant excerpts along with their source document."
    )
    args_schema: Type[BaseModel] = ProductKnowledgeSearchInput

    def _run(self, query: str) -> str:
        results = retrieve(query)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        formatted = []
        for doc, meta in zip(documents, metadatas):
            formatted.append(f"Source: {meta['source']}\n{doc}")

        return "\n\n---\n\n".join(formatted)