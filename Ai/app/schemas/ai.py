from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestResultResponse(BaseModel):
    result_id: int
    user_id: str
    project_id: Optional[int] = None
    application_id: Optional[int] = None
    test_type: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GeneratedReportResponse(BaseModel):
    report_id: int
    team_id: int
    project_id: Optional[int] = None
    created_by: str
    report_type: str
    status: str
    model_id: Optional[str] = None
    title: Optional[str] = None
    s3_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    portfolio_id: int
    user_id: str
    project_id: int
    title: str
    summary: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True