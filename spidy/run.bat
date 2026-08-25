@echo off
REM ================================================================
REM   Spidy - one-click launcher for Windows
REM ================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo    _____       _     _
echo   ^|  ___^|     ^| ^|   ^| ^|
echo   ^| ^|__  _ __ ^| ^|__ _^| ^| _   _
echo   ^|___ \^| '_ \^| / _` ^| ^|^| ^| ^| ^|
echo    ___^) ^| ^|_) ^| ^| (_^| ^|_^| ^|_^| ^|
echo   ^|____/^| .__/^|_^|\__,_(_)__, ^|
echo         ^| ^|             __/ ^|
echo         ^|_^|            ^|___/
echo.
echo   Spidy - your offline AI companion
echo   ==================================
echo.

REM --- Python check ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM --- Virtual env ---
if not exist ".venv\" (
    echo [*] First run - creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM --- Dependencies ---
if not exist ".venv\Lib\site-packages\customtkinter" (
    echo [*] Installing dependencies... this may take a minute
    python -m pip install --upgrade pip >nul
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [!] Dependency install failed. Try running: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM --- Ollama check ---
where ollama >nul 2>&1
if errorlevel 1 (
    echo [!] Ollama not detected. Spidy will still work with rule-based fallback,
    echo     but for smarter conversation install Ollama from https://ollama.com
    echo     Then run:  ollama pull mistral
    echo.
    timeout /t 3 >nul
)

REM --- Launch ---
echo [*] Launching Spidy...
python main.py
if errorlevel 1 (
    echo.
    echo [!] Spidy exited with an error. See message above.
    pause
)
endlocal
