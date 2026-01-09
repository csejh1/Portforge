from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

# 선택적 모듈 로드 (없어도 서비스 실행 가능)
BusinessException = None
LoggingMiddleware = None
all_routers = []

try:
    from app.core.exceptions import BusinessException
except ImportError:
    logger.warning("⚠️ app.core.exceptions 모듈을 찾을 수 없습니다.")

try:
    from app.core.middleware import LoggingMiddleware
except ImportError:
    logger.warning("⚠️ app.core.middleware 모듈을 찾을 수 없습니다.")

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ prometheus_fastapi_instrumentator가 설치되지 않았습니다.")
    PROMETHEUS_AVAILABLE = False

try:
    from app.controllers import all_routers
except ImportError:
    logger.warning("⚠️ app.controllers 모듈을 찾을 수 없습니다.")

# Auth 라우터 임포트
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(title="Portforge-Auth-Service")

# =================================================================
# 1. CORS 설정
# =================================================================
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================
# 2. 미들웨어 및 모니터링 (선택적)
# =================================================================
if LoggingMiddleware:
    app.add_middleware(LoggingMiddleware)

if PROMETHEUS_AVAILABLE:
    try:
        Instrumentator().instrument(app).expose(app)
    except Exception as e:
        logger.warning(f"⚠️ Prometheus 설정 실패: {e}")

# =================================================================
# 3. 라우터 등록
# =================================================================
for router, prefix, tag in all_routers:
    app.include_router(router, prefix=prefix, tags=[tag])

app.include_router(auth_router)
app.include_router(users_router)

# =================================================================
# 4. 예외 핸들러
# =================================================================
if BusinessException:
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.error_code.http_status,
            content={
                "success": False,
                "code": exc.error_code.biz_code,
                "message": exc.message,
                "data": None
            }
        )

@app.get("/")
async def root():
    return {"message": "Auth Service is running", "service": "auth-service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}