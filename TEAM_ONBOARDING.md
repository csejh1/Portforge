# Portforge 환경 구성

## 🔄 기존 팀원 - 코드 업데이트 (git pull 후)

```bash
# 1. 최신 코드 받기
git stash
git pull origin main
git stash pop

# 2. 프론트엔드 패키지 업데이트 (새 패키지 추가된 경우)
cd FE && npm install && cd ..

# 3. 서비스 재시작
start_services.bat
```

> ⚠️ DB 스키마가 변경된 경우에만 `reset_and_seed_all.bat` 실행 필요

---

## 🆕 신규 팀원 - 처음 환경 구성

### 사전 설치 필요
- Python 3.11+
- Poetry
- Node.js 18+
- Docker Desktop

### 1. 클론
```bash
git clone https://github.com/csejh1/Portforge.git
cd Portforge
```

### 2. 의존성 설치
```bash
install_all.bat
```

### 3. 환경변수 복사
```bash
copy Auth\.env.example Auth\.env
copy Project_Service\.env.example Project_Service\.env
copy Team-BE\.env.example Team-BE\.env
copy Ai\.env.example Ai\.env
copy Support_Communication_Service\.env.example Support_Communication_Service\.env
```

### 4. Docker 실행
```bash
docker compose up -d
```
> MySQL healthy 될 때까지 30초 대기

### 5. DB 초기화
```bash
reset_and_seed_all.bat
```

### 6. 서비스 시작
```bash
start_services.bat
```

### 7. 접속
- http://localhost:3000

### 8. 로그인
| 이메일 | 비밀번호 |
|--------|----------|
| admin@example.com | devpass123 |
| member@example.com | devpass123 |
| member2@example.com | devpass123 |

---

## 문제 발생 시 전체 초기화
```bash
docker compose down -v
docker compose up -d
reset_and_seed_all.bat
start_services.bat
```
