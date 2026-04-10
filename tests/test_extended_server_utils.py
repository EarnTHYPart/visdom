"""Extended unit tests for Visdom server utilities."""

import json
import os
import sys
import tempfile
from unittest.mock import Mock

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

from visdom.utils.server_utils import (
    LazyEnvData,
    broadcast,
    compare_envs,
    escape_eid,
    gather_envs,
    load_env,
    register_window,
    serialize_env,
    stringify,
    update_window,
    window,
)


class DummyHandler:
    def __init__(self):
        self.state = {}
        self.subs = {}
        self.writes = []

    def write(self, value):
        self.writes.append(value)


class TestEnvironmentSerialization:
    def test_serialize_simple_environment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state = {"main": {"jsons": {}, "reload": {}}}
            eids = serialize_env(state, ["main"], env_path=tmpdir)
            assert eids == ["main"]
            assert os.path.isfile(os.path.join(tmpdir, "main.json"))

    def test_serialize_ignores_missing_env_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state = {"main": {"jsons": {}, "reload": {}}}
            eids = serialize_env(state, ["missing"], env_path=tmpdir)
            assert eids == []


class TestStringifyFunction:
    def test_stringify_none(self):
        assert isinstance(stringify(None), str)

    def test_stringify_string_is_json_encoded(self):
        assert stringify("test string") == '"test string"'

    def test_stringify_number(self):
        assert stringify(42) == "42"

    def test_stringify_bytes_raises(self):
        try:
            stringify(b"bytes")
            assert False, "Expected TypeError for bytes"
        except TypeError:
            assert True


class TestEnvironmentIDEscaping:
    def test_escape_eid_with_path_separators(self):
        assert escape_eid("env/with/slashes") == "env_with_slashes"


class TestWindowHelpers:
    def test_update_window_updates_layout_and_version(self):
        p = {
            "content": {"layout": {"title": "old"}, "data": [{"name": "a"}]},
            "version": 1,
        }
        updated = update_window(
            p,
            {"layout": {"title": "new"}, "opts": {"legend": ["series_a"]}},
        )
        assert updated["content"]["layout"]["title"] == "new"
        assert updated["version"] == 2

    def test_window_returns_plot_window(self):
        args = {
            "data": [{"type": "scatter", "x": [1], "y": [2]}],
            "layout": {"title": "plot"},
            "opts": {"title": "My Plot"},
        }
        result = window(args)
        assert isinstance(result, dict)
        assert result["type"] == "plot"


class TestEnvironmentLoadingAndGathering:
    def test_gather_envs_from_disk_and_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "disk_env.json"), "w") as f:
                json.dump({"jsons": {}, "reload": {}}, f)

            envs = gather_envs({"memory_env": {"jsons": {}, "reload": {}}}, env_path=tmpdir)
            assert "disk_env" in envs
            assert "memory_env" in envs

    def test_load_env_emits_layout_message(self):
        socket = Mock()
        state = {
            "main": {
                "jsons": {
                    "win_1": {"i": 1, "title": "t", "content": {"data": []}},
                },
                "reload": {},
            }
        }

        load_env(state, "main", socket, env_path=None)

        assert socket.write_message.called


class TestCompareAndBroadcast:
    def test_compare_envs_sets_socket_eid(self):
        socket = Mock()
        state = {
            "e1": {
                "jsons": {
                    "w": {
                        "title": "shared",
                        "type": "plot",
                        "content": {"data": [{"name": "a"}], "layout": {}},
                        "contentID": "1",
                    }
                },
                "reload": {},
            },
            "e2": {
                "jsons": {
                    "w": {
                        "title": "shared",
                        "type": "plot",
                        "content": {"data": [{"name": "b"}], "layout": {}},
                        "contentID": "2",
                    }
                },
                "reload": {},
            },
        }

        compare_envs(state, ["e1", "e2"], socket, env_path=None)

        assert socket.eid == ["e1", "e2"]

    def test_register_window_stores_window(self):
        handler = DummyHandler()
        pane = {"id": "win_1", "content": {"data": [], "layout": {}}, "version": 1}

        register_window(handler, pane, "main")

        assert "main" in handler.state
        assert "win_1" in handler.state["main"]["jsons"]
        assert handler.writes == ["win_1"]

    def test_broadcast_sends_only_matching_eid(self):
        sub_main = Mock()
        sub_main.eid = "main"
        sub_other = Mock()
        sub_other.eid = "other"

        handler = DummyHandler()
        handler.subs = {"a": sub_main, "b": sub_other}

        broadcast(handler, {"command": "window"}, "main")

        assert sub_main.write_message.called
        assert not sub_other.write_message.called


class TestLazyEnvData:
    def test_lazy_env_data_loads_on_access(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, "env.json")
            with open(env_file, "w") as f:
                json.dump({"jsons": {"w": {}}, "reload": {}}, f)

            lazy_env = LazyEnvData(env_file)
            assert "jsons" in lazy_env
            assert lazy_env["jsons"] == {"w": {}}
