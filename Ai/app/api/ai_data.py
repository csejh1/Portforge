from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.ai_model import TestResult, GeneratedReport, Portfolio
from app.schemas.ai import TestResultResponse, GeneratedReportResponse, PortfolioResponse
from app.core.database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/test-results/{application_id}", response_model=TestResultResponse)
async def get_test_result_by_application(
    application_id: int,
    db: AsyncSession = Depends(get_db)
):
    """지원서별 테스트 결과 조회"""
    query = select(TestResult).where(TestResult.application_id == application_id)
    result = await db.execute(query)
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found"
        )
    
    return TestResultResponse(
        result_id=test_result.result_id,
        user_id=test_result.user_id,
        project_id=test_result.project_id,
        application_id=test_result.application_id,
        test_type=test_result.test_type,
        score=test_result.score,
        feedback=test_result.feedback,
        created_at=test_result.created_at
    )

@router.get("/test-results/user/{user_id}", response_model=List[TestResultResponse])
async def get_user_test_results(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """사용자별 테스트 결과 목록 조회"""
    query = select(TestResult).where(TestResult.user_id == user_id)
    result = await db.execute(query)
    test_results = result.scalars().all()
    
    return [
        TestResultResponse(
            result_id=tr.result_id,
            user_id=tr.user_id,
            project_id=tr.project_id,
            application_id=tr.application_id,
            test_type=tr.test_type,
            score=tr.score,
            feedback=tr.feedback,
            created_at=tr.created_at
        ) for tr in test_results
    ]

@router.get("/reports/team/{team_id}", response_model=List[GeneratedReportResponse])
async def get_team_reports(
    team_id: int,
    report_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """팀별 생성된 리포트 목록 조회"""
    query = select(GeneratedReport).where(GeneratedReport.team_id == team_id)
    
    if report_type:
        query = query.where(GeneratedReport.report_type == report_type)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return [
        GeneratedReportResponse(
            report_id=report.report_id,
            team_id=report.team_id,
            project_id=report.project_id,
            created_by=report.created_by,
            report_type=report.report_type,
            status=report.status,
            model_id=report.model_id,
            title=report.title,
            s3_key=report.s3_key,
            created_at=report.created_at
        ) for report in reports
    ]

@router.get("/reports/{report_id}", response_model=GeneratedReportResponse)
async def get_report_detail(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """리포트 상세 정보 조회"""
    query = select(GeneratedReport).where(GeneratedReport.report_id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return GeneratedReportResponse(
        report_id=report.report_id,
        team_id=report.team_id,
        project_id=report.project_id,
        created_by=report.created_by,
        report_type=report.report_type,
        status=report.status,
        model_id=report.model_id,
        title=report.title,
        s3_key=report.s3_key,
        created_at=report.created_at
    )

@router.get("/portfolios/user/{user_id}", response_model=List[PortfolioResponse])
async def get_user_portfolios(
    user_id: str,
    is_public: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """사용자별 포트폴리오 목록 조회"""
    query = select(Portfolio).where(Portfolio.user_id == user_id)
    
    if is_public is not None:
        query = query.where(Portfolio.is_public == is_public)
    
    result = await db.execute(query)
    portfolios = result.scalars().all()
    
    return [
        PortfolioResponse(
            portfolio_id=portfolio.portfolio_id,
            user_id=portfolio.user_id,
            project_id=portfolio.project_id,
            title=portfolio.title,
            summary=portfolio.summary,
            thumbnail_url=portfolio.thumbnail_url,
            is_public=portfolio.is_public,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        ) for portfolio in portfolios
    ]


# =====================================================
# FE_latest 호환 API (TeamSpacePage.tsx / chatClient.ts)
# =====================================================
from pydantic import BaseModel
from datetime import datetime

class MinutesCreateRequest(BaseModel):
    team_id: int
    project_id: int
    messages: List[dict]

@router.post("/minutes/daily")
async def generate_daily_minutes(
    request: MinutesCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """일 단위 회의록 생성 (AI)"""
    # 실제로는 AI Service를 호출하여 요약해야 하지만, 
    # 여기서는 간단히 저장 로직만 구현하거나 Mocking
    
    try:
        from app.services.ai_service import AiService
        ai_service = AiService()
        
        # 채팅 메시지를 텍스트로 변환
        chat_text = "\\n".join([f"{m.get('user', 'Unknown')}: {m.get('msg', '')}" for m in request.messages])
        
        # 프롬프트 구성 (meeting_notes_prompt가 있다고 가정하거나 직접 작성)
        prompt = f"""
        다음은 팀 회의 채팅 로그입니다. 이를 바탕으로 회의록을 작성해주세요.
        
        [채팅 로그]
        {chat_text}
        
        [요청사항]
        1. 회의 안건 (Agenda)
        2. 주요 논의 사항 (Discussion)
        3. 결정 사항 (Decisions)
        4. 향후 계획 (Action Items)
        
        형식은 마크다운으로 작성해주세요.
        """
        
        # 3. AI 모델 호출
        model_id = "anthropic.claude-3-haiku-20240307-v1:0" 
        summary = await ai_service.generate_text(prompt, model_id)
        
        # 4. DB 저장
        today_str = datetime.now().strftime("%Y-%m-%d")
        title = f"{today_str} 일일 회의록"
        
        report = GeneratedReport(
            team_id=request.team_id,
            project_id=request.project_id,
            created_by="system",
            report_type="MEETING_MINUTES",
            status="COMPLETED",
            model_id=model_id,
            title=title,
            s3_key=None, # S3 저장 생략하고 DB나 메모리에만 둘 수도 있음 (여기선 생략)
            feedback=summary # feedback 컬럼에 내용 저장 (임시)
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return {
            "report_id": report.report_id,
            "title": report.title,
            "status": report.status,
            "s3_key": report.s3_key,
            "created_at": report.created_at.isoformat()
        }
        
    except Exception as e:
        print(f"Minutes generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/minutes/daily/{team_id}/{project_id}")
async def get_daily_minutes_list(
    team_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """일 단위 회의록 목록 조회"""
    query = select(GeneratedReport).where(
        GeneratedReport.team_id == team_id,
        GeneratedReport.report_type == "MEETING_MINUTES"
    ).order_by(GeneratedReport.created_at.desc())
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return [
        {
            "report_id": r.report_id,
            "title": r.title,
            "status": r.status,
            "s3_key": r.s3_key,
            "created_at": r.created_at.isoformat()
        } for r in reports
    ]

@router.get("/minutes/{report_id}/content")
async def get_minutes_content(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """회의록 내용 조회"""
    query = select(GeneratedReport).where(GeneratedReport.report_id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # feedback 컬럼에 내용을 저장했으므로 이를 반환
    # 만약 s3_key가 있다면 S3에서 읽어야 함
    return {
        "content": report.feedback or "내용이 없습니다."
    }
