"""Team 서비스 테이블 생성 (동기 방식)"""
import sys
import os

# pymysql 설치 확인
try:
    import pymysql
except ImportError:
    print("📦 pymysql 설치 중...")
    os.system(f"{sys.executable} -m pip install pymysql cryptography -q")
    import pymysql

from sqlalchemy import create_engine, Column, String, DateTime, BigInteger, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

# 동기 엔진 생성
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_team"
engine = create_engine(DATABASE_URL, echo=True)

# Base 클래스
Base = declarative_base()

# Enum 정의
class TeamRole(str, enum.Enum):
    LEADER = "LEADER"
    MEMBER = "MEMBER"

class StackCategory(str, enum.Enum):
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DB = "DB"
    INFRA = "INFRA"
    DESIGN = "DESIGN"
    ETC = "ETC"

class MeetingStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ReportType(str, enum.Enum):
    MEETING_MINUTES = "MEETING_MINUTES"
    PROJECT_PLAN = "PROJECT_PLAN"
    WEEKLY_REPORT = "WEEKLY_REPORT"
    PORTFOLIO = "PORTFOLIO"

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# 모델 정의
class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)

class TeamMember(Base):
    __tablename__ = "team_members"
    
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), primary_key=True)
    user_id = Column(String(36), primary_key=True)
    role = Column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    position_type = Column(SQLEnum(StackCategory), nullable=False)
    updated_at = Column(DateTime, default=func.now())

class MeetingNote(Base):
    __tablename__ = "meeting_notes"
    
    note_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=func.now())

class SharedFile(Base):
    __tablename__ = "shared_files"
    
    file_id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, nullable=False)
    team_id = Column(BigInteger, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_url = Column(String(1024), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    uploaded_by = Column(String(36), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class Invitation(Base):
    __tablename__ = "invitations"
    
    invitation_id = Column(String(36), primary_key=True)
    project_id = Column(BigInteger, nullable=False)
    invitation_code = Column(String(20), unique=True, nullable=False)
    invitation_link = Column(String(1024), nullable=False)
    invited_by = Column(String(36), nullable=False)
    position_type = Column(SQLEnum(StackCategory), nullable=False)
    message = Column(Text)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Integer, default=0)
    used_by = Column(String(36))
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

class MeetingSession(Base):
    __tablename__ = "meeting_sessions"
    
    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.IN_PROGRESS)
    generated_report_id = Column(BigInteger)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    report_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    created_by = Column(String(36), nullable=False)
    type = Column(SQLEnum(ReportType), nullable=False)
    title = Column(String(200))
    content = Column(Text)
    s3_key = Column(String(1024))
    created_at = Column(DateTime, default=func.now())

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    
    created_by = Column(String(36), nullable=False)
    assignee_id = Column(String(36), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

if __name__ == "__main__":
    print("🔨 Creating Team tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Team tables created!")
