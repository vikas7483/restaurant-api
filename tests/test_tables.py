import requests

from harness.contract import load_openapi, validate_response


BASE_URL = "http://127.0.0.1:5000"


def test_list_dining_tables_contract():
    openapi = load_openapi()

    response = requests.get(f"{BASE_URL}/tables")

    assert response.status_code == 200
    validate_response(openapi, response)

    tables = response.json()

    assert len(tables) >= 1
    assert "id" in tables[0]
    assert "label" in tables[0]
    assert "seats" in tables[0]
    assert "active" in tables[0]