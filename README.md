API + OpenAPI Test Harness

A reusable OpenAPI-first HTTP interface harness backed by SQLite, implemented with a canonical Restaurant API.

Product 005 extends the same OpenAPI contract with a generic OpenAPI-to-MCP gateway.

---

## Project Structure

```text
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
Product 004 — Restaurant OpenAPI + SQLite API
Overview

The Restaurant API is an OpenAPI-first Flask application backed by SQLite.

The openapi.yaml contract defines the HTTP interface.

openapi.yaml
     ↓
Flask REST API
     ↓
SQLite

The reusable harness validates the OpenAPI specification, resets the database, starts the API, and runs HTTP tests.

Technology
Python 3
Flask
SQLite
OpenAPI YAML
openapi-core
pytest
HTTP requests
Git
Setup

Create and activate a Python virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt
Database

The database is SQLite.

The database schema is defined in:

schema.sql

Initial seed data is defined in:

seed.sql

The harness resets the database before a test run so tests start from a clean state.

Run the Restaurant API

Start the Flask API:

python -m src.app

The API runs locally on:

http://127.0.0.1:5000
Required API Operations

The API implements these operations:

Operation ID	Method	Path
listMenu	GET	/menu
getMenuItem	GET	/menu/{id}
createCustomer	POST	/customers
listDiningTables	GET	/tables
createReservation	POST	/reservations
getReservation	GET	/reservations/{id}
createOrder	POST	/orders
getOrder	GET	/orders/{id}
updateOrderStatus	PATCH	/orders/{id}/status
listCustomerOrders	GET	/customers/{id}/orders
Restaurant Business Rules
Menu

Menu prices are owned by the server/database.

The client cannot choose the price used for an order.

Unavailable menu items cannot be ordered.

Orders

Order totals are calculated by the backend:

total = quantity × database menu price

Historical order item prices are preserved.

Customers

Customer email addresses must be unique.

Duplicate customer emails are rejected.

Reservations

The reservation party size must be greater than zero.

The party size cannot exceed the selected table capacity.

A dining table cannot have two active reservations at the same time.

Order Status

Valid statuses:

NEW
PREPARING
READY
COMPLETED
CANCELLED

Allowed transitions:

NEW → PREPARING
NEW → CANCELLED

PREPARING → READY

READY → COMPLETED

Invalid transitions return an error.

Product 004 Harness

The harness is reusable and contains no Restaurant-specific business logic.

It performs:

OpenAPI validation
SQLite database reset
API startup
HTTP testing
Request/response contract validation
Business-rule testing
PASS/FAIL reporting

Run the complete Product 004 test harness:

.\run-tests.ps1

Or:

./run-tests.sh

The database is reset before testing.

Product 004 Tests

The tests cover:

Menu operations
Customer creation
Duplicate customer email
Dining tables
Reservations
Oversized reservations
Duplicate reservations
Order creation
Server-side prices
Server-side totals
Order retrieval
Order status transitions
Customer order history
OpenAPI contract validation
Product 004 Canonical Workflow

The normal workflow is:

GET /menu
      ↓
POST /customers
      ↓
GET /tables
      ↓
POST /reservations
      ↓
POST /orders
      ↓
GET /orders/{id}
      ↓
PATCH /orders/{id}/status
      ↓
GET /customers/{id}/orders
Product 005 — Generic OpenAPI-to-MCP Gateway

Product 005 exposes the same OpenAPI contract through MCP.

The architecture is:

OpenAPI
   ↓
MCP Discovery
   ↓
MCP Tool Call
   ↓
HTTP
   ↓
Product 004 REST API
   ↓
SQLite

The gateway is generic.

It does not contain Restaurant-specific business logic.

Product 005 Configuration

The gateway is configured using environment variables.

OPENAPI_FILE
API_BASE_URL
MCP_HOST
MCP_PORT

Default values:

OPENAPI_FILE=openapi.yaml
API_BASE_URL=http://127.0.0.1:5000
MCP_HOST=127.0.0.1
MCP_PORT=8000
Start Product 005

First start the Product 004 API:

python -m src.app

Then start the MCP gateway in another terminal:

python -m mcp_gateway.server

The MCP endpoint is:

http://127.0.0.1:8000/mcp

Swagger UI:

http://127.0.0.1:8000/docs

OpenAPI:

http://127.0.0.1:8000/openapi.yaml
Product 005 MCP Tools

The MCP gateway automatically derives tools from the OpenAPI operationId values.

Expected tools:

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

No Restaurant-specific MCP tools are manually implemented.

The OpenAPI contract is the source of truth.

MCP Discovery

MCP clients can discover the tools using list_tools.

The discovery tests verify that the gateway exposes exactly the required operation IDs.

Run:

pytest tests_mcp\test_discovery.py -v
Product 005 Workflow Tests

The MCP workflow tests verify the Restaurant workflow through MCP instead of calling the REST API directly.

The workflow includes:

List menu
Create customer
List dining tables
Create reservation
Get reservation
Create order
Verify server-side total
Get order
Update order status
Read customer order history

Run:

pytest tests_mcp\test_workflow.py -v
Product 005 Failure Tests

The failure tests verify that upstream errors remain visible through the MCP gateway.

Covered failures include:

Invalid MCP arguments
Missing menu item
Duplicate customer email
Oversized reservation
Duplicate reservation
Invalid order status transition
Backend unavailable

Run:

pytest tests_mcp\test_failures.py -v

The gateway must not return fake success when the REST API fails.

Swagger UI

Swagger UI is available at:

http://127.0.0.1:8000/docs

Swagger uses the same:

openapi.yaml

served by the gateway.

The OpenAPI contract can also be viewed directly at:

http://127.0.0.1:8000/openapi.yaml
Product 005 Tests

Run all MCP tests:

pytest tests_mcp -v

Or:

./run-tests-mcp.sh

The Product 005 test suite covers:

MCP discovery
OpenAPI operation IDs
OpenAPI schema-derived inputs
Menu workflow
Customer workflow
Reservations
Orders
Server-side prices and totals
Order status transitions
Customer order history
Business errors
Backend-down handling
One-Command Scripts

Start the MCP gateway:

./run-mcp.sh

Run the MCP tests:

./run-tests-mcp.sh

Run the Product 004 harness:

./run-tests.sh

On Windows PowerShell:

.\run-tests.ps1
Generic Gateway Boundary

The MCP gateway is responsible for:

Loading OpenAPI
MCP tool discovery
MCP transport
HTTP forwarding
Generic error handling
Configuration
HTTP logging

The Product 004 backend remains responsible for:

Restaurant database
SQLite schema
Seed data
Restaurant handlers
Restaurant SQL
Menu prices
Order totals
Reservation rules
Order state machine

The gateway does not access SQLite directly.

Cross-Fresher Configuration

The gateway can point to another Fresher's Product 004 API using configuration only.

Example:

$env:OPENAPI_FILE="path\to\peer\openapi.yaml"
$env:API_BASE_URL="http://127.0.0.1:5001"

The gateway source code should not need to be changed.

The peer's Product 004 API must pass its own Product 004 tests before being used for cross-Fresher testing.

Development Workflow
Product 004
Update OpenAPI
      ↓
Update backend
      ↓
Reset database
      ↓
Run Product 004 tests
      ↓
PASS
Product 005
OpenAPI
   ↓
MCP Gateway
   ↓
MCP Discovery
   ↓
HTTP forwarding
   ↓
Product 004 API
   ↓
SQLite
Verification

Product 004 should be verified from a clean database:

.\run-tests.ps1

Product 005 should be verified with:

pytest tests_mcp -v

Discovery can be checked separately:

pytest tests_mcp\test_discovery.py -v

Workflow:

pytest tests_mcp\test_workflow.py -v

Failures:

pytest tests_mcp\test_failures.py -v
Important Design Rules
openapi.yaml is the source of truth.
MCP tool names come from OpenAPI operationId.
The gateway forwards MCP calls to the configured REST API.
The gateway does not contain Restaurant business logic.
The gateway does not directly access SQLite.
Product 004 remains the owner of Restaurant behavior.
No separate MCP schemas are manually maintained.
No Restaurant-specific MCP tools are handwritten.
Current Product Structure
Product 004
    OpenAPI
       ↓
    Flask REST API
       ↓
    SQLite
       ↓
    Product 004 Harness

Product 005
    Same OpenAPI
       ↓
    Generic MCP Gateway
       ↓
    MCP Tools
       ↓
    HTTP
       ↓
    Product 004 REST API
       ↓
    SQLite
Final Acceptance

The intended final flow is:

Approved OpenAPI Contract
          ↓
    Swagger UI
          ↓
    MCP Discovery
          ↓
      MCP Tools
          ↓
    HTTP Forwarding
          ↓
   Product 004 API
          ↓
       SQLite

The gateway is successful when the same OpenAPI contract drives both Swagger and MCP without adding Restaurant-specific logic to the gateway.