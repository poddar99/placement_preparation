import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.models.dsa import DSAProgress, DSATopic, UserStats
from app.services.llm_service import llm_service


class MentorService:
    """AI mentor with personalized context from user progress."""

    async def _build_user_context(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = stats_result.scalar_one_or_none()

        progress_result = await db.execute(
            select(DSAProgress, DSATopic)
            .join(DSATopic, DSAProgress.topic_id == DSATopic.id)
            .where(DSAProgress.user_id == user_id)
        )
        progress_rows = progress_result.all()

        dsa_info = []
        for prog, topic in progress_rows:
            pct = (prog.problems_solved / topic.total_problems * 100) if topic.total_problems > 0 else 0
            dsa_info.append({
                "topic": topic.name,
                "solved": prog.problems_solved,
                "total": topic.total_problems,
                "progress_percent": round(pct, 1),
                "level": prog.proficiency_level,
            })

        return {
            "contest_rating": stats.contest_rating if stats else 0,
            "total_problems_solved": stats.total_problems_solved if stats else 0,
            "dsa_progress": dsa_info,
        }

    async def chat(
        self,
        db: AsyncSession,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str]:
        if not session_id:
            session_id = str(uuid.uuid4())

        context = await self._build_user_context(db, user_id)

        history_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(20)
        )
        history = history_result.scalars().all()

        system_content = f"""You are PlacementPilot AI Mentor — a friendly, knowledgeable placement preparation coach.

Student profile:
- Name: {user_profile.get('full_name', 'Student') if user_profile else 'Student'}
- College: {user_profile.get('college', 'N/A') if user_profile else 'N/A'}
- Branch: {user_profile.get('branch', 'N/A') if user_profile else 'N/A'}
- Target companies: {user_profile.get('target_companies', []) if user_profile else []}
- Graduation year: {user_profile.get('graduation_year', 'N/A') if user_profile else 'N/A'}

Current progress:
- Contest rating: {context['contest_rating']}
- Total problems solved: {context['total_problems_solved']}
- DSA progress: {context['dsa_progress']}

Provide personalized, actionable advice. Be encouraging but honest. Reference their actual progress when relevant."""

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        reply = await llm_service.chat(messages, temperature=0.7)

        user_msg = ChatMessage(user_id=user_id, role="user", content=message, session_id=session_id)
        assistant_msg = ChatMessage(user_id=user_id, role="assistant", content=reply, session_id=session_id)
        db.add(user_msg)
        db.add(assistant_msg)
        await db.flush()

        return session_id, reply

    async def get_history(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        if session_id:
            query = query.where(ChatMessage.session_id == session_id)
        query = query.order_by(ChatMessage.created_at.asc())

        result = await db.execute(query)
        return list(result.scalars().all())


mentor_service = MentorService()