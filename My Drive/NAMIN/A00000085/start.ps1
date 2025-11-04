# Tidrapporteringssystem - Startscript för PowerShell
# NAMIN Konsulter

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    TIDRAPPORTERINGSSYSTEM - NAMIN KONSULTER" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Kontrollera om Python är installerat
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✓ $pythonVersion hittat" -ForegroundColor Green
} catch {
    Write-Host "✗ VARNING: Python är inte installerat eller inte i PATH!" -ForegroundColor Red
    Write-Host "Ladda ner Python från: https://python.org" -ForegroundColor Yellow
    Read-Host "Tryck Enter för att avsluta"
    exit 1
}

Write-Host ""
Write-Host "Kontrollerar dependencies..." -ForegroundColor Yellow

# Kontrollera och installera dependencies
try {
    pip show Flask | Out-Null
    Write-Host "✓ Flask dependencies redan installerade" -ForegroundColor Green
} catch {
    Write-Host "Installerar Flask dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installerade!" -ForegroundColor Green
    } else {
        Write-Host "✗ FEL: Kunde inte installera dependencies!" -ForegroundColor Red
        Read-Host "Tryck Enter för att avsluta"
        exit 1
    }
}

Write-Host ""
Write-Host "Startar tidrapporteringssystem..." -ForegroundColor Green
Write-Host ""
Write-Host "Systemet kommer att vara tillgängligt på:" -ForegroundColor Cyan
Write-Host "     http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Admin-inloggning:" -ForegroundColor Cyan
Write-Host "     E-post: admin@tidrapport.se" -ForegroundColor White
Write-Host "     Lösenord: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Tryck Ctrl+C för att stoppa servern" -ForegroundColor Yellow
Write-Host ""

# Starta Flask-applikationen
try {
    python app.py
} catch {
    Write-Host ""
    Write-Host "✗ Ett fel uppstod vid start av servern!" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Servern har stoppats." -ForegroundColor Yellow
    Read-Host "Tryck Enter för att avsluta"
}