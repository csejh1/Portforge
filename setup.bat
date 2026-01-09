@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         🚀 Portforge 원클릭 환경 설정 스크립트           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: 1. 사전 요구사항 체크
:: ========================================
echo [1/7] 사전 요구사항 확인 중...

:: Python 체크
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    https://www.python.org/downloads/ 에서 Python 3.11+ 설치 후 다시 실행하세요.
    pause
    exit /b 1
)
echo    ✅ Python 확인 완료

:: Poetry 체크
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Poetry가 설치되어 있지 않습니다.
    echo    설치 중...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    if errorlevel 1 (
        echo ❌ Poetry 설치 실패. 수동으로 설치해주세요.
        pause
        exit /b 1
    )
    echo    ✅ Poetry 설치 완료
) else (
    echo    ✅ Poetry 확인 완료
)

:: Node.js 체크
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js가 설치되어 있지 않습니다.
    echo    https://nodejs.org/ 에서 Node.js 18+ 설치 후 다시 실행하세요.
    pause
    exit /b 1
)
echo    ✅ Node.js 확인 완료

:: Docker 체크
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 설치되어 있지 않습니다.
    echo    https://www.docker.com/products/docker-desktop/ 에서 Docker Desktop 설치 후 다시 실행하세요.
    pause
    exit /b 1
)
echo    ✅ Docker 확인 완료

:: Docker 실행 중인지 체크
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop이 실행 중이 아닙니다.
    echo    Docker Desktop을 실행한 후 다시 시도하세요.
    pause
    exit /b 1
)
echo    ✅ Docker 실행 중 확인 완료

echo.

:: ========================================
:: 2. 환경 변수 파일 복사
:: ========================================
echo [2/7] 환경 변수 파일 설정 중...

if not exist "Auth\.env" (
    if exist "Auth\.env.example" (
        copy "Auth\.env.example" "Auth\.env" >nul
        echo    ✅ Auth/.env 생성
    )
) else (
    echo    ⏭️  Auth/.env 이미 존재
)

if not exist "Project_Service\.env" (
    if exist "Project_Service\.env.example" (
        copy "Project_Service\.env.example" "Project_Service\.env" >nul
        echo    ✅ Project_Service/.env 생성
    )
) else (
    echo    ⏭️  Project_Service/.env 이미 존재
)

if not exist "Team-BE\.env" (
    if exist "Team-BE\.env.example" (
        copy "Team-BE\.env.example" "Team-BE\.env" >nul
        echo    ✅ Team-BE/.env 생성
    )
) else (
    echo    ⏭️  Team-BE/.env 이미 존재
)

if not exist "Ai\.env" (
    if exist "Ai\.env.example" (
        copy "Ai\.env.example" "Ai\.env" >nul
        echo    ✅ Ai/.env 생성
    )
) else (
    echo    ⏭️  Ai/.env 이미 존재
)

if not exist "Support_Communication_Service\.env" (
    if exist "Support_Communication_Service\.env.example" (
        copy "Support_Communication_Service\.env.example" "Support_Communication_Service\.env" >nul
        echo    ✅ Support_Communication_Service/.env 생성
    )
) else (
    echo    ⏭️  Support_Communication_Service/.env 이미 존재
)

echo.

:: ========================================
:: 3. Python 의존성 설치
:: ========================================
echo [3/7] Python 의존성 설치 중... (시간이 걸릴 수 있습니다)

:: 루트
if exist "pyproject.toml" (
    echo    📦 루트 패키지 설치 중...
    call poetry install --no-root --quiet 2>nul
)

:: Auth
if exist "Auth\pyproject.toml" (
    echo    📦 Auth 서비스 패키지 설치 중...
    cd Auth
    call poetry install --no-root --quiet 2>nul
    cd ..
)

:: Project_Service
if exist "Project_Service\pyproject.toml" (
    echo    📦 Project 서비스 패키지 설치 중...
    cd Project_Service
    call poetry install --no-root --quiet 2>nul
    cd ..
)

:: Team-BE
if exist "Team-BE\pyproject.toml" (
    echo    📦 Team 서비스 패키지 설치 중...
    cd Team-BE
    call poetry install --no-root --quiet 2>nul
    cd ..
)

:: Ai
if exist "Ai\pyproject.toml" (
    echo    📦 AI 서비스 패키지 설치 중...
    cd Ai
    call poetry install --no-root --quiet 2>nul
    cd ..
)

:: Support_Communication_Service
if exist "Support_Communication_Service\pyproject.toml" (
    echo    📦 Support 서비스 패키지 설치 중...
    cd Support_Communication_Service
    call poetry install --no-root --quiet 2>nul
    cd ..
)

echo    ✅ Python 의존성 설치 완료
echo.

:: ========================================
:: 4. Frontend 의존성 설치
:: ========================================
echo [4/7] Frontend 의존성 설치 중...

if exist "FE\package.json" (
    cd FE
    call npm install --silent 2>nul
    cd ..
    echo    ✅ Frontend 의존성 설치 완료
) else (
    echo    ⚠️  FE/package.json 없음, 스킵
)

echo.

:: ========================================
:: 5. Docker 컨테이너 시작
:: ========================================
echo [5/7] Docker 컨테이너 시작 중...

docker compose up -d 2>nul
if errorlevel 1 (
    echo ❌ Docker 컨테이너 시작 실패
    pause
    exit /b 1
)
echo    ✅ Docker 컨테이너 시작 완료

:: MySQL이 준비될 때까지 대기
echo    ⏳ MySQL 준비 대기 중 (최대 60초)...
set /a count=0
:wait_mysql
docker compose exec -T mysql mysqladmin ping -h localhost -u root -prootpassword >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! geq 60 (
        echo ❌ MySQL 시작 시간 초과
        pause
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto wait_mysql
)
echo    ✅ MySQL 준비 완료

echo.

:: ========================================
:: 6. 데이터베이스 초기화
:: ========================================
echo [6/7] 데이터베이스 초기화 중...

:: 테이블 생성
echo    📋 테이블 생성 중...

cd Auth
call poetry run python create_tables.py >nul 2>&1
cd ..

cd Project_Service
call poetry run python create_tables.py >nul 2>&1
cd ..

cd Team-BE
call poetry run python create_tables.py >nul 2>&1
cd ..

cd Ai
call poetry run python create_tables.py >nul 2>&1
cd ..

cd Support_Communication_Service
call poetry run python create_tables.py >nul 2>&1
cd ..

echo    ✅ 테이블 생성 완료

:: 시드 데이터 삽입
echo    🌱 시드 데이터 삽입 중...
python seed_all.py >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  시드 데이터 삽입 중 일부 오류 (무시 가능)
) else (
    echo    ✅ 시드 데이터 삽입 완료
)

echo.

:: ========================================
:: 7. 완료
:: ========================================
echo [7/7] 설정 완료!
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    🎉 환경 설정 완료!                    ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║                                                          ║
echo ║  서비스 시작: start_services.bat                         ║
echo ║  접속 주소:   http://localhost:3000                      ║
echo ║                                                          ║
echo ║  테스트 계정:                                            ║
echo ║    - admin@example.com / devpass123                      ║
echo ║    - member@example.com / devpass123                     ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set /p start_now="지금 서비스를 시작하시겠습니까? (Y/N): "
if /i "%start_now%"=="Y" (
    call start_services.bat
)

endlocal
