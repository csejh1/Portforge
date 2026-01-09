@echo off
echo 📦 Installing dependencies for all microservices...
echo ================================================

echo.
echo 📥 Installing root dependencies (poe tasks)...
poetry install
echo Done.

echo.
echo 📥 Installing Auth Service dependencies...
cd Auth
poetry install
cd ..

echo.
echo 📥 Installing Project Service dependencies...
cd Project_Service
poetry install
cd ..

echo.
echo 📥 Installing Team Service dependencies...
cd Team-BE
poetry install
cd ..

echo.
echo 📥 Installing AI Service dependencies...
cd Ai
poetry install
cd ..

echo.
echo 📥 Installing Support Service dependencies...
cd Support_Communication_Service
poetry install
cd ..

echo.
echo ✅ ALL DEPENDENCIES INSTALLED!
echo ================================================
echo.
echo Available poe commands (from root):
echo   poetry run poe db-up        - Start Docker infrastructure
echo   poetry run poe health-check - Check all services
echo   poetry run poe run-auth     - Run Auth service
echo   poetry run poe run-project  - Run Project service
echo   poetry run poe run-team     - Run Team service
echo   poetry run poe run-ai       - Run AI service
echo   poetry run poe run-support  - Run Support service
echo.
pause
