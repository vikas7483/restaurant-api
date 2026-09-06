from flask import Flask, request

from src.handlers import (
    create_customer,
    create_order,
    create_reservation,
    get_menu_item,
    get_order,
    get_reservation,
    list_customer_orders,
    list_dining_tables,
    list_menu,
    update_order_status,
)

app = Flask(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.get("/menu")
def get_menu():
    return list_menu(), 200


@app.get("/menu/<int:item_id>")
def get_menu_item_route(item_id):
    item = get_menu_item(item_id)

    if item is None:
        return {"error": "Menu item not found"}, 404

    return item, 200


@app.post("/customers")
def create_customer_route():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "name" not in data or "email" not in data:
        return {"error": "name and email are required"}, 400

    try:
        customer = create_customer(data)
        return customer, 201

    except Exception as error:
        if "UNIQUE constraint failed: customers.email" in str(error):
            return {"error": "Customer email already exists"}, 409

        return {"error": "Could not create customer"}, 500


@app.get("/tables")
def get_dining_tables():
    return list_dining_tables(), 200


@app.post("/reservations")
def create_reservation_route():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    required_fields = [
        "customer_id",
        "dining_table_id",
        "reservation_time",
        "party_size",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return {
            "error": "Missing required fields",
            "fields": missing_fields,
        }, 400

    try:
        reservation, error = create_reservation(data)

        if error in {
            "Customer not found",
            "Dining table not found",
        }:
            return {"error": error}, 404

        if error == "Dining table is inactive":
            return {"error": error}, 409

        if error in {
            "party_size must be greater than 0",
            "party_size exceeds table capacity",
        }:
            return {"error": error}, 400

        if error == "Dining table is already reserved for this time":
            return {"error": error}, 409

        return reservation, 201

    except Exception:
        return {"error": "Could not create reservation"}, 500


@app.get("/reservations/<int:reservation_id>")
def get_reservation_route(reservation_id):
    reservation = get_reservation(reservation_id)

    if reservation is None:
        return {"error": "Reservation not found"}, 404

    return reservation, 200


@app.post("/orders")
def create_order_route():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "items" not in data:
        return {"error": "items are required"}, 400

    try:
        order, error = create_order(data)

        if error in {
            "Customer not found",
            "Dining table not found",
            "Reservation not found",
            "Menu item not found",
        }:
            return {"error": error}, 404

        if error in {
            "Order must contain at least one item",
            "quantity must be greater than 0",
        }:
            return {"error": error}, 400

        if error == "Menu item is unavailable":
            return {"error": error}, 409

        return order, 201

    except Exception:
        return {"error": "Could not create order"}, 500


@app.get("/orders/<int:order_id>")
def get_order_route(order_id):
    order = get_order(order_id)

    if order is None:
        return {"error": "Order not found"}, 404

    return order, 200


@app.patch("/orders/<int:order_id>/status")
def update_order_status_route(order_id):
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "status" not in data:
        return {"error": "status is required"}, 400

    try:
        order, error = update_order_status(
            order_id,
            data["status"],
        )

        if error == "Order not found":
            return {"error": error}, 404

        if error == "Invalid order status":
            return {"error": error}, 400

        if error and error.startswith("Cannot change order status"):
            return {"error": error}, 409

        return order, 200

    except Exception:
        return {"error": "Could not update order status"}, 500


@app.get("/customers/<int:customer_id>/orders")
def list_customer_orders_route(customer_id):
    orders, error = list_customer_orders(customer_id)

    if error == "Customer not found":
        return {"error": error}, 404

    return orders, 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )