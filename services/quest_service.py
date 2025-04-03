from db.database import get_session
from db.models import Quest, User
from sqlalchemy.future import select
from sqlalchemy import update, delete
from datetime import datetime
from typing import List, Optional, Dict, Any

from services.user_service import UserService

class QuestService:
    """Service for quest-related operations"""
    
    @staticmethod
    async def add_quest(telegram_id: str, text: str, phase: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new quest for the user.
        
        Args:
            telegram_id: User's Telegram ID
            text: Quest text/description
            phase: Current user phase or None to use user's phase
            
        Returns:
            Dict with quest data and success status
        """
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            # If phase not provided, use user's phase
            if not phase:
                phase = user.phase
            
            # Create new quest
            quest = Quest(
                user_id=user.id,
                text=text,
                status="todo",
                phase=phase,
                created_at=datetime.now()
            )
            
            session.add(quest)
            await session.commit()
            await session.refresh(quest)
            
            # Update last active
            await UserService.update_last_active(telegram_id, "quest", phase)
            
            return {
                "success": True,
                "quest": quest
            }
    
    @staticmethod
    async def complete_quest(telegram_id: str, quest_id: int) -> Dict[str, Any]:
        """
        Mark a quest as completed.
        
        Args:
            telegram_id: User's Telegram ID
            quest_id: Quest ID to complete
            
        Returns:
            Dict with success status and message
        """
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            # Find quest
            result = await session.execute(
                select(Quest).where(Quest.id == quest_id, Quest.user_id == user.id)
            )
            quest = result.scalars().first()
            
            if not quest:
                return {
                    "success": False,
                    "message": "Квест не найден или не принадлежит пользователю"
                }
            
            if quest.status == "done":
                return {
                    "success": False,
                    "message": "Квест уже завершен"
                }
            
            # Update quest status
            stmt = (
                update(Quest)
                .where(Quest.id == quest_id)
                .values(
                    status="done",
                    completed_at=datetime.now()
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            # Update last active
            await UserService.update_last_active(telegram_id, "quest_done")
            
            return {
                "success": True,
                "message": "Квест успешно завершен"
            }
    
    @staticmethod
    async def delete_quest(telegram_id: str, quest_id: int) -> Dict[str, Any]:
        """
        Delete a quest.
        
        Args:
            telegram_id: User's Telegram ID
            quest_id: Quest ID to delete
            
        Returns:
            Dict with success status and message
        """
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            # Find quest
            result = await session.execute(
                select(Quest).where(Quest.id == quest_id, Quest.user_id == user.id)
            )
            quest = result.scalars().first()
            
            if not quest:
                return {
                    "success": False,
                    "message": "Квест не найден или не принадлежит пользователю"
                }
            
            # Delete quest
            stmt = delete(Quest).where(Quest.id == quest_id)
            await session.execute(stmt)
            await session.commit()
            
            return {
                "success": True,
                "message": "Квест успешно удален"
            }
    
    @staticmethod
    async def get_user_quests(telegram_id: str, status: Optional[str] = None) -> List[Quest]:
        """
        Get quests for a user, optionally filtered by status.
        
        Args:
            telegram_id: User's Telegram ID
            status: Optional status filter ("todo", "done", or None for all)
            
        Returns:
            List of quests
        """
        async with get_session() as session:
            user = await UserService.get_or_create_user(telegram_id)
            
            query = select(Quest).where(Quest.user_id == user.id)
            
            if status:
                query = query.where(Quest.status == status)
                
            result = await session.execute(query)
            quests = result.scalars().all()
            
            return quests 