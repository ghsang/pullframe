import random
import string
from datetime import datetime

import pytest  # type: ignore
from dockontext import Config, container_generator_from_image

from pullframe.api import Coordinator
from pullframe.coordinator import zookeeper_coordinator
from pullframe.types import Node, Resource


def test_available_return_none_when_request_other_name(coordinator):
    _notify(coordinator)
    assert coordinator.available(*_request(name="invalid")) is None


def test_available_return_none_when_the_request_cant_be_satisfied(coordinator):
    _notify(coordinator)
    assert coordinator.available(*_request(version=11)) is None


def test_available_return_expected_resource(coordinator):
    _notify(coordinator)
    assert coordinator.available(*_request()) == _resource()


def test_available_apply_updates(coordinator):
    _notify(coordinator)
    last_idx = datetime(2020, 1, 2)
    _notify(coordinator, last_idx=last_idx)
    assert coordinator.available(*_request()) == _resource(last_idx)


def test_version_return_none_if_not_exists(coordinator):
    assert coordinator.version("fakename") is None


def test_version_return_initial_version(coordinator):
    _notify(coordinator)
    assert coordinator.version("fakename") == 10


def test_version_apply_updates(coordinator):
    _notify(coordinator)
    _notify(coordinator, version=11)
    assert coordinator.version("fakename") == 11


create_container = pytest.fixture(container_generator_from_image)


@pytest.fixture
def coordinator(create_container):
    container = create_container(
        Config(f"test_coordinator-{_random_string()}", "zookeeper")
    )
    host = container.ip() + ":2181"

    with zookeeper_coordinator(hosts={host}) as zk:
        yield zk


def _notify(
    coordinator: Coordinator,
    last_idx: datetime = datetime(2020, 1, 1),
    version: int = 10,
):
    node = Node(host="dummyhost", directory="dummydir",)
    coordinator.notify("fakename", node, version, last_idx)


def _request(
    name: str = "fakename",
    last_idx: datetime = datetime(2020, 1, 1),
    version: int = 10,
):
    return name, last_idx, version


def _resource(last_idx=datetime(2020, 1, 1), version=10):
    node = Node(host="dummyhost", directory="dummydir",)
    return Resource(nodes=[node], version=version, last_idx=last_idx)


def _random_string():
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )
