# Portforge 환경 구성

## 사전 설치 필요
- Python 3.11+
- Poetry
- Node.js 18+
- Docker Desktop

---

## 1. 클론
```bash
git clone https://github.com/csejh1/Portforge.git
cd Portforge
```

## 2. 의존성 설치
```bash
install_all.bat
```

## 3. 환경변수 복사
```bash
copy Auth\.env.example Auth\.env
copy Project_Service\.env.example Project_Service\.env
copy Team-BE\.env.example Team-BE\.env
copy Ai\.env.example Ai\.env
copy Support_Communication_Service\.env.example Support_Communication_Service\.env
```

## 4. Docker 실행
```bash
docker compose up -d
```
> MySQL healthy 될 때까지 30초 대기

## 5. DB 초기화
```bash
reset_and_seed_all.bat
```

## 6. 서비스 시작
```bash
start_services.bat
```

## 7. 접속
- http://localhost:3000

## 8. 로그인
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
