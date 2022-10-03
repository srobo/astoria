"""Test the MQTT Wrapper class."""

import asyncio
from typing import Match

import gmqtt
import pytest
from pydantic import BaseModel

from astoria.common.config.system import MQTTBrokerInfo
from astoria.common.ipc import ManagerMessage
from astoria.common.mqtt.topic import Topic
from astoria.common.mqtt.wrapper import MQTTWrapper

BROKER_INFO = MQTTBrokerInfo(
    host="localhost",
    port=1883,
)


class StubModel(BaseModel):
    """Test BaseModel."""

    foo: str


async def stub_message_handler(
    match: Match[str],
    payload: str,
) -> None:
    """Used in tests as a stub with the right type."""
    pass


def test_wrapper_init_minimal() -> None:
    """Test initialising the wrapper with minimal options."""
    wr = MQTTWrapper("foo", BROKER_INFO)

    assert wr._client_name == "foo"
    assert wr._last_will is None
    assert len(wr._dependencies) == 0
    assert len(wr._dependency_events) == 0
    assert wr._no_dependency_event is None

    assert len(wr._topic_handlers) == 2
    assert wr._topic_handlers[Topic(["astoria", "+"])] == wr._dependency_message_handler
    assert wr._topic_handlers[
        Topic(["astoria", "+", "request", "+", "+"])
    ] == wr._request_response_message_handler

    assert wr._client._client_id == "foo"


def test_wrapper_init_dependencies() -> None:
    """Test that the wrapper constructor sets up dependencies."""
    deps = ["foo", "bar", "bees"]
    wr = MQTTWrapper("foo", BROKER_INFO, dependencies=deps)

    assert len(deps) == len(wr._dependency_events)
    assert len(deps) == len(wr._dependencies)

    for d in deps:
        assert d in wr._dependency_events
        assert d in wr._dependencies


def test_wrapper_init_last_will() -> None:
    """Test that the wrapper constructor sets up the last will."""
    lw = ManagerMessage(status="RUNNING")
    wr = MQTTWrapper("foo", BROKER_INFO, last_will=lw)
    assert wr._last_will is lw


def test_wrapper_init_event() -> None:
    """Test that the no_dep_event is passed properly."""
    ev = asyncio.Event()
    wr = MQTTWrapper("foo", BROKER_INFO, no_dependency_event=ev)

    assert wr._no_dependency_event is ev


def test_wrapper_is_connected_at_init() -> None:
    """Test that the wrapper is not connected to the broker at init."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert not wr.is_connected


def test_wrapper_last_will_message_null() -> None:
    """Test that the last will message is None when not supplied."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert wr.last_will_message is None


def test_wrapper_last_will_message() -> None:
    """Test that the wrapper gives a valid last will message."""
    lw = ManagerMessage(status="RUNNING")
    wr = MQTTWrapper("foo", BROKER_INFO, last_will=lw)

    message = wr.last_will_message
    assert isinstance(message, gmqtt.Message)
    assert message.topic == b"astoria/foo"
    assert message.qos == 0
    assert message.retain
    assert message.payload == lw.json().encode()


def test_wrapper_mqtt_prefix() -> None:
    """Test that the MQTT prefix is as expected."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert wr.mqtt_prefix == "astoria/foo"


def test_subscribe() -> None:
    """Test that subscribing works as expected."""
    wr = MQTTWrapper("foo", BROKER_INFO)

    assert len(wr._topic_handlers) == 2
    assert wr._topic_handlers[Topic(["astoria", "+"])] == wr._dependency_message_handler
    assert wr._topic_handlers[
        Topic(["astoria", "+", "request", "+", "+"])
    ] == wr._request_response_message_handler

    wr.subscribe("bees/+", stub_message_handler)
    assert len(wr._topic_handlers) == 3
    assert wr._topic_handlers[Topic(["astoria", "+"])] == wr._dependency_message_handler
    assert wr._topic_handlers[Topic(["astoria", "bees", "+"])] == stub_message_handler
    assert wr._topic_handlers[
        Topic(["astoria", "+", "request", "+", "+"])
    ] == wr._request_response_message_handler


@pytest.mark.filterwarnings("ignore")
@pytest.mark.asyncio
async def test_connect_disconnect() -> None:
    """Test that the wrapper can connect and disconnect from the broker."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    await wr.connect()
    assert wr.is_connected

    await wr.disconnect()
    assert not wr.is_connected


@pytest.mark.asyncio
async def test_handler_called() -> None:
    """Test that subscription handlers are called correctly."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        assert payload == "hive"
        ev.set()

    wr = MQTTWrapper("foo", BROKER_INFO)
    wr.subscribe("bees/+", test_handler)
    await wr.connect()

    # Manually call on_message
    res = await wr.on_message(
        wr._client,
        "astoria/bees/bar",
        b"hive",
        0,
        {},
    )
    assert res == gmqtt.constants.PubRecReasonCode.SUCCESS

    await asyncio.wait_for(ev.wait(), 0.1)

    await wr.disconnect()


@pytest.mark.asyncio
async def test_publish_send_and_receive() -> None:
    """Test that we can publish and receive a message."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        ev.set()

    wr_sub = MQTTWrapper("foo", BROKER_INFO)
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    wr_sub.subscribe("bar/bees/+", test_handler)
    await wr_sub.connect()
    await wr_pub.connect()

    wr_pub.publish("bees/foo", StubModel(foo="bar"))

    await asyncio.wait_for(ev.wait(), 0.5)

    await wr_sub.disconnect()
    await wr_pub.disconnect()


@pytest.mark.asyncio
async def test_publish_send_and_receive_on_self() -> None:
    """Test that we can publish and receive a message on it's own topic."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        ev.set()

    wr_sub = MQTTWrapper("foo", BROKER_INFO)
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    wr_sub.subscribe("bar", test_handler)
    await wr_sub.connect()
    await wr_pub.connect()

    wr_pub.publish("", StubModel(foo="bar"))

    await asyncio.wait_for(ev.wait(), 0.5)

    await wr_sub.disconnect()
    await wr_pub.disconnect()


@pytest.mark.asyncio
async def test_publish_bad_topic_error() -> None:
    """Test that we cannot publish to an invalid topic."""
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    await wr_pub.connect()

    with pytest.raises(ValueError):
        wr_pub.publish("bees/+", StubModel(foo="bar"))

    with pytest.raises(ValueError):
        wr_pub.publish("bees/#", StubModel(foo="bar"))

    with pytest.raises(ValueError):
        wr_pub.publish("bees/", StubModel(foo="bar"))

    await wr_pub.disconnect()
