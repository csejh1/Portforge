from fastapi import APIRouter, Depends
from typing import Optional

from app.schemas.base import ResponseEnvelope
from app.core.deps import get_current_user
from app.services.notification_service import list_notifications

router = APIRouter()


@router.get("", response_model=ResponseEnvelope)
async def list_notifications_api(user_id: Optional[str] = None, current_user=Depends(get_current_user)):
    data = await list_notifications(user_id or str(current_user.get("id")))
    return ResponseEnvelope(success=True, code="NOTI_000", message="Notifications", data=data)
