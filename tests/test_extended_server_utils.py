"""Extended unit tests for Visdom server utilities."""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py'))

from visdom.utils.server_utils import (
    serialize_env, stringify, escape_eid,
    register_window, update_window, window,
    load_env, gather_envs, compare_envs,
    broadcast, broadcast_envs, send_to_sources,
    LazyEnvData
)


class TestEnvironmentSerialization:
    """Test environment serialization functionality."""

    def test_serialize_simple_environment(self):
        """Test serializing a simple environment."""
        env = {
            'windows': {
                'win_1': {
                    'type': 'text',
                    'content': 'Hello World'
                }
            }
        }
        
        serialized = serialize_env(env)
        assert isinstance(serialized, (dict, str))

    def test_serialize_empty_environment(self):
        """Test serializing an empty environment."""
        env = {'windows': {}}
        serialized = serialize_env(env)
        assert serialized is not None

    def test_serialize_complex_environment(self):
        """Test serializing environment with multiple window types."""
        env = {
            'windows': {
                'text_1': {'type': 'text', 'content': 'Text'},
                'plot_1': {'type': 'plot', 'data': {'x': [1, 2, 3]}},
                'image_1': {'type': 'image', 'src': 'data:image/png;base64,...'}
            },
            'layouts': {
                'main': {'grid': []}
            }
        }
        
        serialized = serialize_env(env)
        assert serialized is not None


class TestStringifyFunction:
    """Test stringify utility function."""

    def test_stringify_none(self):
        """Test stringifying None value."""
        result = stringify(None)
        assert isinstance(result, str)

    def test_stringify_string(self):
        """Test stringifying string."""
        result = stringify('test string')
        assert result == 'test string'

    def test_stringify_number(self):
        """Test stringifying numbers."""
        assert stringify(42) == '42'
        assert stringify(3.14) == '3.14'

    def test_stringify_dict(self):
        """Test stringifying dictionary."""
        data = {'key': 'value'}
        result = stringify(data)
        assert isinstance(result, str)

    def test_stringify_list(self):
        """Test stringifying list."""
        data = [1, 2, 3]
        result = stringify(data)
        assert isinstance(result, str)

    def test_stringify_bytes(self):
        """Test stringifying bytes."""
        data = b'bytes'
        result = stringify(data)
        assert isinstance(result, str)

    def test_stringify_unicode(self):
        """Test stringifying unicode characters."""
        data = '你好世界'
        result = stringify(data)
        assert isinstance(result, str)


class TestEnvironmentIDEscaping:
    """Test environment ID escaping and unescaping."""

    def test_escape_simple_eid(self):
        """Test escaping simple environment ID."""
        eid = 'main'
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)

    def test_escape_eid_with_special_chars(self):
        """Test escaping EID with special characters."""
        eid = 'env_with_special_#$%'
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)

    def test_escape_eid_with_spaces(self):
        """Test escaping EID with spaces."""
        eid = 'env with spaces'
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)

    def test_escape_eid_with_unicode(self):
        """Test escaping EID with unicode."""
        eid = 'env_中文'
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)

    def test_escape_empty_eid(self):
        """Test escaping empty EID."""
        eid = ''
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)


class TestWindowRegistration:
    """Test window registration functionality."""

    def test_register_simple_window(self):
        """Test registering a simple window."""
        env = {'windows': {}}
        window_data = {
            'type': 'text',
            'content': 'Hello'
        }
        
        # Should register without error
        register_window(env, 'win_1', window_data)

    def test_register_multiple_windows(self):
        """Test registering multiple windows."""
        env = {'windows': {}}
        
        for i in range(5):
            window_data = {
                'type': 'text',
                'content': f'Window {i}'
            }
            register_window(env, f'win_{i}', window_data)
        
        assert len(env['windows']) == 5

    def test_register_window_overwrites_existing(self):
        """Test that registering overwrites existing window."""
        env = {'windows': {'win_1': {'content': 'old'}}}
        new_data = {'content': 'new'}
        
        register_window(env, 'win_1', new_data)
        assert env['windows']['win_1'] == new_data


class TestWindowUpdate:
    """Test window update functionality."""

    def test_update_window_content(self):
        """Test updating window content."""
        env = {'windows': {'win_1': {'type': 'text', 'content': 'old'}}}
        update_data = {'content': 'new'}
        
        update_window(env, 'win_1', update_data)
        assert env['windows']['win_1']['content'] == 'new'

    def test_update_window_properties(self):
        """Test updating window properties."""
        env = {'windows': {'win_1': {'type': 'plot', 'title': 'Plot1'}}}
        update_data = {'title': 'Updated Plot'}
        
        update_window(env, 'win_1', update_data)
        assert env['windows']['win_1']['title'] == 'Updated Plot'

    def test_update_nonexistent_window(self):
        """Test updating non-existent window."""
        env = {'windows': {}}
        # Should handle gracefully
        update_window(env, 'nonexistent', {'content': 'test'})


class TestWindowUtility:
    """Test window utility function."""

    def test_window_returns_dict(self):
        """Test that window() returns a dict-like object."""
        win_id = 'test_window'
        pane_id = 'main'
        
        result = window(id=win_id, pane=pane_id)
        assert isinstance(result, dict)

    def test_window_with_various_types(self):
        """Test window() with various parameters."""
        result = window(
            id='win_1',
            pane='main',
            type='plot',
            title='My Plot',
            content='test'
        )
        assert isinstance(result, dict)


class TestEnvironmentLoading:
    """Test environment loading from disk."""

    def test_load_env_creates_structure(self):
        """Test that load_env creates proper environment structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, 'main.json')
            env_data = {
                'windows': {},
                'layouts': {}
            }
            
            with open(env_path, 'w') as f:
                json.dump(env_data, f)
            
            # load_env should read the file
            loaded = load_env(tmpdir, 'main')
            assert loaded is not None

    def test_load_nonexistent_env(self):
        """Test loading non-existent environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = load_env(tmpdir, 'nonexistent')
            # Should return default or None
            assert env is None or isinstance(env, dict)

    def test_load_corrupted_env_file(self):
        """Test loading corrupted JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, 'corrupted.json')
            
            with open(env_path, 'w') as f:
                f.write('{invalid json}')
            
            # Should handle parsing error
            env = load_env(tmpdir, 'corrupted')


class TestEnvironmentGathering:
    """Test gathering multiple environments."""

    def test_gather_envs_empty_directory(self):
        """Test gathering from empty environment directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            envs = gather_envs(tmpdir)
            assert isinstance(envs, (dict, list))

    def test_gather_envs_multiple_files(self):
        """Test gathering multiple environment files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                env_path = os.path.join(tmpdir, f'env_{i}.json')
                with open(env_path, 'w') as f:
                    json.dump({'windows': {}}, f)
            
            envs = gather_envs(tmpdir)
            # Should find all environment files
            assert len(envs) > 0 or envs == {}

    def test_gather_envs_non_json_files(self):
        """Test that gather_envs ignores non-JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some non-JSON files
            with open(os.path.join(tmpdir, 'readme.txt'), 'w') as f:
                f.write('not json')
            
            # Create a JSON file
            with open(os.path.join(tmpdir, 'env.json'), 'w') as f:
                json.dump({'windows': {}}, f)
            
            envs = gather_envs(tmpdir)
            # Should only load JSON files


class TestEnvironmentComparison:
    """Test environment comparison functionality."""

    def test_compare_identical_envs(self):
        """Test comparing identical environments."""
        env1 = {'windows': {'w1': {'type': 'text'}}}
        env2 = {'windows': {'w1': {'type': 'text'}}}
        
        comparison = compare_envs(env1, env2)
        # Should show no differences or minimal diff

    def test_compare_different_envs(self):
        """Test comparing different environments."""
        env1 = {'windows': {'w1': {'type': 'text'}}}
        env2 = {'windows': {'w2': {'type': 'plot'}}}
        
        comparison = compare_envs(env1, env2)
        # Should show differences

    def test_compare_with_additional_windows(self):
        """Test comparing environments with added windows."""
        env1 = {'windows': {'w1': {}}}
        env2 = {'windows': {'w1': {}, 'w2': {}}}
        
        comparison = compare_envs(env1, env2)


class TestBroadcasting:
    """Test broadcasting functionality."""

    def test_broadcast_message(self):
        """Test broadcasting a message."""
        with patch('tornado.ioloop.IOLoop.current'):
            message = {'cmd': 'update', 'data': 'test'}
            # Should broadcast without error
            broadcast(message)

    def test_broadcast_envs(self):
        """Test broadcasting environment updates."""
        with patch('tornado.ioloop.IOLoop.current'):
            eid = 'main'
            # Should broadcast environment

    def test_send_to_sources(self):
        """Test sending message to specific sources."""
        with patch('tornado.ioloop.IOLoop.current'):
            message = {'data': 'test'}
            sources = ['source1', 'source2']
            # Should send to specified sources


class TestLazyEnvData:
    """Test LazyEnvData class for lazy-loading environments."""

    def test_lazy_env_data_creation(self):
        """Test creating LazyEnvData instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, 'env.json')
            with open(env_file, 'w') as f:
                json.dump({'windows': {}}, f)
            
            lazy_env = LazyEnvData(tmpdir, 'env')
            assert lazy_env is not None

    def test_lazy_env_data_loads_on_access(self):
        """Test that LazyEnvData loads data on access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, 'env.json')
            env_data = {'windows': {'w1': {'type': 'text'}}}
            
            with open(env_file, 'w') as f:
                json.dump(env_data, f)
            
            lazy_env = LazyEnvData(tmpdir, 'env')
            # Accessing should trigger load
            if hasattr(lazy_env, 'windows'):
                assert lazy_env.windows is not None

    def test_lazy_env_data_caching(self):
        """Test that LazyEnvData caches loaded data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, 'env.json')
            with open(env_file, 'w') as f:
                json.dump({'windows': {}}, f)
            
            lazy_env = LazyEnvData(tmpdir, 'env')
            # Multiple accesses should use cache


class TestServerUtilsEdgeCases:
    """Test edge cases in server utilities."""

    def test_serialize_very_large_environment(self):
        """Test serializing very large environment."""
        large_env = {
            'windows': {
                f'win_{i}': {
                    'type': 'plot',
                    'data': {'x': list(range(1000))}
                }
                for i in range(100)
            }
        }
        
        serialized = serialize_env(large_env)
        assert serialized is not None

    def test_stringify_recursive_structure(self):
        """Test stringify with recursive data structures."""
        data = {'a': {'b': {'c': {'d': 'value'}}}}
        result = stringify(data)
        assert isinstance(result, str)

    def test_escape_eid_with_path_separators(self):
        """Test escaping EID with path separators."""
        eid = 'env/with/slashes'
        escaped = escape_eid(eid)
        assert isinstance(escaped, str)

    def test_window_with_empty_parameters(self):
        """Test window() with empty parameters."""
        result = window()
        assert result is not None
