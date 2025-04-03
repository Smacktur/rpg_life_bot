from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model representing a Telegram user"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, index=True)
    phase = Column(String, nullable=True)
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, phase={self.phase})>"

class Quest(Base):
    """Quest model representing a user task"""
    __tablename__ = "quests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    status = Column(String, default="todo")
    phase = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Quest(id={self.id}, text={self.text[:20]}{'...' if len(self.text) > 20 else ''}, status={self.status})>"

class Insight(Base):
    """Insight model representing user thoughts and ideas"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Insight(id={self.id}, text={self.text[:20]}{'...' if len(self.text) > 20 else ''})>"

class Reflection(Base):
    """Reflection model for evening reflections"""
    __tablename__ = "reflections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    important = Column(Text, nullable=True)
    worked = Column(Text, nullable=True)
    change = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Reflection(id={self.id}, created_at={self.created_at})>"

class LastActive(Base):
    """Last active model to track user activity"""
    __tablename__ = "last_active"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    timestamp = Column(DateTime, default=datetime.now)
    context = Column(String)
    phase = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<LastActive(user_id={self.user_id}, context={self.context})>" 