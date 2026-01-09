import json
import boto3
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from botocore.client import Config
from app.models.ai_model import Portfolio, GeneratedReport, TestResult
from app.core.exceptions import BusinessException, ErrorCode
from app.adapters.internal_adapters import project_adapter
from app.services.ai_service import ai_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.AWS_REGION
        )
        self.bucket_name = "local-bucket"  # 실제로는 settings나 DB에서 관리

    async def generate_portfolio(self, db: AsyncSession, user_id: str, project_id: int) -> dict:
        """
        포트폴리오 생성 및 저장 (초안)
        """
        # [TEST MODE] 강제로 Seed User ID 사용
        # 실제 운영시에는 제거해야 합니다.
        original_user_id = user_id
        user_id = "dummy_user_1" 

        # 1. 프로젝트 정보 조회
        try:
            # 실제로는 user_id로 해당 프로젝트에 속한 팀 ID를 찾아야 함.
            # 지금은 Seeder 데이터에 맞춰 team_id=1로 가정하거나, 
            # 단순히 해당 프로젝트의 리포트를 모두 가져온다고 가정
            project_info = await project_adapter.get_project_details(project_id)
        except Exception:
            raise BusinessException(ErrorCode.INVALID_INPUT, "프로젝트 정보를 불러올 수 없습니다.")

        # 2. 회의록 수집 (S3 Content 읽기)
        # Seeder에서 team_id=1로 넣었으므로, team_id=1인 리포트 조회 (간소화)
        team_id = 1 
        reports_res = await db.execute(
            select(GeneratedReport)
            .where(GeneratedReport.team_id == team_id)
            .where(GeneratedReport.report_type == 'MEETING')
        )
        reports = reports_res.scalars().all()

        meeting_data_list = []
        for report in reports:
            if report.s3_key:
                try:
                    # S3에서 파일 다운로드 및 읽기 (동기식 boto3 호출을 비동기 서비스에서 쓸 땐 주의 필요하나 MVP 등에서는 허용)
                    # 실제 운영 환경에서는 aioboto3 사용 권장
                    obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=report.s3_key)
                    file_content = obj['Body'].read().decode('utf-8')
                    meeting_json = json.loads(file_content)
                    meeting_data_list.append(meeting_json)
                except Exception as e:
                    logger.warning(f"Failed to read S3 file {report.s3_key}: {e}")

        # 3. 역량 테스트 결과 수집
        tests_res = await db.execute(select(TestResult).where(TestResult.user_id == user_id))
        test_results = tests_res.scalars().all()
        verified_skills = [f"{t.feedback} (Score: {t.score})" for t in test_results if t.score and t.score >= 70] # 70점 이상만 인증

        # 4. 프롬프트 구성
        system_prompt = "You are a professional IT career consultant. Analyze the provided meeting logs and project info to generate a structured portfolio summary."
        
        user_prompt = f"""
        Analyze the following data and generate a portfolio summary for the user '{user_id}' (assuming User ID 'dummy_user_1' is '김코딩').
        
        [Project Info]
        Title: {project_info['title']}
        Period: {project_info.get('period', '기간 미정')}
        Stack: {', '.join(project_info['tech_stacks'])}
        
        [Verified Skills (AI Test)]
        {json.dumps(verified_skills, ensure_ascii=False)}
        
        [Meeting Logs (Activity Evidence)]
        {json.dumps(meeting_data_list, ensure_ascii=False, default=str)}
        
        [Task]
        Generate a JSON output with the following fields (Korean):
        1. "role": User's main role inferred from activities (e.g. Frontend Lead).
        2. "period": Project period string.
        3. "stack": Tech stack used (highlight verified skills).
        4. "contributions": Array of objects {{ "category": "String", "text": "String" }}. Extract 3 key achievements using STAR method.
        5. "aiAnalysis": A professional one-paragraph evaluation of the user's performance and soft skills based on meeting behaviors.
        
        Output valid JSON only. No markdown.
        """

        # 5. Bedrock 호출
        try:
            ai_response = await ai_service._invoke_bedrock(system_prompt, user_prompt)
            cleaned = ai_response.strip().replace("```json", "").replace("```", "").strip()
            result_data = json.loads(cleaned)
        except Exception as e:
            logger.error(f"AI Generation Failed: {e}")
            # Fallback Mock Data
            result_data = {
                "role": "개발자",
                "period": "2024.06 ~ 2024.08",
                "stack": "React, Node.js",
                "contributions": [{"category": "일반", "text": "AI 서비스 연결 오류로 기본 데이터만 표시됩니다."}],
                "aiAnalysis": "분석 실패"
            }

        # 6. DB 저장/업데이트
        # 기존 데이터 확인 (Upsert)
        existing_res = await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .where(Portfolio.project_id == project_id)
        )
        existing_portfolio = existing_res.scalar_one_or_none()
        
        if existing_portfolio:
            existing_portfolio.summary = json.dumps(result_data, ensure_ascii=False)
            # 기존 객체 업데이트
            portfolio = existing_portfolio
        else:
            new_portfolio = Portfolio(
                user_id=user_id,
                project_id=project_id,
                title=f"{project_info['title']} - 포트폴리오",
                summary=json.dumps(result_data, ensure_ascii=False)
            )
            db.add(new_portfolio)
            portfolio = new_portfolio
            
        await db.commit()
        await db.refresh(portfolio)
        
        return result_data

portfolio_service = PortfolioService()
