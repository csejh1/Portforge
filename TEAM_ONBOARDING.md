# Portforge 환경 구성

## 🆕 신규 팀원 - 원클릭 설치

### 사전 설치 필요
- Python 3.11+ ([다운로드](https://www.python.org/downloads/))
- Node.js 18+ ([다운로드](https://nodejs.org/))
- Docker Desktop ([다운로드](https://www.docker.com/products/docker-desktop/))

### 설치
```bash
git clone https://github.com/csejh1/Portforge.git
cd Portforge
.\setup.bat
```

### ⚠️ 중요: Cognito 설정
회원가입/로그인이 작동하려면 `Auth/.env` 파일에 실제 Cognito 값을 설정해야 합니다.
팀장에게 아래 값들을 받아서 `Auth/.env`에 입력하세요:
- `COGNITO_USERPOOL_ID`
- `COGNITO_APP_CLIENT_ID`
- `COGNITO_DOMAIN` (소셜 로그인 사용 시)

---

## 🔄 기존 팀원 - 코드 업데이트

```bash
git stash
git pull origin main
git stash pop
.\start_services.bat
```

> DB 스키마 변경 시에만: `.\reset_and_seed_all.bat`

---

## 시작하기
1. 서비스 시작: `.\start_services.bat`
2. 접속: http://localhost:3000
3. 회원가입 (이메일 인증 필요)
4. 로그인 후 프로젝트 생성/참여

---

## 문제 발생 시
```bash
docker compose down -v
.\setup.bat
```
