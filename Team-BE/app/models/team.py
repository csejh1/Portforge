from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TeamRole, StackCategory, MeetingStatus, ReportType

class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, unique=True, nullable=False)  # 외래키 제약조건 제거 (다른 서비스)
    name = Column(String(50), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
    
    # 관계 설정 (같은 서비스 내에서만)
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    meeting_notes = relationship("MeetingNote", back_populates="team", cascade="all, delete-orphan")
    meeting_sessions = relationship("MeetingSession", back_populates="team", cascade="all, delete-orphan")
    generated_reports = relationship("GeneratedReport", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), primary_key=True)
    user_id = Column(String(36), primary_key=True)
    role = Column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    position_type = Column(SQLEnum(StackCategory), nullable=False)
    updated_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    team = relationship("Team", back_populates="members")

class MeetingNote(Base):
    __tablename__ = "meeting_notes"
    
    note_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    team = relationship("Team", back_populates="meeting_notes")

# 칸반 보드용 Task 모델은 app.models.task에 정의됨

# 파일 공유용 SharedFile 모델
class SharedFile(Base):
    __tablename__ = "shared_files"
    
    file_id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, nullable=False)
    team_id = Column(BigInteger, nullable=True)  # team_id 추가 (MSA 호환)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_url = Column(String(1024), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    uploaded_by = Column(String(36), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

# 팀원 초대용 Invitation 모델
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
    is_used = Column(Integer, default=0)  # 0: 미사용, 1: 사용됨
    used_by = Column(String(36))
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


# 회의 세션 모델 (AI 회의록 생성용)
class MeetingSession(Base):
    __tablename__ = "meeting_sessions"
    
    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, comment="종료 시점 기록")
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.IN_PROGRESS)
    generated_report_id = Column(BigInteger)  # 외래키 제약조건 제거 (MSA)
    
    # 관계 설정
    team = relationship("Team", back_populates="meeting_sessions")


# AI 생성 리포트 모델
class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    report_id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(BigInteger, ForeignKey("teams.team_id"), nullable=False)
    created_by = Column(String(36), nullable=False)  # 외래키 제약 조건 제거 (MSA)
    type = Column(SQLEnum(ReportType), nullable=False)
    title = Column(String(200), comment="OO월 OO일 회의록 / OO 프로젝트 기획서")
    content = Column(Text, comment="본문 내용 (짧은 경우)")
    s3_key = Column(String(1024), comment="PDF/Docx 파일 경로")
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    team = relationship("Team", back_populates="generated_reports")