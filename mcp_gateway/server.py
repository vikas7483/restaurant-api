import time

import httpx2
import yaml
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import OpenAPIProvider
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from mcp_gateway.config import OPENAPI_FILE, API_BASE_URL, MCP_HOST, MCP_PORT


# Load OpenAPI specification at startup
try:
    with open(OPENAPI_FILE, "r", encoding="utf-8") as file:
        openapi_spec = yaml.safe_load(file)

    if not isinstance(openapi_spec, dict):
        raise ValueError("OpenAPI specification must be a YAML object.")

except FileNotFoundError:
    raise RuntimeError(
        f"OpenAPI specification not found: {OPENAPI_FILE}"
    )
except yaml.YAMLError as exc:
    raise RuntimeError(
        f"Invalid OpenAPI YAML: {exc}"
    ) from exc
except Exception as exc:
    raise RuntimeError(
        f"Failed to load OpenAPI specification '{OPENAPI_FILE}': {exc}"
    ) from exc


print(f"OpenAPI loaded: {bool(openapi_spec)}")


# HTTP logging hooks
async def log_request(request):
    request.extensions["gateway_start_time"] = time.perf_counter()

    print(
        f"[MCP->REST] {request.method} {request.url.path}"
    )


async def log_response(response):
    start_time = response.request.extensions.get(
        "gateway_start_time"
    )

    elapsed_ms = 0
    if start_time is not None:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(
        f"[MCP->REST] {response.request.method} "
        f"{response.request.url.path} "
        f"-> {response.status_code} "
        f"({elapsed_ms:.1f} ms)"
    )


# HTTP client used for MCP -> REST forwarding
http_client = httpx2.AsyncClient(
    base_url=API_BASE_URL,
    event_hooks={
        "request": [log_request],
        "response": [log_response],
    },
)


# Generic OpenAPI -> MCP provider
provider = OpenAPIProvider(
    openapi_spec,
    client=http_client,
)


mcp = FastMCP(
    name="OpenAPI MCP Gateway",
    providers=[provider],
)


# Serve the exact OpenAPI file used by the gateway
@mcp.custom_route("/openapi.yaml", methods=["GET"])
async def openapi_yaml(request: Request):
    with open(OPENAPI_FILE, "rb") as file:
        content = file.read()

    return Response(
        content=content,
        media_type="text/yaml",
    )


# Swagger UI
@mcp.custom_route("/docs", methods=["GET"])
async def swagger_docs(request: Request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenAPI MCP Gateway - Swagger UI</title>
        <link rel="stylesheet"
              href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>

        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js">
        </script>

        <script>
            window.onload = () => {
                SwaggerUIBundle({
                    url: "/openapi.yaml",
                    dom_id: "#swagger-ui"
                });
            };
        </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=MCP_HOST,
        port=MCP_PORT,
    )