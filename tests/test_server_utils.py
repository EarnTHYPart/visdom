import json
import os

from visdom.utils import server_utils


def test_hash_password_is_deterministic_and_hex():
    value = server_utils.hash_password("secret")

    assert value == server_utils.hash_password("secret")
    assert len(value) == 64
    assert all(ch in "0123456789abcdef" for ch in value)


def test_extract_eid_defaults_to_main_and_escapes_slashes():
    assert server_utils.extract_eid({}) == "main"
    assert server_utils.extract_eid({"eid": "team/exp"}) == "team_exp"
    assert server_utils.extract_eid({"eid": "team\\exp"}) == "team_exp"


def test_window_builds_plot_payload_by_default():
    args = {
        "data": [{"type": "line", "y": [1, 2, 3]}],
        "layout": {"title": "plot"},
        "opts": {"title": "Demo Plot", "width": 400, "height": 300},
    }

    result = server_utils.window(args)

    assert result["command"] == "window"
    assert result["type"] == "plot"
    assert result["title"] == "Demo Plot"
    assert result["content"]["layout"]["title"] == "plot"


def test_update_window_applies_non_none_layout_and_opts():
    pane = {
        "version": 1,
        "title": "Old",
        "content": {
            "layout": {"xaxis": {"title": "x"}},
            "data": [{"name": "old-a"}, {"name": "old-b"}],
        },
    }

    updated = server_utils.update_window(
        pane,
        {
            "layout": {"xaxis": {"title": "new-x"}, "yaxis": None},
            "opts": {"title": "New", "legend": ["A", "B"], "height": None},
        },
    )

    assert updated["version"] == 2
    assert updated["title"] == "New"
    assert updated["content"]["layout"]["xaxis"]["title"] == "new-x"
    assert "yaxis" not in updated["content"]["layout"]
    assert [d["name"] for d in updated["content"]["data"]] == ["A", "B"]


class _DummySocket:
    def __init__(self):
        self.messages = []
        self.eid = None

    def write_message(self, msg):
        self.messages.append(msg)


def _plot_env(title):
    return {
        "jsons": {
            "win": {
                "type": "plot",
                "title": title,
                "content": {"data": [{"name": "trace"}], "layout": {}},
                "i": 1,
            }
        },
        "reload": {},
    }


def test_compare_envs_does_not_load_from_parent_directory(tmp_path):
    env_path = tmp_path / "envs"
    env_path.mkdir()
    traversal_eid = os.path.join("..", "secret")
    (tmp_path / "secret.json").write_text(
        json.dumps(_plot_env("outside")), encoding="utf-8"
    )

    state = {"safe": _plot_env("safe")}
    socket = _DummySocket()

    server_utils.compare_envs(
        state, ["safe", traversal_eid], socket, env_path=str(env_path)
    )

    assert traversal_eid not in state


def test_resolve_env_path_file_normalizes_eid_and_stays_within_base_dir(tmp_path):
    env_path = tmp_path / "envs"
    env_path.mkdir()

    resolved = server_utils.resolve_env_path_file(str(env_path), "../secret")

    assert resolved == os.path.realpath(env_path / ".._secret.json")
    assert os.path.commonpath([os.path.realpath(env_path), resolved]) == os.path.realpath(
        env_path
    )


def test_compare_envs_returns_when_no_environments_are_available(tmp_path):
    env_path = tmp_path / "envs"
    env_path.mkdir()

    state = {}
    socket = _DummySocket()

    server_utils.compare_envs(
        state,
        ["missing_a", "missing_b"],
        socket,
        env_path=str(env_path),
    )

    assert socket.messages == []
    assert state == {}


def test_load_env_does_not_load_from_parent_directory(tmp_path):
    env_path = tmp_path / "envs"
    env_path.mkdir()
    traversal_eid = os.path.join("..", "secret")
    (tmp_path / "secret.json").write_text(
        json.dumps(_plot_env("outside")), encoding="utf-8"
    )

    state = {}
    socket = _DummySocket()

    server_utils.load_env(state, traversal_eid, socket, env_path=str(env_path))

    assert traversal_eid not in state
