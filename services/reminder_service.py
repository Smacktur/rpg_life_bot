from db.database import get_session
from db.models import User
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Optional
from datetime import datetime

class ReminderService:
    """Service for managing reminder settings and operations"""
    
    @staticmethod
    async def set_reminder(telegram_id: str, time: str, enabled: bool = True) -> bool:
        """
        Set reminder time for a user.
        
        Args:
            telegram_id: User's Telegram ID
            time: Time string in HH:MM format
            enabled: Whether the reminder is enabled
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate time format
            datetime.strptime(time, "%H:%M")
            
            async with get_session() as session:
                # Get user
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalars().first()
                
                if not user:
                    return False
                
                # Update reminder settings
                stmt = (
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        reminder_time=time,
                        reminder_enabled=enabled
                    )
                )
                await session.execute(stmt)
                await session.commit()
                
                return True
        except ValueError:
            # Invalid time format
            return False
        except Exception:
            return False
    
    @staticmethod
    async def disable_reminder(telegram_id: str) -> bool:
        """
        Disable reminder for a user.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with get_session() as session:
                # Update reminder settings
                stmt = (
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(reminder_enabled=False)
                )
                await session.execute(stmt)
                await session.commit()
                
                return True
        except Exception:
            return False
    
    @staticmethod
    async def get_users_for_reminder(time: str) -> List[User]:
        """
        Get all users who should receive a reminder at the specified time.
        
        Args:
            time: Time string in HH:MM format
            
        Returns:
            List of users who have reminders set for the specified time
        """
        async with get_session() as session:
            result = await session.execute(
                select(User).where(
                    User.reminder_enabled == True,
                    User.reminder_time == time
                )
            )
            return result.scalars().all() 