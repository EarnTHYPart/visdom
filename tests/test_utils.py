"""
Test utilities and helpers for Visdom tests.

This module provides common testing patterns, mock factories, and assertion helpers
to make tests cleaner, more readable, and easier to maintain.
"""

import json
import tempfile
import os
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from pathlib import Path


# ============================================================================
# ENVIRONMENT BUILDERS - Create test data easily
# ============================================================================

class EnvironmentBuilder:
    """Builder class for creating environments with a fluent API."""

    def __init__(self):
        """Initialize with empty environment."""
        self.env = {'windows': {}, 'layouts': {}}

    def add_window(self, window_id, window_type='text', **props):
        """Add a window to the environment."""
        self.env['windows'][window_id] = {
            'type': window_type,
            **props
        }
        return self

    def add_text_window(self, window_id, content, title=''):
        """Add a text window."""
        return self.add_window(window_id, 'text', content=content, title=title)

    def add_plot_window(self, window_id, data, title=''):
        """Add a plot window."""
        return self.add_window(window_id, 'plot', data=data, title=title)

    def add_image_window(self, window_id, src, title=''):
        """Add an image window."""
        return self.add_window(window_id, 'image', src=src, title=title)

    def add_layout(self, layout_id, grid=None):
        """Add a layout."""
        self.env['layouts'][layout_id] = {'grid': grid or []}
        return self

    def build(self):
        """Return the built environment."""
        return self.env


# ============================================================================
# MESSAGE BUILDERS - Create WebSocket messages easily
# ============================================================================

class WebSocketMessageBuilder:
    """Builder for creating WebSocket messages."""

    def __init__(self, cmd):
        """Initialize with command type."""
        self.message = {'cmd': cmd}

    @staticmethod
    def close_window(window_id):
        """Create a close window message."""
        return {'cmd': 'close', 'win': window_id}

    @staticmethod
    def save_environment(env_id):
        """Create a save environment message."""
        return {'cmd': 'save', 'eid': env_id}

    @staticmethod
    def update_window(window_id, data):
        """Create an update window message."""
        return {'cmd': 'update', 'win': window_id, 'data': data}

    @staticmethod
    def update_layout(layout):
        """Create an update layout message."""
        return {'cmd': 'layout', 'layout': layout}

    def with_field(self, key, value):
        """Add a field to the message."""
        self.message[key] = value
        return self

    def build(self):
        """Return the built message."""
        return self.message


# ============================================================================
# TEMPORARY FILE HELPERS - Manage test files easily
# ============================================================================

@contextmanager
def temp_env_file(env_data=None):
    """
    Create a temporary environment file for testing.
    
    Context manager that creates a JSON file with environment data,
    yields the file path, and cleans up afterwards.
    
    Args:
        env_data: Dictionary to save as JSON (optional)
    
    Yields:
        Path to temporary environment file
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        if env_data:
            json.dump(env_data, f)
        filepath = f.name
    
    try:
        yield filepath
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


@contextmanager
def temp_env_directory(env_files=None):
    """
    Create a temporary directory with environment files.
    
    Context manager that creates a temporary directory, optionally
    populated with environment JSON files, and cleans up afterwards.
    
    Args:
        env_files: Dict of {filename: env_data} to create (optional)
    
    Yields:
        Path to temporary directory
    """
    tmpdir = tempfile.mkdtemp()
    
    try:
        if env_files:
            for filename, env_data in env_files.items():
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'w') as f:
                    json.dump(env_data, f)
        yield tmpdir
    finally:
        # Clean up directory and all files
        import shutil
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


# ============================================================================
# MOCK FACTORIES - Create realistic mocks
# ============================================================================

def create_mock_handler(handler_class=None, **custom_attrs):
    """
    Create a mock handler with common attributes.
    
    Args:
        handler_class: Optional handler class to base mock on
        **custom_attrs: Custom attributes to add
    
    Returns:
        MagicMock: Configured handler mock
    """
    handler = MagicMock()
    handler.application = MagicMock()
    handler.request = MagicMock()
    handler.set_header = MagicMock()
    handler.write = MagicMock()
    handler.get_secure_cookie = MagicMock(return_value=None)
    handler.set_secure_cookie = MagicMock()
    handler.finish = MagicMock()
    
    for key, value in custom_attrs.items():
        setattr(handler, key, value)
    
    return handler


def create_mock_request(method='GET', arguments=None, headers=None, body=b''):
    """
    Create a mock Tornado request.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        arguments: URL arguments dict
        headers: Request headers dict
        body: Request body bytes
    
    Returns:
        MagicMock: Configured request mock
    """
    request = MagicMock()
    request.method = method
    request.arguments = arguments or {}
    request.headers = headers or {}
    request.body = body
    request.host = 'localhost:8097'
    request.uri = '/'
    request.full_url = 'http://localhost:8097/'
    return request


def create_mock_app(state=None, layouts=None, **custom_attrs):
    """
    Create a mock Tornado application.
    
    Args:
        state: Initial state dict (optional)
        layouts: Initial layouts dict (optional)
        **custom_attrs: Custom attributes to add
    
    Returns:
        MagicMock: Configured app mock
    """
    app = MagicMock()
    app.state = state or {}
    app.layouts = layouts or {}
    app.user_settings = {}
    app.subs = {}
    app.sources = {}
    app.settings = {'debug': False}
    
    for key, value in custom_attrs.items():
        setattr(app, key, value)
    
    return app


# ============================================================================
# ASSERTION HELPERS - Common test validations
# ============================================================================

class EnvironmentValidator:
    """Validate environment structure and content."""

    @staticmethod
    def has_window(env, window_id):
        """Check if environment has a window."""
        assert window_id in env['windows'], f"Window '{window_id}' not found"
        return True

    @staticmethod
    def window_has_property(env, window_id, prop):
        """Check if window has a property."""
        assert EnvironmentValidator.has_window(env, window_id)
        window = env['windows'][window_id]
        assert prop in window, f"Window '{window_id}' missing property '{prop}'"
        return True

    @staticmethod
    def is_valid_structure(env):
        """Check if environment has valid structure."""
        assert isinstance(env, dict)
        assert 'windows' in env and isinstance(env['windows'], dict)
        return True

    @staticmethod
    def window_count(env):
        """Get number of windows in environment."""
        return len(env['windows'])

    @staticmethod
    def has_layout(env, layout_id):
        """Check if environment has a layout."""
        assert layout_id in env.get('layouts', {}), f"Layout '{layout_id}' not found"
        return True


# ============================================================================
# TEST DATA GENERATORS - Create various test scenarios
# ============================================================================

class TestDataGenerator:
    """Generate realistic test data."""

    @staticmethod
    def unicode_strings():
        """Generate strings with various unicode characters."""
        return [
            'Hello World',
            '你好世界',
            'مرحبا بالعالم',
            'Привет мир',
            '🚀 Rocket Launch 🎉',
            'Café ☕',
        ]

    @staticmethod
    def special_characters():
        """Generate strings with special characters."""
        return [
            'test!@#$%^&*()',
            'path/with/slashes',
            'data\\with\\backslashes',
            'quote"inside"quotes',
            "single'quotes",
            'newline\ncharacter',
            'tab\tcharacter',
        ]

    @staticmethod
    def large_strings(size=1024):
        """Generate large strings for testing."""
        return 'x' * size

    @staticmethod
    def edge_case_numbers():
        """Generate edge case numeric values."""
        return [0, 1, -1, 9999999, -9999999, 0.0, 1e-10, float('inf')]

    @staticmethod
    def sample_plot_data(points=10):
        """Generate sample plot data."""
        return {
            'x': list(range(points)),
            'y': [i**2 for i in range(points)],
            'type': 'scatter',
            'name': 'Sample Data',
        }


# ============================================================================
# COMPARISON HELPERS - Assert data changes
# ============================================================================

def assert_data_changed(before, after, path):
    """
    Assert that data changed at a specific path.
    
    Args:
        before: Data before change
        after: Data after change
        path: Dot-separated path to property (e.g., 'windows.win_1.content')
    """
    before_val = _get_nested_value(before, path)
    after_val = _get_nested_value(after, path)
    assert before_val != after_val, f"Expected change at '{path}', but value unchanged"


def assert_data_unchanged(before, after, path):
    """
    Assert that data did NOT change at a specific path.
    
    Args:
        before: Data before change
        after: Data after change
        path: Dot-separated path to property
    """
    before_val = _get_nested_value(before, path)
    after_val = _get_nested_value(after, path)
    assert before_val == after_val, f"Expected no change at '{path}', but value changed"


def _get_nested_value(obj, path):
    """Get nested value using dot notation."""
    keys = path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value[key]
        else:
            value = getattr(value, key)
    return value


# ============================================================================
# CONTEXT MANAGERS - Simplified test setup/teardown
# ============================================================================

@contextmanager
def mock_urlopen(response_data=None, status_code=200):
    """
    Context manager for mocking urlopen with a response.
    
    Args:
        response_data: Data to return from urlopen (default: empty bytes)
        status_code: HTTP status code (default: 200)
    
    Yields:
        Mock urlopen function
    """
    response = MagicMock()
    response.read.return_value = response_data or b''
    response.code = status_code
    response.msg = 'OK' if status_code == 200 else 'Error'
    
    with patch('urllib.request.urlopen', return_value=response) as mock:
        yield mock


@contextmanager
def isolated_environment(env_data=None):
    """
    Context manager for isolated environment testing.
    
    Creates a temporary directory with environment files and yields it.
    
    Args:
        env_data: Dict of environment data to create
    
    Yields:
        Path to temporary environment directory
    """
    with temp_env_directory({'main.json': env_data or {'windows': {}}}) as tmpdir:
        yield tmpdir
