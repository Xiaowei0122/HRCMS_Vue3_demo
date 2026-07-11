@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title HRCMS Dev Startup

echo.
echo ========================================================
echo    HRCMS - One-Click Dev Services Startup
echo ========================================================
echo.
echo    Frontend : http://localhost:3000
echo    Backend  : http://localhost:8080/docs
echo    MongoDB  : 192.168.1.111:32769
echo    Database : hrcms_test
echo.
echo ========================================================
echo.

REM ============================================================
REM  1.  Check / Start MongoDB
REM ============================================================
echo [1/3] Checking MongoDB ... (testing, please wait)

powershell -Command "try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('192.168.1.111',32769);$c.Close();exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel% equ 0 (
    echo        [OK] MongoDB is reachable
) else (
    echo        [WARN] MongoDB not reachable at 192.168.1.111:32769
    echo        Please ensure MongoDB is running before proceeding.
)
echo.

REM ============================================================
REM  2.  Start Backend (FastAPI on port 8080)
REM ============================================================
echo [2/3] Starting Backend  -^> http://localhost:8080
if not exist "backend\main.py" (
    echo        [ERROR] backend\main.py not found!
    pause
    exit /b 1
)
start "HRCMS-Backend-8080" cmd /k "cd /d "%~dp0backend" && echo HRCMS Backend starting... && venv\Scripts\python.exe main.py"
echo        [OK] Backend launched in a new window
echo.

REM ============================================================
REM  3.  Start Frontend (Vite on port 3000)
REM ============================================================
echo [3/3] Starting Frontend -^> http://localhost:3000
if not exist "package.json" (
    echo        [ERROR] package.json not found!
    pause
    exit /b 1
)
start "HRCMS-Frontend-3000" cmd /k "cd /d "%~dp0" && echo HRCMS Frontend starting... && npm run dev"
echo        [OK] Frontend launched in a new window
echo.

REM ============================================================
REM  Open browser
REM ============================================================
echo Waiting 6 seconds for services to compile...
timeout /t 6 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo    All services started!
echo.
echo    Frontend : http://localhost:3000
echo    Backend  : http://localhost:8080/docs
echo.
echo    Close each CMD window to stop its service.
echo ========================================================
echo.

pause
