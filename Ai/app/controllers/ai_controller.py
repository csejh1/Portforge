from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db 
from app.schemas.ai_schema import (
    QuestionRequest, QuestionResponse, AnalysisRequest, AnalysisResponse,
    MeetingStartRequest, MeetingStartResponse, MeetingEndRequest, MeetingEndResponse,
    PortfolioRequest, PortfolioResponse,
    ApplicantAnalysisRequest, ApplicantAnalysisResponse,
    MinutesGenerateRequest, MinutesResponse
)
from app.models.ai_model import GeneratedReport
from app.services.ai_service import ai_service
from app.services.meeting_service import meeting_service
from app.services.portfolio_service import portfolio_service
from app.repositories.ai_repository import TestRepository
from app.core.exceptions import BusinessException, ErrorCode

router = APIRouter()

async def get_repository(db: AsyncSession = Depends(get_db)): # type: ignore
    return TestRepository(db)

# --- Test API ---
@router.post("/test/questions", response_model=QuestionResponse)
async def generate_test_questions(
    request: QuestionRequest, 
    repo: TestRepository = Depends(get_repository)
):
    user_id = "test_user_uuid" # [MOCK]
    if not request.stack:
        raise BusinessException(ErrorCode.INVALID_INPUT, "기술 스택(stack)은 필수 입력값입니다.")
    return await ai_service.generate_questions(request, repo, user_id)

@router.post("/test/analyze", response_model=AnalysisResponse)
async def analyze_test_results(
    request: AnalysisRequest,
    repo: TestRepository = Depends(get_repository)
):
    return await ai_service.analyze_results(request, repo, request.user_id)

@router.get("/test/result/{user_id}", response_model=Optional[AnalysisResponse])
async def get_user_test_result(
    user_id: str,
    repo: TestRepository = Depends(get_repository)
):
    return await ai_service.get_latest_result(user_id, repo)

@router.post("/recruit/analyze", response_model=ApplicantAnalysisResponse)
async def analyze_applicants(request: ApplicantAnalysisRequest):
    data = [applicant.model_dump() for applicant in request.applicants]
    analysis = await ai_service.predict_applicant_suitability(data)
    return ApplicantAnalysisResponse(analysis=analysis)

# --- Meeting API ---
@router.post("/meeting/start", response_model=MeetingStartResponse)
async def start_meeting(
    request: MeetingStartRequest,
    db: AsyncSession = Depends(get_db)
):
    session = await meeting_service.start_meeting(db, request.team_id, request.project_id)
    return MeetingStartResponse(
        session_id=session.session_id,
        status=session.status,
        start_time=session.start_time
    )

@router.post("/meeting/end", response_model=MeetingEndResponse)
async def end_meeting(
    request: MeetingEndRequest,
    db: AsyncSession = Depends(get_db)
):
    user_id = "test_user_uuid" # [MOCK]
    report = await meeting_service.end_meeting(db, request.session_id, user_id)
    return MeetingEndResponse(
        report_id=report.report_id,
        title=str(report.title),
        content_summary="Summary available in S3"
    )

# --- Portfolio API ---
@router.post("/portfolio/generate", response_model=PortfolioResponse)
async def generate_portfolio(
    request: PortfolioRequest,
    db: AsyncSession = Depends(get_db)
):
    result_data = await portfolio_service.generate_portfolio(db, request.user_id, request.project_id)
    return PortfolioResponse(result=result_data)

# --- Minutes API ---
@router.get("/minutes", response_model=list[MinutesResponse])
async def list_minutes(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(GeneratedReport).where(
        GeneratedReport.team_id == team_id,
        GeneratedReport.report_type == "MEETING_MINUTES"
    ).order_by(GeneratedReport.created_at.desc())
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    return [
        MinutesResponse(
            report_id=r.report_id,
            title=str(r.title),
            status=str(r.status) if r.status else "COMPLETED",
            s3_key=r.s3_key,
            created_at=r.created_at
        ) for r in reports
    ]

@router.post("/minutes", response_model=MinutesResponse)
async def generate_minutes(
    request: MinutesGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    user_id = "test_user_uuid" # [MOCK]
    
    msgs = [m.model_dump() for m in request.messages]
    
    if not msgs:
        raise BusinessException(ErrorCode.INVALID_INPUT, "채팅 메시지가 없습니다.")
    
    report = await meeting_service.generate_meeting_minutes(db, request.team_id, request.project_id, msgs, user_id)
    return MinutesResponse(
        report_id=report.report_id,
        title=str(report.title),
        status=str(report.status) if report.status else "COMPLETED",
        s3_key=report.s3_key,
        created_at=report.created_at
    )

@router.get("/minutes/{report_id}", response_model=MinutesResponse)
async def get_minutes_metadata(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(GeneratedReport).where(GeneratedReport.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise BusinessException(ErrorCode.NOT_FOUND, "Report not found")
    return MinutesResponse(
        report_id=report.report_id,
        title=str(report.title),
        status=str(report.status) if report.status else "COMPLETED",
        s3_key=report.s3_key,
        created_at=report.created_at
    )

@router.get("/minutes/{report_id}/content")
async def get_minutes_content(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(GeneratedReport).where(GeneratedReport.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report or not report.s3_key:
        raise BusinessException(ErrorCode.NOT_FOUND, "Report or Content not found")
    
    content = await meeting_service.get_report_content(report.s3_key)
    return content

# --- Daily Meeting Minutes API ---
@router.post("/minutes/daily", response_model=MinutesResponse)
async def generate_daily_minutes(
    request: MinutesGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    일단위 회의록 생성/업데이트
    - 같은 날 회의록이 이미 있으면 기존 내용 + 새 내용 합쳐서 업데이트
    """
    user_id = "test_user_uuid"  # [MOCK]
    
    msgs = [m.model_dump() for m in request.messages]
    
    if not msgs:
        raise BusinessException(ErrorCode.INVALID_INPUT, "채팅 메시지가 없습니다.")
    
    report = await meeting_service.generate_daily_meeting_minutes(
        db, 
        request.team_id, 
        request.project_id, 
        msgs, 
        user_id
    )
    
    return MinutesResponse(
        report_id=report.report_id,
        title=str(report.title),
        status=str(report.status) if report.status else "COMPLETED",
        s3_key=report.s3_key,
        created_at=report.created_at
    )

@router.get("/minutes/daily/{team_id}/{project_id}")
async def list_daily_minutes(
    team_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """일단위 회의록 목록 조회"""
    stmt = select(GeneratedReport).where(
        GeneratedReport.team_id == team_id,
        GeneratedReport.project_id == project_id,
        GeneratedReport.report_type == "DAILY_MEETING_MINUTES"
    ).order_by(GeneratedReport.created_at.desc())
    
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    return [
        MinutesResponse(
            report_id=r.report_id,
            title=str(r.title),
            status=str(r.status) if r.status else "COMPLETED",
            s3_key=r.s3_key,
            created_at=r.created_at
        ) for r in reports
    ]

