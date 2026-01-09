from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ai_model import MeetingSession, GeneratedReport
from app.core.exceptions import BusinessException, ErrorCode
from app.core.database import aws_manager
import logging
from app.adapters.s3_adapter import s3_adapter
from app.utils.s3_paths import s3_path_manager, get_meeting_s3_key, get_chat_backup_s3_key

logger = logging.getLogger(__name__)

class MeetingService:
    async def start_meeting(self, db: AsyncSession, team_id: int, project_id: int = None) -> MeetingSession:
        """
        회의 시작: 세션 기록 생성
        
        Args:
            db: DB 세션
            team_id: 팀 ID
            project_id: 프로젝트 ID (선택)
        """
        new_session = MeetingSession(
            team_id=team_id,
            project_id=project_id,
            start_time=datetime.now(),
            status="IN_PROGRESS"
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        
        return new_session

    async def end_meeting(self, db: AsyncSession, session_id: int, user_id: str) -> GeneratedReport:
        """
        회의 종료: 
        1. 세션 상태 종료로 변경
        2. DDB에서 채팅 로그 수집
        3. Bedrock으로 회의록 요약 생성
        4. 결과 저장
        """
        # 1. 세션 조회 및 종료 처리
        result = await db.execute(select(MeetingSession).where(MeetingSession.session_id == session_id))
        session = result.scalar_one_or_none()
        
        if not session:
            raise BusinessException(ErrorCode.INVALID_INPUT, "존재하지 않는 회의 세션입니다.")
            
        if session.status == "COMPLETED":
            raise BusinessException(ErrorCode.INVALID_INPUT, "이미 종료된 회의입니다.")
            
        session.end_time = datetime.now()
        session.status = "COMPLETED"
        
        # 2. 채팅 로그 수집 (DynamoDB)
        chat_logs = await self._fetch_chat_logs_from_ddb(
            team_id=session.team_id, 
            project_id=session.project_id,
            start_time=session.start_time, 
            end_time=session.end_time
        )
        
        if not chat_logs:
            summary_content = {"summary": "회의 중 대화 내용이 없습니다."}
        else:
            # 3. AI 요약 생성
            from app.services.ai_service import ai_service
            from app.core.config import settings
            chats_text = "\n".join([f"[{c['time']}] {c['user']}: {c['msg']}" for c in chat_logs])
            summary_content = await ai_service.generate_minutes_from_chat(chats_text)

        # 4. 리포트 생성 (PENDING)
        report = GeneratedReport(
            team_id=session.team_id,
            project_id=session.project_id,
            created_by=user_id,
            report_type="MEETING_MINUTES",
            title=f"{session.start_time.strftime('%Y-%m-%d')} 정기 회의록",
            status="PENDING"
        )
        db.add(report)
        await db.flush()
        
        # 5. Upload to S3 (using s3_paths module)
        s3_key = s3_path_manager.team_report(session.team_id, report.report_id, "meeting_minutes")
        await aws_manager.get_s3_adapter().upload_json(s3_key, summary_content)
        
        # 6. Update Report
        report.s3_key = s3_key
        report.status = "COMPLETED"
        
        # 세션과 리포트 연결
        session.generated_report_id = report.report_id
        await db.commit()
        
        return report

    async def _fetch_chat_logs_from_ddb(
        self, 
        team_id: int, 
        project_id: int,
        start_time: datetime, 
        end_time: datetime
    ) -> list[dict]:
        """
        DynamoDB에서 회의 중 채팅 로그를 조회
        """
        from app.adapters.dynamodb_adapter import dynamodb_adapter
        
        try:
            start_date = start_time.strftime("%Y-%m-%d")
            end_date = end_time.strftime("%Y-%m-%d")
            
            effective_project_id = project_id if project_id else 1
            if not project_id:
                logger.warning(f"project_id is None - using default project_id=1")
            
            messages = await dynamodb_adapter.get_chat_messages(
                team_id=team_id,
                project_id=effective_project_id,
                start_date=start_date,
                end_date=end_date,
                meeting_only=True
            )
            
            # 시간 범위로 추가 필터링
            start_timestamp = int(start_time.timestamp() * 1000)
            end_timestamp = int(end_time.timestamp() * 1000)
            
            filtered_messages = [
                msg for msg in messages
                if start_timestamp <= msg.get('timestamp', 0) <= end_timestamp
            ]
            
            logger.info(f"Fetched {len(filtered_messages)} chat messages from DynamoDB for team {team_id}, project {effective_project_id}")
            return filtered_messages
            
        except Exception as e:
            logger.error(f"Failed to fetch chat logs from DynamoDB: {e}")
            return []

    async def _generate_meeting_minutes_ai(self, chat_logs: list[dict]) -> str:
        """
        AWS Bedrock 호출하여 회의록 생성
        """
        from app.services.ai_service import ai_service
        
        chats_text = "\n".join([f"[{c['time']}] {c['user']}: {c['msg']}" for c in chat_logs])
        
        system_prompt = "You are an expert meeting secretary."
        user_prompt = f"""
        Summarize the following meeting chat logs into a structured meeting minute.
        Include: Date, Attendees, Agenda, Key Decisions, Action Items.
        Language: Korean.
        
        [Chat Logs]
        {chats_text}
        """
        
        return await ai_service._invoke_bedrock(system_prompt, user_prompt)

    async def generate_meeting_minutes(self, db: AsyncSession, team_id: int, project_id: int, messages: list[dict], user_id: str) -> GeneratedReport:
        # 1. Create Report Record (PENDING)
        new_report = GeneratedReport(
            team_id=team_id,
            project_id=project_id,
            created_by=user_id,
            report_type="MEETING_MINUTES",
            title=f"{datetime.now().strftime('%Y-%m-%d')} 정기 회의록",
            status="PENDING"
        )
        db.add(new_report)
        await db.flush()

        try:
            from app.services.ai_service import ai_service
            from app.core.config import settings
            
            chat_text = "\n".join([f"[{m.get('time','?')}] {m.get('user','?')}: {m.get('msg','')}" for m in messages])
            
            # 2. Upload Raw Chat Logs (using s3_paths module)
            raw_key = get_chat_backup_s3_key(team_id)
            await aws_manager.get_s3_adapter().upload_json(raw_key, messages)

            # 3. Generate Minutes via AI
            minutes_json = await ai_service.generate_minutes_from_chat(chat_text)

            # 4. Upload Result to S3 (using s3_paths module)
            result_key = s3_path_manager.team_report(team_id, new_report.report_id, "meeting_minutes")
            await aws_manager.get_s3_adapter().upload_json(result_key, minutes_json)

            # 5. Update Report Status
            new_report.s3_key = result_key
            new_report.status = "COMPLETED"
            await db.commit()
            
            return new_report

        except Exception as e:
            logger.error(f"Failed to generate minutes: {e}")
            new_report.status = "FAILED"
            await db.commit()
            raise BusinessException(ErrorCode.AI_GENERATION_FAILED, str(e))

    async def get_report_content(self, s3_key: str) -> dict:
        logger.info(f"Fetching report content from S3: {s3_key}")
        try:
            content = await aws_manager.get_s3_adapter().get_json(s3_key)
            logger.info(f"Successfully fetched content: {list(content.keys()) if isinstance(content, dict) else type(content)}")
            return content
        except Exception as e:
            logger.error(f"Failed to read report content from {s3_key}: {e}")
            raise BusinessException(ErrorCode.NOT_FOUND, f"리포트 파일을 찾을 수 없습니다: {s3_key}")

    async def generate_daily_meeting_minutes(
        self, 
        db: AsyncSession, 
        team_id: int, 
        project_id: int, 
        messages: list[dict], 
        user_id: str,
        target_date: str = None
    ) -> GeneratedReport:
        """
        일단위 회의록 생성/업데이트
        - 같은 날 회의록이 이미 있으면 기존 내용 + 새 내용 합쳐서 업데이트
        - 없으면 새로 생성
        """
        from app.services.ai_service import ai_service
        from app.core.config import settings
        from datetime import date as date_type
        
        if not target_date:
            target_date = date_type.today().isoformat()
        
        logger.info(f"Generating daily minutes for team={team_id}, project={project_id}, date={target_date}")
        logger.info(f"New messages count: {len(messages)}")
        
        # 1. 해당 날짜의 기존 회의록 확인
        existing_report = await db.execute(
            select(GeneratedReport).where(
                GeneratedReport.team_id == team_id,
                GeneratedReport.project_id == project_id,
                GeneratedReport.report_type == "DAILY_MEETING_MINUTES",
                GeneratedReport.title == f"{target_date} 일일 회의록"
            )
        )
        existing = existing_report.scalar_one_or_none()
        
        # Using s3_paths module for consistent path generation
        daily_s3_key = get_meeting_s3_key(team_id, target_date)
        chat_s3_key = get_chat_backup_s3_key(team_id, target_date)
        
        logger.info(f"S3 keys - meetings: {daily_s3_key}, chats: {chat_s3_key}")
        
        # 2. 기존 원본 메시지 + 새 메시지 합치기
        all_messages = []
        if existing and existing.s3_key:
            try:
                logger.info(f"Loading existing chat messages from {chat_s3_key}")
                existing_raw = await aws_manager.get_s3_adapter().get_json(chat_s3_key)
                if isinstance(existing_raw, list):
                    all_messages.extend(existing_raw)
                    logger.info(f"Loaded {len(existing_raw)} existing messages")
            except Exception as e:
                logger.warning(f"Failed to load existing raw messages (may not exist yet): {e}")
        
        # 새 메시지 추가
        for msg in messages:
            all_messages.append({
                'user': msg.get('user', ''),
                'msg': msg.get('msg', ''),
                'time': msg.get('time', ''),
                'timestamp': msg.get('timestamp', 0),
                'is_in_meeting': msg.get('is_in_meeting', msg.get('isInMeeting', True))
            })
        
        logger.info(f"Total messages after merge: {len(all_messages)}")
        
        # 3. 원본 채팅 메시지 저장
        await aws_manager.get_s3_adapter().upload_json(chat_s3_key, all_messages)
        logger.info(f"Saved chat messages to {chat_s3_key}")
        
        # 4. AI로 전체 내용 기반 회의록 재생성
        chat_text = "\n".join([f"[{m.get('time','?')}] {m.get('user','?')}: {m.get('msg','')}" for m in all_messages])
        logger.info(f"Generating AI summary for {len(all_messages)} messages")
        
        minutes_json = await ai_service.generate_minutes_from_chat(chat_text)
        logger.info(f"AI generated minutes: {list(minutes_json.keys()) if isinstance(minutes_json, dict) else 'not a dict'}")
        
        # 5. 결과 저장
        await aws_manager.get_s3_adapter().upload_json(daily_s3_key, minutes_json)
        logger.info(f"Saved minutes to {daily_s3_key}")
        
        # 6. DB 레코드 생성 또는 업데이트
        if existing:
            existing.status = "COMPLETED"
            existing.s3_key = daily_s3_key
            await db.commit()
            logger.info(f"Updated existing daily meeting minutes for {target_date}, report_id={existing.report_id}")
            return existing
        else:
            new_report = GeneratedReport(
                team_id=team_id,
                project_id=project_id,
                created_by=user_id,
                report_type="DAILY_MEETING_MINUTES",
                title=f"{target_date} 일일 회의록",
                status="COMPLETED",
                s3_key=daily_s3_key
            )
            db.add(new_report)
            await db.commit()
            await db.refresh(new_report)
            logger.info(f"Created new daily meeting minutes for {target_date}, report_id={new_report.report_id}")
            return new_report


meeting_service = MeetingService()
