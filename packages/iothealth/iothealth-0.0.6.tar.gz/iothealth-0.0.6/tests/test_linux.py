"""Unit tests for Linux module."""

from iothealth import linux


def test_basic():
    assert linux.Linux().summary() is not None
