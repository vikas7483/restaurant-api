#!/usr/bin/env bash

set -e

echo "========================================"
echo " Restaurant API Test Harness"
echo "========================================"

echo
echo "[1/4] Resetting database..."
python harness/reset_db.py

echo
echo "[2/4] Validating OpenAPI..."
python harness/validate_openapi.py

echo
echo "[3/4] Starting Flask API..."
python -m src.app > flask.log 2>&1 &
SERVER_PID=$!

cleanup() {
    kill $SERVER_PID 2>/dev/null || true
    echo
    echo "Flask API stopped."
}

trap cleanup EXIT

echo "Waiting for API..."

for i in {1..20}; do
    if curl -s http://127.0.0.1:5000/menu > /dev/null; then
        echo "API startup: PASS"
        break
    fi

    sleep 1
done

if ! curl -s http://127.0.0.1:5000/menu > /dev/null; then
    echo "API startup: FAIL"
    cat flask.log
    exit 1
fi

echo
echo "[4/4] Running tests..."
python -m pytest -v

echo
echo "========================================"
echo " TEST RESULT: PASS"
echo "========================================"