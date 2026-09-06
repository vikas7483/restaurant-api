import requests

from harness.contract import load_openapi, validate_response


BASE_URL = "http://127.0.0.1:5000"


def test_create_reservation_contract():
    openapi = load_openapi()

    response = requests.post(
        f"{BASE_URL}/reservations",
        json={
            "customer_id": 1,
            "dining_table_id": 3,
            "reservation_time": "2026-09-07T19:00:00",
            "party_size": 2,
        },
    )

    assert response.status_code == 201
    validate_response(openapi, response)


def test_get_reservation_contract():
    openapi = load_openapi()

    create_response = requests.post(
        f"{BASE_URL}/reservations",
        json={
            "customer_id": 1,
            "dining_table_id": 3,
            "reservation_time": "2026-09-08T19:00:00",
            "party_size": 2,
        },
    )

    assert create_response.status_code == 201

    reservation_id = create_response.json()["id"]

    response = requests.get(
        f"{BASE_URL}/reservations/{reservation_id}"
    )

    assert response.status_code == 200
    validate_response(openapi, response)


def test_reservation_rejects_exceeding_table_capacity():
    response = requests.post(
        f"{BASE_URL}/reservations",
        json={
            "customer_id": 1,
            "dining_table_id": 2,
            "reservation_time": "2026-09-09T19:00:00",
            "party_size": 5,
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "party_size exceeds table capacity"


def test_reservation_rejects_duplicate_table_time():
    reservation_data = {
        "customer_id": 1,
        "dining_table_id": 2,
        "reservation_time": "2026-09-10T19:00:00",
        "party_size": 2,
    }

    first_response = requests.post(
        f"{BASE_URL}/reservations",
        json=reservation_data,
    )

    assert first_response.status_code == 201

    second_response = requests.post(
        f"{BASE_URL}/reservations",
        json=reservation_data,
    )

    assert second_response.status_code == 409
    assert second_response.json()["error"] == (
        "Dining table is already reserved for this time"
    )
def test_reservation_rejects_invalid_party_size():
    response = requests.post(
        f"{BASE_URL}/reservations",
        json={
            "customer_id": 1,
            "dining_table_id": 2,
            "reservation_time": "2026-09-11T19:00:00",
            "party_size": 0,
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "party_size must be greater than 0"