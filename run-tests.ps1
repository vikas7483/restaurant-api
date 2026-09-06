$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host " Restaurant API Test Harness"
Write-Host "========================================"
Write-Host ""

Write-Host "[1/4] Resetting database..."
python -m harness.reset_db

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database reset: FAIL"
    exit 1
}

Write-Host ""
Write-Host "[2/4] Validating OpenAPI..."
python -m harness.validate_openapi

if ($LASTEXITCODE -ne 0) {
    Write-Host "OpenAPI validation: FAIL"
    exit 1
}

Write-Host ""
Write-Host "[3/4] Starting Flask API..."

$server = Start-Process `
    -FilePath "python" `
    -ArgumentList "-m src.app" `
    -PassThru `
    -WindowStyle Hidden

try {
    Write-Host "Waiting for API..."

    $ready = $false

    for ($i = 1; $i -le 30; $i++) {
        Start-Sleep -Seconds 1

        try {
            $response = Invoke-WebRequest `
                -Uri "http://127.0.0.1:5000/health" `
                -UseBasicParsing `
                -TimeoutSec 2

            if ($response.StatusCode -eq 200) {
                $ready = $true
                break
            }
        }
        catch {
            # API is not ready yet
        }
    }

    if (-not $ready) {
        Write-Host "API startup: FAIL"
        exit 1
    }

    Write-Host "API startup: PASS"

    Write-Host ""
    Write-Host "[4/4] Running tests..."
    python -m pytest -v

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " TEST RESULT: FAIL"
        Write-Host "========================================"
        exit 1
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host " TEST RESULT: PASS"
    Write-Host "========================================"
}
finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id -Force
        Write-Host ""
        Write-Host "Flask API stopped."
    }
}