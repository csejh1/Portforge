"""
파일 업로드/다운로드 서비스 (MinIO S3)
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "password")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "team-files")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        # MinIO 클라이언트 초기화
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # 버킷 생성 (없으면)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """버킷이 존재하지 않으면 생성"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"버킷 '{self.bucket_name}' 생성 완료")
        except S3Error as e:
            logger.error(f"버킷 생성 실패: {e}")
    
    def upload_file(self, file: UploadFile, team_id: int, user_id: str) -> dict:
        """
        파일 업로드
        
        Args:
            file: 업로드할 파일
            team_id: 팀 ID
            user_id: 업로드한 사용자 ID
            
        Returns:
            dict: 업로드된 파일 정보
        """
        try:
            # 파일 크기 체크 (10MB = 10 * 1024 * 1024 bytes)
            MAX_FILE_SIZE = 10 * 1024 * 1024
            
            # 파일 크기 확인
            file.file.seek(0, 2)  # 파일 끝으로 이동
            file_size = file.file.tell()
            file.file.seek(0)  # 파일 시작으로 되돌리기
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="파일 크기가 10MB를 초과합니다."
                )
            
            # 파일명 생성 (UUID + 원본 파일명)
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # S3 키 생성 (teams/{team_id}/shared_files/{unique_filename})
            s3_key = f"teams/{team_id}/shared_files/{unique_filename}"
            
            # MinIO에 파일 업로드
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=s3_key,
                data=file.file,
                length=file_size,
                content_type=file.content_type or "application/octet-stream"
            )
            
            logger.info(f"파일 업로드 성공: {s3_key}")
            
            return {
                "s3_key": s3_key,
                "original_filename": file.filename,
                "file_size": file_size,
                "content_type": file.content_type,
                "uploaded_by": user_id,
                "uploaded_at": datetime.now()
            }
            
        except S3Error as e:
            logger.error(f"MinIO 업로드 실패: {e}")
            raise HTTPException(
                status_code=500,
                detail="파일 업로드에 실패했습니다."
            )
        except Exception as e:
            logger.error(f"파일 업로드 실패: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
            )
    
    def get_download_url(self, s3_key: str, expires: int = 3600) -> str:
        """
        파일 다운로드 URL 생성 (임시 URL)
        
        Args:
            s3_key: S3 객체 키
            expires: URL 만료 시간 (초, 기본 1시간)
            
        Returns:
            str: 다운로드 URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=s3_key,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"다운로드 URL 생성 실패: {e}")
            raise HTTPException(
                status_code=500,
                detail="다운로드 URL 생성에 실패했습니다."
            )
    
    def delete_file(self, s3_key: str) -> bool:
        """
        파일 삭제
        
        Args:
            s3_key: 삭제할 파일의 S3 키
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=s3_key
            )
            logger.info(f"파일 삭제 성공: {s3_key}")
            return True
        except S3Error as e:
            logger.error(f"파일 삭제 실패: {e}")
            return False
    
    def get_file_info(self, s3_key: str) -> Optional[dict]:
        """
        파일 정보 조회
        
        Args:
            s3_key: S3 객체 키
            
        Returns:
            dict: 파일 정보 또는 None
        """
        try:
            stat = self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=s3_key
            )
            return {
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "etag": stat.etag
            }
        except S3Error as e:
            logger.error(f"파일 정보 조회 실패: {e}")
            return None

# 전역 파일 서비스 인스턴스
file_service = FileService()
