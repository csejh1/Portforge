"""AI 서비스 테이블 생성 (동기 방식)"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# 동기 엔진 생성
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_ai"
engine = create_engine(DATABASE_URL, echo=True)

# Base 클래스
Base = declarative_base()

# 모델 임포트 (Base에 자동 등록됨)
from app.models.ai_model import Test, TestResult, MeetingSession, GeneratedReport, Portfolio

if __name__ == "__main__":
    print("🔨 Creating AI tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ AI tables created!")
