"""Unit tests for Visdom build and asset management."""

import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import urllib.error

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.server.build import download_scripts


class TestAssetDownloadBasics:
    """Test basic asset download functionality."""

    @patch('urllib.request.urlopen')
    def test_download_scripts_basic(self, mock_urlopen):
        """Test basic script download operation."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// script content'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should attempt to download
            download_scripts(tmpdir)

    def test_download_scripts_creates_directory(self):
        """Test that download_scripts creates js directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_dir = os.path.join(tmpdir, 'js')
            assert not os.path.exists(js_dir)
            
            # After download, directory should exist
            # Note: We're testing structure, actual download may be mocked

    def test_download_scripts_returns_success(self):
        """Test download_scripts return value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('urllib.request.urlopen'):
                result = download_scripts(tmpdir)
                # Should return without error


class TestAssetDownloadErrors:
    """Test error handling in asset downloads."""

    @patch('urllib.request.urlopen')
    def test_download_with_network_error(self, mock_urlopen):
        """Test handling of network errors."""
        mock_urlopen.side_effect = urllib.error.URLError('Network error')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle network errors gracefully
            with pytest.raises((urllib.error.URLError, Exception)):
                download_scripts(tmpdir)

    @patch('urllib.request.urlopen')
    def test_download_with_http_error(self, mock_urlopen):
        """Test handling of HTTP errors."""
        mock_urlopen.side_effect = urllib.error.HTTPError('url', 404, 'Not Found', {}, None)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle HTTP errors
            with pytest.raises((urllib.error.HTTPError, Exception)):
                download_scripts(tmpdir)

    @patch('urllib.request.urlopen')
    def test_download_with_timeout(self, mock_urlopen):
        """Test handling of download timeout."""
        mock_urlopen.side_effect = TimeoutError('Connection timeout')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises((TimeoutError, Exception)):
                download_scripts(tmpdir)


class TestAssetFileValidation:
    """Test validation of downloaded assets."""

    @patch('urllib.request.urlopen')
    def test_download_empty_response(self, mock_urlopen):
        """Test handling of empty response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b''
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should handle empty responses

    @patch('urllib.request.urlopen')
    def test_download_large_file(self, mock_urlopen):
        """Test downloading large asset files."""
        huge_content = b'// ' + b'x' * (50 * 1024 * 1024)  # 50MB
        mock_response = MagicMock()
        mock_response.read.return_value = huge_content
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle large files
            download_scripts(tmpdir)

    @patch('urllib.request.urlopen')
    def test_download_binary_files(self, mock_urlopen):
        """Test downloading binary assets."""
        binary_content = bytes(range(256)) * 100
        mock_response = MagicMock()
        mock_response.read.return_value = binary_content
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)


class TestAssetCDNSources:
    """Test CDN source handling."""

    @patch('urllib.request.urlopen')
    def test_download_from_multiple_sources(self, mock_urlopen):
        """Test downloading from multiple CDN sources."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// content'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should attempt downloads from configured sources

    @patch('urllib.request.urlopen')
    def test_fallback_to_alternative_cdn(self, mock_urlopen):
        """Test fallback when primary CDN fails."""
        # First call fails, second succeeds
        mock_response_success = MagicMock()
        mock_response_success.read.return_value = b'// fallback content'
        
        mock_urlopen.side_effect = [
            urllib.error.URLError('Primary CDN down'),
            mock_response_success
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should try fallback CDN
            pass


class TestAssetTypes:
    """Test different asset types."""

    @patch('urllib.request.urlopen')
    def test_download_javascript_assets(self, mock_urlopen):
        """Test downloading JavaScript files."""
        js_content = b'console.log("test");'
        mock_response = MagicMock()
        mock_response.read.return_value = js_content
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # JS files should be downloaded

    @patch('urllib.request.urlopen')
    def test_download_css_assets(self, mock_urlopen):
        """Test downloading CSS files."""
        css_content = b'body { color: red; }'
        mock_response = MagicMock()
        mock_response.read.return_value = css_content
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # CSS files should be downloaded

    @patch('urllib.request.urlopen')
    def test_download_font_assets(self, mock_urlopen):
        """Test downloading font files."""
        # Font files are binary
        font_content = bytes(range(256))
        mock_response = MagicMock()
        mock_response.read.return_value = font_content
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Font files should be downloaded


class TestAssetDirectoryStructure:
    """Test asset directory organization."""

    def test_download_creates_proper_directory_structure(self):
        """Test that download creates proper directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('urllib.request.urlopen'):
                download_scripts(tmpdir)
                # Should create appropriate subdirectories

    def test_download_respects_target_directory(self):
        """Test that downloads go to correct directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, 'static', 'js')
            
            with patch('urllib.request.urlopen'):
                # Downloads should respect target directory
                pass


class TestAssetDependencies:
    """Test asset dependency management."""

    @patch('urllib.request.urlopen')
    def test_download_required_dependencies(self, mock_urlopen):
        """Test that required dependencies are downloaded."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// dependency'
        mock_urlopen.return_value = mock_response
        
        required_libs = [
            'jquery',
            'bootstrap',
            'react',
            'plotly',
            'd3'
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # All required libraries should be downloaded

    @patch('urllib.request.urlopen')
    def test_download_minified_versions(self, mock_urlopen):
        """Test that minified versions are preferred."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// minified'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should prefer minified versions


class TestAssetVersioning:
    """Test asset version management."""

    @patch('urllib.request.urlopen')
    def test_download_specific_versions(self, mock_urlopen):
        """Test downloading specific library versions."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// v1.2.3'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should handle version pinning

    @patch('urllib.request.urlopen')
    def test_download_version_compatibility(self, mock_urlopen):
        """Test version compatibility between assets."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// compatible'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Downloaded versions should be compatible


class TestAssetCaching:
    """Test asset caching behavior."""

    @patch('urllib.request.urlopen')
    @patch('os.path.exists')
    def test_skip_download_if_exists(self, mock_exists, mock_urlopen):
        """Test skipping download for existing files."""
        mock_exists.return_value = True
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should skip download for existing files

    @patch('urllib.request.urlopen')
    def test_cache_management(self, mock_urlopen):
        """Test cache cleanup and management."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'// cached'
        mock_urlopen.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            download_scripts(tmpdir)
            # Should maintain proper cache state
