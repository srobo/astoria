"""Tests for MQTT topic abstraction."""

from re import compile

import pytest

from astoria.common.topic import Topic

BASIC_TOPICS = [
    (["foo", "bar", "biz"], "foo/bar/biz"),
    (["superfoo", "12", "uberbar"], "superfoo/12/uberbar"),
]

WILDCARD_TOPICS = [
    (["foo", "#"], "foo/#", "foo/bar/biz"),
    (["superfoo", "+", "uberbar"], "superfoo/+/uberbar", "superfoo/12/uberbar"),
]


def test_topic_init() -> None:
    """Test that we can construct Topic objects."""
    for parts, topic in BASIC_TOPICS:
        t = Topic(parts)
        assert isinstance(t, Topic)


def test_topic_str() -> None:
    """Test the str render of a topic."""
    for parts, topic in BASIC_TOPICS:
        t = Topic(parts)
        assert str(t) == topic

    for parts, topic, _ in WILDCARD_TOPICS:
        t = Topic(parts)
        assert str(t) == topic


def test_topic_repr() -> None:
    """Test repr."""
    t = Topic(["bees"])
    assert repr(t) == "Topic(\"bees\")"


def test_topic_equality() -> None:
    """Test topic equality."""
    t = Topic(["bees"])
    assert t == t
    assert t != 3
    assert t != "bees"
    assert t != Topic(["bees", "hive"])


def test_topic_parse() -> None:
    """Test that we can parse topics."""
    for parts, topic in BASIC_TOPICS:
        assert Topic(parts) == Topic.parse(topic)

    for parts, topic, _ in WILDCARD_TOPICS:
        assert Topic(parts) == Topic.parse(topic)


def test_topic_parse_no_slash() -> None:
    """Test that preceeding and following slashes are rejected."""
    cases = [
        "foo/bar/",
        "/foo/bar",
        "/foo/bar/"
        "//",
        "/",
        "",
    ]

    for topic in cases:
        with pytest.raises(ValueError):
            Topic.parse(topic)


def test_topic_is_publishable() -> None:
    """Test the is_publishable property."""
    for parts, _ in BASIC_TOPICS:
        t = Topic(parts)
        assert t.is_publishable

    for parts, _, _ in WILDCARD_TOPICS:
        t = Topic(parts)
        assert not t.is_publishable


def test_topic_regex() -> None:
    """Test the regex property."""
    for parts, topic in BASIC_TOPICS:
        t = Topic(parts)
        assert t.regex == f"^{topic}$"

    for parts, topic, example in WILDCARD_TOPICS:
        t = Topic(parts)
        reg = compile(t.regex)
        assert reg.match(example)
        assert not reg.match("u85932q4fds9/3£2####")
