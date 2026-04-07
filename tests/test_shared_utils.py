import os

from visdom.utils import shared_utils


def test_get_new_window_id_has_prefix_and_unique_values():
    first = shared_utils.get_new_window_id()
    second = shared_utils.get_new_window_id()

    assert first.startswith("window_")
    assert second.startswith("window_")
    assert first != second


def test_ensure_dir_exists_creates_nested_directory(tmp_path):
    target = tmp_path / "a" / "b" / "c"

    shared_utils.ensure_dir_exists(target)

    assert os.path.isdir(target)


def test_warn_once_only_emits_single_warning():
    shared_utils._seen_warnings.clear()

    with shared_utils.warnings.catch_warnings(record=True) as caught:
        shared_utils.warnings.simplefilter("always")
        shared_utils.warn_once("duplicate-warning", UserWarning)
        shared_utils.warn_once("duplicate-warning", UserWarning)

    assert len(caught) == 1
    assert "duplicate-warning" in str(caught[0].message)
