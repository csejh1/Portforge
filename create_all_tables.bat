@echo off
echo ========================================
echo Creating tables for all MSA services
echo ========================================

echo.
echo [1/5] Auth Service...
cd Auth
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python create_tables.py
    call deactivate
) else (
    python create_tables.py
)
if %errorlevel% neq 0 (
    echo ERROR: Auth tables creation failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [2/5] Project Service...
cd Project_Service
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python create_tables.py
    call deactivate
) else (
    python create_tables.py
)
if %errorlevel% neq 0 (
    echo ERROR: Project tables creation failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [3/5] Team Service...
cd Team-BE
python create_tables.py
if %errorlevel% neq 0 (
    echo ERROR: Team tables creation failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [4/5] AI Service...
cd Ai
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python create_tables.py
    call deactivate
) else (
    python create_tables.py
)
if %errorlevel% neq 0 (
    echo ERROR: AI tables creation failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [5/5] Support Service...
cd Support_Communication_Service
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python create_tables.py
    call deactivate
) else (
    python create_tables.py
)
if %errorlevel% neq 0 (
    echo ERROR: Support tables creation failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo SUCCESS! All tables created!
echo ========================================
