from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

MOCK_ORDERS = {
    "12345": {
        "status": "in transit",
        "tracking_code": "BR123456789",
        "estimated_delivery": "2026-07-02",
    },
    "67890": {
        "status": "delivered",
        "tracking_code": "BR987654321",
        "estimated_delivery": "2026-06-20",
    },
}


class OrderLookupInput(BaseModel):
    order_id: str = Field(..., description="The customer's order number to look up.")


class OrderLookupTool(BaseTool):
    name: str = "Order Lookup"
    description: str = (
        "Looks up the current status, tracking code, and estimated delivery date for a "
        "specific order, given its order number."
    )
    args_schema: Type[BaseModel] = OrderLookupInput

    def _run(self, order_id: str) -> str:
        order = MOCK_ORDERS.get(order_id)
        if not order:
            return f"No order found with number {order_id}."
        return (
            f"Order {order_id}: status={order['status']}, "
            f"tracking_code={order['tracking_code']}, "
            f"estimated_delivery={order['estimated_delivery']}"
        )