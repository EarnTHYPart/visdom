"""Unit tests for the Visdom Application main module."""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.server.app import Application


class TestApplicationInitialization:
    """Test Application class initialization and setup."""

    def test_application_init_creates_tornado_app(self):
        """Test that Application creates a valid Tornado application."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            assert app is not None
            assert hasattr(app, 'handlers')

    def test_application_with_custom_base_url(self):
        """Test Application initialization with custom base URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=9000,
                base_url='/visdom/',
                env_path=tmpdir,
            )
            assert app.base_url == '/visdom/'

    def test_application_env_path_set(self):
        """Test that Application stores env_path correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, 'new_env_path')
            
            app = Application(
                port=8097,
                base_url='/',
                env_path=env_path,
            )
            assert app.env_path == env_path


class TestApplicationHandlers:
    """Test Application handler registration."""

    def test_handlers_are_registered(self):
        """Test that application handlers are properly registered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                hostname='localhost',
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            handlers = app.application.handlers
            # Should have handlers registered
            assert len(handlers) > 0

    def test_handler_patterns_are_valid(self):
        """Test that registered handler patterns are valid regex."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                hostname='localhost',
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            # All handler tuples should be (pattern, handler) pairs
            for route_spec in app.application.handlers[0]:
                if hasattr(route_spec, '__iter__') and not isinstance(route_spec, str):
                    # Should be a tuple with pattern and handler
                    assert len(route_spec) >= 2


class TestApplicationStateManagement:
    """Test Application state management."""

    def test_application_state_structure(self):
        """Test that application maintains proper state structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            # Should have state dictionary
            assert hasattr(app, 'state')
            assert isinstance(app.state, dict)


class TestApplicationPortConfiguration:
    """Test Application port configuration."""

    def test_valid_port_numbers(self):
        """Test Application with various valid port numbers."""
        valid_ports = [8080, 8097, 5000, 9000]
        for port in valid_ports:
            with tempfile.TemporaryDirectory() as tmpdir:
                app = Application(
                    port=port,
                    base_url='/',
                    env_path=tmpdir,
                )
                assert app.port == port

    def test_port_configuration_works(self):
        """Test that port configuration works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8888,
                base_url='/',
                env_path=tmpdir,
            )
            assert app.port == 8888


class TestApplicationSettings:
    """Test Application configuration settings."""

    def test_readonly_mode(self):
        """Test Application readonly mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
                readonly=True,
            )
            assert app.readonly is True

    def test_polling_mode(self):
        """Test Application frontend polling mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
                use_frontend_client_polling=True,
            )
            assert app.wrap_socket is True

    def test_eager_loading(self):
        """Test Application eager data loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
                eager_data_loading=True,
            )
            assert app.eager_data_loading is True
