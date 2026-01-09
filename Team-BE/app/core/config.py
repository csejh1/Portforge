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
    
    # DynamoDB 설정
    DYNAMODB_TABLE_CHATS: str = "team_chats"
    DYNAMODB_TABLE_ROOMS: str = "chat_rooms"
    
    class Config:
        env_file = ".env"

settings = Settings()