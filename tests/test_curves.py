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
