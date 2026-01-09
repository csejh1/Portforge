from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # [추가] CORS 미들웨어

# 팀 템플릿에 있는 모듈들 (파일이 없다면 에러가 날 수 있으니 확인 필요)
try:
    from app.core.exceptions import BusinessException
    from app.core.middleware import LoggingMiddleware
    from prometheus_fastapi_instrumentator import Instrumentator
    from app.controllers import all_routers
except ImportError:
    # 혹시 모듈이 없을 경우를 대비한 더미 설정 (에러 방지용)
    BusinessException = Exception
    LoggingMiddleware = None
    all_routers = []
    print("⚠️ 경고: 팀 템플릿 모듈(core, controllers)을 찾을 수 없습니다.")

# [추가] 방금 만든 Auth 라우터 임포트
from app.api.auth import router as auth_router
from app.api.users import router as users_router  # 새로 추가

app = FastAPI(title="Base-Template")

# =================================================================
# 1. CORS 설정 (프론트엔드 연동 필수)
# =================================================================
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================
# 2. 미들웨어 및 모니터링 (팀 템플릿 유지)
# =================================================================
if LoggingMiddleware:
    app.add_middleware(LoggingMiddleware)

Instrumentator().instrument(app).expose(app)

# =================================================================
# 3. 라우터 등록
# =================================================================
# (1) 팀 템플릿에 정의된 라우터들 자동 등록
for router, prefix, tag in all_routers:
    app.include_router(router, prefix=prefix, tags=[tag])

# (2) [추가] 우리가 만든 Auth 라우터 수동 등록
app.include_router(auth_router)  # /auth 경로로 자동 연결됨
app.include_router(users_router)  # /users 경로로 자동 연결됨

# =================================================================
# 4. 예외 핸들러 (팀 템플릿 유지)
# =================================================================
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