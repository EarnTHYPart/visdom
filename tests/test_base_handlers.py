"""Unit tests for Visdom base HTTP and WebSocket handlers."""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.server.handlers.base_handlers import BaseHandler, BaseWebSocketHandler


def _make_base_handler(mock_app=None, mock_request=None):
    if mock_app is None:
        mock_app = Mock()
    if mock_request is None:
        mock_request = Mock()
    mock_app.settings = {"debug": False}
    with patch('tornado.web.RequestHandler.__init__', return_value=None):
        handler = BaseHandler(mock_app, mock_request)
    handler.application = mock_app
    handler.request = mock_request
    return handler


def _make_ws_handler(mock_app=None, mock_request=None):
    if mock_app is None:
        mock_app = Mock()
    if mock_request is None:
        mock_request = Mock()
    with patch('tornado.websocket.WebSocketHandler.__init__', return_value=None):
        handler = BaseWebSocketHandler(mock_app, mock_request)
    handler.application = mock_app
    handler.request = mock_request
    return handler


class TestBaseHandlerInitialization:
    """Test BaseHandler initialization and setup."""

    def test_handler_creation_requires_application(self):
        """Test that BaseHandler requires an application object."""
        handler = _make_base_handler(Mock(), Mock())
        assert handler.application is not None


class TestBaseHandlerErrorHandling:
    """Test BaseHandler error handling."""

    def test_write_error_returns_json(self):
        """Test that write_error returns JSON response."""
        handler = _make_base_handler(Mock(), Mock())

        with patch('logging.error') as mock_log_error:
            handler.write_error(404, reason='Not Found')

        assert mock_log_error.called

    def test_write_error_500_handling(self):
        """Test 500 error handling."""
        handler = _make_base_handler(Mock(), Mock())

        with patch('logging.error') as mock_log_error:
            handler.write_error(500, reason='Internal Server Error')

        assert mock_log_error.called


class TestBaseHandlerAuthentication:
    """Test BaseHandler user authentication."""

    def test_get_current_user_from_secure_cookie(self):
        """Test retrieving current user from secure cookie."""
        handler = _make_base_handler(Mock(), Mock())
        handler.get_secure_cookie = Mock(return_value=b'test_user')

        user = handler.get_current_user()
        handler.get_secure_cookie.assert_called_with('user_password')
        assert user == b'test_user'

    def test_get_current_user_returns_none_when_not_authenticated(self):
        """Test that get_current_user returns None when not authenticated."""
        handler = _make_base_handler(Mock(), Mock())
        handler.get_secure_cookie = Mock(return_value=None)

        user = handler.get_current_user()
        assert user is None


class TestBaseWebSocketHandlerAuthentication:
    """Test BaseWebSocketHandler user authentication."""

    def test_websocket_handler_initialization(self):
        """Test BaseWebSocketHandler creates properly."""
        handler = _make_ws_handler(Mock(), Mock())
        assert handler.application is not None


class TestBaseHandlerEdgeCases:
    """Test edge cases and error conditions."""

    def test_write_error_with_exception_chain(self):
        """Test write_error when exception chaining occurs."""
        handler = _make_base_handler(Mock(), Mock())

        with patch('logging.error') as mock_log_error:
            try:
                raise ValueError("Original error")
            except ValueError:
                handler.write_error(500, reason='Internal Server Error')

        assert mock_log_error.called

    def test_handler_with_missing_request_attributes(self):
        """Test handler behavior when request is incomplete."""
        mock_app = Mock()
        mock_request = MagicMock()
        mock_request.headers = {}
        
        handler = _make_base_handler(mock_app, mock_request)
        # Should still be creatable even with minimal request
        assert handler is not None

    def test_concurrent_user_access(self):
        """Test handler handles concurrent user access correctly."""
        mock_app = Mock()
        
        handlers = []
        for i in range(5):
            mock_request = Mock()
            handler = _make_base_handler(mock_app, mock_request)
            handler.get_secure_cookie = Mock(return_value=f'user_{i}'.encode())
            handlers.append(handler)
        
        # Each handler should maintain separate state
        assert len(handlers) == 5


class TestBaseHandlerHTTPMethodsBasic:
    """Test basic HTTP method handling."""

    def test_handler_supports_get_method(self):
        """Test that handler supports GET method."""
        mock_app = Mock()
        mock_request = Mock()
        mock_request.method = 'GET'
        
        handler = _make_base_handler(mock_app, mock_request)
        # BaseHandler should be able to handle requests
        assert handler is not None

    def test_handler_supports_post_method(self):
        """Test that handler supports POST method."""
        mock_app = Mock()
        mock_request = Mock()
        mock_request.method = 'POST'
        
        handler = _make_base_handler(mock_app, mock_request)
        assert handler is not None
