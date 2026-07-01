from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sac_assistant.rag.retriever import retrieve


class KnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="The customer's question to search the knowledge base for.")


def _search(collection_name: str, query: str) -> str:
    results = retrieve(query, collection_name=collection_name)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return (
            "No relevant information was found in the knowledge base for this question. "
            "Do not guess — tell the customer you don't have this information."
        )

    formatted = []
    for doc, meta in zip(documents, metadatas):
        formatted.append(f"Source: {meta['source']}\n{doc}")

    return "\n\n---\n\n".join(formatted)


class ProductKnowledgeSearchTool(BaseTool):
    name: str = "Product Knowledge Search"
    description: str = (
        "Searches the product knowledge base (catalog, warranty, usage and care) "
        "for information relevant to a customer's question about products. "
        "Returns relevant excerpts along with their source document."
    )
    args_schema: Type[BaseModel] = KnowledgeSearchInput

    def _run(self, query: str) -> str:
        return _search("products", query)


class DeliveryKnowledgeSearchTool(BaseTool):
    name: str = "Delivery Knowledge Search"
    description: str = (
        "Searches the delivery knowledge base (shipping coverage, timeframes, tracking, free shipping) "
        "for information relevant to a customer's question about deliveries. "
        "Returns relevant excerpts along with their source document."
    )
    args_schema: Type[BaseModel] = KnowledgeSearchInput

    def _run(self, query: str) -> str:
        return _search("delivery", query)


class PaymentKnowledgeSearchTool(BaseTool):
    name: str = "Payment Knowledge Search"
    description: str = (
        "Searches the payment knowledge base (payment methods, installments, refund timelines) "
        "for information relevant to a customer's question about payments. "
        "Returns relevant excerpts along with their source document."
    )
    args_schema: Type[BaseModel] = KnowledgeSearchInput

    def _run(self, query: str) -> str:
        return _search("payments", query)