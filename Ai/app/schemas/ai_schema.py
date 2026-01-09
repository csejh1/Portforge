from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Test Schemas ---
class QuestionRequest(BaseModel):
    stack: str
    difficulty: str = "초급"
    count: int = 5
    previous_questions: Optional[List[str]] = []

class QuestionItem(BaseModel):
    question: str
    options: List[str]
    answer: int
    explanation: str

class QuestionResponse(BaseModel):
    questions: List[QuestionItem]

class AnalysisRequest(BaseModel):
    stack: str
    total_questions: int
    correct_count: int
    score: int
    user_id: str
    user_answers: Optional[List[int]] = None

class AnalysisResponse(BaseModel):
    score: int
    level: str
    feedback: str

# --- Meeting Schemas ---
class MeetingStartRequest(BaseModel):
    team_id: int
    project_id: int = 1  # 프로젝트 ID 추가 (기본값 1)

class MeetingStartResponse(BaseModel):
    session_id: int
    status: str
    start_time: datetime

class MeetingEndRequest(BaseModel):
    session_id: int

class MeetingEndResponse(BaseModel):
    report_id: int
    title: str
    content_summary: str

# --- Portfolio Schemas ---
class PortfolioRequest(BaseModel):
    project_id: int
    user_id: str

class PortfolioResponse(BaseModel):
    result: dict

class ApplicantData(BaseModel):
    name: str
    position: str
    message: str
    score: Optional[int] = 0
    feedback: Optional[str] = ""

class ApplicantAnalysisRequest(BaseModel):
    applicants: List[ApplicantData]

class ApplicantAnalysisResponse(BaseModel):
    analysis: str

# --- Minutes Schemas ---
class ChatMessage(BaseModel):
    user: str
    msg: str
    time: Optional[str] = ""

class MinutesGenerateRequest(BaseModel):
    team_id: int
    project_id: int
    messages: List[ChatMessage]

class MinutesResponse(BaseModel):
    report_id: int
    title: str
    status: str
    s3_key: Optional[str]
    created_at: datetime
