"""Creates the tables (if missing) and seeds them from store/data.py.

Safe to re-run: skips seeding a table that already has rows.
"""

from sac_assistant.db.models import Base, Order, OrderItem, Product
from sac_assistant.db.session import SessionLocal, engine
from sac_assistant.store.data import ORDERS, PRODUCTS


def seed() -> None:
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        if session.query(Product).count() == 0:
            for product in PRODUCTS.values():
                session.add(
                    Product(
                        id=product["id"],
                        title=product["title"],
                        price=product["price"],
                        category=product["category"],
                    )
                )
            print(f"Seeded {len(PRODUCTS)} products.")
        else:
            print("Products table already has data, skipping.")

        if session.query(Order).count() == 0:
            for order in ORDERS.values():
                session.add(
                    Order(
                        id=order["id"],
                        status=order["status"],
                        purchase_date=order["purchase_date"],
                        estimated_delivery=order["estimated_delivery"],
                        tracking_code=order["tracking_code"],
                        payment_method=order["payment_method"],
                        shipping_address=order["shipping_address"],
                    )
                )
                for line in order["products"]:
                    session.add(
                        OrderItem(
                            order_id=order["id"],
                            product_id=line["productId"],
                            quantity=line["quantity"],
                        )
                    )
            print(f"Seeded {len(ORDERS)} orders.")
        else:
            print("Orders table already has data, skipping.")

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed()
