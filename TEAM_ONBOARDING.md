# 🚀 Portforge MSA 팀원 온보딩 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [프로젝트 클론](#프로젝트-클론)
3. [인프라 실행](#인프라-실행)
4. [백엔드 서비스 설정](#백엔드-서비스-설정)
5. [프론트엔드 설정](#프론트엔드-설정)
6. [데이터베이스 초기화](#데이터베이스-초기화)
7. [서비스 실행](#서비스-실행)
8. [환경변수 설명](#환경변수-설명)

---

## 사전 요구사항

### 필수 설치
- **Python 3.11+**
- **Poetry** (Python 패키지 관리자)
  ```bash
  pip install poetry
  ```
- **Node.js 18+** & **npm**
- **Docker Desktop**
- **MySQL Client** (선택사항, DB 확인용)

### Poetry 설정 (가상환경을 프로젝트 내부에 생성)
```bash
poetry config virtualenvs.in-project true
```

---

## 프로젝트 클론

```bash
git clone <repository-url>
cd Portforge
```

---

## 인프라 실행

Docker로 MySQL, MinIO(S3), DynamoDB Local을 실행합니다.

```bash
docker-compose up -d
```

### 실행되는 서비스
| 서비스 | 포트 | 용도 |
|--------|------|------|
| MySQL | 3306 | 메인 데이터베이스 |
| MinIO | 9000, 9001 | S3 호환 스토리지 |
| DynamoDB Local | 8089 | 채팅 데이터 저장 |

### 확인
```bash
docker-compose ps
```

---

## 백엔드 서비스 설정

### 1. 의존성 설치 (전체)

```bash
# Windows
install_all.bat

# 또는 수동으로
poetry install                    # 루트 (poe 태스크용)
cd Auth && poetry install && cd ..
cd Project_Service && poetry install && cd ..
cd Team-BE && poetry install && cd ..
cd Ai && poetry install && cd ..
cd Support_Communication_Service && poetry install && cd ..
```

### 2. 환경변수 설정

각 서비스 폴더에서 `.env.example`을 `.env`로 복사합니다.

```bash
# Windows (PowerShell)
Copy-Item Auth\.env.example Auth\.env
Copy-Item Project_Service\.env.example Project_Service\.env
Copy-Item Team-BE\.env.example Team-BE\.env
Copy-Item Ai\.env.example Ai\.env
Copy-Item Support_Communication_Service\.env.example Support_Communication_Service\.env

# Linux/Mac
cp Auth/.env.example Auth/.env
cp Project_Service/.env.example Project_Service/.env
cp Team-BE/.env.example Team-BE/.env
cp Ai/.env.example Ai/.env
cp Support_Communication_Service/.env.example Support_Communication_Service/.env
```

### 3. 환경변수 수정 (필요시)

대부분의 값은 로컬 개발용으로 이미 설정되어 있습니다.
**Cognito 관련 값만 팀 리더에게 받아서 입력하세요.**

---

## 프론트엔드 설정

```bash
cd FE
cp .env.example .env.local
npm install
cd ..
```

---

## 데이터베이스 초기화

### 1. MySQL 데이터베이스 생성

```bash
python reset_all_db.py
```
> `yes` 입력하여 확인

### 2. 테이블 생성

```bash
# Windows
create_all_tables.bat

# 또는 각 서비스에서 수동으로 (poetry run 필수!)
cd Auth && poetry run python create_tables.py && cd ..
cd Project_Service && poetry run python create_tables.py && cd ..
cd Team-BE && poetry run python create_tables.py && cd ..
cd Ai && poetry run python create_tables.py && cd ..
cd Support_Communication_Service && poetry run python create_tables.py && cd ..
```

### 3. DynamoDB 테이블 생성

```bash
python create_dynamodb_tables.py
```

### 4. 시드 데이터 삽입

```bash
python seed_all.py
```

### 생성되는 테스트 계정
| 역할 | 이메일 | User ID |
|------|--------|---------|
| Admin | admin@example.com | admin-uuid-0000 |
| Member | member@example.com | user2-uuid-5678 |
| Member2 | member2@example.com | user3-uuid-9999 |

---

## 서비스 실행

### 방법 1: Poe 태스크 사용 (권장)

루트 폴더에서 `poetry run poe` 명령어로 실행:

```bash
# 인프라 실행
poetry run poe db-up

# 개별 서비스 실행 (각각 별도 터미널에서)
poetry run poe run-auth      # Auth (포트 8000)
poetry run poe run-project   # Project (포트 8001)
poetry run poe run-team      # Team (포트 8002)
poetry run poe run-ai        # AI (포트 8003)
poetry run poe run-support   # Support (포트 8004)

# 프론트엔드
poetry run poe run-fe        # FE (포트 3000)

# 헬스체크
poetry run poe health-check
```

### 방법 2: 배치 파일 사용

```bash
# Windows
start_services.bat

# 또는 Python 스크립트
python start_services.py
```

### 방법 3: 개별 서비스 직접 실행

```bash
# Auth Service (포트 8000)
cd Auth
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Project Service (포트 8001)
cd Project_Service
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Team Service (포트 8002)
cd Team-BE
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# AI Service (포트 8003)
cd Ai
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Support Service (포트 8004)
cd Support_Communication_Service
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### 프론트엔드 실행

```bash
cd FE
npm run dev
```

### 서비스 URL
| 서비스 | URL | Swagger Docs |
|--------|-----|--------------|
| Auth | http://localhost:8000 | http://localhost:8000/docs |
| Project | http://localhost:8001 | http://localhost:8001/docs |
| Team | http://localhost:8002 | http://localhost:8002/docs |
| AI | http://localhost:8003 | http://localhost:8003/docs |
| Support | http://localhost:8004 | http://localhost:8004/docs |
| Frontend | http://localhost:3000 | - |
| MinIO Console | http://localhost:9001 | - |

---

## 환경변수 설명

### 공통 환경변수 (모든 백엔드 서비스)

```bash
# =================================================================
# [App Settings]
# =================================================================
PROJECT_NAME="서비스명"
ENV=local                    # local, dev, staging, prod
DEBUG=True                   # 개발 시 True

# =================================================================
# [Database - MySQL]
# 각 서비스별 스키마 사용
# =================================================================
DATABASE_URL=mysql+aiomysql://root:rootpassword@localhost:3306/portforge_<서비스명>
# 예: portforge_auth, portforge_project, portforge_team, portforge_ai, portforge_support

# =================================================================
# [AWS - LocalStack/MinIO (로컬 개발용)]
# 로컬에서는 Docker로 실행되는 MinIO/DynamoDB Local 사용
# =================================================================
DDB_ENDPOINT_URL=http://localhost:8089    # DynamoDB Local
S3_ENDPOINT_URL=http://localhost:9000     # MinIO
AWS_ACCESS_KEY_ID=admin                   # MinIO 기본값
AWS_SECRET_ACCESS_KEY=password123         # MinIO 기본값
AWS_REGION=ap-northeast-2

# =================================================================
# [AWS Cognito - 팀 리더에게 받아야 함!]
# =================================================================
COGNITO_REGION=ap-northeast-2
COGNITO_USERPOOL_ID=ap-northeast-2_XXXXXXX    # 👈 팀 리더에게 문의
COGNITO_APP_CLIENT_ID=XXXXXXXXXXXXXXXXXX      # 👈 팀 리더에게 문의
```

### 서비스별 추가 환경변수

#### Auth Service
```bash
# Cognito 소셜 로그인
COGNITO_DOMAIN="https://your-domain.auth.ap-northeast-2.amazoncognito.com"
REDIRECT_URI="http://localhost:3000/"
```

#### Team Service
```bash
# JWT 설정
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# S3 버킷
S3_BUCKET_NAME=portforge-bucket

# DynamoDB 테이블
DYNAMODB_TABLE_CHATS=team_chats
DYNAMODB_TABLE_ROOMS=chat_rooms
```

#### AI Service
```bash
# DynamoDB
DDB_TABLE_NAME=team_chats

# S3
AWS_S3_BUCKET=portforge-bucket
S3_PREFIX=ai-generated/

# AWS Bedrock (AI 모델)
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0  # 선택사항
```

### 프론트엔드 환경변수 (FE/.env.local)

```bash
# =================================================================
# [API Endpoints]
# =================================================================
VITE_AUTH_API_URL=http://localhost:8000
VITE_PROJECT_API_URL=http://localhost:8001
VITE_TEAM_API_URL=http://localhost:8002
VITE_AI_API_URL=http://localhost:8003
VITE_SUPPORT_API_URL=http://localhost:8004

# =================================================================
# [Cognito 소셜 로그인 - 팀 리더에게 받아야 함!]
# =================================================================
VITE_COGNITO_DOMAIN=https://your-domain.auth.ap-northeast-2.amazoncognito.com
VITE_COGNITO_APP_CLIENT_ID=XXXXXXXXXXXXXXXXXX
VITE_REDIRECT_URI=http://localhost:3000/#/auth/callback

# =================================================================
# [AI 서비스]
# =================================================================
GEMINI_API_KEY=                           # 선택사항
```

---

## 🔧 문제 해결

### Poetry 가상환경이 프로젝트 외부에 생성되는 경우
```bash
poetry config virtualenvs.in-project true
rm -rf .venv  # 기존 가상환경 삭제
poetry install  # 다시 설치
```

### MySQL 연결 오류
```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# MySQL 로그 확인
docker-compose logs mysql
```

### 포트 충돌
```bash
# Windows - 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

### MSA 헬스체크
```bash
poetry run poe health-check
# 또는
python test_msa_communication.py
```

---

## 📚 참고 문서

- `ERD_v2.dbml` - 데이터베이스 스키마
- `README_MSA_SETUP.md` - MSA 아키텍처 설명
- 각 서비스의 `README.md` - 서비스별 상세 문서
- Swagger UI (`/docs`) - API 문서

---

## ⚠️ 주의사항

1. **`.env` 파일은 절대 Git에 커밋하지 마세요!** (이미 `.gitignore`에 포함됨)
2. **Cognito 관련 값은 팀 리더에게 별도로 받으세요**
3. **AWS 실제 키는 로컬 개발에서 사용하지 마세요** (MinIO/DynamoDB Local 사용)
4. **DB 스키마 변경 시 팀원들에게 공유하세요**
