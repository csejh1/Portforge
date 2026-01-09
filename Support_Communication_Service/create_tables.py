"""
Support 서비스 테이블 생성 스크립트
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
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_support"

def create_tables():
    """테이블 생성"""
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        Base = declarative_base()
        
        # 모델 정의
        from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, BigInteger, Text, Boolean
        from sqlalchemy.sql import func
        import enum
        
        class ReportStatus(str, enum.Enum):
            PENDING = "PENDING"
            RESOLVED = "RESOLVED"
            REJECTED = "REJECTED"
        
        class ProjectReport(Base):
            __tablename__ = "project_reports"
            
            report_id = Column(BigInteger, primary_key=True, autoincrement=True)
            project_id = Column(BigInteger, nullable=False)
            reporter_id = Column(String(36), nullable=False)
            reason = Column(Text, nullable=False)
            status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
            created_at = Column(DateTime, default=func.now())
            resolved_at = Column(DateTime)
        
        class Notification(Base):
            __tablename__ = "notifications"
            
            notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(String(36), nullable=False)
            message = Column(Text, nullable=False)
            link = Column(String(1024))
            is_read = Column(Boolean, default=False)
            created_at = Column(DateTime, default=func.now())
        
        class Notice(Base):
            __tablename__ = "notices"
            
            notice_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(200), nullable=False)
            content = Column(Text, nullable=False)
            created_at = Column(DateTime, default=func.now())
            updated_at = Column(DateTime)
        
        class Banner(Base):
            __tablename__ = "banners"
            
            banner_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(200), nullable=False)
            image_url = Column(String(1024))
            link = Column(String(1024))
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime, default=func.now())
        
        class Event(Base):
            __tablename__ = "events"
            
            event_id = Column(BigInteger, primary_key=True, autoincrement=True)
            title = Column(String(200), nullable=False)
            category = Column(String(50))
            description = Column(Text)
            image_url = Column(String(1024))
            start_date = Column(DateTime)
            end_date = Column(DateTime)
            method = Column(String(50))
            created_at = Column(DateTime, default=func.now())
        
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
