import asyncio
import time
from datetime import datetime, timedelta

from fastmcp import Client


MCP_URL = "http://127.0.0.1:8000/mcp"

CUSTOMER_ID = None
RESERVATION_ID = None
ORDER_ID = None

RESERVATION_TIME = (
    datetime.now() + timedelta(days=30)
).replace(microsecond=0).isoformat()


def call_tool(name, arguments):
    async def run():
        async with Client(MCP_URL) as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(run())

def test_list_menu():
    result = call_tool(
        "listMenu",
        {},
    )

    print("\nMenu result:")
    print(result)

    assert result is not None
    assert not result.is_error
    assert len(result.data) >= 1


def test_create_customer():
    global CUSTOMER_ID

    result = call_tool(
        "createCustomer",
        {
            "name": "Alice",
            "email": f"alice_{int(time.time())}@example.com",
        },
    )

    print("\nCustomer result:")
    print(result)

    assert result is not None
    assert not result.is_error

    CUSTOMER_ID = result.data.id


def test_list_tables():
    result = call_tool(
        "listDiningTables",
        {},
    )

    print("\nTables result:")
    print(result)

    assert result is not None
    assert not result.is_error


def test_create_reservation():
    global RESERVATION_ID

    result = call_tool(
        "createReservation",
        {
            "customer_id": CUSTOMER_ID,
            "dining_table_id": 2,
            "reservation_time": RESERVATION_TIME,
            "party_size": 2,
        },
    )

    print("\nReservation result:")
    print(result)

    assert result is not None
    assert not result.is_error

    RESERVATION_ID = result.data.id


def test_get_reservation():
    result = call_tool(
        "getReservation",
        {
            "id": RESERVATION_ID,
        },
    )

    print("\nGet reservation result:")
    print(result)

    assert result is not None
    assert not result.is_error

def test_create_order():
    global ORDER_ID

    result = call_tool(
        "createOrder",
        {
            "customer_id": CUSTOMER_ID,
            "dining_table_id": 2,
            "reservation_id": RESERVATION_ID,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 2,
                }
            ],
        },
    )

    print("\nOrder result:")
    print(result)

    assert result is not None
    assert not result.is_error

    ORDER_ID = result.data.id
    assert result.data.total_cents == 50000

def test_get_order():
    result = call_tool(
        "getOrder",
        {
            "id": ORDER_ID,
        },
    )

    print("\nGet order result:")
    print(result)

    assert result is not None
    assert not result.is_error
    assert result.data.id == ORDER_ID
    assert result.data.total_cents == 50000

def test_order_status_transitions():
    for status in ["PREPARING", "READY", "COMPLETED"]:
        result = call_tool(
            "updateOrderStatus",
            {
                "id": ORDER_ID,
                "status": status,
            },
        )

        print(f"\nStatus {status}:")
        print(result)

        assert result is not None
        assert not result.is_error
        assert result.data.status == status

def test_customer_order_history():
    result = call_tool(
        "listCustomerOrders",
        {
            "id": CUSTOMER_ID,
        },
    )

    print("\nCustomer order history:")
    print(result)

    assert result is not None
    assert not result.is_error
    assert len(result.data) >= 1
    assert any(order.id == ORDER_ID for order in result.data)