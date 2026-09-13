import asyncio
import time

import httpx2
import yaml
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.providers.openapi import OpenAPIProvider


MCP_URL = "http://127.0.0.1:8000/mcp"


def call_tool(name, arguments):
    async def run():
        async with Client(MCP_URL) as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(run())


def test_invalid_tool_arguments():
    try:
        call_tool("getMenuItem", {})
        assert False, "Expected invalid arguments to fail"
    except ToolError as exc:
        error = str(exc).lower()
        assert "error calling tool" in error
        assert "404" in error


def test_backend_business_error_visible():
    try:
        call_tool("getMenuItem", {"id": 999999})
        assert False, "Expected missing menu item to fail"
    except ToolError as exc:
        assert "404" in str(exc) or "not found" in str(exc).lower()


def test_duplicate_customer_email_visible():
    email = f"duplicate_failure_test_{int(time.time())}@example.com"

    first = call_tool(
        "createCustomer",
        {"name": "Failure Test", "email": email},
    )

    assert not first.is_error

    try:
        call_tool(
            "createCustomer",
            {"name": "Failure Test 2", "email": email},
        )
        assert False, "Expected duplicate email to fail"
    except ToolError as exc:
        assert "409" in str(exc) or "already" in str(exc).lower()


def test_reservation_oversized_party_visible():
    try:
        call_tool(
            "createReservation",
            {
                "customer_id": 1,
                "dining_table_id": 2,
                "reservation_time": "2026-09-20T19:00:00",
                "party_size": 5,
            },
        )
        assert False, "Expected oversized party to fail"
    except ToolError as exc:
        error = str(exc)
        assert "400" in error
        assert "party_size exceeds table capacity" in error


def test_duplicate_reservation_visible():
    reservation_data = {
        "customer_id": 1,
        "dining_table_id": 2,
       "reservation_time": f"2035-01-15T19:{int(time.time()) % 60:02d}:00",
        "party_size": 2,
    }

    first = call_tool("createReservation", reservation_data)
    assert not first.is_error

    try:
        call_tool("createReservation", reservation_data)
        assert False, "Expected duplicate reservation to fail"
    except ToolError as exc:
        error = str(exc)
        assert "409" in error
        assert "already reserved" in error


def test_backend_down_fails_clearly():
    with open("openapi.yaml", "r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)

    async def run():
        client_http = httpx2.AsyncClient(
            base_url="http://127.0.0.1:5999",
            timeout=2.0,
        )

        provider = OpenAPIProvider(
            spec,
            client=client_http,
        )

        test_mcp = FastMCP(
            name="Backend Down Test",
            providers=[provider],
        )

        async with Client(test_mcp) as client:
            try:
                await client.call_tool("listMenu", {})
                return None
            except Exception as exc:
                return str(exc)

    start = time.time()
    error = asyncio.run(run())
    elapsed = time.time() - start

    assert error is not None
    assert elapsed < 5
    assert (
        "connect" in error.lower()
        or "connection" in error.lower()
        or "request error" in error.lower()
    )


def test_order_invalid_status_transition_visible():
    result = call_tool(
        "createOrder",
        {
            "customer_id": 1,
            "dining_table_id": 3,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert not result.is_error
    order_id = result.data.id

    # NEW -> PREPARING
    result = call_tool(
        "updateOrderStatus",
        {
            "id": order_id,
            "status": "PREPARING",
        },
    )

    assert not result.is_error

    # PREPARING -> COMPLETED is invalid
    try:
        call_tool(
            "updateOrderStatus",
            {
                "id": order_id,
                "status": "COMPLETED",
            },
        )
        assert False, "Expected invalid status transition to fail"
    except ToolError as exc:
        error = str(exc)
        assert "409" in error