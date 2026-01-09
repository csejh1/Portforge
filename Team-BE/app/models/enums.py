from enum import Enum

# 사용자 역할
class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

# 팀 역할
class TeamRole(Enum):
    LEADER = "LEADER"
    MEMBER = "MEMBER"

# 프로젝트 타입
class ProjectType(Enum):
    PROJECT = "PROJECT"
    STUDY = "STUDY"

# 프로젝트 방식
class ProjectMethod(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MIXED = "MIXED"

# 프로젝트 상태
class ProjectStatus(Enum):
    RECRUITING = "RECRUITING"
    PROCEEDING = "PROCEEDING"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"

# 지원 상태
class ApplicationStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

# 스택 카테고리
class StackCategory(Enum):
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DB = "DB"
    INFRA = "INFRA"
    DESIGN = "DESIGN"
    ETC = "ETC"

# 기술 스택 (주요 기술들만)
class TechStack(Enum):
    # Frontend
    REACT = "React"
    VUE = "Vue"
    NEXTJS = "Nextjs"
    TYPESCRIPT = "TypeScript"
    JAVASCRIPT = "JavaScript"
    
    # Backend
    JAVA = "Java"
    SPRING = "Spring"
    NODEJS = "Nodejs"
    PYTHON = "Python"
    DJANGO = "Django"
    FLASK = "Flask"
    
    # Database
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"
    MONGODB = "MongoDB"
    REDIS = "Redis"
    
    # Infrastructure
    AWS = "AWS"
    DOCKER = "Docker"
    KUBERNETES = "Kubernetes"
    
    # Design
    FIGMA = "Figma"
    PHOTOSHOP = "Photoshop"

# 회의 상태
class MeetingStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# 리포트 타입
class ReportType(Enum):
    MEETING_MINUTES = "MEETING_MINUTES"
    PROJECT_PLAN = "PROJECT_PLAN"
    PROGRESS_REPORT = "PROGRESS_REPORT"