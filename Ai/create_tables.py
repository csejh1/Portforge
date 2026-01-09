"""
AI 서비스 테이블 생성 스크립트
동기 방식으로 테이블을 생성합니다.
실제 모델(app.models.ai_model)과 동일한 구조로 정의합니다.
"""
import sys
import os

# pymysql 설치 확인
try:
    import pymysql
except ImportError:
    print("📦 pymysql 설치 중...")
    os.system(f"{sys.executable} -m pip install pymysql cryptography -q")
    import pymysql

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# 동기 엔진 생성 (pymysql 사용)
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_ai"

def create_tables():
    """테이블 생성"""
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        Base = declarative_base()
        
        # 모델 정의 (app.models.ai_model과 동일한 구조)
        from sqlalchemy import Column, String, DateTime, BigInteger, Text, Boolean, JSON, ForeignKey
        from datetime import datetime
        
        class Test(Base):
            __tablename__ = "tests"
            
            test_id = Column(BigInteger, primary_key=True, autoincrement=True)
            stack_name = Column(String(50), nullable=False)
            question_json = Column(JSON, nullable=False)
            difficulty = Column(String(20), default="초급")
            source_prompt = Column(Text, nullable=True)
            created_at = Column(DateTime, default=datetime.now)
        
        class TestResult(Base):
            __tablename__ = "test_results"
            
            result_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False)
            project_id = Column(BigInteger, nullable=True)
            application_id = Column(BigInteger, unique=True, nullable=True)
            test_type = Column(String(20), default="APPLICATION")
            score = Column(BigInteger, nullable=True)
            feedback = Column(Text, nullable=True)
            created_at = Column(DateTime, default=datetime.now)
        
        class GeneratedReport(Base):
            __tablename__ = "generated_reports"
            
            report_id = Column(BigInteger, primary_key=True, autoincrement=True)
            team_id = Column(BigInteger, nullable=False)
            project_id = Column(BigInteger, nullable=True)
            created_by = Column(String(36), nullable=False)
            report_type = Column(String(50), nullable=False)
            status = Column(String(20), default="PENDING")
            model_id = Column(String(100), nullable=True)
            title = Column(String(200), nullable=True)
            s3_key = Column(String(1024), nullable=True)
            created_at = Column(DateTime, default=datetime.now)
        
        class MeetingSession(Base):
            __tablename__ = "meeting_sessions"
            
            session_id = Column(BigInteger, primary_key=True, autoincrement=True)
            team_id = Column(BigInteger, nullable=False)
            project_id = Column(BigInteger, nullable=True)
            start_time = Column(DateTime, nullable=False, default=datetime.now)
            end_time = Column(DateTime, nullable=True)
            status = Column(String(20), default="IN_PROGRESS")
            generated_report_id = Column(BigInteger, ForeignKey("generated_reports.report_id"), nullable=True)
        
        class Portfolio(Base):
            __tablename__ = "portfolios"
            
            portfolio_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False)
            project_id = Column(BigInteger, nullable=False)
            title = Column(String(200), default='프로젝트 회고록')
            summary = Column(Text, nullable=True)
            role_description = Column(Text, nullable=True)
            problem_solving = Column(Text, nullable=True)
            tech_stack_usage = Column(Text, nullable=True)
            growth_point = Column(Text, nullable=True)
            thumbnail_url = Column(String(1024), nullable=True)
            is_public = Column(Boolean, default=True)
            created_at = Column(DateTime, default=datetime.now)
            updated_at = Column(DateTime)
        
        print("🔨 Creating AI tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ AI tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
