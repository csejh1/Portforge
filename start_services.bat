@echo off
echo 🏗️ Starting Portforge MSA Services...
echo ================================================

echo 🚀 Starting Auth Service on port 8000...
start "Auth Service" cmd /k "cd Auth && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo 🚀 Starting Project Service on port 8001...
start "Project Service" cmd /k "cd Project_Service && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul

echo 🚀 Starting Team Service on port 8002...
start "Team Service" cmd /k "cd Team-BE && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 3 /nobreak >nul

echo 🚀 Starting AI Service on port 8003...
start "AI Service" cmd /k "cd Ai && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload"
timeout /t 3 /nobreak >nul

echo 🚀 Starting Support Service on port 8004...
start "Support Service" cmd /k "cd Support_Communication_Service && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"

echo.
echo ================================================
echo ✅ All services are starting...
echo.
echo 🌐 Service URLs:
echo   Auth Service: http://localhost:8000
echo   Project Service: http://localhost:8001  
echo   Team Service: http://localhost:8002
echo   AI Service: http://localhost:8003
echo   Support Service: http://localhost:8004
echo.
echo 📚 API Documentation:
echo   Auth Service: http://localhost:8000/docs
echo   Project Service: http://localhost:8001/docs
echo   Team Service: http://localhost:8002/docs
echo   AI Service: http://localhost:8003/docs
echo   Support Service: http://localhost:8004/docs
echo.
echo ⚠️  Close individual command windows to stop services
pause