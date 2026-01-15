import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import json

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.core.intelligence.shadow_monitor import ShadowMonitor

# Mock Response Object
class MockGeminiResponse:
    def __init__(self, text_content):
        self.text = text_content

@pytest.fixture
def mock_settings():
    # app.services.core/intelligence/shadow_monitor.py uses 'config.settings.get_settings'
    # Wait, the import in shadow_monitor.py is: from config.settings import get_settings
    # So we should patch where it is IMPORTED
    with patch("app.services.core.intelligence.shadow_monitor.get_settings") as mock:
        mock.return_value.SHADOW_MODEL = "models/gemini-mock"
        yield mock

@pytest.fixture
def shadow_monitor(mock_settings):
    # Mock OS environ to pass API Key check
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"}):
        # Mock genai.Client
        with patch("google.genai.Client") as mock_client_cls:
            monitor = ShadowMonitor()
            
            # Setup AsyncMock for aio.models.generate_content
            mock_client_instance = mock_client_cls.return_value
            mock_client_instance.aio.models.generate_content = AsyncMock()
            
            # Since ShadowMonitor stores self.client, we can verify calls on the mock instance
            yield monitor

@pytest.mark.asyncio
async def test_analyze_stuck_candidate(shadow_monitor):
    # Arrange
    history = [
        {"role": "assistant", "content": "Question 1"},
        {"role": "user", "content": "Answer 1"},
        {"role": "assistant", "content": "Hard Question"},
        {"role": "user", "content": "I don't know..."}
    ]
    
    expected_response = {
        "status": "stuck",
        "intervention": "Give a hint."
    }
    
    shadow_monitor.client.aio.models.generate_content.return_value = MockGeminiResponse(
        json.dumps(expected_response)
    )

    # Act
    intervention = await shadow_monitor.analyze(history, "Dev", "tech")

    # Assert
    assert intervention == "Give a hint."
    shadow_monitor.client.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_good_flow(shadow_monitor):
    # Arrange
    history = [
        {"role": "assistant", "content": "Q"},
        {"role": "user", "content": "Perfect Answer"}
    ] * 2
    
    expected_response = {
        "status": "flowing",
        "intervention": "null" # or actually None in JSON usually implies key missing or explicit null
    }
    # JSON 'null' parses to Python None
    
    shadow_monitor.client.aio.models.generate_content.return_value = MockGeminiResponse(
        json.dumps({"status": "flowing", "intervention": None})
    )

    # Act
    intervention = await shadow_monitor.analyze(history, "Dev", "tech")

    # Assert
    assert intervention is None

@pytest.mark.asyncio
async def test_short_context_ignored(shadow_monitor):
    # Arrange
    history = [{"role": "user", "content": "Hi"}] # Only 1 message

    # Act
    intervention = await shadow_monitor.analyze(history, "Dev", "tech")

    # Assert
    assert intervention is None
    shadow_monitor.client.aio.models.generate_content.assert_not_called()

@pytest.mark.asyncio
async def test_api_error_handling(shadow_monitor):
    # Arrange
    history = [{"role": "user", "content": "..."}] * 3
    
    # Simulate Exception
    shadow_monitor.client.aio.models.generate_content.side_effect = Exception("API Down")

    # Act
    intervention = await shadow_monitor.analyze(history, "Dev", "tech")

    # Assert
    assert intervention is None
