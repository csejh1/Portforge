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
:: 3. Python 의존성 설치 (venv 검증 포함)
:: ========================================
echo [3/7] Python 의존성 설치 중...

:: 서비스별 venv 검증 및 설치 함수 호출
call :install_service "Auth"
call :install_service "Project_Service"
call :install_service "Team-BE"
call :install_service "Ai"
call :install_service "Support_Communication_Service"

echo    ✅ Python 의존성 설치 완료
echo.

:: ========================================
:: 4. Frontend 의존성 설치
:: ========================================
echo [4/7] Frontend 의존성 설치 중...

if exist "FE\package.json" (
    cd FE
    if exist "node_modules" (
        :: node_modules 유효성 검사
        if exist "node_modules\.package-lock.json" (
            echo    ⏭️  FE/node_modules 이미 존재, 업데이트 확인 중...
            call npm install --silent 2>nul
        ) else (
            echo    🔄 FE/node_modules 손상됨, 재설치 중...
            rmdir /s /q node_modules 2>nul
            call npm install --silent 2>nul
        )
    ) else (
        echo    📦 FE 패키지 설치 중...
        call npm install --silent 2>nul
    )
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

echo    - Auth 테이블 생성...
cd Auth
call poetry run python create_tables.py
if errorlevel 1 (
    echo    ⚠️  Auth 테이블 생성 실패
) else (
    echo    ✅ Auth 테이블 생성 완료
)
cd ..

echo    - Project 테이블 생성...
cd Project_Service
call poetry run python create_tables.py
if errorlevel 1 (
    echo    ⚠️  Project 테이블 생성 실패
) else (
    echo    ✅ Project 테이블 생성 완료
)
cd ..

echo    - Team 테이블 생성...
cd Team-BE
call poetry run python create_tables.py
if errorlevel 1 (
    echo    ⚠️  Team 테이블 생성 실패
) else (
    echo    ✅ Team 테이블 생성 완료
)
cd ..

echo    - AI 테이블 생성...
cd Ai
call poetry run python create_tables.py
if errorlevel 1 (
    echo    ⚠️  AI 테이블 생성 실패
) else (
    echo    ✅ AI 테이블 생성 완료
)
cd ..

echo    - Support 테이블 생성...
cd Support_Communication_Service
call poetry run python create_tables.py
if errorlevel 1 (
    echo    ⚠️  Support 테이블 생성 실패
) else (
    echo    ✅ Support 테이블 생성 완료
)
cd ..

echo    ✅ 데이터베이스 초기화 완료 (시드 데이터 없음)

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
echo ║  서비스 시작: .\start_services.bat                       ║
echo ║  접속 주소:   http://localhost:3000                      ║
echo ║                                                          ║
echo ║  시작하기:                                               ║
echo ║    1. 회원가입 후 로그인                                 ║
echo ║    2. 프로젝트 생성/참여                                 ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set /p start_now="지금 서비스를 시작하시겠습니까? (Y/N): "
if /i "%start_now%"=="Y" (
    call start_services.bat
)

endlocal
exit /b 0

:: ========================================
:: 서비스별 venv 검증 및 설치 함수
:: ========================================
:install_service
set "service=%~1"

if not exist "%service%\pyproject.toml" (
    goto :eof
)

echo    📦 %service% 서비스 확인 중...

cd %service%

:: .venv 존재 여부 확인
if exist ".venv" (
    :: .venv 유효성 검사 (python 실행 가능 여부)
    if exist ".venv\Scripts\python.exe" (
        :: python 실행 테스트
        .venv\Scripts\python.exe --version >nul 2>&1
        if errorlevel 1 (
            echo       🔄 %service%/.venv 손상됨, 재생성 중...
            rmdir /s /q .venv 2>nul
            call poetry install --no-root --quiet 2>nul
        ) else (
            :: poetry.lock 변경 확인하여 업데이트 필요 여부 판단
            echo       ⏭️  %service%/.venv 유효, 패키지 동기화 중...
            call poetry install --no-root --quiet 2>nul
        )
    ) else (
        echo       🔄 %service%/.venv 불완전, 재생성 중...
        rmdir /s /q .venv 2>nul
        call poetry install --no-root --quiet 2>nul
    )
) else (
    echo       📦 %service%/.venv 생성 중...
    call poetry install --no-root --quiet 2>nul
)

cd ..
goto :eof
