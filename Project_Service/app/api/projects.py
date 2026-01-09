from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.project_recruitment import Project, Application, ProjectRecruitmentPosition
from app.schemas.project import ProjectResponse, ApplicationResponse, ProjectDetailResponse, RecruitmentPositionResponse
from app.core.database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectDetailResponse])
async def get_projects(
    page: int = 1,
    size: int = 20,
    type: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트 목록 조회 (공개 API - 인증 불필요)"""
    query = select(Project).options(selectinload(Project.recruitment_positions))
    
    if type:
        query = query.where(Project.type == type)
    if status:
        query = query.where(Project.status == status)
    
    # 최신순 정렬 및 페이지네이션
    query = query.order_by(Project.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return [
        ProjectDetailResponse(
            project_id=p.project_id,
            user_id=p.user_id,
            type=p.type.value if hasattr(p.type, 'value') else p.type,
            title=p.title,
            description=p.description,
            method=p.method.value if hasattr(p.method, 'value') else p.method,
            status=p.status.value if hasattr(p.status, 'value') else p.status,
            start_date=p.start_date,
            end_date=p.end_date,
            test_required=p.test_required,
            views=p.views,
            created_at=p.created_at,
            updated_at=p.updated_at,
            recruitment_positions=[
                RecruitmentPositionResponse(
                    position_type=pos.position_type.value if hasattr(pos.position_type, 'value') else str(pos.position_type),
                    required_stacks=[pos.required_stacks.value] if pos.required_stacks and hasattr(pos.required_stacks, 'value') else [],
                    target_count=pos.target_count or 0,
                    current_count=pos.current_count or 0,
                    recruitment_deadline=pos.recruitment_deadline
                ) for pos in (p.recruitment_positions or [])
            ]
        ) for p in projects
    ]

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트 상세 정보 조회 (다른 서비스에서 호출)"""
    query = select(Project).options(selectinload(Project.recruitment_positions)).where(Project.project_id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectDetailResponse(
        project_id=project.project_id,
        user_id=project.user_id,
        type=project.type.value if hasattr(project.type, 'value') else project.type,
        title=project.title,
        description=project.description,
        method=project.method.value if hasattr(project.method, 'value') else project.method,
        status=project.status.value if hasattr(project.status, 'value') else project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        test_required=project.test_required,
        views=project.views,
        created_at=project.created_at,
        updated_at=project.updated_at,
        recruitment_positions=[
            RecruitmentPositionResponse(
                position_type=pos.position_type.value if hasattr(pos.position_type, 'value') else str(pos.position_type),
                required_stacks=[pos.required_stacks.value] if pos.required_stacks and hasattr(pos.required_stacks, 'value') else [],
                target_count=pos.target_count or 0,
                current_count=pos.current_count or 0,
                recruitment_deadline=pos.recruitment_deadline
            ) for pos in (project.recruitment_positions or [])
        ]
    )

@router.get("/{project_id}/basic", response_model=ProjectResponse)
async def get_project_basic(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트 기본 정보만 조회 (가벼운 조회용)"""
    query = select(Project).where(Project.project_id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse(
        project_id=project.project_id,
        title=project.title,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date
    )

@router.post("/batch", response_model=List[ProjectResponse])
async def get_projects_batch(
    project_ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """여러 프로젝트 정보 일괄 조회"""
    query = select(Project).where(Project.project_id.in_(project_ids))
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return [
        ProjectResponse(
            project_id=project.project_id,
            title=project.title,
            description=project.description,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date
        ) for project in projects
    ]

@router.get("/{project_id}/applications", response_model=List[ApplicationResponse])
async def get_project_applications(
    project_id: int,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트의 지원서 목록 조회"""
    query = select(Application).where(Application.project_id == project_id)
    
    if status:
        query = query.where(Application.status == status)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return [
        ApplicationResponse(
            application_id=app.application_id,
            project_id=app.project_id,
            user_id=app.user_id,
            position_type=app.position_type,
            status=app.status,
            created_at=app.created_at
        ) for app in applications
    ]

@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application_detail(
    application_id: int,
    db: AsyncSession = Depends(get_db)
):
    """지원서 상세 정보 조회"""
    query = select(Application).where(Application.application_id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return ApplicationResponse(
        application_id=application.application_id,
        project_id=application.project_id,
        user_id=application.user_id,
        position_type=application.position_type,
        status=application.status,
        created_at=application.created_at
    )