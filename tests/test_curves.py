"""Unit tests for ROC/PR helper plotting APIs."""

import os
import sys

import numpy as np
import pytest

# Add py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

from visdom import Visdom


def _viz():
    return Visdom(send=False, use_incoming_socket=False)


def test_roc_curve_from_labels_and_scores():
    vis = _viz()
    y_true = np.array([0, 0, 1, 1])
    y_score = np.array([0.1, 0.4, 0.35, 0.8])

    msg, endpoint = vis.roc_curve(y_true=y_true, y_score=y_score)

    assert endpoint == "events"
    assert msg["pane_type"] == "roc_curve"
    assert msg["data"][0]["type"] == "scatter"
    assert msg["data"][0]["mode"] == "lines"
    assert msg["data"][0]["x"][0] == 0.0
    assert msg["data"][0]["y"][0] == 0.0
    assert msg["data"][0]["x"][-1] == 1.0
    assert msg["data"][0]["y"][-1] == 1.0


def test_roc_curve_from_precomputed_points():
    vis = _viz()

    msg, endpoint = vis.roc_curve(fpr=[1.0, 0.0, 0.5], tpr=[1.0, 0.0, 0.75])

    assert endpoint == "events"
    assert msg["pane_type"] == "roc_curve"
    assert msg["data"][0]["x"] == [0.0, 0.5, 1.0]
    assert msg["data"][0]["y"] == [0.0, 0.75, 1.0]


def test_pr_curve_from_labels_and_scores():
    vis = _viz()
    y_true = np.array([0, 0, 1, 1])
    y_score = np.array([0.1, 0.4, 0.35, 0.8])

    msg, endpoint = vis.pr_curve(y_true=y_true, y_score=y_score)

    assert endpoint == "events"
    assert msg["pane_type"] == "pr_curve"
    assert msg["data"][0]["x"][0] == 0.0
    assert msg["data"][0]["y"][0] == 1.0
    assert msg["data"][1]["y"] == [0.5, 0.5]


def test_pr_curve_from_precomputed_points():
    vis = _viz()

    msg, endpoint = vis.pr_curve(precision=[0.9, 0.7, 0.8], recall=[1.0, 0.5, 0.0])

    assert endpoint == "events"
    assert msg["pane_type"] == "pr_curve"
    assert msg["data"][0]["x"] == [0.0, 0.5, 1.0]
    assert msg["data"][0]["y"] == [0.8, 0.7, 0.9]


def test_curve_requires_exactly_one_input_mode():
    vis = _viz()

    with pytest.raises(AssertionError):
        vis.roc_curve(y_true=[0, 1], y_score=[0.1, 0.9], fpr=[0.0, 1.0], tpr=[0.0, 1.0])

    with pytest.raises(AssertionError):
        vis.pr_curve()


def test_roc_curve_rejects_non_finite_scores():
    vis = _viz()

    with pytest.raises(AssertionError, match="finite"):
        vis.roc_curve(y_true=[0, 1], y_score=[0.2, np.nan])


def test_curve_rejects_out_of_range_precomputed_values():
    vis = _viz()

    with pytest.raises(AssertionError, match=r"\[0, 1\]"):
        vis.roc_curve(fpr=[0.0, 1.2], tpr=[0.0, 1.0])

    with pytest.raises(AssertionError, match=r"\[0, 1\]"):
        vis.pr_curve(precision=[0.9, -0.1], recall=[0.0, 1.0])


def test_curve_uses_default_legends_when_invalid():
    vis = _viz()

    roc_msg, _ = vis.roc_curve(fpr=[0.0, 1.0], tpr=[0.0, 1.0], opts={"legend": ["ROC only"]})
    assert roc_msg["data"][0]["name"] == "ROC"
    assert roc_msg["data"][1]["name"] == "Chance"

    pr_msg, _ = vis.pr_curve(
        precision=[0.9, 0.8],
        recall=[1.0, 0.0],
        opts={"legend": "not-a-legend"},
    )
    assert pr_msg["data"][0]["name"] == "PR"
    assert pr_msg["data"][1]["name"] == "Baseline"
