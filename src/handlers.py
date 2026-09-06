from src.db import get_db_connection


def list_menu():
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                menu_items.id,
                menu_items.name,
                menu_items.description,
                menu_items.price_cents,
                menu_items.available,
                menu_categories.id AS category_id,
                menu_categories.name AS category_name
            FROM menu_items
            JOIN menu_categories
                ON menu_items.category_id = menu_categories.id
            ORDER BY
                menu_categories.sort_order,
                menu_items.id
            """
        ).fetchall()

        return [
            {
                "id": row["id"],
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "name": row["name"],
                "description": row["description"],
                "price_cents": row["price_cents"],
                "available": bool(row["available"]),
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_menu_item(item_id):
    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT
                menu_items.id,
                menu_items.name,
                menu_items.description,
                menu_items.price_cents,
                menu_items.available,
                menu_categories.id AS category_id,
                menu_categories.name AS category_name
            FROM menu_items
            JOIN menu_categories
                ON menu_items.category_id = menu_categories.id
            WHERE menu_items.id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "category_id": row["category_id"],
            "category_name": row["category_name"],
            "name": row["name"],
            "description": row["description"],
            "price_cents": row["price_cents"],
            "available": bool(row["available"]),
        }

    finally:
        connection.close()


def create_customer(data):
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO customers (name, email, phone)
            VALUES (?, ?, ?)
            """,
            (
                data["name"],
                data["email"],
                data.get("phone"),
            ),
        )

        customer_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT id, name, email, phone
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        ).fetchone()

        connection.commit()

        return dict(row)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def list_dining_tables():
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                label,
                seats,
                active
            FROM dining_tables
            WHERE active = 1
            ORDER BY id
            """
        ).fetchall()

        return [
            {
                "id": row["id"],
                "label": row["label"],
                "seats": row["seats"],
                "active": bool(row["active"]),
            }
            for row in rows
        ]

    finally:
        connection.close()


def create_reservation(data):
    connection = get_db_connection()

    try:
        customer = connection.execute(
            """
            SELECT id
            FROM customers
            WHERE id = ?
            """,
            (data["customer_id"],),
        ).fetchone()

        if customer is None:
            return None, "Customer not found"

        table = connection.execute(
            """
            SELECT id, seats, active
            FROM dining_tables
            WHERE id = ?
            """,
            (data["dining_table_id"],),
        ).fetchone()

        if table is None:
            return None, "Dining table not found"

        if not table["active"]:
            return None, "Dining table is inactive"

        party_size = data["party_size"]

        if party_size <= 0:
            return None, "party_size must be greater than 0"

        if party_size > table["seats"]:
            return None, "party_size exceeds table capacity"

        existing = connection.execute(
            """
            SELECT id
            FROM reservations
            WHERE dining_table_id = ?
              AND reservation_time = ?
              AND status = 'ACTIVE'
            """,
            (
                data["dining_table_id"],
                data["reservation_time"],
            ),
        ).fetchone()

        if existing is not None:
            return None, "Dining table is already reserved for this time"

        cursor = connection.execute(
            """
            INSERT INTO reservations (
                customer_id,
                dining_table_id,
                reservation_time,
                party_size,
                status
            )
            VALUES (?, ?, ?, ?, 'ACTIVE')
            """,
            (
                data["customer_id"],
                data["dining_table_id"],
                data["reservation_time"],
                party_size,
            ),
        )

        reservation_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT
                id,
                customer_id,
                dining_table_id,
                reservation_time,
                party_size,
                status
            FROM reservations
            WHERE id = ?
            """,
            (reservation_id,),
        ).fetchone()

        connection.commit()

        return dict(row), None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_reservation(reservation_id):
    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                customer_id,
                dining_table_id,
                reservation_time,
                party_size,
                status
            FROM reservations
            WHERE id = ?
            """,
            (reservation_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def create_order(data):
    connection = get_db_connection()

    try:
        if data.get("customer_id") is not None:
            customer = connection.execute(
                """
                SELECT id
                FROM customers
                WHERE id = ?
                """,
                (data["customer_id"],),
            ).fetchone()

            if customer is None:
                return None, "Customer not found"

        if data.get("dining_table_id") is not None:
            table = connection.execute(
                """
                SELECT id
                FROM dining_tables
                WHERE id = ?
                  AND active = 1
                """,
                (data["dining_table_id"],),
            ).fetchone()

            if table is None:
                return None, "Dining table not found"

        if data.get("reservation_id") is not None:
            reservation = connection.execute(
                """
                SELECT id
                FROM reservations
                WHERE id = ?
                """,
                (data["reservation_id"],),
            ).fetchone()

            if reservation is None:
                return None, "Reservation not found"

        items = data.get("items", [])

        if not items:
            return None, "Order must contain at least one item"

        order_items = []
        total_cents = 0

        for item in items:
            menu_item_id = item["menu_item_id"]
            quantity = item["quantity"]

            if quantity <= 0:
                return None, "quantity must be greater than 0"

            menu_item = connection.execute(
                """
                SELECT
                    id,
                    price_cents,
                    available
                FROM menu_items
                WHERE id = ?
                """,
                (menu_item_id,),
            ).fetchone()

            if menu_item is None:
                return None, "Menu item not found"

            if not menu_item["available"]:
                return None, "Menu item is unavailable"

            unit_price_cents = menu_item["price_cents"]
            line_total_cents = quantity * unit_price_cents

            order_items.append(
                (
                    menu_item_id,
                    quantity,
                    unit_price_cents,
                    line_total_cents,
                )
            )

            total_cents += line_total_cents

        cursor = connection.execute(
            """
            INSERT INTO orders (
                customer_id,
                dining_table_id,
                reservation_id,
                status,
                total_cents,
                created_at
            )
            VALUES (?, ?, ?, 'NEW', ?, strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
            """,
            (
                data.get("customer_id"),
                data.get("dining_table_id"),
                data.get("reservation_id"),
                total_cents,
            ),
        )

        order_id = cursor.lastrowid

        for (
            menu_item_id,
            quantity,
            unit_price_cents,
            line_total_cents,
        ) in order_items:
            connection.execute(
                """
                INSERT INTO order_items (
                    order_id,
                    menu_item_id,
                    quantity,
                    unit_price_cents,
                    line_total_cents
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    menu_item_id,
                    quantity,
                    unit_price_cents,
                    line_total_cents,
                ),
            )

        connection.commit()

        return {
            "id": order_id,
            "customer_id": data.get("customer_id"),
            "dining_table_id": data.get("dining_table_id"),
            "reservation_id": data.get("reservation_id"),
            "status": "NEW",
            "total_cents": total_cents,
        }, None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_order(order_id):
    connection = get_db_connection()

    try:
        order = connection.execute(
            """
            SELECT
                id,
                customer_id,
                dining_table_id,
                reservation_id,
                status,
                total_cents,
                created_at
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            return None

        item_rows = connection.execute(
            """
            SELECT
                order_items.id,
                order_items.menu_item_id,
                menu_items.name AS menu_item_name,
                order_items.quantity,
                order_items.unit_price_cents,
                order_items.line_total_cents
            FROM order_items
            JOIN menu_items
                ON order_items.menu_item_id = menu_items.id
            WHERE order_items.order_id = ?
            ORDER BY order_items.id
            """,
            (order_id,),
        ).fetchall()

        result = dict(order)

        result["items"] = [
            {
                "id": row["id"],
                "menu_item_id": row["menu_item_id"],
                "menu_item_name": row["menu_item_name"],
                "quantity": row["quantity"],
                "unit_price_cents": row["unit_price_cents"],
                "line_total_cents": row["line_total_cents"],
            }
            for row in item_rows
        ]

        return result

    finally:
        connection.close()


def update_order_status(order_id, new_status):
    allowed_statuses = {
        "NEW",
        "PREPARING",
        "READY",
        "COMPLETED",
        "CANCELLED",
    }

    connection = get_db_connection()

    try:
        order = connection.execute(
            """
            SELECT id, status
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            return None, "Order not found"

        if new_status not in allowed_statuses:
            return None, "Invalid order status"

        current_status = order["status"]

        allowed_transitions = {
            "NEW": {"PREPARING", "CANCELLED"},
            "PREPARING": {"READY"},
            "READY": {"COMPLETED"},
            "COMPLETED": set(),
            "CANCELLED": set(),
        }

        if new_status not in allowed_transitions[current_status]:
            return None, (
                f"Cannot change order status from "
                f"{current_status} to {new_status}"
            )

        connection.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            """,
            (new_status, order_id),
        )

        connection.commit()

        updated_order = connection.execute(
            """
            SELECT
                id,
                customer_id,
                dining_table_id,
                reservation_id,
                status,
                total_cents,
                created_at
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        return dict(updated_order), None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def list_customer_orders(customer_id):
    connection = get_db_connection()

    try:
        customer = connection.execute(
            """
            SELECT id
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        ).fetchone()

        if customer is None:
            return None, "Customer not found"

        orders = connection.execute(
            """
            SELECT
                id,
                customer_id,
                dining_table_id,
                reservation_id,
                status,
                total_cents,
                created_at
            FROM orders
            WHERE customer_id = ?
            ORDER BY id
            """,
            (customer_id,),
        ).fetchall()

        return [dict(order) for order in orders], None

    finally:
        connection.close()