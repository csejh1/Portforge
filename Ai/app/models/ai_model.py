from sqlalchemy import Column, BigInteger, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Test(Base):
    __tablename__ = "tests"

    test_id = Column(BigInteger, primary_key=True, autoincrement=True)
    stack_name = Column(String(50), nullable=False) # Enum 대신 문자열로 처리 (간소화)
    question_json = Column(JSON, nullable=False)
    difficulty = Column(String(20), default="초급")
    source_prompt = Column(Text, nullable=True) # 로그용
    created_at = Column(DateTime, default=datetime.now)

class TestResult(Base):
    __tablename__ = "test_results"

    result_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False) # UUID -> String
    
    project_id = Column(BigInteger, nullable=True)
    application_id = Column(BigInteger, unique=True, nullable=True)
    
    test_type = Column(String(20), default="APPLICATION") # TYPE Enum -> String
    
    score = Column(BigInteger, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class MeetingSession(Base):
    __tablename__ = "meeting_sessions"
    
    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, nullable=False)
    project_id = Column(BigInteger, nullable=True)  # 프로젝트 ID 추가
    
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    
    status = Column(String(20), default="IN_PROGRESS")
    
    generated_report_id = Column(BigInteger, ForeignKey("generated_reports.report_id"), nullable=True)
    
    # Relationship
    report = relationship("GeneratedReport", back_populates="meeting_session")

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    report_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, nullable=False)
    project_id = Column(BigInteger, nullable=True)  # 프로젝트별 회의록 조회 지원
    created_by = Column(String(36), nullable=False) # UUID -> String
    
    report_type = Column(String(50), nullable=False) # MEETING_MINUTES, PROJECT_PLAN, WEEKLY_REPORT, PORTFOLIO
    status = Column(String(20), default="PENDING")  # PENDING, COMPLETED, FAILED - 비동기 생성 상태 추적
    model_id = Column(String(100), nullable=True)  # AI 모델 ID 기록용
    
    title = Column(String(200), nullable=True)
    # content 필드 제거 - S3에 JSON으로 저장하므로 DB에 중복 저장 불필요
    s3_key = Column(String(1024), nullable=True)  # S3에 JSON으로 저장된 회의록 내용 경로
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    meeting_session = relationship("MeetingSession", back_populates="report", uselist=False)

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
    updated_at = Column(DateTime, onupdate=datetime.now)
