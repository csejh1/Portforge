#!/usr/bin/env python3
"""
Team Service 개발 서버 실행 스크립트
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Team Service 개발 서버 시작...")
    print("📋 API 문서: http://localhost:8002/docs")
    print("🔍 ReDoc: http://localhost:8002/redoc")
    print("💚 Health Check: http://localhost:8002/health")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,  # 새로운 포트 사용
        reload=True,
        log_level="info"
    )

    