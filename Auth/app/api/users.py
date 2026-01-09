from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.user import User, UserStack
from app.schemas.user import UserResponse, UserStackResponse, UserDetailResponse
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """사용자 상세 정보 조회 (다른 서비스에서 호출)"""
    # 사용자 기본 정보 조회
    user_query = select(User).where(User.user_id == user_id)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 사용자 기술 스택 조회
    stacks_query = select(UserStack).where(UserStack.user_id == user_id)
    stacks_result = await db.execute(stacks_query)
    stacks = stacks_result.scalars().all()
    
    return UserDetailResponse(
        user_id=user.user_id,
        email=user.email,
        nickname=user.nickname,
        role=user.role,
        profile_image_url=user.profile_image_url,
        liked_project_ids=user.liked_project_ids or [],
        test_count=user.test_count,
        created_at=user.created_at,
        updated_at=user.updated_at,
        stacks=[
            UserStackResponse(
                stack_id=stack.stack_id,
                position_type=stack.position_type,
                stack_name=stack.stack_name,
                created_at=stack.created_at,
                updated_at=stack.updated_at
            ) for stack in stacks
        ]
    )

@router.get("/{user_id}/basic", response_model=UserResponse)
async def get_user_basic(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """사용자 기본 정보만 조회 (가벼운 조회용)"""
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        nickname=user.nickname,
        role=user.role,
        profile_image_url=user.profile_image_url,
        created_at=user.created_at
    )

@router.post("/batch", response_model=List[UserResponse])
async def get_users_batch(
    user_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    """여러 사용자 정보 일괄 조회"""
    query = select(User).where(User.user_id.in_(user_ids))
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        UserResponse(
            user_id=user.user_id,
            email=user.email,
            nickname=user.nickname,
            role=user.role,
            profile_image_url=user.profile_image_url,
            created_at=user.created_at
        ) for user in users
    ]

@router.get("/{user_id}/stacks", response_model=List[UserStackResponse])
async def get_user_stacks(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """사용자 기술 스택 조회"""
    query = select(UserStack).where(UserStack.user_id == user_id)
    result = await db.execute(query)
    stacks = result.scalars().all()
    
    return [
        UserStackResponse(
            stack_id=stack.stack_id,
            position_type=stack.position_type,
            stack_name=stack.stack_name,
            created_at=stack.created_at,
            updated_at=stack.updated_at
        ) for stack in stacks
    ]