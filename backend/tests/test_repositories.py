"""
Tests for repositories - Using mocked database sessions.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.application_repo import ApplicationRepository
from app.repositories.session_repo import SessionRepository
from app.models.interview import InterviewApplication, InterviewSession


# ===== Fixtures =====

@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def mock_application():
    """Create a mock InterviewApplication."""
    app = MagicMock(spec=InterviewApplication)
    app.id = "test-app-id"
    app.user_id = "user-123"
    app.job_role = "Software Engineer"
    app.status = "in_progress"
    app.current_stage = 1
    return app


@pytest.fixture
def mock_session():
    """Create a mock InterviewSession."""
    session = MagicMock(spec=InterviewSession)
    session.id = 1
    session.session_id = "session-abc"
    session.user_id = "user-123"
    session.job_role = "Software Engineer"
    session.status = "pending"
    session.stage_type = "hr"
    return session


# ===== ApplicationRepository Tests =====

class TestApplicationRepositoryGetById:
    """Tests for ApplicationRepository.get_by_id."""
    
    @pytest.mark.asyncio
    async def test_returns_application_when_found(self, mock_db, mock_application):
        """Should return application when found."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_application
        mock_db.execute.return_value = mock_result
        
        repo = ApplicationRepository(mock_db)
        result = await repo.get_by_id("test-app-id")
        
        assert result is not None
        assert result.id == "test-app-id"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, mock_db):
        """Should return None when application not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        repo = ApplicationRepository(mock_db)
        result = await repo.get_by_id("nonexistent-id")
        
        assert result is None


class TestApplicationRepositoryGetByIdAndUser:
    """Tests for ApplicationRepository.get_by_id_and_user."""
    
    @pytest.mark.asyncio
    async def test_returns_application_for_valid_user(self, mock_db, mock_application):
        """Should return application when user matches."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_application
        mock_db.execute.return_value = mock_result
        
        repo = ApplicationRepository(mock_db)
        result = await repo.get_by_id_and_user("test-app-id", "user-123")
        
        assert result is not None
        assert result.user_id == "user-123"
    
    @pytest.mark.asyncio
    async def test_returns_none_for_wrong_user(self, mock_db):
        """Should return None when user doesn't match."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        repo = ApplicationRepository(mock_db)
        result = await repo.get_by_id_and_user("test-app-id", "wrong-user")
        
        assert result is None


class TestApplicationRepositoryCreate:
    """Tests for ApplicationRepository.create."""
    
    @pytest.mark.asyncio
    async def test_creates_application_with_defaults(self, mock_db):
        """Should create application with default status and stage."""
        repo = ApplicationRepository(mock_db)
        
        await repo.create(
            application_id="new-app-id",
            user_id="user-123",
            job_role="Developer"
        )
        
        # Verify db.add was called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify the object passed to add
        added_app = mock_db.add.call_args[0][0]
        assert added_app.status == "in_progress"
        assert added_app.current_stage == 1


class TestApplicationRepositoryUpdateStage:
    """Tests for ApplicationRepository.update_stage."""
    
    @pytest.mark.asyncio
    async def test_updates_stage_number(self, mock_db, mock_application):
        """Should update stage number."""
        repo = ApplicationRepository(mock_db)
        
        await repo.update_stage(mock_application, new_stage=2)
        
        assert mock_application.current_stage == 2
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_updates_status_when_provided(self, mock_db, mock_application):
        """Should update status when provided."""
        repo = ApplicationRepository(mock_db)
        
        await repo.update_stage(mock_application, new_stage=3, status="completed")
        
        assert mock_application.current_stage == 3
        assert mock_application.status == "completed"


# ===== SessionRepository Tests =====

class TestSessionRepositoryGetBySessionId:
    """Tests for SessionRepository.get_by_session_id."""
    
    @pytest.mark.asyncio
    async def test_returns_session_when_found(self, mock_db, mock_session):
        """Should return session when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result
        
        repo = SessionRepository(mock_db)
        result = await repo.get_by_session_id("session-abc")
        
        assert result is not None
        assert result.session_id == "session-abc"
    
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, mock_db):
        """Should return None when session not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        repo = SessionRepository(mock_db)
        result = await repo.get_by_session_id("nonexistent")
        
        assert result is None


class TestSessionRepositoryCreate:
    """Tests for SessionRepository.create."""
    
    @pytest.mark.asyncio
    async def test_creates_session_with_stage_type(self, mock_db):
        """Should create session with stage_type."""
        repo = SessionRepository(mock_db)
        
        await repo.create(
            session_id="new-session",
            user_id="user-123",
            job_role="Developer",
            stage_type="technical"
        )
        
        mock_db.add.assert_called_once()
        added_session = mock_db.add.call_args[0][0]
        assert added_session.stage_type == "technical"
        assert added_session.status == "pending"


class TestSessionRepositoryUpdateTranscript:
    """Tests for SessionRepository.update_transcript."""
    
    @pytest.mark.asyncio
    async def test_updates_transcript_and_returns_true(self, mock_db):
        """Should update transcript and return True."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db.execute.return_value = mock_result
        
        repo = SessionRepository(mock_db)
        result = await repo.update_transcript("session-abc", '{"messages":[]}')
        
        assert result is True
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self, mock_db):
        """Should return False when session not found."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db.execute.return_value = mock_result
        
        repo = SessionRepository(mock_db)
        result = await repo.update_transcript("nonexistent", '{}')
        
        assert result is False


class TestSessionRepositoryUpdateFeedback:
    """Tests for SessionRepository.update_feedback."""
    
    @pytest.mark.asyncio
    async def test_updates_feedback_and_score(self, mock_db):
        """Should update feedback and overall score."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db.execute.return_value = mock_result
        
        repo = SessionRepository(mock_db)
        result = await repo.update_feedback(
            "session-abc",
            "Great interview!",
            overall_score=85
        )
        
        assert result is True
        mock_db.commit.assert_called_once()
