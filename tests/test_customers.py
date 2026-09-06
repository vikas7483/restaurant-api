import requests

from harness.contract import load_openapi, validate_response


BASE_URL = "http://127.0.0.1:5000"


def test_create_customer_contract():
    openapi = load_openapi()

    response = requests.post(
        f"{BASE_URL}/customers",
        json={
            "name": "Contract Test Customer",
            "email": "contract-test@example.com",
            "phone": "8888888888",
        },
    )

    assert response.status_code == 201
    validate_response(openapi, response)

    data = response.json()
    assert data["name"] == "Contract Test Customer"
    assert data["email"] == "contract-test@example.com"


def test_create_customer_rejects_duplicate_email():
    response = requests.post(
        f"{BASE_URL}/customers",
        json={
            "name": "Duplicate Customer",
            "email": "test@example.com",
            "phone": "7777777777",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "Customer email already exists"