"""Tests for environment file path escaping utilities."""

import json
import os
import sys
from tempfile import TemporaryDirectory

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

from visdom.utils.server_utils import escape_eid, env_path_file_for, load_env, serialize_env


class _Socket:
    def __init__(self):
        self.messages = []
        self.eid = None

    def write_message(self, message):
        self.messages.append(message)


def test_env_path_escaping_round_trip():
    with TemporaryDirectory() as tmpdir:
        eid = r"team\models/run-01"
        state = {eid: {"jsons": {"win": {"title": "ok"}}, "reload": {}}}

        saved = serialize_env(state, [eid], env_path=tmpdir)
        assert saved == [eid]

        expected_path = os.path.join(tmpdir, "team_models_run-01.json")
        assert env_path_file_for(tmpdir, eid) == expected_path
        assert os.path.exists(expected_path)

        with open(expected_path, "r") as fn:
            assert json.load(fn) == state[eid]

        socket = _Socket()
        loaded_state = {}
        load_env(loaded_state, eid, socket, env_path=tmpdir)

        escaped_eid = escape_eid(eid)
        assert loaded_state[escaped_eid] == state[eid]
        assert socket.eid == escaped_eid
        assert socket.messages[-1] == json.dumps({"command": "layout"})
