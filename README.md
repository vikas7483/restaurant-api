# Restaurant API + OpenAPI Test Harness

## Overview

This project implements a Restaurant HTTP API backed by SQLite and validated against an OpenAPI contract.

The project also contains a reusable test Harness that:

- Validates the OpenAPI specification before the application starts.
- Creates a clean SQLite database from `schema.sql` and `seed.sql`.
- Starts the Flask API in a predictable local HTTP test mode.
- Runs automated HTTP contract and business-rule tests.
- Reports a clear PASS/FAIL result.
- Stops the Flask API after the test run.

## Technology

- Python 3
- Flask
- SQLite
- OpenAPI
- openapi-core
- pytest
- requests

## Project Structure

```text
restaurant-api/
|-- openapi.yaml
|-- schema.sql
|-- seed.sql
|-- src/
|   |-- app.py
|   |-- db.py
|   `-- handlers.py
|-- harness/
|   |-- validate_openapi.py
|   |-- reset_db.py
|   `-- contract.py
|-- tests/
|   |-- test_customers.py
|   |-- test_menu.py
|   |-- test_orders.py
|   |-- test_reservations.py
|   `-- test_tables.py
|-- requirements.txt
|-- run-tests.ps1
|-- run-tests.sh
`-- README.md