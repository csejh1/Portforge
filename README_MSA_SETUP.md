# 🚀 Portforge MSA 설정 및 실행 가이드

## 📋 개요

Portforge는 5개의 마이크로서비스로 구성된 프로젝트 협업 플랫폼입니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │ Project Service │    │  Team Service   │
│    Port 8000    │    │    Port 8001    │    │    Port 8002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐
         │   AI Service    │    │ Support Service │
         │    Port 8003    │    │    Port 8004    │
         └─────────────────┘    └─────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Infrastructure                     │
         │  MySQL (3306) | DynamoDB (8001) | MinIO (9000) │
         └─────────────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 1. 인프라 시작
```bash
# Docker 컨테이너 시작 (MySQL, DynamoDB, MinIO)
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 2. 환경 설정
```bash
# 각 서비스별 환경 변수 설정
cp Auth/.env.example Auth/.env
cp Project_Service/.env.example Project_Service/.env
cp Team-BE/.env.example Team-BE/.env
cp Ai/.env.example Ai/.env
cp Support_Communication_Service/.env.example Support_Communication_Service/.env
```

### 3. 데이터베이스 마이그레이션
```bash
# Auth Service
cd Auth && poetry run alembic upgrade head

# Project Service  
cd Project_Service && poetry run alembic upgrade head

# Team Service
cd Team-BE && python -m alembic upgrade head

# AI Service
cd Ai && poetry run alembic upgrade head

# Support Service
cd Support_Communication_Service && poetry run alembic upgrade head
```

### 4. 서비스 시작

#### Windows (배치 파일 사용)
```bash
start_services.bat
```

#### Python 스크립트 사용
```bash
# 모든 서비스 시작
python start_services.py

# 개별 서비스 시작
python start_services.py "Auth Service"
python start_services.py "Project Service"
```

#### 수동 시작
```bash
# 각각 별도 터미널에서 실행
cd Auth && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd Project_Service && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
cd Team-BE && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
cd Ai && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
cd Support_Communication_Service && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## 🧪 테스트

### 통신 테스트
```bash
python test_msa_communication.py
```

### API 문서 확인
- Auth Service: http://localhost:8000/docs
- Project Service: http://localhost:8001/docs
- Team Service: http://localhost:8002/docs
- AI Service: http://localhost:8003/docs
- Support Service: http://localhost:8004/docs

## 📊 서비스별 역할

| 서비스 | 포트 | 주요 기능 | 데이터베이스 |
|--------|------|-----------|--------------|
| **Auth** | 8000 | 사용자 인증, 프로필 관리 | `portforge_auth` |
| **Project** | 8001 | 프로젝트, 지원서 관리 | `portforge_project` |
| **Team** | 8002 | 팀, 협업 도구 관리 | `portforge_team` |
| **AI** | 8003 | AI 테스트, 회의록 생성 | `portforge_ai` |
| **Support** | 8004 | 채팅, 고객지원 | `portforge_support` |

## 🔗 MSA 통신 예시

### 사용자 정보와 함께 프로젝트 조회
```python
from app.utils.msa_client import msa_client

# Project Service에서 Auth Service 호출
user_info = await msa_client.get_user_basic("user-123")
project_info = await msa_client.get_project_detail(1)
```

### 회의록 생성을 위한 채팅 로그 조회
```python
# AI Service에서 Support Service 호출
chat_logs = await msa_client.get_meeting_chat_logs(
    team_id=1,
    start_time="2024-01-01T10:00:00",
    end_time="2024-01-01T12:00:00"
)
```

## 🛠️ 개발 도구

### 데이터베이스 관리
- **MySQL**: `mysql -h localhost -u dev_user -pdev_password`
- **DynamoDB Admin**: http://localhost:8002
- **MinIO Console**: http://localhost:9001 (admin/password123)

### 모니터링
- **Prometheus Metrics**: http://localhost:800X/metrics
- **Health Check**: http://localhost:800X/health

## 🚨 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인 (Windows)
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

### 데이터베이스 연결 오류
```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs mysql
```

### 서비스 간 통신 오류
```bash
# 통신 테스트 실행
python test_msa_communication.py

# 개별 서비스 로그 확인
```

## 📚 추가 문서

- [MSA Database Guide](MSA_DATABASE_GUIDE.md)
- [MSA API Guide](MSA_API_GUIDE.md)
- [ERD Documentation](ERD_v2.dbml)

## 🎯 다음 단계

1. **프론트엔드 연동**: React 앱과 API 연결
2. **인증 시스템**: AWS Cognito 연동
3. **실시간 기능**: WebSocket 채팅 구현
4. **배포**: Docker 컨테이너화 및 클라우드 배포
5. **모니터링**: 로그 수집 및 성능 모니터링

---

🎉 **축하합니다!** Portforge MSA 환경이 성공적으로 구축되었습니다.