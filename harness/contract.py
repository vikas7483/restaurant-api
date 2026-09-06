from pathlib import Path

import yaml
from openapi_core import OpenAPI
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests.responses import RequestsOpenAPIResponse


ROOT_DIR = Path(__file__).resolve().parent.parent
OPENAPI_PATH = ROOT_DIR / "openapi.yaml"


def load_openapi():
    with open(OPENAPI_PATH, "r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)

    return OpenAPI.from_dict(spec)


def validate_response(openapi, response):
    request = RequestsOpenAPIRequest(response.request)
    openapi_response = RequestsOpenAPIResponse(response)

    result = openapi.unmarshal_response(
        request,
        openapi_response,
    )

    return result