"""
MySQL 데이터베이스 전체 초기화 스크립트
모든 MSA 서비스의 데이터베이스를 삭제하고 재생성합니다.
"""
import pymysql
import sys

# --- Configurations ---
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "rootpassword"

# 모든 MSA 서비스의 데이터베이스
DATABASES = [
    "portforge_auth",
    "portforge_project", 
    "portforge_team",
    "portforge_ai",
    "portforge_support"
]

def reset_databases():
    """모든 데이터베이스를 삭제하고 재생성"""
    try:
        print("🔌 Connecting to MySQL...")
        conn = pymysql.connect(
            host=DB_HOST, 
            port=DB_PORT, 
            user=DB_USER, 
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        for db in DATABASES:
            print(f"🗑️  Dropping database: {db}")
            cursor.execute(f"DROP DATABASE IF EXISTS {db}")
            
            print(f"✨ Creating database: {db}")
            cursor.execute(f"CREATE DATABASE {db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ All databases reset successfully!")
        print("\n📋 Next steps:")
        print("1. Run table creation for each service:")
        print("   cd Auth && python -c \"from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)\"")
        print("   cd Project_Service && python -c \"from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)\"")
        print("   cd Team-BE && python -c \"from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)\"")
        print("   cd Ai && python -c \"from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)\"")
        print("   cd Support_Communication_Service && python -c \"from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)\"")
        print("\n2. Run seed script:")
        print("   python seed_all.py")
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # pymysql 설치 확인
    try:
        import pymysql
    except ImportError:
        print("📦 Installing pymysql...")
        import subprocess
        subprocess.run(["pip", "install", "pymysql", "cryptography"], check=True)
        import pymysql
    
    print("⚠️  WARNING: This will DELETE ALL DATA in the following databases:")
    for db in DATABASES:
        print(f"   - {db}")
    
    # 자동 모드 (stdin이 없는 경우)
    import sys
    if sys.stdin.isatty():
        response = input("\n❓ Are you sure you want to continue? (yes/no): ")
    else:
        response = "yes"
        print("\n🤖 Auto-confirmed (non-interactive mode)")
    
    if response.lower() in ['yes', 'y']:
        reset_databases()
    else:
        print("❌ Operation cancelled.")
        sys.exit(0)
