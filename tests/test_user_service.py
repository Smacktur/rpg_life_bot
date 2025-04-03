import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Base, User
from services.user_service import UserService

# Configure test logger
logging.basicConfig(level=logging.DEBUG)

# Create test database in memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def setup_test_db():
    """Set up an in-memory test database"""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Yield the session factory for tests
    yield async_session
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_get_or_create_user(setup_test_db):
    """Test creating and retrieving a user"""
    # Mock the database session
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    
    # Mock the query result for a non-existent user
    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    session.execute.return_value = result_mock
    
    # Mock the session context manager
    session_factory = setup_test_db
    session_factory.return_value.__aenter__.return_value = session
    
    with patch('services.user_service.get_session', return_value=session_factory()):
        # Test creating a new user
        telegram_id = "123456789"
        user = await UserService.get_or_create_user(telegram_id)
        
        # Verify session.add was called
        assert session.add.called
        
        # Verify commit was called
        assert session.commit.called
        
        # Verify refresh was called
        assert session.refresh.called


@pytest.mark.asyncio
async def test_update_phase(setup_test_db):
    """Test updating a user's phase"""
    # Mock the database session
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    
    # Mock the get_or_create_user method
    user_mock = MagicMock()
    user_mock.id = 1
    
    # Mock the session context manager
    session_factory = setup_test_db
    session_factory.return_value.__aenter__.return_value = session
    
    with patch('services.user_service.get_session', return_value=session_factory()):
        with patch('services.user_service.UserService.get_or_create_user', 
                  AsyncMock(return_value=user_mock)):
            with patch('services.user_service.UserService.update_last_active', 
                      AsyncMock()):
                # Test updating phase
                telegram_id = "123456789"
                phase = "active"
                await UserService.update_phase(telegram_id, phase)
                
                # Verify execute was called
                assert session.execute.called
                
                # Verify commit was called
                assert session.commit.called 