@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title HRCMS Dev Startup

echo.
echo ========================================================
echo    HRCMS - One-Click Dev Services Startup
echo ========================================================
echo.
echo    CMS Backend  : http://localhost:8080/docs
echo    CMS Frontend : http://localhost:5173
echo    MiniProgram  : http://localhost:5174
echo    MongoDB      : 127.0.0.1:27017
echo    Database     : hrcms_test
echo.
echo ========================================================
echo.

REM ============================================================
REM  1.  Check / Start MongoDB
REM ============================================================
echo [1/5] Checking MongoDB ... (testing, please wait)

powershell -Command "try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('192.168.1.111',32769);$c.Close();exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel% equ 0 (
    echo        [OK] MongoDB is reachable
) else (
    echo        [WARN] MongoDB not reachable at 127.0.0.1:27017
    echo        Please ensure MongoDB is running before proceeding.
)
echo.

REM ============================================================
REM  2.  Start Backend (FastAPI on port 8080)
REM ============================================================
echo [2/5] Starting CMS Backend  -^> http://localhost:8080
if not exist "backend\main.py" (
    echo        [ERROR] backend\main.py not found!
    pause
    exit /b 1
)
start "HRCMS-Backend-8080" cmd /k "cd /d "%~dp0backend" && echo HRCMS Backend starting... && venv\Scripts\python.exe main.py"
echo        [OK] Backend launched in a new window
echo.

REM ============================================================
REM  3.  Start CMS Frontend (Vite on port 5173)
REM ============================================================
echo [3/5] Starting CMS Frontend -^> http://localhost:5173
if not exist "package.json" (
    echo        [ERROR] package.json not found!
    pause
    exit /b 1
)
start "HRCMS-Frontend-5173" cmd /k "cd /d "%~dp0" && echo HRCMS Frontend starting... && npm run dev"
echo        [OK] CMS Frontend launched in a new window
echo.

REM ============================================================
REM  4.  Start MiniProgram (uni-app H5 on port 5174)
REM ============================================================
echo [4/5] Starting MiniProgram  -^> http://localhost:5174
if not exist "miniprogram\package.json" (
    echo        [WARN] miniprogram\package.json not found, skip
) else (
    start "HRCMS-MiniProgram-5174" cmd /k "cd /d "%~dp0miniprogram" && echo HRCMS MiniProgram starting... && npm run dev"
    echo        [OK] MiniProgram H5 launched in a new window
)
echo.

REM ============================================================
REM  Open browser
REM ============================================================
echo [5/5] Waiting for services to compile...
timeout /t 8 /nobreak >nul
start http://localhost:5173
start http://localhost:5174

echo.
echo ========================================================
echo    All services started!
echo.
echo    CMS Frontend : http://localhost:5173
echo    MiniProgram  : http://localhost:5174
echo    CMS Backend  : http://localhost:8080/docs
echo.
echo    Close each CMD window to stop its service.
echo ========================================================
echo.

pause
