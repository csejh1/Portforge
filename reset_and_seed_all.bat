@echo off
echo ========================================
echo MSA Database Reset and Seed Script
echo ========================================
echo.
echo This script will:
echo 1. Drop and recreate all databases
echo 2. Create tables from models
echo 3. Seed initial data
echo.
echo WARNING: This will DELETE ALL DATA!
echo.
pause

echo.
echo [Step 1/3] Resetting databases...
python reset_all_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database reset failed!
    pause
    exit /b 1
)

echo.
echo [Step 2/3] Creating tables...
python create_all_tables.py
if %errorlevel% neq 0 (
    echo ERROR: Table creation failed!
    pause
    exit /b 1
)

echo.
echo [Step 3/3] Seeding data...
python seed_all.py
if %errorlevel% neq 0 (
    echo ERROR: Data seeding failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! All databases are ready!
echo ========================================
pause
