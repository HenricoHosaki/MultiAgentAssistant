from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from sac_assistant.db.models import Order, OrderItem, Product
from sac_assistant.db.session import SessionLocal

router = APIRouter(prefix="/store", tags=["store"])


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/products/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "title": product.title,
        "price": float(product.price),
        "category": product.category,
    }


@router.get("/orders/{order_id}")
def get_order(order_id: str, session: Session = Depends(get_session)):
    order = (
        session.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    items = []
    amount_paid = 0.0
    for line in order.items:
        price = float(line.product.price)
        line_total = round(price * line.quantity, 2)
        amount_paid += line_total
        items.append(
            {
                "title": line.product.title,
                "quantity": line.quantity,
                "unit_price": price,
                "line_total": line_total,
            }
        )

    return {
        "id": order.id,
        "status": order.status,
        "purchase_date": order.purchase_date,
        "estimated_delivery": order.estimated_delivery,
        "tracking_code": order.tracking_code,
        "payment_method": order.payment_method,
        "shipping_address": order.shipping_address,
        "items": items,
        "amount_paid": round(amount_paid, 2),
    }
