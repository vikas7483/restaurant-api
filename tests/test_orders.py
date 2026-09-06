import requests

from harness.contract import load_openapi, validate_response


BASE_URL = "http://127.0.0.1:5000"

TEST_CUSTOMER_ID = 1
TEST_TABLE_ID = 3


def create_test_order():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": TEST_CUSTOMER_ID,
            "dining_table_id": TEST_TABLE_ID,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 2,
                },
                {
                    "menu_item_id": 3,
                    "quantity": 1,
                },
            ],
        },
    )

    assert response.status_code == 201

    return response


def test_create_order_contract():
    openapi = load_openapi()

    response = create_test_order()

    validate_response(openapi, response)

    data = response.json()

    assert data["status"] == "NEW"
    assert data["total_cents"] == 80000


def test_get_order_contract():
    openapi = load_openapi()

    response = create_test_order()

    order_id = response.json()["id"]

    get_response = requests.get(
        f"{BASE_URL}/orders/{order_id}"
    )

    assert get_response.status_code == 200

    validate_response(openapi, get_response)

    data = get_response.json()

    assert data["total_cents"] == 80000
    assert len(data["items"]) == 2


def test_order_status_state_machine():
    response = create_test_order()

    order_id = response.json()["id"]

    transitions = [
        ("PREPARING", 200),
        ("READY", 200),
        ("COMPLETED", 200),
    ]

    for status, expected_status_code in transitions:
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": status},
        )

        assert response.status_code == expected_status_code
        assert response.json()["status"] == status


def test_order_rejects_invalid_status_transition():
    response = create_test_order()

    order_id = response.json()["id"]

    # NEW -> PREPARING
    response = requests.patch(
        f"{BASE_URL}/orders/{order_id}/status",
        json={"status": "PREPARING"},
    )

    assert response.status_code == 200

    # PREPARING -> COMPLETED is not allowed.
    response = requests.patch(
        f"{BASE_URL}/orders/{order_id}/status",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 409


def test_customer_order_history_contract():
    openapi = load_openapi()

    create_response = create_test_order()

    assert create_response.status_code == 201

    response = requests.get(
        f"{BASE_URL}/customers/{TEST_CUSTOMER_ID}/orders"
    )

    assert response.status_code == 200

    validate_response(openapi, response)

    orders = response.json()

    assert len(orders) >= 1


def test_order_ignores_client_supplied_price():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": TEST_CUSTOMER_ID,
            "dining_table_id": TEST_TABLE_ID,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 2,
                    "price_cents": 1,
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["total_cents"] == 50000

    order_id = data["id"]

    get_response = requests.get(
        f"{BASE_URL}/orders/{order_id}"
    )

    assert get_response.status_code == 200

    order_data = get_response.json()

    assert order_data["total_cents"] == 50000
    assert order_data["items"][0]["unit_price_cents"] == 25000
    assert order_data["items"][0]["line_total_cents"] == 50000


def test_order_rejects_unavailable_menu_item():
    # Temporarily make menu item 1 unavailable.
    import sqlite3

    connection = sqlite3.connect("restaurant.db")

    try:
        connection.execute(
            "UPDATE menu_items SET available = 0 WHERE id = ?",
            (1,),
        )
        connection.commit()
    finally:
        connection.close()

    try:
        response = requests.post(
            f"{BASE_URL}/orders",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "dining_table_id": TEST_TABLE_ID,
                "items": [
                    {
                        "menu_item_id": 1,
                        "quantity": 1,
                    }
                ],
            },
        )

        assert response.status_code == 409
        assert response.json()["error"] == "Menu item is unavailable"

    finally:
        # Restore menu item 1 for other tests.
        connection = sqlite3.connect("restaurant.db")

        try:
            connection.execute(
                "UPDATE menu_items SET available = 1 WHERE id = ?",
                (1,),
            )
            connection.commit()
        finally:
            connection.close()


def test_order_can_be_cancelled_from_new():
    response = create_test_order()

    order_id = response.json()["id"]

    response = requests.patch(
        f"{BASE_URL}/orders/{order_id}/status",
        json={"status": "CANCELLED"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

def test_order_preserves_historical_menu_price():
    import sqlite3

    connection = sqlite3.connect("restaurant.db")

    original_price = connection.execute(
        "SELECT price_cents FROM menu_items WHERE id = 1"
    ).fetchone()[0]

    connection.close()

    # Create an order using the current menu price.
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 201

    order = response.json()

    assert order["total_cents"] == original_price

    order_id = order["id"]

    # Change the menu price after the order was created.
    connection = sqlite3.connect("restaurant.db")

    connection.execute(
        "UPDATE menu_items SET price_cents = ? WHERE id = 1",
        (original_price + 1000,),
    )
    connection.commit()
    connection.close()

    # Fetch the existing order again.
    response = requests.get(f"{BASE_URL}/orders/{order_id}")

    assert response.status_code == 200

    order = response.json()

    # Historical order price must remain unchanged.
    assert order["items"][0]["unit_price_cents"] == original_price
    assert order["items"][0]["line_total_cents"] == original_price

    # Restore the original menu price.
    connection = sqlite3.connect("restaurant.db")

    connection.execute(
        "UPDATE menu_items SET price_cents = ? WHERE id = 1",
        (original_price,),
    )
    connection.commit()
    connection.close()
def test_order_rejects_empty_items():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "items": [],
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Order must contain at least one item"

def test_order_rejects_invalid_quantity():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 0,
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "quantity must be greater than 0"

def test_order_rejects_missing_menu_item():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "items": [
                {
                    "menu_item_id": 999999,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "Menu item not found"

def test_order_rejects_missing_customer():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 999999,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"

def test_order_rejects_missing_dining_table():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "dining_table_id": 999999,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "Dining table not found"

def test_order_rejects_missing_reservation():
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_id": 1,
            "reservation_id": 999999,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "Reservation not found"