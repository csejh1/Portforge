
"""
MSA 전체 서비스 시드 데이터 생성 스크립트
ERD v2 기준으로 작성됨
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

# --- Test Data ---
ADMIN_ID = "admin-uuid-0000"
MEMBER_ID = "user2-uuid-5678"
MEMBER2_ID = "user3-uuid-9999"
PROJECT_ID = 1

def seed_auth():
    """Auth 서비스: users, user_stacks"""
    print(f"🔹 Seeding Auth DB ({DB_AUTH})...")
    engine = create_engine(AUTH_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Users 삽입
            conn.execute(text(f"""
                INSERT INTO users (user_id, email, nickname, role, test_count, created_at)
                VALUES 
                ('{ADMIN_ID}', 'admin@example.com', 'AdminLeader', 'ADMIN', 99, NOW()),
                ('{MEMBER_ID}', 'member@example.com', 'TeamMember', 'USER', 5, NOW()),
                ('{MEMBER2_ID}', 'member2@example.com', 'Designer', 'USER', 3, NOW())
                ON DUPLICATE KEY UPDATE nickname=VALUES(nickname), role=VALUES(role)
            """))
            
            # User Stacks 삽입
            conn.execute(text(f"""
                INSERT INTO user_stacks (user_id, position_type, stack_name, created_at)
                VALUES 
                ('{ADMIN_ID}', 'BACKEND', 'Spring', NOW()),
                ('{ADMIN_ID}', 'BACKEND', 'MySQL', NOW()),
                ('{MEMBER_ID}', 'BACKEND', 'Nodejs', NOW()),
                ('{MEMBER_ID}', 'BACKEND', 'PostgreSQL', NOW()),
                ('{MEMBER2_ID}', 'DESIGN', 'Figma', NOW()),
                ('{MEMBER2_ID}', 'FRONTEND', 'React', NOW())
                ON DUPLICATE KEY UPDATE stack_name=VALUES(stack_name)
            """))
            
            trans.commit()
            print("  ✅ Users & User Stacks seeded.")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_auth: {e}")
            raise

def seed_project():
    """Project 서비스: projects, project_recruitment_positions, applications"""
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
            
            # Projects 삽입 (ERD 기준)
            conn.execute(text(f"""
                INSERT INTO projects (project_id, user_id, title, description, type, method, status, start_date, end_date, test_required, views, created_at)
                VALUES 
                ({PROJECT_ID}, '{ADMIN_ID}', 'MSA Portforge Refactoring', 'MSA 구조로 리팩토링하는 프로젝트입니다.', 'PROJECT', 'ONLINE', 'RECRUITING', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), TRUE, 0, NOW())
            """))

            # Project Recruitment Positions 삽입
            conn.execute(text(f"""
                INSERT INTO project_recruitment_positions (project_id, position_type, required_stacks, target_count, current_count, recruitment_deadline, created_at)
                VALUES 
                ({PROJECT_ID}, 'BACKEND', 'Spring,Nodejs', 2, 1, DATE_ADD(CURDATE(), INTERVAL 7 DAY), NOW()),
                ({PROJECT_ID}, 'FRONTEND', 'React,TypeScript', 2, 0, DATE_ADD(CURDATE(), INTERVAL 7 DAY), NOW()),
                ({PROJECT_ID}, 'DESIGN', 'Figma', 1, 0, DATE_ADD(CURDATE(), INTERVAL 7 DAY), NOW())
            """))

            # Applications 삽입 (prefer_stacks 컬럼 제거됨)
            conn.execute(text(f"""
                INSERT INTO applications (project_id, user_id, position_type, message, status, created_at)
                VALUES 
                ({PROJECT_ID}, '{MEMBER_ID}', 'BACKEND', '열심히하겠습니다!', 'ACCEPTED', NOW()),
                ({PROJECT_ID}, '{MEMBER2_ID}', 'DESIGN', '디자인 경험 많습니다!', 'PENDING', NOW())
            """))
            
            trans.commit()
            print("  ✅ Projects, Positions & Applications seeded.")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_project: {e}")
            raise

def seed_team():
    """Team 서비스: teams, team_members, tasks"""
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
            
            # Teams 삽입
            conn.execute(text(f"""
                INSERT INTO teams (project_id, name, s3_key, created_at)
                VALUES ({PROJECT_ID}, 'MSA Team', 'teams/{PROJECT_ID}/', NOW())
            """))
            
            # Get Team ID
            team_res = conn.execute(text(f"SELECT team_id FROM teams WHERE project_id={PROJECT_ID}"))
            team_id = team_res.scalar()
            
            if team_id:
                # Team Members 삽입
                conn.execute(text(f"""
                    INSERT INTO team_members (team_id, user_id, role, position_type, updated_at)
                    VALUES 
                    ({team_id}, '{ADMIN_ID}', 'LEADER', 'BACKEND', NOW()),
                    ({team_id}, '{MEMBER_ID}', 'MEMBER', 'BACKEND', NOW())
                """))

                # Tasks 삽입
                conn.execute(text(f"""
                    INSERT INTO tasks (project_id, title, description, status, priority, created_by, assignee_id, due_date, created_at)
                    VALUES
                    ({PROJECT_ID}, '기획서 작성', '노션에 기획서 정리', 'DONE', 'HIGH', '{ADMIN_ID}', '{ADMIN_ID}', DATE_ADD(NOW(), INTERVAL 1 DAY), NOW()),
                    ({PROJECT_ID}, 'DB 설계', 'ERD 작성 및 공유', 'IN_PROGRESS', 'HIGH', '{ADMIN_ID}', '{MEMBER_ID}', DATE_ADD(NOW(), INTERVAL 3 DAY), NOW()),
                    ({PROJECT_ID}, 'API 구현', 'User API 구현', 'TODO', 'MEDIUM', '{ADMIN_ID}', '{MEMBER_ID}', DATE_ADD(NOW(), INTERVAL 7 DAY), NOW())
                """))
            
            trans.commit()
            print("  ✅ Teams, Members & Tasks seeded.")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_team: {e}")
            raise

def seed_ai():
    """AI 서비스: tests, test_results, portfolios"""
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
            
            # Test Results 삽입 (MEMBER가 테스트 응시)
            conn.execute(text(f"""
                INSERT INTO test_results (user_id, project_id, test_type, score, feedback, created_at)
                VALUES 
                ('{MEMBER_ID}', {PROJECT_ID}, 'APPLICATION', 85, '우수한 성적입니다!', NOW())
            """))
            
            trans.commit()
            print("  ✅ Tests & Test Results seeded.")
        except Exception as e:
            trans.rollback()
            print(f"  ❌ Error in seed_ai: {e}")
            raise

def seed_support():
    """Support 서비스: notifications, notices, banners"""
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
            
            # Notifications 삽입
            conn.execute(text(f"""
                INSERT INTO notifications (user_id, message, link, is_read, created_at)
                VALUES 
                ('{ADMIN_ID}', '새로운 지원자가 있습니다!', '/projects/{PROJECT_ID}/applications', 0, NOW()),
                ('{MEMBER_ID}', '지원이 승인되었습니다!', '/projects/{PROJECT_ID}', 0, NOW())
            """))
            
            # Notices 삽입
            conn.execute(text("""
                INSERT INTO notices (title, content, created_at)
                VALUES 
                ('서비스 점검 안내', '2026년 1월 10일 새벽 2시~4시 서비스 점검이 있습니다.', NOW()),
                ('신규 기능 출시', 'AI 포트폴리오 자동 생성 기능이 추가되었습니다!', NOW())
            """))
            
            # Banners 삽입
            conn.execute(text("""
                INSERT INTO banners (title, link, is_active, created_at)
                VALUES 
                ('2026 신년 이벤트', '/events/newyear', 1, NOW()),
                ('프로젝트 매칭 서비스', '/projects', 1, NOW())
            """))
            
            trans.commit()
            print("  ✅ Notifications, Notices & Banners seeded.")
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
        print("✅ All data seeded successfully!")
        print("\n📋 Test Accounts:")
        print(f"   👤 ADMIN:  {ADMIN_ID} (admin@example.com)")
        print(f"   👤 MEMBER: {MEMBER_ID} (member@example.com)")
        print(f"   👤 MEMBER2: {MEMBER2_ID} (member2@example.com)")
        print(f"\n📊 Project ID: {PROJECT_ID}")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
