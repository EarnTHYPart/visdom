"""Unit tests for Visdom build and asset management."""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

from visdom.server.build import download_scripts


def _setup_network_mocks(mock_build_opener, mock_requests_get, body=b"// asset"):
    opener = MagicMock()
    opener.open.return_value.read.return_value = body
    mock_build_opener.return_value = opener
    mock_requests_get.return_value = MagicMock(content=b"// mathjax")
    return opener


class TestAssetDownloadBasics:
    """Test basic asset download functionality."""

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_scripts_basic(self, mock_build_opener, mock_requests_get):
        """Test basic script download operation."""
        opener = _setup_network_mocks(mock_build_opener, mock_requests_get)

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)

            assert opener.open.called

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_scripts_creates_directory(self, mock_build_opener, mock_requests_get):
        """Test that download_scripts creates expected static directories."""
        _setup_network_mocks(mock_build_opener, mock_requests_get)

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)

            assert os.path.isdir(os.path.join(tmpdir, "static", "js"))
            assert os.path.isdir(os.path.join(tmpdir, "static", "css"))
            assert os.path.isdir(os.path.join(tmpdir, "static", "fonts"))


class TestAssetDownloadErrors:
    """Test error handling in asset downloads."""

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_with_network_error(self, mock_build_opener, mock_requests_get):
        """URLError from opener should be handled without raising."""
        from urllib.error import URLError

        opener = MagicMock()
        opener.open.side_effect = URLError("Network error")
        mock_build_opener.return_value = opener
        mock_requests_get.return_value = MagicMock(content=b"// mathjax")

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_with_http_error(self, mock_build_opener, mock_requests_get):
        """HTTP errors should be handled without raising."""
        from urllib.error import HTTPError

        opener = MagicMock()
        opener.open.side_effect = HTTPError("url", 404, "Not Found", {}, None)
        mock_build_opener.return_value = opener
        mock_requests_get.return_value = MagicMock(content=b"// mathjax")

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)


class TestAssetOutput:
    """Test output artifacts and options."""

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_writes_version_file(self, mock_build_opener, mock_requests_get):
        """Version marker should be written after successful build."""
        _setup_network_mocks(mock_build_opener, mock_requests_get)

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)

            version_file = os.path.join(tmpdir, "static", "version.built")
            assert os.path.isfile(version_file)

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_binary_files(self, mock_build_opener, mock_requests_get):
        """Binary payloads should be written without conversion errors."""
        _setup_network_mocks(
            mock_build_opener,
            mock_requests_get,
            body=bytes(range(64)) * 4,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(install_dir=tmpdir)


class TestAssetProxyConfig:
    """Test proxy handling behavior."""

    @patch("requests.get")
    @patch("urllib.request.build_opener")
    def test_download_accepts_proxy_mapping(self, mock_build_opener, mock_requests_get):
        """Passing a proxy mapping should still build an opener and proceed."""
        _setup_network_mocks(mock_build_opener, mock_requests_get)

        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(
                proxies={"http": "http://127.0.0.1:3128"},
                install_dir=tmpdir,
            )

            assert mock_build_opener.called
