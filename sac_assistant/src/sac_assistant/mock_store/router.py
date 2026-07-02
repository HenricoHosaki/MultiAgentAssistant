from fastapi import APIRouter, HTTPException

from sac_assistant.mock_store.data import ORDERS, PRODUCTS

router = APIRouter(prefix="/mock", tags=["mock-store"])


@router.get("/products/{product_id}")
def get_product(product_id: int):
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/orders/{order_id}")
def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    items = []
    amount_paid = 0.0
    for line in order["products"]:
        product = PRODUCTS.get(line["productId"], {})
        title = product.get("title", f"product #{line['productId']}")
        price = product.get("price", 0.0)
        quantity = line["quantity"]
        line_total = round(price * quantity, 2)
        amount_paid += line_total
        items.append(
            {
                "title": title,
                "quantity": quantity,
                "unit_price": price,
                "line_total": line_total,
            }
        )

    return {
        "id": order["id"],
        "status": order["status"],
        "purchase_date": order["purchase_date"],
        "estimated_delivery": order["estimated_delivery"],
        "tracking_code": order["tracking_code"],
        "payment_method": order["payment_method"],
        "shipping_address": order["shipping_address"],
        "items": items,
        "amount_paid": round(amount_paid, 2),
    }
