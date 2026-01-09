"""
AI 서비스 테이블 생성 스크립트
동기 방식으로 테이블을 생성합니다.
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
        
        # 모델 정의
        from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, BigInteger, Text
        from sqlalchemy.sql import func
        import enum
        
        class TestType(str, enum.Enum):
            APPLICATION = "APPLICATION"
            SKILL_CHECK = "SKILL_CHECK"
        
        class ReportType(str, enum.Enum):
            MEETING_MINUTES = "MEETING_MINUTES"
            PROJECT_PLAN = "PROJECT_PLAN"
            WEEKLY_REPORT = "WEEKLY_REPORT"
            PORTFOLIO = "PORTFOLIO"
        
        class ReportStatus(str, enum.Enum):
            PENDING = "PENDING"
            COMPLETED = "COMPLETED"
            FAILED = "FAILED"
        
        class MeetingStatus(str, enum.Enum):
            IN_PROGRESS = "IN_PROGRESS"
            COMPLETED = "COMPLETED"
        
        class Test(Base):
            __tablename__ = "tests"
            
            test_id = Column(BigInteger, primary_key=True, autoincrement=True)
            stack_name = Column(String(50), nullable=False)
            question_json = Column(Text, nullable=False)
            difficulty = Column(String(20), default="초급")
            created_at = Column(DateTime, default=func.now())
        
        class TestResult(Base):
            __tablename__ = "test_results"
            
            result_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False)
            project_id = Column(BigInteger)
            application_id = Column(BigInteger)
            test_type = Column(SQLEnum(TestType), default=TestType.APPLICATION)
            score = Column(Integer)
            feedback = Column(Text)
            created_at = Column(DateTime, default=func.now())
        
        class MeetingSession(Base):
            __tablename__ = "meeting_sessions"
            
            session_id = Column(BigInteger, primary_key=True, autoincrement=True)
            team_id = Column(BigInteger, nullable=False)
            start_time = Column(DateTime, nullable=False)
            end_time = Column(DateTime)
            status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.IN_PROGRESS)
            generated_report_id = Column(BigInteger)
        
        class GeneratedReport(Base):
            __tablename__ = "generated_reports"
            
            report_id = Column(BigInteger, primary_key=True, autoincrement=True)
            team_id = Column(BigInteger, nullable=False)
            project_id = Column(BigInteger)
            created_by = Column(String(36), nullable=False)
            report_type = Column(SQLEnum(ReportType), nullable=False)
            status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
            title = Column(String(200))
            content = Column(Text)
            s3_key = Column(String(1024))
            created_at = Column(DateTime, default=func.now())
        
        class Portfolio(Base):
            __tablename__ = "portfolios"
            
            portfolio_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False)
            title = Column(String(200))
            content = Column(Text)
            s3_key = Column(String(1024))
            created_at = Column(DateTime, default=func.now())
        
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
