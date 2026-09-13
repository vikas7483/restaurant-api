import os

OPENAPI_FILE = os.getenv("OPENAPI_FILE", "openapi.yaml")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))