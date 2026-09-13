import asyncio
import yaml
from fastmcp import Client

MCP_URL = "http://127.0.0.1:8000/mcp"

EXPECTED_TOOLS = [
    "listMenu",
    "getMenuItem",
    "createCustomer",
    "listDiningTables",
    "createReservation",
    "getReservation",
    "createOrder",
    "getOrder",
    "updateOrderStatus",
    "listCustomerOrders",
]


def test_discovery():
    async def run():
        async with Client(MCP_URL) as client:
            return await client.list_tools()

    tools = asyncio.run(run())
    names = [tool.name for tool in tools]

    print("\nDiscovered tools:")
    for tool in tools:
        print(f"{tool.name}: {tool.input_schema}")

    assert sorted(names) == sorted(EXPECTED_TOOLS)


def test_openapi_has_expected_operations():
    with open("openapi.yaml", "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    operation_ids = []

    for path in spec["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operation_ids.append(operation["operationId"])

    assert sorted(operation_ids) == sorted(EXPECTED_TOOLS)