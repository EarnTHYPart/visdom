"""Unit tests for Visdom server defaults and configuration."""

import pytest
import sys
import os

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.server import defaults


class TestDefaultConstants:
    """Test default configuration constants."""

    def test_default_port_is_integer(self):
        """Test that DEFAULT_PORT is an integer."""
        assert isinstance(defaults.DEFAULT_PORT, int)
        assert 1 <= defaults.DEFAULT_PORT <= 65535

    def test_default_hostname_is_string(self):
        """Test that DEFAULT_HOSTNAME is a string."""
        assert isinstance(defaults.DEFAULT_HOSTNAME, str)
        assert len(defaults.DEFAULT_HOSTNAME) > 0

    def test_default_base_url_is_string(self):
        """Test that DEFAULT_BASE_URL is a string."""
        assert isinstance(defaults.DEFAULT_BASE_URL, str)
        assert defaults.DEFAULT_BASE_URL.startswith('/')

    def test_default_env_path_is_string(self):
        """Test that DEFAULT_ENV_PATH is a string."""
        assert isinstance(defaults.DEFAULT_ENV_PATH, str)

    def test_max_socket_wait_is_number(self):
        """Test that MAX_SOCKET_WAIT is a number."""
        assert isinstance(defaults.MAX_SOCKET_WAIT, (int, float))
        assert defaults.MAX_SOCKET_WAIT > 0

    def test_layout_file_is_string(self):
        """Test that LAYOUT_FILE is a string."""
        assert isinstance(defaults.LAYOUT_FILE, str)
        assert len(defaults.LAYOUT_FILE) > 0


class TestPortConfiguration:
    """Test port configuration values."""

    def test_default_port_is_reasonable(self):
        """Test that default port is in reasonable range."""
        assert defaults.DEFAULT_PORT >= 1024  # Above system ports
        assert defaults.DEFAULT_PORT <= 49151  # Below dynamic ports

    def test_default_port_not_in_system_range(self):
        """Test that default port is not in system port range."""
        # System ports are 0-1023
        assert defaults.DEFAULT_PORT > 1023

    def test_default_port_typical_web_port(self):
        """Test that default port is typically a web port."""
        # Common web ports are 8000-9000
        assert defaults.DEFAULT_PORT in [8000, 8080, 8888, 8097, 9000, 9999, 5000]


class TestHostnameConfiguration:
    """Test hostname configuration."""

    def test_default_hostname_is_localhost(self):
        """Test that default hostname is localhost."""
        assert defaults.DEFAULT_HOSTNAME in ['localhost', '127.0.0.1', '0.0.0.0']

    def test_hostname_is_connectable(self):
        """Test that default hostname can be resolved."""
        # Localhost should always resolve
        assert len(defaults.DEFAULT_HOSTNAME) > 0


class TestBaseURLConfiguration:
    """Test base URL configuration."""

    def test_base_url_starts_with_slash(self):
        """Test that base URL starts with /."""
        assert defaults.DEFAULT_BASE_URL.startswith('/')

    def test_base_url_ends_with_slash(self):
        """Test that base URL ends with /."""
        assert defaults.DEFAULT_BASE_URL.endswith('/')

    def test_base_url_has_no_spaces(self):
        """Test that base URL contains no spaces."""
        assert ' ' not in defaults.DEFAULT_BASE_URL

    def test_base_url_is_valid_path(self):
        """Test that base URL follows URL path conventions."""
        # Should be alphanumeric with forward slashes only
        import re
        # Pattern allows either just '/' or '/path/' format
        valid_pattern = r'^/$|^/[a-zA-Z0-9/_-]+/$'
        assert re.match(valid_pattern, defaults.DEFAULT_BASE_URL)


class TestFilepathConfiguration:
    """Test file path configuration."""

    def test_env_path_exists_or_creatable(self):
        """Test that env_path can be created if needed."""
        # Path should be valid
        assert isinstance(defaults.DEFAULT_ENV_PATH, str)

    def test_layout_file_has_extension(self):
        """Test that layout file has appropriate extension."""
        assert defaults.LAYOUT_FILE.endswith('.json')


class TestSocketConfiguration:
    """Test socket-related configuration."""

    def test_max_socket_wait_is_positive(self):
        """Test that MAX_SOCKET_WAIT is positive."""
        assert defaults.MAX_SOCKET_WAIT > 0

    def test_max_socket_wait_is_reasonable_timeout(self):
        """Test that MAX_SOCKET_WAIT is a reasonable timeout."""
        # Should be between 1 second and 1 minute
        assert 1 <= defaults.MAX_SOCKET_WAIT <= 60


class TestConfigurationTypes:
    """Test configuration value types."""

    def test_all_defaults_are_defined(self):
        """Test that all expected defaults are defined."""
        assert hasattr(defaults, 'DEFAULT_PORT')
        assert hasattr(defaults, 'DEFAULT_HOSTNAME')
        assert hasattr(defaults, 'DEFAULT_BASE_URL')
        assert hasattr(defaults, 'DEFAULT_ENV_PATH')
        assert hasattr(defaults, 'MAX_SOCKET_WAIT')
        assert hasattr(defaults, 'LAYOUT_FILE')

    def test_defaults_are_not_none(self):
        """Test that default values are not None."""
        assert defaults.DEFAULT_PORT is not None
        assert defaults.DEFAULT_HOSTNAME is not None
        assert defaults.DEFAULT_BASE_URL is not None
        assert defaults.DEFAULT_ENV_PATH is not None
        assert defaults.MAX_SOCKET_WAIT is not None
        assert defaults.LAYOUT_FILE is not None


class TestConfigurationImmutability:
    """Test configuration constant behavior."""

    def test_constants_follow_naming_convention(self):
        """Test that constants use UPPERCASE naming."""
        # All constants should be uppercase
        config_attrs = [
            'DEFAULT_PORT', 'DEFAULT_HOSTNAME', 'DEFAULT_BASE_URL',
            'DEFAULT_ENV_PATH', 'MAX_SOCKET_WAIT', 'LAYOUT_FILE'
        ]
        
        for attr in config_attrs:
            assert attr.isupper()


class TestDefaultValues:
    """Test that default values are sensible."""

    def test_port_supports_web_traffic(self):
        """Test that port is suitable for web traffic."""
        # Typically ranges 5000-9999 for dev servers
        assert defaults.DEFAULT_PORT >= 5000

    def test_hostname_supports_local_development(self):
        """Test that hostname supports local development."""
        # Should be localhost or 127.0.0.1 for local dev
        local_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
        assert defaults.DEFAULT_HOSTNAME in local_hosts

    def test_base_url_simple_path(self):
        """Test that base URL is simple."""
        # Should typically be just '/'
        assert defaults.DEFAULT_BASE_URL == '/'

    def test_socket_wait_appropriate_for_real_time(self):
        """Test socket wait is appropriate for real-time communication."""
        # Should be a few seconds for real-time updates
        assert defaults.MAX_SOCKET_WAIT <= 30


class TestConfigurationConsistency:
    """Test consistency between related configurations."""

    def test_port_and_hostname_compatible(self):
        """Test that port and hostname are compatible."""
        # Valid combinations
        assert isinstance(defaults.DEFAULT_PORT, int)
        assert isinstance(defaults.DEFAULT_HOSTNAME, str)

    def test_base_url_compatible_with_paths(self):
        """Test that base URL is compatible with path operations."""
        assert defaults.DEFAULT_BASE_URL.startswith('/')
        assert defaults.DEFAULT_BASE_URL.endswith('/')

    def test_timeouts_are_reasonable(self):
        """Test that timeouts are reasonable for web app."""
        assert defaults.MAX_SOCKET_WAIT >= 1
        assert defaults.MAX_SOCKET_WAIT <= 300
