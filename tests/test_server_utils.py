from visdom.utils import server_utils


def test_hash_password_is_deterministic_and_hex():
    value = server_utils.hash_password("secret")

    assert value == server_utils.hash_password("secret")
    assert len(value) == 64
    assert all(ch in "0123456789abcdef" for ch in value)


def test_extract_eid_defaults_to_main_and_escapes_slashes():
    assert server_utils.extract_eid({}) == "main"
    assert server_utils.extract_eid({"eid": "team/exp"}) == "team_exp"


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
