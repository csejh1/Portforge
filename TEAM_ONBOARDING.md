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
setup.bat
```

끝! 스크립트가 모든 것을 자동으로 설정합니다.

---

## 🔄 기존 팀원 - 코드 업데이트

```bash
git stash
git pull origin main
git stash pop
start_services.bat
```

> DB 스키마 변경 시에만: `reset_and_seed_all.bat`

---

## 테스트 계정
| 이메일 | 비밀번호 |
|--------|----------|
| admin@example.com | devpass123 |
| member@example.com | devpass123 |
| member2@example.com | devpass123 |

---

## 문제 발생 시
```bash
docker compose down -v
setup.bat
```
