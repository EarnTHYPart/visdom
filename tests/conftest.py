"""
Pytest configuration and shared fixtures for Visdom tests.
Provides reusable test utilities and mocking helpers for cleaner, more maintainable tests.
"""

import pathlib
import sys
import pytest
from unittest.mock import Mock, MagicMock
import json

# Add py directory to path
ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_DIR = ROOT / "py"
if str(PY_DIR) not in sys.path:
    sys.path.insert(0, str(PY_DIR))


# ============================================================================
# TORNADO HANDLER FIXTURES - Simplify handler testing
# ============================================================================

@pytest.fixture
def mock_tornado_app():
    """Create a properly configured mock Tornado application with all required attributes."""
    app = MagicMock()
    app.state = {}
    app.layouts = {}
    app.user_settings = {}
    app.subs = {}
    app.sources = {}
    app.handlers = []
    app.settings = {'debug': False, 'template_path': '/static', 'static_path': '/static'}
    app.readonly = False
    app.wrap_socket = False
    return app


@pytest.fixture
def mock_tornado_request():
    """Create a properly configured mock Tornado request object."""
    request = MagicMock()
    request.headers = {}
    request.arguments = {}
    request.body = b''
    request.host = 'localhost:8097'
    request.uri = '/'
    request.method = 'GET'
    request.path = '/'
    request.query = ''
    request.full_url = 'http://localhost:8097/'
    request.connection = MagicMock()
    return request


@pytest.fixture
def mock_handler_context(mock_tornado_app, mock_tornado_request):
    """Provide both mock app and request for handlers."""
    return {'app': mock_tornado_app, 'request': mock_tornado_request}


# ============================================================================
# ENVIRONMENT & DATA FIXTURES - Test data for consistent testing
# ============================================================================

@pytest.fixture
def sample_environment():
    """Create a sample environment with windows and layouts."""
    return {
        'windows': {
            'win_1': {'type': 'text', 'content': 'Sample Text', 'title': 'Text Window'},
            'win_2': {'type': 'plot', 'data': {'x': [1, 2, 3], 'y': [1, 4, 9]}, 'title': 'Plot'},
        },
        'layouts': {
            'main': {'grid': [{'i': 'win_1', 'x': 0, 'y': 0}, {'i': 'win_2', 'x': 1, 'y': 0}]}
        },
    }


@pytest.fixture
def empty_environment():
    """Create an empty environment."""
    return {'windows': {}, 'layouts': {}}


@pytest.fixture
def large_environment():
    """Create a large environment with 100 windows for scaling tests."""
    windows = {}
    for i in range(100):
        windows[f'win_{i}'] = {
            'type': 'plot' if i % 2 == 0 else 'text',
            'data': {'x': list(range(100)), 'y': list(range(100))} if i % 2 == 0 else f'Content {i}',
            'title': f'Window {i}',
        }
    return {
        'windows': windows,
        'layouts': {'main': {'grid': [{'i': f'win_{i}', 'x': i % 3, 'y': i // 3} for i in range(100)]}},
    }


# ============================================================================
# WEBSOCKET & MESSAGE FIXTURES - Message testing convenience
# ============================================================================

@pytest.fixture
def sample_websocket_message():
    """Create a typical WebSocket message."""
    return {'cmd': 'update', 'win': 'win_1', 'data': {'content': 'Updated'}}


@pytest.fixture
def websocket_message_variants():
    """Provide various WebSocket message types for comprehensive testing."""
    return {
        'close_window': {'cmd': 'close', 'win': 'win_1'},
        'save_env': {'cmd': 'save', 'eid': 'main'},
        'update_layout': {'cmd': 'layout', 'layout': {'grid': []}},
        'invalid_command': {'cmd': 'unknown', 'data': {}},
        'missing_fields': {'cmd': 'close'},  # Missing 'win' field
    }


# ============================================================================
# CREDENTIALS FIXTURES - Security testing
# ============================================================================

@pytest.fixture
def sample_credentials():
    """Create sample credentials for testing authentication."""
    return {'username': 'testuser', 'password': 'test_password_123'}


@pytest.fixture
def sample_secure_cookie():
    """Create a sample secure cookie value."""
    return b'test_user_session_token'


# ============================================================================
# ASSERTION HELPERS - Common validation functions
# ============================================================================

def assert_valid_environment(env):
    """Validate environment structure."""
    assert isinstance(env, dict), "Environment must be a dict"
    assert 'windows' in env, "Environment must have 'windows' key"
    assert isinstance(env['windows'], dict), "Windows must be a dict"


def assert_valid_window(window):
    """Validate window structure."""
    assert isinstance(window, dict), "Window must be a dict"
    assert 'type' in window, "Window must have 'type'"


def assert_json_serializable(obj):
    """Assert object can be JSON serialized."""
    try:
        json.dumps(obj)
    except (TypeError, ValueError) as e:
        raise AssertionError(f"Object not JSON serializable: {e}")


def assert_environment_unchanged(env_before, env_after):
    """Assert that two environments are identical."""
    assert env_before == env_after, "Environment was modified unexpectedly"


def assert_window_exists(env, window_id):
    """Assert that a window exists in environment."""
    assert window_id in env['windows'], f"Window '{window_id}' not found in environment"


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers for test categorization."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "edge_case: marks tests that cover edge cases")
    config.addinivalue_line("markers", "handler: marks tests for request handlers")
    config.addinivalue_line("markers", "network: marks tests that involve network operations")
