
"""
MSA 전체 서비스 시드 데이터 생성 스크립트
ERD v2 기준으로 작성됨

⚠️ 주의: 이 스크립트는 개발/테스트 환경에서만 사용하세요.
프로덕션 환경에서는 실제 Cognito 회원가입을 통해 사용자를 생성해야 합니다.
"""
import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# --- Configurations ---
DB_HOST = "localhost"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = "rootpassword"

# Database Names
DB_AUTH = "portforge_auth"
DB_PROJECT = "portforge_project"
DB_TEAM = "portforge_team"
DB_AI = "portforge_ai"
DB_SUPPORT = "portforge_support"

# Connection Strings
AUTH_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_AUTH}"
PROJECT_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_PROJECT}"
TEAM_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TEAM}"
AI_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_AI}"
SUPPORT_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SUPPORT}"

# --- Sample Data IDs ---
# ⚠️ 실제 사용 시 Cognito에서 발급받은 user_id(sub)로 교체 필요
SAMPLE_USER_ID = "sample-user-uuid-0001"
PROJECT_ID = 1

def seed_auth():
    """Auth 서비스: 샘플 데이터 (실제 사용자는 Cognito 회원가입으로 생성)"""
    print(f"🔹 Seeding Auth DB ({DB_AUTH})...")
    engine = create_engine(AUTH_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # ⚠️ 참고: 실제 사용자는 Cognito 회원가입을 통해 생성됩니다.
            # 이 시드 데이터는 DB 구조 테스트용입니다.
            print("  ℹ️  Auth 서비스는 Cognito 회원가입으로 사용자 생성")
            print("  ℹ️  회원가입: http://localhost:3000/#/signup")
            
            trans.commit()
            print("  ✅ Auth DB 준비 완료")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_auth: {e}")
            raise

def seed_project():
    """Project 서비스: 샘플 프로젝트 데이터"""
    print(f"🔹 Seeding Project DB ({DB_PROJECT})...")
    engine = create_engine(PROJECT_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            try:
                conn.execute(text("TRUNCATE TABLE applications"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE project_recruitment_positions"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE projects"))
            except: pass
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # ⚠️ 프로젝트는 실제 사용자가 생성해야 합니다.
            # 샘플 프로젝트는 user_id가 없으므로 생성하지 않습니다.
            print("  ℹ️  프로젝트는 로그인 후 직접 생성하세요")
            
            trans.commit()
            print("  ✅ Project DB 준비 완료")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_project: {e}")
            raise

def seed_team():
    """Team 서비스: 테이블 초기화"""
    print(f"🔹 Seeding Team DB ({DB_TEAM})...")
    engine = create_engine(TEAM_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            try:
                conn.execute(text("TRUNCATE TABLE team_members"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE tasks"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE teams"))
            except: pass
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # ⚠️ 팀은 프로젝트 생성 시 자동으로 생성됩니다.
            print("  ℹ️  팀은 프로젝트 생성 시 자동 생성됩니다")
            
            trans.commit()
            print("  ✅ Team DB 준비 완료")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_team: {e}")
            raise

def seed_ai():
    """AI 서비스: 샘플 테스트 문제"""
    print(f"🔹 Seeding AI DB ({DB_AI})...")
    engine = create_engine(AI_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            try:
                conn.execute(text("TRUNCATE TABLE test_results"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE tests"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE portfolios"))
            except: pass
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Tests 삽입 (샘플 문제)
            conn.execute(text("""
                INSERT INTO tests (stack_name, question_json, difficulty, created_at)
                VALUES 
                ('React', '{"q": "React의 Hook은 무엇인가요?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."}', '초급', NOW()),
                ('Spring', '{"q": "Spring Boot의 장점은?", "options": ["A", "B", "C", "D"], "answer": "B", "explanation": "..."}', '중급', NOW()),
                ('Nodejs', '{"q": "Node.js의 비동기 처리 방식은?", "options": ["A", "B", "C", "D"], "answer": "C", "explanation": "..."}', '초급', NOW())
            """))
            
            trans.commit()
            print("  ✅ AI 샘플 테스트 문제 생성 완료")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_ai: {e}")
            raise

def seed_support():
    """Support 서비스: 공지사항, 배너"""
    print(f"🔹 Seeding Support DB ({DB_SUPPORT})...")
    engine = create_engine(SUPPORT_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            try:
                conn.execute(text("TRUNCATE TABLE notifications"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE notices"))
            except: pass
            try:
                conn.execute(text("TRUNCATE TABLE banners"))
            except: pass
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Notices 삽입
            conn.execute(text("""
                INSERT INTO notices (title, content, created_at)
                VALUES 
                ('Portforge 서비스 오픈!', '프로젝트 팀 매칭 플랫폼 Portforge가 오픈했습니다. 회원가입 후 이용해주세요!', NOW()),
                ('신규 기능 안내', 'AI 기반 역량 테스트 기능이 추가되었습니다.', NOW())
            """))
            
            # Banners 삽입
            conn.execute(text("""
                INSERT INTO banners (title, link, is_active, created_at)
                VALUES 
                ('프로젝트 팀원 모집', '/projects', 1, NOW()),
                ('이벤트 참여하기', '/events', 1, NOW())
            """))
            
            trans.commit()
            print("  ✅ 공지사항 & 배너 생성 완료")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_support: {e}")
            raise

if __name__ == "__main__":
    try:
        import pymysql
    except ImportError:
        print("📦 Installing pymysql...")
        os.system("pip install pymysql cryptography")

    print("🚀 Starting MSA Data Seeding...")
    print("=" * 60)
    
    try:
        seed_auth()
        seed_project()
        seed_team()
        seed_ai()
        seed_support()
        
        print("=" * 60)
        print("✅ 데이터베이스 초기화 완료!")
        print("\n📋 시작하기:")
        print("   1. 서비스 시작: .\\start_services.bat")
        print("   2. 접속: http://localhost:3000")
        print("   3. 회원가입 후 로그인")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
