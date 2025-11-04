@echo off
echo ================================================
echo    TIDRAPPORTERINGSSYSTEM - NAMIN KONSULTER
echo ================================================
echo.

REM Kontrollera om Python är installerat
python --version >nul 2>&1
if errorlevel 1 (
    echo VARNING: Python är inte installerat eller inte i PATH!
    echo Ladda ner Python från: https://python.org
    pause
    exit /b 1
)

echo Python hittat - kontrollerar dependencies...
echo.

REM Installera dependencies om de inte finns
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installerar Flask dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo FEL: Kunde inte installera dependencies!
        pause
        exit /b 1
    )
    echo Dependencies installerade!
    echo.
)

echo Startar tidrapporteringssystem...
echo.
echo Systemet kommer att vara tillgängligt på:
echo     http://localhost:5000
echo.
echo Admin-inloggning:
echo     E-post: admin@tidrapport.se
echo     Lösenord: admin123
echo.
echo Tryck Ctrl+C för att stoppa servern
echo.

REM Starta Flask-applikationen
python app.py

echo.
echo Servern har stoppats.
pause