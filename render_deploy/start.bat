@echo off
echo ================================
echo   Resume Analyzer - Starting
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Edit .env and add your GROQ_API_KEY
    echo             Then run this script again.
    pause
    exit /b 1
)

REM Load environment variables from .env
for /f "tokens=1,* delims==" %%a in (.env) do (
    set %%a=%%b
)

if "%GROQ_API_KEY%"=="" (
    echo [ERROR] GROQ_API_KEY not set in .env
    echo         Please add your Groq API key to .env file
    pause
    exit /b 1
)

echo [OK] Environment variables loaded
echo.

REM Install dependencies
echo [INSTALL] Installing dependencies...
pip install -r requirements.txt
echo.

REM Start server
echo [START] Starting server...
echo         Local: http://localhost:8000
echo         API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn resumeAnalyzer_groq:app --host 0.0.0.0 --port 8000 --reload

pause
