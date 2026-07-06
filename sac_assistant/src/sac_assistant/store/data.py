"""Seed data for the mock store service.

Products mirror the names and prices in the Products knowledge base (knowledge/products/*.md)
so the order integration stays coherent with what the RAG agent knows about. Orders reference
products by id; the router resolves them into a rich order (item names, totals, payment,
address, dates, status) — the shape a real order/CRM API would return.
"""

PRODUCTS = {
    1: {"id": 1, "title": "Razer BlackWidow V4 X", "price": 169.99, "category": "keyboards"},
    2: {"id": 2, "title": "Redragon Kumara K552", "price": 39.99, "category": "keyboards"},
    3: {"id": 3, "title": "Corsair K70 RGB Pro", "price": 179.99, "category": "keyboards"},
    4: {"id": 4, "title": "Logitech G502 X Plus", "price": 159.99, "category": "mice"},
    5: {"id": 5, "title": "Razer DeathAdder V3", "price": 89.99, "category": "mice"},
    6: {"id": 6, "title": "Redragon M711 Cobra", "price": 24.99, "category": "mice"},
    7: {"id": 7, "title": "Razer BlackShark V2 Pro", "price": 199.99, "category": "headsets"},
    8: {"id": 8, "title": "HyperX Cloud II", "price": 99.99, "category": "headsets"},
    9: {"id": 9, "title": "Corsair HS65 Surround", "price": 69.99, "category": "headsets"},
    10: {"id": 10, "title": "LG UltraGear 27GP850", "price": 379.99, "category": "monitors"},
    11: {"id": 11, "title": "Samsung Odyssey G5", "price": 279.99, "category": "monitors"},
    12: {"id": 12, "title": "DXRacer Formula Series", "price": 329.99, "category": "chairs"},
    13: {"id": 13, "title": "ThunderX3 EC3", "price": 249.99, "category": "chairs"},
    14: {"id": 14, "title": 'Razer Rogue Backpack V3 15"', "price": 99.99, "category": "backpacks"},
    15: {"id": 15, "title": "Corsair Carbide Backpack", "price": 79.99, "category": "backpacks"},
    16: {"id": 16, "title": "Logitech C920", "price": 69.99, "category": "webcams"},
    17: {"id": 17, "title": "Razer Kiyo", "price": 99.99, "category": "webcams"},
    18: {"id": 18, "title": "Dazz Speed", "price": 14.99, "category": "mousepads"},
    19: {"id": 19, "title": "Corsair MM300 Extended", "price": 29.99, "category": "mousepads"},
    20: {"id": 20, "title": "Xbox Wireless Controller", "price": 59.99, "category": "controllers"},
    21: {"id": 21, "title": "8BitDo Ultimate Controller", "price": 64.99, "category": "controllers"},
    22: {"id": 22, "title": "Anker 7-in-1 PowerExpand", "price": 39.99, "category": "usb_hubs"},
    23: {"id": 23, "title": "CalDigit TS3 Plus", "price": 239.99, "category": "usb_hubs"},
    24: {"id": 24, "title": "Anker 65W GaNPrime", "price": 34.99, "category": "chargers"},
    25: {"id": 25, "title": "Anker PowerCore 20000mAh", "price": 49.99, "category": "chargers"},
    26: {"id": 26, "title": "Kingston NV2 1TB", "price": 54.99, "category": "ssds"},
    27: {"id": 27, "title": "Samsung 980 Pro 2TB", "price": 159.99, "category": "ssds"},
}

ORDERS = {
    "12345": {
        "id": "12345",
        "status": "in transit",
        "purchase_date": "2026-06-25",
        "estimated_delivery": "2026-07-02",
        "tracking_code": "BR123456789",
        "payment_method": "Credit card (Visa ****4242), 3x installments",
        "shipping_address": "Rua das Flores, 123, Apt 45 - São Paulo/SP, 01000-000",
        "products": [
            {"productId": 3, "quantity": 1},
            {"productId": 5, "quantity": 1},
        ],
    },
    "67890": {
        "id": "67890",
        "status": "delivered",
        "purchase_date": "2026-06-10",
        "estimated_delivery": "2026-06-20",
        "tracking_code": "BR987654321",
        "payment_method": "Pix",
        "shipping_address": "Av. Atlântica, 500 - Rio de Janeiro/RJ, 22010-000",
        "products": [
            {"productId": 7, "quantity": 1},
        ],
    },
    "11223": {
        "id": "11223",
        "status": "processing",
        "purchase_date": "2026-06-29",
        "estimated_delivery": "2026-07-09",
        "tracking_code": None,
        "payment_method": "Boleto (bank slip)",
        "shipping_address": "Rua da Bahia, 1000 - Belo Horizonte/MG, 30160-011",
        "products": [
            {"productId": 10, "quantity": 1},
            {"productId": 13, "quantity": 1},
        ],
    },
    "44556": {
        "id": "44556",
        "status": "cancelled",
        "purchase_date": "2026-06-15",
        "estimated_delivery": None,
        "tracking_code": None,
        "payment_method": "Debit card (refunded)",
        "shipping_address": "Rua XV de Novembro, 200 - Curitiba/PR, 80020-310",
        "products": [
            {"productId": 6, "quantity": 2},
            {"productId": 18, "quantity": 3},
        ],
    },
}
