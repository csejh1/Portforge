from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.ai_model import Test, TestResult, Portfolio, MeetingSession, GeneratedReport
from typing import List, Optional
from datetime import datetime, timedelta

class TestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_test(self, test: Test) -> Test:
        self.session.add(test)
        await self.session.commit()
        await self.session.refresh(test)
        return test

    async def get_random_questions(self, stack: str, difficulty: str, limit: int) -> List[Test]:
        # MySQL의 RAND()는 성능 이슈가 있을 수 있어, 우선 간단히 최신순으로 가져와서 랜덤은 서비스 레벨에서 처리 추천
        # 여기서는 단순 조회 구현
        result = await self.session.execute(
            select(Test)
            .where(Test.stack_name == stack)
            .where(Test.difficulty == difficulty)
            .order_by(desc(Test.created_at)) 
            .limit(limit * 2) # 여유 있게 가져옴
        )
        return result.scalars().all()

    async def create_test_result(self, result: TestResult):
        self.session.add(result)
        await self.session.commit()
        return result

    async def count_weekly_tests(self, user_id: str) -> int:
        one_week_ago = datetime.now() - timedelta(days=7)
        result = await self.session.execute(
            select(func.count(TestResult.result_id))
            .where(TestResult.user_id == user_id)
            .where(TestResult.created_at >= one_week_ago)
        )
        return result.scalar() or 0

    async def get_latest_result_by_user(self, user_id: str) -> Optional[TestResult]:
        result = await self.session.execute(
            select(TestResult)
            .where(TestResult.user_id == user_id)
            .order_by(desc(TestResult.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

class PortfolioRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_portfolio(self, portfolio: Portfolio):
        self.session.add(portfolio)
        await self.session.commit()
        return portfolio
    
    async def get_portfolio_by_project(self, user_id: str, project_id: int):
        result = await self.session.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .where(Portfolio.project_id == project_id)
        )
        return result.scalar_one_or_none()
