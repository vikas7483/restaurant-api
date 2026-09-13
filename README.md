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

The OpenAPI specification in `openapi.yaml` defines the HTTP interface used by the API and tests.

---

## Technology

- Python 3
- Flask
- SQLite
- OpenAPI
- openapi-core
- pytest
- requests
- Git

---

## Project Structure
restaurant-api/
│
├── openapi.yaml
├── schema.sql
├── seed.sql
│
├── src/
│   ├── app.py
│   ├── db.py
│   └── handlers.py
│
├── harness/
│   ├── validate_openapi.py
│   ├── reset_db.py
│   └── contract.py
│
├── mcp_gateway/
│   ├── server.py
│   ├── config.py
│   └── swagger.py
│
├── tests/
│   ├── test_customers.py
│   ├── test_menu.py
│   ├── test_orders.py
│   ├── test_reservations.py
│   └── test_tables.py
│
├── tests_mcp/
│   ├── test_discovery.py
│   ├── test_workflow.py
│   ├── test_failures.py
│   └── test_cross_fresher.py
│
├── requirements.txt
├── run-tests.ps1
├── run-tests.sh
├── run-mcp.sh
├── run-tests-mcp.sh
└── README.md

Setup
1. Open the project directory

Open PowerShell or another terminal and move to the project directory.

Example:

cd D:\restaurant-api
2. Create a virtual environment

If the virtual environment does not already exist:

python -m venv venv
3. Activate the virtual environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1

Windows Command Prompt:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate
4. Install dependencies
python -m pip install -r requirements.txt
Database

The application uses SQLite.

The database file is:

restaurant.db

The database is disposable and can be recreated at any time.

The database structure is defined in:

schema.sql

Initial data is defined in:

seed.sql
Reset the database

Run:

python -m harness.reset_db

Expected output:

Database reset: PASS

The reset operation:

Deletes the existing restaurant.db.
Creates a new SQLite database.
Applies schema.sql.
Applies seed.sql.
Enables SQLite foreign-key enforcement.

This makes test runs deterministic.

Running the API

Start the Flask application with:

python -m src.app

The API runs locally at:

http://127.0.0.1:5000

Keep this terminal running while manually inspecting the API.

To stop the API:

Ctrl+C
Inspecting the API

The API can be inspected using:

Browser
curl
PowerShell
Postman
Any HTTP client

For example, after starting the API:

curl http://127.0.0.1:5000/menu

The OpenAPI contract is available in:

openapi.yaml
Required API Operations
Method	Path	Operation
GET	/menu	List menu
GET	/menu/{id}	Get menu item
POST	/customers	Create customer
GET	/tables	List dining tables
POST	/reservations	Create reservation
GET	/reservations/{id}	Get reservation
POST	/orders	Create order
GET	/orders/{id}	Get order
PATCH	/orders/{id}/status	Update order status
GET	/customers/{id}/orders	List customer orders
Running the Tests
Validate OpenAPI

Validate the OpenAPI specification with:

python -m harness.validate_openapi

Expected output:

OpenAPI validation: PASS

The OpenAPI specification must be valid before the API test suite is considered ready to run.

Run pytest directly

If the API is already running:

python -m pytest -v

The tests exercise the HTTP interface and validate responses against the OpenAPI contract.

One-Command Test Harness

The recommended way to run the complete test harness on Windows is:

.\run-tests.ps1

The harness performs these steps:

1. Reset database
2. Validate OpenAPI
3. Start Flask API
4. Wait for API startup
5. Run HTTP tests
6. Stop Flask API
7. Report PASS or FAIL

A successful run ends with:

========================================
 TEST RESULT: PASS
========================================

The Bash runner can be used on Linux/macOS:

./run-tests.sh
Test Coverage

The automated tests cover the required Restaurant API behavior.

Menu
List menu items.
Get a menu item.
Handle a missing menu item.
Customers
Create a customer.
Reject duplicate customer email addresses.
Dining Tables
List active dining tables.
Reservations
Create a reservation.
Reject invalid party sizes.
Reject reservations exceeding table capacity.
Reject duplicate reservations for the same table and reservation time.
Get a reservation.
Orders
Create an order.
Validate menu item availability.
Calculate prices using database menu prices.
Calculate the server-side order total.
Reject invalid quantities.
Get an order with its order items.
Preserve historical item prices.
List orders belonging to a customer.
Order Status

Supported statuses:

NEW
PREPARING
READY
COMPLETED
CANCELLED

Valid transitions:

NEW -> PREPARING
NEW -> CANCELLED

PREPARING -> READY

READY -> COMPLETED

Invalid status transitions are rejected.

Business Rules

The Restaurant API enforces the following rules.

Menu Pricing

Order prices are taken from the SQLite database.

The client cannot choose or override the menu item price.

The order total is calculated by the server:

total = sum(quantity × database menu price)
Menu Availability

Unavailable menu items cannot be ordered.

Reservation Capacity

The reservation party size must:

party_size > 0

and:

party_size <= selected table seats
Duplicate Reservations

The same dining table cannot have two active reservations for the same reservation time.

Historical Order Prices

When an order is created, the menu price at that time is stored in order_items.

Changing a menu item's current price must not change the historical price of an existing order.

Order Status

Only valid state transitions are accepted.

NEW
 |
 +----> CANCELLED
 |
 v
PREPARING
 |
 v
READY
 |
 v
COMPLETED
Canonical Workflow

The main Restaurant workflow can be exercised through the HTTP API in this order:

Clean database
     |
     v
GET /menu
     |
     v
POST /customers
     |
     v
GET /tables
     |
     v
Choose a suitable table
     |
     v
POST /reservations
     |
     v
POST /orders
     |
     v
GET /orders/{id}
     |
     v
PATCH /orders/{id}/status
     |
     v
PATCH /orders/{id}/status
     |
     v
PATCH /orders/{id}/status
     |
     v
PATCH /orders/{id}/status
     |
     v
GET /customers/{id}/orders
     |
     v
Full Harness PASS

The normal order status workflow is:

NEW
 |
 v
PREPARING
 |
 v
READY
 |
 v
COMPLETED

An order may also be cancelled from:

NEW -> CANCELLED
Adding a New Endpoint

When adding a new endpoint, update the project in this order.

1. Update the OpenAPI contract

Add the endpoint to:

openapi.yaml

Define:

HTTP method
Path
Operation ID
Request parameters
Request body
Response status codes
Response schemas
Error responses where required

The OpenAPI contract describes the HTTP interface.

2. Update the Flask application

Add the corresponding route in:

src/app.py
3. Implement the endpoint behavior

Add or update the required application logic in:

src/handlers.py

Use the SQLite database layer in:

src/db.py
4. Add HTTP tests

Add tests under:

tests/

Tests should call the HTTP endpoint rather than directly testing handler functions.

5. Validate the OpenAPI specification

Run:

python -m harness.validate_openapi

Expected result:

OpenAPI validation: PASS
6. Run the complete test harness

Run:

.\run-tests.ps1

The endpoint should not be considered complete until the full test suite passes.

Harness Design

The Harness is separated from Restaurant-specific application logic.

The main Harness responsibilities are:

OpenAPI validation
       |
       v
Database reset
       |
       v
API startup
       |
       v
HTTP tests
       |
       v
OpenAPI response validation
       |
       v
PASS / FAIL

The Harness is intended to be reusable for another HTTP backend by replacing the API-specific:

OpenAPI specification
Database schema
Seed data
API tests

Restaurant-specific business rules belong to the application and its tests, not to the generic Harness.

HTTP Contract Validation

The Harness validates the real HTTP interface.

For each tested HTTP response, the Harness checks the response against the OpenAPI contract, including:

HTTP status code
Response structure
Response schema
Required fields
Field types

When contract validation fails, the test output reports the related operation ID and validation error.

This helps identify whether an endpoint is returning a response that does not match its declared API contract.

Clean Test Runs

Each complete test run is intended to start from a clean SQLite database.

To manually reset the database:

python -m harness.reset_db

To run the complete clean workflow:

.\run-tests.ps1

The test suite should be repeatable from a fresh database.

Running the complete harness again should produce the same expected test result.

Troubleshooting
Python command not found

Check the installed Python version:

python --version
Virtual environment is not active

Activate the environment:

.\venv\Scripts\Activate.ps1
Dependencies are missing

Install them with:

python -m pip install -r requirements.txt
OpenAPI validation fails

Run:

python -m harness.validate_openapi

Read the reported validation error and fix the OpenAPI contract before running the application tests.

API does not start

Start the API manually:

python -m src.app

Check the terminal output for the startup error.

Tests fail

Run the tests with verbose output:

python -m pytest -v

The output identifies the failing test.

For the complete clean workflow, run:

.\run-tests.ps1
Development Workflow

The project follows an OpenAPI-first development approach:

OpenAPI contract
       |
       v
HTTP implementation
       |
       v
Automated HTTP tests
       |
       v
OpenAPI contract validation

The goal is to verify the behavior of the real HTTP interface rather than only testing internal Python functions.

Expected Verification

Before considering the project complete, verify:

[ ] Dependencies installed
[ ] Database reset works
[ ] OpenAPI validation passes
[ ] API starts successfully
[ ] HTTP tests pass
[ ] Complete Windows test harness passes
[ ] Complete test harness can be repeated from a clean database
[ ] README explains setup
[ ] README explains database reset
[ ] README explains how to run the service
[ ] README explains how to run tests
[ ] README explains how to inspect the API
[ ] README explains how to add an endpoint

The recommended final verification command on Windows is:

.\run-tests.ps1

A successful project verification should finish with:

========================================
 TEST RESULT: PASS
========================================

After pasting it, save the file and run:

```powershell
.\run-tests.ps1


# Product 005 - Generic OpenAPI-to-MCP Gateway

Product 005 exposes the same OpenAPI contract through MCP.

Architecture:

OpenAPI -> MCP Discovery -> HTTP -> Product 004 API -> SQLite

The MCP gateway is generic and contains no restaurant-specific business logic.

## Product 005 Configuration

The gateway uses environment variables:

OPENAPI_FILE
API_BASE_URL
MCP_HOST
MCP_PORT

Defaults:

OPENAPI_FILE=openapi.yaml
API_BASE_URL=http://127.0.0.1:5000
MCP_HOST=127.0.0.1
MCP_PORT=8000

## Start the MCP Gateway

Start Product 004 first:

python -m src.app

Then start the gateway:

python -m mcp_gateway.server

MCP endpoint:

http://127.0.0.1:8000/mcp

Swagger UI:

http://127.0.0.1:8000/docs

OpenAPI:

http://127.0.0.1:8000/openapi.yaml

## Product 005 Tests

Run all MCP tests:

pytest tests_mcp -v

Or use:

./run-tests-mcp.sh

The tests cover:

- MCP discovery
- OpenAPI schema fidelity
- Menu and customer workflow
- Reservations
- Orders and server-side totals
- Order status transitions
- Customer order history
- Backend and business failures
- Backend-down handling
- Cross-Fresher configuration

## Expected MCP Tools

The gateway automatically derives these tools from OpenAPI operationId:

listMenu
getMenuItem
createCustomer
listDiningTables
createReservation
getReservation
createOrder
getOrder
updateOrderStatus
listCustomerOrders

No restaurant-specific MCP tools are handwritten.

## Cross-Fresher

To use another Fresher's Product 004 API, change configuration only:

$env:OPENAPI_FILE="path\to\peer\openapi.yaml"
$env:API_BASE_URL="http://127.0.0.1:5001"

No mcp_gateway source-code changes are required.

## Product 005 One-Command Scripts

Start gateway:

./run-mcp.sh

Run MCP tests:

./run-tests-mcp.sh