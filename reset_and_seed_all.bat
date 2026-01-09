@echo off
chcp 65001 > nul
echo ============================================
echo   Portforge MSA - DB 초기화 및 시딩
echo ============================================
echo.
echo ⚠️  경고: 모든 데이터가 삭제됩니다!
echo.
set /p confirm="계속하시겠습니까? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo [1/3] 데이터베이스 초기화 중...
python reset_all_db.py < nul
if errorlevel 1 (
    echo ❌ 데이터베이스 초기화 실패
    pause
    exit /b 1
)
echo.

echo [2/3] 테이블 생성 중...
call create_all_tables.bat
echo.

echo [3/3] 시드 데이터 삽입 중...
python seed_all.py
if errorlevel 1 (
    echo ❌ 시드 데이터 삽입 실패
    pause
    exit /b 1
)

echo.
echo ============================================
echo ✅ 초기화 완료!
echo ============================================
echo.
echo 다음 단계: start_services.bat
echo.
pause
