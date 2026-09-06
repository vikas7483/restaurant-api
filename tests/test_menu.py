import requests

from harness.contract import load_openapi, validate_response


BASE_URL = "http://127.0.0.1:5000"


def test_list_menu_contract():
    openapi = load_openapi()

    response = requests.get(f"{BASE_URL}/menu")

    assert response.status_code == 200

    validate_response(openapi, response)


def test_get_menu_item_contract():
    openapi = load_openapi()

    response = requests.get(f"{BASE_URL}/menu/1")

    assert response.status_code == 200

    validate_response(openapi, response)


def test_get_missing_menu_item_returns_404():
    response = requests.get(f"{BASE_URL}/menu/999999")

    assert response.status_code == 404
    assert response.json()["error"] == "Menu item not found"