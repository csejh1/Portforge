from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 데이터베이스 설정 (MySQL 사용)
    DATABASE_URL: str = "mysql+aiomysql://root:rootpassword@localhost:3306/portforge_team"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS 설정
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str = "team-platform-bucket"
    S3_ENDPOINT_URL: Optional[str] = None
    DDB_ENDPOINT_URL: Optional[str] = None
    
    # DynamoDB 설정
    DYNAMODB_TABLE_CHATS: str = "team_chats"
    DYNAMODB_TABLE_ROOMS: str = "chat_rooms"
    
    # MinIO 설정 (로컬 개발용)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "portforge-files"
    MINIO_SECURE: bool = False
    
    class Config:
        env_file = ".env"
        extra = "allow"  # .env 파일의 추가 키 허용

settings = Settings()