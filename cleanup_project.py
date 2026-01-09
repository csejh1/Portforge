"""
Portforge 프로젝트 정리 스크립트
팀 공유를 위해 불필요한 파일들을 삭제합니다.
(.gitignore에 포함된 파일은 제외 - 어차피 Git에 안 올라감)
"""
import os
import shutil
from pathlib import Path

# ============================================================
# 삭제할 폴더 목록
# ============================================================
FOLDERS_TO_DELETE = [
    # 백업 폴더 (중복)
    "Ai_latest",
    "FE_latest",
    "Support_Communication_Service_latest",
    "Team_BE_latest",
    
    # shared 폴더 (MSA에서 부적절 - 실제로 사용되지 않음)
    # 각 서비스는 자체 app/utils/ 사용
    "shared",
    
    # 빈 폴더
    "Ai/scripts",
    "Team-BE/Template-Repo",
]

# ============================================================
# 삭제할 파일 목록
# ============================================================
FILES_TO_DELETE = [
    # ----------------------------------------------------------
    # 루트 - 불필요한 문서 (개발 완료 후 불필요)
    # ----------------------------------------------------------
    "MSA_ANALYSIS_REPORT.md",
    "MSA_API_GUIDE.md",
    "MSA_DATABASE_GUIDE.md",
    "MSA_RESILIENCE_GUIDE.md",
    "MSA_SEPARATION_GUIDE.md",
    "DATABASE_RESET_GUIDE.md",
    "exAPI 명세서 (2).html",
    
    # ----------------------------------------------------------
    # 루트 - 중복/대체된 스크립트
    # ----------------------------------------------------------
    "create_all_tables.py",      # .bat으로 대체
    "reset_and_seed_all.py",     # .bat으로 대체
    "test_simple_service.py",    # test_msa_communication.py로 대체
    "seed_chat_data.py",         # 임시 테스트
    
    # ----------------------------------------------------------
    # Ai - 임시/중복 스크립트
    # ----------------------------------------------------------
    "Ai/init_dynamodb.py",       # 루트 create_dynamodb_tables.py로 대체
    "Ai/init_dynamodb_aws.py",   # 루트 create_dynamodb_tables.py로 대체
    "Ai/check_db.py",            # 디버깅용 임시
    "Ai/cleanup_reports.py",     # 유지보수용 임시
    "Ai/reset_alembic.py",       # 유지보수용 임시
    "Ai/seeder.py",              # seed_all.py로 통합
    "Ai/test_pipeline.py",       # 테스트용 임시
    
    # ----------------------------------------------------------
    # Project_Service - 임시/테스트 파일
    # ----------------------------------------------------------
    "Project_Service/simple_server.py",
    "Project_Service/minimal_swagger.py",
    "Project_Service/test_swagger.py",
    "Project_Service/create_tables.sql",      # create_tables.py로 대체
    "Project_Service/MYSQL_SETUP_COMPLETE.md",
    "Project_Service/db_init.py",             # create_tables.py로 대체
    
    # ----------------------------------------------------------
    # Support_Communication_Service - 검증용 임시 파일
    # ----------------------------------------------------------
    "Support_Communication_Service/verify_app.py",
    "Support_Communication_Service/verify_chat_impl.py",
    "Support_Communication_Service/verify_chat.py",
    
    # ----------------------------------------------------------
    # Auth - 중복 스크립트 (reset_all_db.py로 대체)
    # ----------------------------------------------------------
    "Auth/drop_tables.py",
    "Auth/reset_db.py",
    
    # ----------------------------------------------------------
    # Team-BE - 임시/문서 파일
    # ----------------------------------------------------------
    "Team-BE/db_init.py",                          # create_tables.py로 대체
    "Team-BE/test_file_sharing.py",                # 테스트용 임시
    "Team-BE/api_documentation.md",                # Swagger로 대체
    "Team-BE/frontend_compatibility_checklist.md", # 완료된 체크리스트
]

# ============================================================
# 유지해야 할 파일 (참고용 - 삭제하지 않음)
# ============================================================
FILES_TO_KEEP = """
[필수 유지 파일]
- docker-compose.yml          # 인프라 실행
- init-db.sql                 # DB 스키마 생성
- ERD_v2.dbml                 # DB 설계 문서
- create_dynamodb_tables.py   # DynamoDB 테이블 생성
- seed_all.py                 # 시드 데이터
- reset_all_db.py             # DB 리셋
- create_all_tables.bat       # 테이블 생성
- reset_and_seed_all.bat      # DB 초기화 통합
- start_services.py           # 서비스 시작
- start_services.bat          # 서비스 시작 (Windows)
- install_all.bat             # 의존성 설치
- test_msa_communication.py   # MSA 헬스체크
- README_MSA_SETUP.md         # 설정 가이드
- **/create_tables.py         # 서비스별 테이블 생성
- **/.env.example             # 환경변수 템플릿
- **/pyproject.toml           # 의존성 정의
- **/poetry.lock              # 의존성 잠금
- **/alembic.ini              # 마이그레이션 설정
- **/migrations/              # 마이그레이션 파일
- **/README.md                # 서비스별 문서
- shared/                     # 공유 유틸리티
"""

def delete_folder(path):
    """폴더 삭제"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"  ✅ 삭제: {path}")
            return True
        except Exception as e:
            print(f"  ❌ 실패: {path} - {e}")
            return False
    return False

def delete_file(path):
    """파일 삭제"""
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"  ✅ 삭제: {path}")
            return True
        except Exception as e:
            print(f"  ❌ 실패: {path} - {e}")
            return False
    return False

def main():
    print("=" * 60)
    print("🧹 Portforge 프로젝트 정리 스크립트")
    print("=" * 60)
    print()
    print("ℹ️  .gitignore에 포함된 파일은 삭제하지 않습니다:")
    print("   - .venv/, node_modules/ (가상환경)")
    print("   - .env (환경변수)")
    print("   - __pycache__/ (캐시)")
    print("   - .vscode/ (IDE 설정)")
    print()
    print("⚠️  다음 항목들이 삭제됩니다:")
    print("   - 백업 폴더 (*_latest)")
    print("   - shared/ 폴더 (MSA에서 부적절, 미사용)")
    print("   - 임시/테스트 스크립트들")
    print("   - 불필요한 문서들")
    print()
    print("✅ 유지되는 핵심 파일:")
    print("   - 모든 .git/ 폴더 (Git 이력 유지)")
    print("   - docker-compose.yml, init-db.sql")
    print("   - seed_all.py, reset_all_db.py")
    print("   - create_all_tables.bat, start_services.py")
    print("   - test_msa_communication.py")
    print("   - TEAM_ONBOARDING.md")
    print("   - 모든 app/, migrations/ 폴더")
    print()
    
    response = input("❓ 계속하시겠습니까? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ 취소되었습니다.")
        return
    
    print()
    
    # 폴더 삭제
    print("📁 폴더 삭제 중...")
    folder_count = 0
    for folder in FOLDERS_TO_DELETE:
        if delete_folder(folder):
            folder_count += 1
    
    # 파일 삭제
    print()
    print("📄 파일 삭제 중...")
    file_count = 0
    for file in FILES_TO_DELETE:
        if delete_file(file):
            file_count += 1
    
    # 결과 출력
    print()
    print("=" * 60)
    print("✅ 정리 완료!")
    print("=" * 60)
    print(f"  삭제된 폴더: {folder_count}개")
    print(f"  삭제된 파일: {file_count}개")
    print()
    print("📋 팀원 온보딩 순서:")
    print("  1. docker-compose up -d (또는 poetry run poe db-up)")
    print("  2. install_all.bat")
    print("  3. 각 서비스에서 cp .env.example .env")
    print("  4. python reset_all_db.py")
    print("  5. create_all_tables.bat")
    print("  6. python seed_all.py")
    print("  7. python create_dynamodb_tables.py")
    print("  8. poetry run poe health-check")
    print("  9. poetry run poe run-auth (각 서비스 별도 터미널)")
    print()
    print("📚 자세한 내용은 TEAM_ONBOARDING.md 참고")

if __name__ == "__main__":
    main()
