@echo off
echo ========================================
echo Portforge Project Cleanup Script
echo ========================================
echo.
echo .gitignore files will NOT be deleted:
echo   - .venv/, node_modules/
echo   - .env files
echo   - __pycache__/
echo   - .vscode/
echo.
echo Files to be KEPT:
echo   - All .git/ folders (Git history)
echo   - docker-compose.yml, init-db.sql
echo   - seed_all.py, reset_all_db.py
echo   - create_all_tables.bat, start_services.py
echo   - test_msa_communication.py
echo   - TEAM_ONBOARDING.md
echo   - All app/, migrations/ folders
echo.
pause

echo.
echo [1/3] Deleting backup folders (*_latest) and unused shared/...
if exist "Ai_latest" rmdir /s /q "Ai_latest"
if exist "FE_latest" rmdir /s /q "FE_latest"
if exist "Support_Communication_Service_latest" rmdir /s /q "Support_Communication_Service_latest"
if exist "Team_BE_latest" rmdir /s /q "Team_BE_latest"
if exist "shared" rmdir /s /q "shared"
echo Done.

echo.
echo [2/3] Deleting empty folders...
if exist "Ai\scripts" rmdir /s /q "Ai\scripts"
if exist "Team-BE\Template-Repo" rmdir /s /q "Team-BE\Template-Repo"
echo Done.

echo.
echo [3/3] Deleting unnecessary files...

REM Root - Unnecessary docs
if exist "MSA_ANALYSIS_REPORT.md" del /q "MSA_ANALYSIS_REPORT.md"
if exist "MSA_API_GUIDE.md" del /q "MSA_API_GUIDE.md"
if exist "MSA_DATABASE_GUIDE.md" del /q "MSA_DATABASE_GUIDE.md"
if exist "MSA_RESILIENCE_GUIDE.md" del /q "MSA_RESILIENCE_GUIDE.md"
if exist "MSA_SEPARATION_GUIDE.md" del /q "MSA_SEPARATION_GUIDE.md"
if exist "DATABASE_RESET_GUIDE.md" del /q "DATABASE_RESET_GUIDE.md"
if exist "exAPI 명세서 (2).html" del /q "exAPI 명세서 (2).html"

REM Root - Duplicate scripts
if exist "create_all_tables.py" del /q "create_all_tables.py"
if exist "reset_and_seed_all.py" del /q "reset_and_seed_all.py"
if exist "test_simple_service.py" del /q "test_simple_service.py"
if exist "seed_chat_data.py" del /q "seed_chat_data.py"

REM Ai - Temp scripts
if exist "Ai\init_dynamodb.py" del /q "Ai\init_dynamodb.py"
if exist "Ai\init_dynamodb_aws.py" del /q "Ai\init_dynamodb_aws.py"
if exist "Ai\check_db.py" del /q "Ai\check_db.py"
if exist "Ai\cleanup_reports.py" del /q "Ai\cleanup_reports.py"
if exist "Ai\reset_alembic.py" del /q "Ai\reset_alembic.py"
if exist "Ai\seeder.py" del /q "Ai\seeder.py"
if exist "Ai\test_pipeline.py" del /q "Ai\test_pipeline.py"

REM Project_Service - Temp files
if exist "Project_Service\simple_server.py" del /q "Project_Service\simple_server.py"
if exist "Project_Service\minimal_swagger.py" del /q "Project_Service\minimal_swagger.py"
if exist "Project_Service\test_swagger.py" del /q "Project_Service\test_swagger.py"
if exist "Project_Service\create_tables.sql" del /q "Project_Service\create_tables.sql"
if exist "Project_Service\MYSQL_SETUP_COMPLETE.md" del /q "Project_Service\MYSQL_SETUP_COMPLETE.md"
if exist "Project_Service\db_init.py" del /q "Project_Service\db_init.py"

REM Support_Communication_Service - Verify scripts
if exist "Support_Communication_Service\verify_app.py" del /q "Support_Communication_Service\verify_app.py"
if exist "Support_Communication_Service\verify_chat_impl.py" del /q "Support_Communication_Service\verify_chat_impl.py"
if exist "Support_Communication_Service\verify_chat.py" del /q "Support_Communication_Service\verify_chat.py"

REM Auth - Duplicate scripts
if exist "Auth\drop_tables.py" del /q "Auth\drop_tables.py"
if exist "Auth\reset_db.py" del /q "Auth\reset_db.py"

REM Team-BE - Temp files
if exist "Team-BE\db_init.py" del /q "Team-BE\db_init.py"
if exist "Team-BE\test_file_sharing.py" del /q "Team-BE\test_file_sharing.py"
if exist "Team-BE\api_documentation.md" del /q "Team-BE\api_documentation.md"
if exist "Team-BE\frontend_compatibility_checklist.md" del /q "Team-BE\frontend_compatibility_checklist.md"
echo Done.

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Team Onboarding Steps:
echo   1. docker-compose up -d
echo   2. install_all.bat
echo   3. Copy .env.example to .env in each service
echo   4. python reset_all_db.py
echo   5. create_all_tables.bat
echo   6. python seed_all.py
echo   7. python test_msa_communication.py
echo   8. start_services.bat
echo.
pause
