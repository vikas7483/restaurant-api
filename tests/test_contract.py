import requests

from harness.contract import load_openapi, validate_response


def test_harness_rejects_invalid_response():
    response = requests.get("http://127.0.0.1:5000/menu")

    response._content = b'{"wrong": "response"}'
    response.headers["Content-Type"] = "application/json"

    openapi = load_openapi()

    try:
        validate_response(openapi, response)
    except AssertionError as exc:
        assert "OpenAPI response validation failed" in str(exc)
    else:
        raise AssertionError(
            "Harness accepted an intentionally invalid response"
        )

def test_harness_rejects_invalid_status_code():
    response = requests.get("http://127.0.0.1:5000/menu")

    response.status_code = 418

    openapi = load_openapi()

    try:
        validate_response(openapi, response)
    except AssertionError as exc:
        assert "OpenAPI response validation failed" in str(exc)
    else:
        raise AssertionError(
            "Harness accepted an intentionally invalid status code"
        )