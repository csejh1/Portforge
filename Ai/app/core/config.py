from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# .env 파일을 시스템 환경변수보다 우선하도록 강제 로드
load_dotenv(override=True)

class Settings(BaseSettings):
    # [App Settings]
    PROJECT_NAME: str = "Jerry-Architect-Template"
    ENV: str = "local"
    DEBUG: bool = True

    # [Database - MySQL]
    DATABASE_URL: str = ""

    # [AWS Infrastructure - LocalStack/MinIO]
    DDB_ENDPOINT_URL: str = ""
    DDB_TABLE_NAME: str = "chat_messages"  # DynamoDB 채팅 테이블
    S3_ENDPOINT_URL: str = ""
    AWS_S3_BUCKET: str = "local-bucket"    # S3 버킷 이름
    S3_PREFIX: str = "ai-generated/"       # S3 파일 경로 접두사
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    
    # MinIO Specific
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "password"

    # [AWS Cognito - Auth]
    COGNITO_REGION: str = ""
    COGNITO_USERPOOL_ID: str = ""
    COGNITO_APP_CLIENT_ID: str = ""
    
    # [AI Service]
    # Default: Claude 3.5 Sonnet (us-east-1 requires enabling) or Haiku. 
    # Example: "anthropic.claude-3-5-sonnet-20240620-v1:0"
    BEDROCK_MODEL_ID: str = ""
    
    # [Security - JWT Settings]
    # Cognito는 RS256을 사용하므로 알고리즘을 고정합니다.
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def COGNITO_JWKS_URL(self) -> str:
        """AWS에서 제공하는 공개키 목록 주소를 동적으로 생성합니다."""
        return f"https://cognito-idp.{self.AWS_REGION}.amazonaws.com/{self.COGNITO_USERPOOL_ID}/.well-known/jwks.json"

    # Pydantic Settings 설정
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )

# 인스턴스화
settings = Settings() # type: ignore