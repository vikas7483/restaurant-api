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


def get_operation_id(response):
    method = response.request.method.lower()
    actual_path = response.request.path_url.split("?", 1)[0]

    with open(OPENAPI_PATH, "r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)

    paths = spec.get("paths", {})

    # First try an exact path match.
    operation = paths.get(actual_path, {}).get(method)

    if operation:
        return operation.get(
            "operationId",
            f"{method.upper()} {actual_path}"
        )

    # Match OpenAPI path templates such as:
    # /orders/{id}
    # /customers/{id}/orders
    for template, path_item in paths.items():
        template_parts = template.strip("/").split("/")
        actual_parts = actual_path.strip("/").split("/")

        if len(template_parts) != len(actual_parts):
            continue

        matches = True

        for template_part, actual_part in zip(
            template_parts,
            actual_parts
        ):
            # {id}, {customerId}, etc. are path parameters.
            if (
                template_part.startswith("{")
                and template_part.endswith("}")
            ):
                continue

            if template_part != actual_part:
                matches = False
                break

        if matches:
            operation = path_item.get(method)

            if operation:
                return operation.get(
                    "operationId",
                    f"{method.upper()} {actual_path}"
                )

    return f"{method.upper()} {actual_path}"


def validate_response(openapi, response):
    request = RequestsOpenAPIRequest(response.request)
    openapi_response = RequestsOpenAPIResponse(response)

    result = openapi.unmarshal_response(
        request,
        openapi_response
    )

    if result.errors:
        operation_id = get_operation_id(response)

        raise AssertionError(
            "OpenAPI response validation failed\n"
            f"operationId: {operation_id}\n"
            f"method: {response.request.method}\n"
            f"path: {response.request.path_url}\n"
            f"errors: {result.errors}"
        )

    return result