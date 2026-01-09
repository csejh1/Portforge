"""
Support 서비스 테이블 생성 스크립트
동기 방식으로 테이블을 생성합니다.
실제 모델(app.models.support)과 동일한 구조로 정의합니다.
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
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_support"

def create_tables():
    """테이블 생성"""
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        Base = declarative_base()
        
        # 모델 정의 (app.models.support와 동일한 구조)
        from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, BigInteger, Text, Boolean
        from sqlalchemy.sql import func
        import enum
        
        class ProjectReportType(str, enum.Enum):
            REPORT = "REPORT"
            INQUIRY = "INQUIRY"
            BUG = "BUG"
        
        class ProjectReportStatus(str, enum.Enum):
            PENDING = "PENDING"
            IN_PROGRESS = "IN_PROGRESS"
            RESOLVED = "RESOLVED"
            DISMISSED = "DISMISSED"
        
        class EventCategory(str, enum.Enum):
            CONTEST = "CONTEST"
            HACKATHON = "HACKATHON"
        
        class ProjectReport(Base):
            __tablename__ = "project_reports"
            
            report_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False, index=True)
            project_id = Column(BigInteger, nullable=False, index=True)
            type = Column(SQLEnum(ProjectReportType), nullable=False)
            content = Column(Text, nullable=False)
            status = Column(SQLEnum(ProjectReportStatus), nullable=False, server_default=ProjectReportStatus.PENDING.value)
            resolution_note = Column(Text)
            created_at = Column(DateTime, nullable=False, server_default=func.now())
            updated_at = Column(DateTime)
        
        class Notification(Base):
            __tablename__ = "notifications"
            
            notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False, index=True)
            message = Column(Text)
            link = Column(Text)
            is_read = Column(Boolean, nullable=False, server_default="0")
            created_at = Column(DateTime, nullable=False, server_default=func.now())
        
        class Notice(Base):
            __tablename__ = "notices"
            
            notice_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(100), nullable=False)
            content = Column(Text, nullable=False)
            created_at = Column(DateTime, nullable=False, server_default=func.now())
            updated_at = Column(DateTime)
        
        class Banner(Base):
            __tablename__ = "banners"
            
            banner_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(100))
            link = Column(Text)
            is_active = Column(Boolean, nullable=False, server_default="1")
            created_at = Column(DateTime, nullable=False, server_default=func.now())
            updated_at = Column(DateTime)
        
        class Event(Base):
            __tablename__ = "events"
            
            event_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(100))
            category = Column(SQLEnum(EventCategory))
            event_description = Column(Text)
            image_url = Column(Text)
            event_date = Column(DateTime)
            created_at = Column(DateTime, nullable=False, server_default=func.now())
            updated_at = Column(DateTime)
        
        print("🔨 Creating Support tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Support tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
