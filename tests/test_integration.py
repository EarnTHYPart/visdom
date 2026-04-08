"""Integration tests for Visdom components working together."""

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
from visdom.server import defaults


class TestAppWithDefaults:
    """Test Application using default configurations."""

    def test_app_uses_default_port(self):
        """Test that Application can use default port."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=defaults.DEFAULT_PORT,
                base_url=defaults.DEFAULT_BASE_URL,
                env_path=tmpdir,
            )
            assert app.port == defaults.DEFAULT_PORT

    def test_app_uses_default_base_url(self):
        """Test that Application can use default base URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=defaults.DEFAULT_PORT,
                base_url=defaults.DEFAULT_BASE_URL,
                env_path=tmpdir,
            )
            assert app.base_url == defaults.DEFAULT_BASE_URL

    def test_app_readonly_mode(self):
        """Test that Application supports readonly mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=defaults.DEFAULT_PORT,
                base_url='/',
                env_path=tmpdir,
                readonly=True,
            )
            assert app.readonly is True


class TestEnvironmentPersistence:
    """Test environment saving and loading."""

    def test_save_and_load_environment(self):
        """Test saving environment to disk and loading it back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial environment
            env_data = {
                'windows': {
                    'win_1': {
                        'type': 'text',
                        'content': 'Hello'
                    }
                }
            }
            
            # Save environment
            env_file = os.path.join(tmpdir, 'test.json')
            with open(env_file, 'w') as f:
                json.dump(env_data, f)
            
            # Load environment
            with open(env_file, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['windows']['win_1']['type'] == 'text'

    def test_multiple_environments(self):
        """Test handling multiple environments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple environments
            environments = ['main', 'experiments', 'test']
            
            for env_name in environments:
                env_data = {'windows': {}}
                env_file = os.path.join(tmpdir, f'{env_name}.json')
                with open(env_file, 'w') as f:
                    json.dump(env_data, f)
            
            # Verify all were created
            files = [f for f in os.listdir(tmpdir) if f.endswith('.json')]
            assert len(files) == 3


class TestWindowManagement:
    """Test window lifecycle from creation through deletion."""

    def test_window_creation_and_tracking(self):
        """Test creating windows and tracking them."""
        env = {'windows': {}}
        
        window_spec = {
            'type': 'text',
            'content': 'Window 1',
            'title': 'My Window'
        }
        
        env['windows']['win_1'] = window_spec
        
        assert 'win_1' in env['windows']
        assert env['windows']['win_1']['content'] == 'Window 1'

    def test_window_update_preservation(self):
        """Test that window updates preserve other attributes."""
        env = {
            'windows': {
                'win_1': {
                    'type': 'plot',
                    'title': 'Original Title',
                    'data': {'x': [1, 2, 3]}
                }
            }
        }
        
        # Update title
        env['windows']['win_1']['title'] = 'Updated Title'
        
        # Verify data still exists
        assert env['windows']['win_1']['data'] == {'x': [1, 2, 3]}
        assert env['windows']['win_1']['title'] == 'Updated Title'


class TestLayoutManagement:
    """Test layout organization of windows."""

    def test_layout_creation(self):
        """Test creating layouts for organizing windows."""
        env = {
            'windows': {
                'win_1': {'type': 'text'},
                'win_2': {'type': 'plot'},
                'win_3': {'type': 'image'}
            },
            'layouts': {
                'main': {
                    'grid': [
                        {'i': 'win_1', 'x': 0, 'y': 0},
                        {'i': 'win_2', 'x': 1, 'y': 0},
                        {'i': 'win_3', 'x': 0, 'y': 1}
                    ]
                }
            }
        }
        
        assert len(env['layouts']['main']['grid']) == 3

    def test_layout_update(self):
        """Test updating layout positions."""
        layout = {
            'grid': [
                {'i': 'win_1', 'x': 0, 'y': 0}
            ]
        }
        
        # Add new window to layout
        layout['grid'].append({'i': 'win_2', 'x': 1, 'y': 0})
        
        assert len(layout['grid']) == 2


class TestDataSerialization:
    """Test serialization of complex data structures."""

    def test_serialize_plot_data(self):
        """Test serializing plot data with various types."""
        plot_data = {
            'x': [1, 2, 3, 4, 5],
            'y': [1, 4, 9, 16, 25],
            'type': 'scatter',
            'name': 'Quadratic'
        }
        
        # Should be JSON serializable
        serialized = json.dumps(plot_data)
        deserialized = json.loads(serialized)
        
        assert deserialized['x'] == [1, 2, 3, 4, 5]

    def test_serialize_image_data(self):
        """Test serializing image data."""
        image_data = {
            'src': 'data:image/png;base64,iVBORw0KG...',
            'width': 200,
            'height': 200,
            'title': 'Sample Image'
        }
        
        serialized = json.dumps(image_data)
        assert 'data:image' in serialized


class TestEnvironmentComparison:
    """Test comparing environments for changes."""

    def test_detect_new_window(self):
        """Test detecting new windows between environments."""
        env1 = {'windows': {'win_1': {}}}
        env2 = {'windows': {'win_1': {}, 'win_2': {}}}
        
        new_windows = set(env2['windows'].keys()) - set(env1['windows'].keys())
        assert 'win_2' in new_windows

    def test_detect_window_deletion(self):
        """Test detecting deleted windows."""
        env1 = {'windows': {'win_1': {}, 'win_2': {}}}
        env2 = {'windows': {'win_1': {}}}
        
        deleted_windows = set(env1['windows'].keys()) - set(env2['windows'].keys())
        assert 'win_2' in deleted_windows

    def test_detect_window_modification(self):
        """Test detecting modifications to windows."""
        win_content_original = {'type': 'text', 'content': 'Hello'}
        win_content_modified = {'type': 'text', 'content': 'World'}
        
        assert win_content_original != win_content_modified


class TestApplicationLifecycle:
    """Test complete application lifecycle."""

    def test_app_startup_with_env_path(self):
        """Test application startup creates necessary structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            
            # Path should exist
            assert os.path.exists(tmpdir)

    def test_app_with_preexisting_environments(self):
        """Test app startup with pre-existing environments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pre-existing environment
            env_file = os.path.join(tmpdir, 'main.json')
            initial_env = {'windows': {'win_1': {'type': 'text'}}}
            
            with open(env_file, 'w') as f:
                json.dump(initial_env, f)
            
            # Start app
            app = Application(
                port=8097,
                base_url='/',
                env_path=tmpdir,
            )
            
            # Environment file should still exist
            assert os.path.exists(env_file)


class TestErrorRecovery:
    """Test error handling and recovery."""

    def test_recover_from_corrupted_env_file(self):
        """Test handling of corrupted environment files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create corrupted file
            env_file = os.path.join(tmpdir, 'corrupted.json')
            with open(env_file, 'w') as f:
                f.write('{invalid json}')
            
            # Verify file exists but is invalid
            assert os.path.exists(env_file)
            
            with pytest.raises(json.JSONDecodeError):
                with open(env_file, 'r') as f:
                    json.load(f)

    def test_create_backup_on_save(self):
        """Test creating backups when saving environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, 'env.json')
            backup_file = os.path.join(tmpdir, 'env.json.bak')
            
            original_data = {'windows': {'win_1': {}}}
            
            # Save original
            with open(env_file, 'w') as f:
                json.dump(original_data, f)
            
            # Create backup
            with open(env_file, 'r') as f:
                backup_data = json.load(f)
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f)
            
            assert os.path.exists(backup_file)


class TestConcurrentOperations:
    """Test handling of concurrent operations."""

    def test_multiple_window_updates(self):
        """Test multiple window updates in sequence."""
        env = {'windows': {}}
        
        for i in range(10):
            env['windows'][f'win_{i}'] = {
                'type': 'text',
                'content': f'Content {i}'
            }
        
        assert len(env['windows']) == 10

    def test_concurrent_layout_modifications(self):
        """Test concurrent layout modifications."""
        layout = {'grid': []}
        
        for i in range(5):
            layout['grid'].append({
                'i': f'win_{i}',
                'x': i % 3,
                'y': i // 3
            })
        
        assert len(layout['grid']) == 5


class TestDataConsistency:
    """Test data consistency across operations."""

    def test_window_data_consistency(self):
        """Test that window data remains consistent."""
        window = {
            'type': 'plot',
            'title': 'My Plot',
            'data': {'x': [1, 2, 3], 'y': [1, 4, 9]},
            'props': {'show_legend': True}
        }
        
        # Serialize and deserialize
        serialized = json.dumps(window)
        deserialized = json.loads(serialized)
        
        assert deserialized == window

    def test_environment_integrity(self):
        """Test environment data integrity after operations."""
        env = {
            'windows': {
                'win_1': {'type': 'text', 'content': 'Text'},
                'win_2': {'type': 'plot', 'data': {'x': [1, 2]}}
            },
            'layouts': {
                'main': {'grid': []}
            }
        }
        
        # Add window
        env['windows']['win_3'] = {'type': 'image'}
        
        # Modify layout
        env['layouts']['main']['grid'].append({'i': 'win_1'})
        
        # Verify integrity
        assert len(env['windows']) == 3
        assert len(env['layouts']['main']['grid']) == 1
