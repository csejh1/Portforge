from datetime import datetime, timedelta
import json
import random
import logging
import aioboto3
from typing import Optional
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.exceptions import BusinessException, ErrorCode
from app.schemas.ai_schema import (
    QuestionRequest, QuestionResponse, AnalysisRequest, AnalysisResponse, 
    QuestionItem, AnalysisResponse
)
from app.repositories.ai_repository import TestRepository
from app.models.ai_model import Test, TestResult

logger = logging.getLogger(__name__)

class AiService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.model_id = settings.BEDROCK_MODEL_ID
        self.region = settings.AWS_REGION
        
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.warning("AWS Credentials are missing. Bedrock calls may fail.")

    async def _invoke_bedrock(self, system_prompt: str, user_prompt: str) -> str:
        """
        Common method to invoke AWS Bedrock
        """
        async with self.session.client("bedrock-runtime", region_name=self.region) as client:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
                response = await client.invoke_model(modelId=self.model_id, body=json.dumps(body))
                response_body = await response['body'].read()
                response_json = json.loads(response_body)
                
                if 'content' in response_json:
                    return response_json['content'][0]['text']
                else:
                    raise BusinessException(ErrorCode.AI_INVALID_RESPONSE, "Invalid response format from Bedrock")
            except ClientError as e:
                logger.error(f"Bedrock ClientError: {e}")
                raise BusinessException(ErrorCode.AI_GENERATION_FAILED, f"AWS Bedrock Error: {str(e)}")
            except Exception as e:
                logger.error(f"Bedrock invocation failed: {e}")
                if isinstance(e, BusinessException): raise e
                raise BusinessException(ErrorCode.AI_GENERATION_FAILED, str(e))

    async def generate_questions(self, request: QuestionRequest, repo: TestRepository, user_id: str) -> QuestionResponse:
        # 1. 주간 테스트 횟수 제한 체크 (DB 실패 시 무시하고 진행)
        try:
            weekly_count = await repo.count_weekly_tests(user_id)
            if weekly_count >= 5:
                raise BusinessException(ErrorCode.TEST_LIMIT_EXCEEDED, "이번 주 테스트 가능 횟수(5회)를 모두 소진했습니다.")
        except BusinessException:
            raise
        except Exception:
            logger.warning("Failed to check weekly count (DB Error). Proceeding without check.")

        target_count = request.count
        db_limit = 3

        # 2. DB에서 문제 조회 (DB 실패 시 전량 AI 생성)
        existing_questions: list[Test] = []
        try:
            existing_questions = await repo.get_random_questions(request.stack, request.difficulty, db_limit)
        except Exception:
            logger.warning("Failed to fetch existing questions (DB Error). Fetching all from AI.")
        
        current_count = len(existing_questions)
        needed_from_ai = target_count - current_count
        
        # 최소 2개는 AI가 새로 만들도록 보장
        if needed_from_ai < 2:
            needed_from_ai = 2
            
        ai_questions_item = []
        if needed_from_ai > 0:
            ai_questions_item = await self._generate_questions_from_ai(request.stack, request.difficulty, needed_from_ai)
            
            # 4. 새로 생성된 문제는 DB에 저장 (실패 시 무시)
            try:
                for q_item in ai_questions_item:
                    new_test_row = Test(
                        stack_name=request.stack,
                        question_json=q_item.model_dump(),
                        difficulty=request.difficulty,
                        source_prompt="Hybrid Generation"
                    )
                    await repo.create_test(new_test_row)
            except Exception:
                logger.warning("Failed to save generated questions to DB.")
        
        # 5. DB 형식을 응답 형식으로 변환
        db_questions_item = [QuestionItem(**q.question_json) for q in existing_questions]
        
        # 6. 합치기 및 셔플
        final_list = db_questions_item + ai_questions_item
        random.shuffle(final_list)
        
        # 정확히 target_count 개수만큼 자르기
        final_list = final_list[:target_count]
        
        return QuestionResponse(questions=final_list)

    async def _generate_questions_from_ai(self, stack: str, difficulty: str, count: int) -> list[QuestionItem]:
        system_prompt = "당신은 전문 기술 면접관입니다. JSON 배열만 출력하세요."
        user_prompt = f"""
        '{stack}' 기술에 대한 {difficulty} 난이도의 객관식 문제 {count}개를 한국어로 생성하세요.
        
        형식: JSON 배열 (각 객체는 question, options[], answer(0-3), explanation 포함)
        - question: 질문 (한국어)
        - options: 4개의 선택지 (한국어)
        - answer: 정답 인덱스 (0~3)
        - explanation: 정답 설명 (한국어)
        
        JSON만 출력하세요. 마크다운 코드 블럭 없이 순수 JSON만.
        """
        try:
            result_text = await self._invoke_bedrock(system_prompt, user_prompt)
            # Markdown cleaning
            cleaned_text = result_text.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_text)
            return [QuestionItem(**item) for item in data]
        except Exception:
            raise BusinessException(ErrorCode.AI_INVALID_RESPONSE, "Failed to parse AI question response")

    async def analyze_results(self, request: AnalysisRequest, repo: TestRepository, user_id: str) -> AnalysisResponse:
        # 레벨 결정 로직
        level = self._determine_level(request.score)
        
        # AI 피드백 생성 (JSON 구조화: 장단점, 성장 가이드, 채용 가이드)
        system_prompt = "You are a senior developer mentor. Output strictly in valid JSON format."
        user_prompt = f"""
        Analyze the test result for stack '{request.stack}' (Score: {request.score}, Level: {level}).
        
        Provide the output in valid JSON format with the following keys:
        - "summary": (String) A detailed analysis of strengths and weaknesses (Combined, Korean, 2-3 sentences).
        - "growth_guide": (String) Specific technical topics to study next for the applicant (Korean).
        - "hiring_guide": (String) Advice for the hiring manager (Korean).

        Ensure the JSON is valid. Do not include markdown code blocks (```json).
        """
        try:
            feedback = await self._invoke_bedrock(system_prompt, user_prompt)
            # Markdown 코드 블럭 제거 (혹시 포함될 경우)
            feedback = feedback.replace("```json", "").replace("```", "").strip()
        except Exception as e:
            logger.error(f"Failed to generate AI feedback: {e}", exc_info=True)
            feedback = f"AI 분석 서비스를 일시적으로 사용할 수 없습니다. (Error: {str(e)[:50]}...)"

        # 결과 DB 저장
        try:
            new_result = TestResult(
                user_id=user_id,
                project_id=None, # 연습 모드인 경우
                test_type="APPLICATION", # 일단 기본값
                score=request.score,
                feedback=feedback
            )
            print(f"DEBUG: Saving TestResult for user {user_id}...")
            await repo.create_test_result(new_result)
            print(f"DEBUG: TestResult saved successfully!")
        except Exception as e:
            print(f"DEBUG: Failed to save test result: {e}")
            logger.error(f"Failed to save test result: {e}")
            # 저장은 실패해도 리턴은 해주는게 UX상 나음 (선택사항)
            # raise BusinessException(ErrorCode.DB_ERROR, "결과 저장 실패")
        
        return AnalysisResponse(
            score=request.score,
            level=level,
            feedback=feedback
        )

    async def get_latest_result(self, user_id: str, repo: TestRepository) -> Optional[AnalysisResponse]:
        try:
            result = await repo.get_latest_result_by_user(user_id)
            if not result:
                return None
            
            # Level 계산 (DB에 없으므로)
            score = result.score or 0
            level = "고급" if score >= 80 else "중급" if score >= 60 else "초급"
            
            return AnalysisResponse(
                score=score,
                level=level,
                feedback=result.feedback or ""
            )
        except Exception as e:
            logger.error(f"Error fetching test result: {e}")
            return None

    def _determine_level(self, score: int) -> str:
        if score >= 90: return '고급 (Expert)'
        if score >= 65: return '중급 (Advanced)'
        if score >= 35: return '초급 (Beginner)'
        return '입문 (Novice)'

    async def predict_applicant_suitability(self, applicants_data: list[dict]) -> str:
        system_prompt = "You are an expert HR manager and technical team lead."
        user_prompt = f"""
        Analyze the following candidates for a software project team:
        {json.dumps(applicants_data, ensure_ascii=False, indent=2)}

        Task:
        1. Recommend the most suitable candidate(s).
        2. Briefly analyze each candidate's strengths and weaknesses based on their score, feedback, and message.
        3. Provide final hiring advice.
        
        Language: Korean
        Format: Markdown (Use bullet points and bold text)
        """
        return await self._invoke_bedrock(system_prompt, user_prompt)

    async def generate_minutes_from_chat(self, chat_text: str) -> dict:
        """회의록 생성: 채팅 텍스트를 분석하여 구조화된 회의록 JSON 반환"""
        system_prompt = "You are an expert meeting secretary. Output purely JSON."
        user_prompt = f"""
    Summarize the following meeting chat logs into a structured JSON.
    JSON Structure: {{
        "date": "YYYY-MM-DD",
        "attendees": ["Name", ...],
        "agenda": "Main Topic",
        "decisions": ["Decision 1", ...],
        "action_items": [ {{"task": "Task description", "assignee": "Name"}} ],
        "summary": "Overall summary of the meeting"
    }}
    Language: Korean.
    
    [Chat Logs]
    {chat_text}
    """
        response_text = await self._invoke_bedrock(system_prompt, user_prompt)
        try:
             cleaned = response_text.strip().replace("```json", "").replace("```", "").strip()
             return json.loads(cleaned)
        except Exception:
             # Fallback if JSON parsing fails
             logger.warning("Failed to parse AI response as JSON. Returning raw text.")
             return {"summary": response_text}

ai_service = AiService()
