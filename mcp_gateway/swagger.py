from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from mcp_gateway.config import OPENAPI_FILE


def register_swagger(app: Flask):
    swaggerui_blueprint = get_swaggerui_blueprint(
        "/docs",
        f"/openapi.yaml",
        config={
            "app_name": "OpenAPI MCP Gateway",
            "deepLinking": True,
        },
    )

    app.register_blueprint(swaggerui_blueprint)

    @app.get("/openapi.yaml")
    def openapi_yaml():
        with open(OPENAPI_FILE, "r", encoding="utf-8") as file:
            return file.read(), 200, {
                "Content-Type": "text/yaml; charset=utf-8"
            }