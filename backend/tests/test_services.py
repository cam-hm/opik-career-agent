"""
Tests for services - Business logic layer.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.core.exceptions import ApplicationNotFoundError, ApplicationNotInProgressError


# ===== Fixtures =====

@pytest.fixture
def mock_app_repo():
    """Create a mock ApplicationRepository."""
    return AsyncMock()


@pytest.fixture
def mock_session_repo():
    """Create a mock SessionRepository."""
    return AsyncMock()


@pytest.fixture
def mock_application():
    """Create a mock application object."""
    app = MagicMock()
    app.id = "app-123"
    app.user_id = "user-123"
    app.job_role = "Developer"
    app.status = "in_progress"
    app.current_stage = 1
    return app


# ===== ApplicationService Tests =====

class TestApplicationServiceCreateApplication:
    """Tests for ApplicationService.create_application."""
    
    @pytest.mark.asyncio
    async def test_creates_application_with_uuid(self, mock_app_repo):
        """Should create application with generated UUID."""
        mock_app_repo.create.return_value = MagicMock(id="generated-uuid")
        
        service = ApplicationService(mock_app_repo)
        result = await service.create_application(
            user_id="user-123",
            job_role="Developer"
        )
        
        mock_app_repo.create.assert_called_once()
        # Verify UUID was generated (36 chars with dashes)
        call_args = mock_app_repo.create.call_args
        assert len(call_args.kwargs["application_id"]) == 36


class TestApplicationServiceGetApplication:
    """Tests for ApplicationService.get_application."""
    
    @pytest.mark.asyncio
    async def test_returns_application_when_found(self, mock_app_repo, mock_application):
        """Should return application when found."""
        mock_app_repo.get_by_id_and_user.return_value = mock_application
        
        service = ApplicationService(mock_app_repo)
        result = await service.get_application("app-123", "user-123")
        
        assert result.id == "app-123"
    
    @pytest.mark.asyncio
    async def test_raises_not_found_when_missing(self, mock_app_repo):
        """Should raise ApplicationNotFoundError when not found."""
        mock_app_repo.get_by_id_and_user.return_value = None
        
        service = ApplicationService(mock_app_repo)
        
        with pytest.raises(ApplicationNotFoundError):
            await service.get_application("nonexistent", "user-123")


class TestApplicationServiceStartStage:
    """Tests for ApplicationService.start_stage."""
    
    @pytest.mark.asyncio
    async def test_returns_app_and_stage_type(self, mock_app_repo, mock_application):
        """Should return application and correct stage type."""
        mock_app_repo.get_by_id_and_user.return_value = mock_application
        
        service = ApplicationService(mock_app_repo)
        app, stage_type = await service.start_stage("app-123", "user-123")
        
        assert app.id == "app-123"
        assert stage_type == "hr"  # Stage 1 = HR
    
    @pytest.mark.asyncio
    async def test_raises_not_found_when_missing(self, mock_app_repo):
        """Should raise ApplicationNotFoundError when app not found."""
        mock_app_repo.get_by_id_and_user.return_value = None
        
        service = ApplicationService(mock_app_repo)
        
        with pytest.raises(ApplicationNotFoundError):
            await service.start_stage("nonexistent", "user-123")
    
    @pytest.mark.asyncio
    async def test_raises_not_in_progress(self, mock_app_repo, mock_application):
        """Should raise ApplicationNotInProgressError when status is not in_progress."""
        mock_application.status = "completed"
        mock_app_repo.get_by_id_and_user.return_value = mock_application
        
        service = ApplicationService(mock_app_repo)
        
        with pytest.raises(ApplicationNotInProgressError):
            await service.start_stage("app-123", "user-123")


class TestApplicationServiceAdvanceStage:
    """Tests for ApplicationService.advance_stage."""
    
    @pytest.mark.asyncio
    async def test_increments_stage_from_1_to_2(self, mock_app_repo, mock_application):
        """Should increment stage from 1 to 2."""
        mock_application.current_stage = 1
        mock_app_repo.get_by_id.return_value = mock_application
        mock_app_repo.update_stage.return_value = mock_application
        
        service = ApplicationService(mock_app_repo)
        await service.advance_stage("app-123")
        
        mock_app_repo.update_stage.assert_called_once()
        call_args = mock_app_repo.update_stage.call_args
        assert call_args.args[1] == 2  # new_stage
    
    @pytest.mark.asyncio
    async def test_completes_at_stage_3(self, mock_app_repo, mock_application):
        """Should set status to completed at stage 3."""
        mock_application.current_stage = 3
        mock_app_repo.get_by_id.return_value = mock_application
        mock_app_repo.update_stage.return_value = mock_application
        
        service = ApplicationService(mock_app_repo)
        await service.advance_stage("app-123")
        
        call_args = mock_app_repo.update_stage.call_args
        assert call_args.kwargs.get("status") == "completed"
    
    @pytest.mark.asyncio
    async def test_raises_not_found(self, mock_app_repo):
        """Should raise ApplicationNotFoundError when not found."""
        mock_app_repo.get_by_id.return_value = None
        
        service = ApplicationService(mock_app_repo)
        
        with pytest.raises(ApplicationNotFoundError):
            await service.advance_stage("nonexistent")


# ===== InterviewService Tests =====

class TestInterviewServiceCreateSession:
    """Tests for InterviewService.create_session."""
    
    @pytest.mark.asyncio
    async def test_creates_session_with_stage_type(self, mock_session_repo):
        """Should create session with stage_type."""
        mock_session_repo.create.return_value = MagicMock(session_id="session-xyz")
        
        service = InterviewService(mock_session_repo)
        result = await service.create_session(
            resume_text="Python developer",
            job_role="Developer",
            stage_type="technical"
        )
        
        mock_session_repo.create.assert_called_once()
        call_args = mock_session_repo.create.call_args
        assert call_args.kwargs["stage_type"] == "technical"
    
    @pytest.mark.asyncio
    async def test_generates_session_id(self, mock_session_repo):
        """Should generate session_id starting with 'session_'."""
        mock_session_repo.create.return_value = MagicMock()
        
        service = InterviewService(mock_session_repo)
        await service.create_session(
            resume_text="Resume",
            job_role="Developer"
        )
        
        call_args = mock_session_repo.create.call_args
        assert call_args.kwargs["session_id"].startswith("session_")


class TestInterviewServiceGetSession:
    """Tests for InterviewService.get_session."""
    
    @pytest.mark.asyncio
    async def test_returns_session_when_found(self, mock_session_repo):
        """Should return session when found."""
        mock_session = MagicMock(session_id="session-abc")
        mock_session_repo.get_by_session_id.return_value = mock_session
        
        service = InterviewService(mock_session_repo)
        result = await service.get_session("session-abc")
        
        assert result.session_id == "session-abc"
    
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, mock_session_repo):
        """Should return None when session not found."""
        mock_session_repo.get_by_session_id.return_value = None
        
        service = InterviewService(mock_session_repo)
        result = await service.get_session("nonexistent")
        
        assert result is None


class TestInterviewServiceUpdateFeedback:
    """Tests for InterviewService.update_feedback."""
    
    @pytest.mark.asyncio
    async def test_updates_feedback_successfully(self, mock_session_repo):
        """Should update feedback and return True."""
        mock_session_repo.update_feedback.return_value = True
        
        service = InterviewService(mock_session_repo)
        result = await service.update_feedback(
            "session-abc",
            "Great job!",
            overall_score=90
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        mock_session_repo.update_feedback.assert_called_once_with(
            "session-abc", "Great job!", 90
        )
