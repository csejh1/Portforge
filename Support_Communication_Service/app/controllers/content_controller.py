from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.schemas.base import ResponseEnvelope
from app.services.notice_service import list_notices, create_notice as create_notice_service
from app.services.banner_service import list_banners as get_banners
from app.core.deps import get_current_user

router = APIRouter()


class NoticeCreateRequest(BaseModel):
    title: str
    content: str


class BannerCreateRequest(BaseModel):
    title: str
    link: str
    is_active: Optional[bool] = True


@router.get("/notices", response_model=ResponseEnvelope)
async def get_notices():
    """공지사항 목록 조회"""
    notices = await list_notices(limit=20)
    return ResponseEnvelope(success=True, code="CNT_000", message="Notices list", data=notices)


@router.post("/notices", response_model=ResponseEnvelope, status_code=201)
async def create_notice(payload: NoticeCreateRequest, current_user=Depends(get_current_user)):
    """공지사항 생성 (관리자 전용)"""
    notice = await create_notice_service(title=payload.title, content=payload.content)
    return ResponseEnvelope(success=True, code="CNT_002", message="Notice created", data=notice)


@router.get("/notices/latest", response_model=ResponseEnvelope)
async def get_latest_notice():
    """최신 공지사항 조회"""
    notices = await list_notices(limit=1)
    latest = notices[0] if notices else None
    return ResponseEnvelope(success=True, code="CNT_000", message="Latest notice", data=latest)


@router.get("/banners", response_model=ResponseEnvelope)
async def list_banners():
    """배너 목록 조회"""
    try:
        banners = await get_banners()
        return ResponseEnvelope(success=True, code="CNT_001", message="Banners", data=banners)
    except Exception:
        # 서비스 오류 시 기본 배너 반환
        banners = [
            {"id": 1, "title": "AI 해커톤", "image": "https://cdn.example.com/banner1.png", "link": "https://example.com/event/1"}
        ]
        return ResponseEnvelope(success=True, code="CNT_001", message="Banners", data=banners)
