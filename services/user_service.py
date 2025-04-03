from db.database import get_session
from db.models import User, Quest, Insight, Reflection, LastActive
from sqlalchemy.future import select
from sqlalchemy import update, delete
from datetime import datetime
from typing import List, Optional, Dict, Any

class UserService:
    """Service for user-related operations"""
    
    @staticmethod
    async def get_or_create_user(telegram_id: str) -> User:
        """Get user by telegram_id or create if not exists"""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalars().first()
            
            if not user:
                user = User(telegram_id=telegram_id)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                
            return user
    
    @staticmethod
    async def update_phase(telegram_id: str, phase: str) -> None:
        """Update user phase"""
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(phase=phase)
            )
            await session.execute(stmt)
            
            # Update last active
            await UserService.update_last_active(telegram_id, "phase", phase)
            await session.commit()
    
    @staticmethod
    async def update_last_active(telegram_id: str, context: str, phase: Optional[str] = None) -> None:
        """Update user's last active status"""
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            # Get current phase if not provided
            if not phase:
                phase = user.phase
            
            # Check if last active exists
            result = await session.execute(
                select(LastActive).where(LastActive.user_id == user.id)
            )
            last_active = result.scalars().first()
            
            if last_active:
                # Update existing
                stmt = (
                    update(LastActive)
                    .where(LastActive.user_id == user.id)
                    .values(
                        timestamp=datetime.now(),
                        context=context,
                        phase=phase
                    )
                )
                await session.execute(stmt)
            else:
                # Create new
                last_active = LastActive(
                    user_id=user.id,
                    timestamp=datetime.now(),
                    context=context,
                    phase=phase
                )
                session.add(last_active)
            
            await session.commit()
            
    @staticmethod
    async def get_user_data(telegram_id: str) -> Dict[str, Any]:
        """Get comprehensive user data including stats"""
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            # Get quests
            result = await session.execute(
                select(Quest).where(Quest.user_id == user.id)
            )
            quests = result.scalars().all()
            
            # Get insights
            result = await session.execute(
                select(Insight).where(Insight.user_id == user.id)
            )
            insights = result.scalars().all()
            
            # Get reflections
            result = await session.execute(
                select(Reflection).where(Reflection.user_id == user.id)
            )
            reflections = result.scalars().all()
            
            # Get last active
            result = await session.execute(
                select(LastActive).where(LastActive.user_id == user.id)
            )
            last_active = result.scalars().first()
            
            # Calculate stats
            active_quests = [q for q in quests if q.status == "todo"]
            done_quests = [q for q in quests if q.status == "done"]
            
            return {
                "user": user,
                "phase": user.phase,
                "quests": quests,
                "insights": insights,
                "reflections": reflections,
                "last_active": last_active,
                "stats": {
                    "active_quests": len(active_quests),
                    "done_quests": len(done_quests),
                    "total_insights": len(insights),
                    "total_reflections": len(reflections)
                }
            } 