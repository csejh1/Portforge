"""
Auth 서비스 테이블 생성 스크립트
동기 방식으로 테이블을 생성합니다.
실제 모델(app.models.user)과 동일한 구조로 정의합니다.
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
DATABASE_URL = "mysql+pymysql://root:rootpassword@localhost:3306/portforge_auth"

def create_tables():
    """테이블 생성"""
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        Base = declarative_base()
        
        # 모델 정의 (app.models.user와 동일한 구조)
        from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, BigInteger, Text, JSON
        from sqlalchemy.dialects.mysql import CHAR
        from sqlalchemy.sql import func
        import enum
        
        class UserRole(str, enum.Enum):
            USER = "USER"
            ADMIN = "ADMIN"
        
        class StackCategory(str, enum.Enum):
            FRONTEND = "FRONTEND"
            BACKEND = "BACKEND"
            DB = "DB"
            INFRA = "INFRA"
            DESIGN = "DESIGN"
            ETC = "ETC"
        
        # TechStack enum (실제 모델과 동일)
        class TechStack(str, enum.Enum):
            # Frontend
            React = "React"
            Vue = "Vue"
            Nextjs = "Nextjs"
            Svelte = "Svelte"
            Angular = "Angular"
            TypeScript = "TypeScript"
            JavaScript = "JavaScript"
            TailwindCSS = "TailwindCSS"
            StyledComponents = "StyledComponents"
            Redux = "Redux"
            Recoil = "Recoil"
            Vite = "Vite"
            Webpack = "Webpack"
            # Backend
            Java = "Java"
            Spring = "Spring"
            Nodejs = "Nodejs"
            Nestjs = "Nestjs"
            Go = "Go"
            Python = "Python"
            Django = "Django"
            Flask = "Flask"
            Express = "Express"
            php = "php"
            Laravel = "Laravel"
            GraphQL = "GraphQL"
            RubyOnRails = "RubyOnRails"
            CSharp = "CSharp"
            DotNET = "DotNET"
            # Database
            MySQL = "MySQL"
            PostgreSQL = "PostgreSQL"
            MongoDB = "MongoDB"
            Redis = "Redis"
            Oracle = "Oracle"
            SQLite = "SQLite"
            MariaDB = "MariaDB"
            Cassandra = "Cassandra"
            DynamoDB = "DynamoDB"
            FirebaseFirestore = "FirebaseFirestore"
            Prisma = "Prisma"
            # Infrastructure
            AWS = "AWS"
            Docker = "Docker"
            Kubernetes = "Kubernetes"
            GCP = "GCP"
            Azure = "Azure"
            Terraform = "Terraform"
            Jenkins = "Jenkins"
            GithubActions = "GithubActions"
            Nginx = "Nginx"
            Linux = "Linux"
            Vercel = "Vercel"
            Netlify = "Netlify"
            # Design
            Figma = "Figma"
            AdobeXD = "AdobeXD"
            Sketch = "Sketch"
            Canva = "Canva"
            Photoshop = "Photoshop"
            Illustrator = "Illustrator"
            Blender = "Blender"
            UIUX_Design = "UIUX_Design"
            Branding = "Branding"
            # ETC
            Git = "Git"
            Slack = "Slack"
            Jira = "Jira"
            Notion = "Notion"
            Discord = "Discord"
            Postman = "Postman"
            Swagger = "Swagger"
            Zeplin = "Zeplin"
        
        class User(Base):
            __tablename__ = "users"
            
            user_id = Column(CHAR(36), primary_key=True)
            email = Column(String(100), unique=True, nullable=False)
            nickname = Column(String(20), nullable=False)
            role = Column(SQLEnum(UserRole), default=UserRole.USER)
            profile_image_url = Column(Text, nullable=True)
            liked_project_ids = Column(JSON, nullable=True)
            test_count = Column(Integer, default=5)
            created_at = Column(DateTime, default=func.now())
            updated_at = Column(DateTime, nullable=True)
        
        class UserStack(Base):
            __tablename__ = "user_stacks"
            
            stack_id = Column(BigInteger, primary_key=True, autoincrement=True)
            user_id = Column(CHAR(36), nullable=False, index=True)
            position_type = Column(SQLEnum(StackCategory), nullable=False)
            # stack_name을 String으로 변경 (ENUM 대신) - 시드 데이터 호환성
            stack_name = Column(String(50), nullable=False)
            created_at = Column(DateTime, default=func.now())
            updated_at = Column(DateTime, default=func.now())
        
        print("🔨 Creating Auth tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Auth tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
