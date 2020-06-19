from datetime import datetime
from pathlib import Path

import pandas as pd  # type: ignore
import pytest  # type: ignore
from fastapi.testclient import TestClient  # type: ignore

from pullframe.exceptions import AllSyncFailed, NoResourceAvailable
from pullframe.persist import PERSIST
from pullframe.pullframe import _PullFrame
from pullframe.sender import app  # type: ignore
from pullframe.types import CacheFormat, Demand, Node, Resource

from .utils import sample_df, to_df

_ = sample_df
client = TestClient(app)


def test_sync_raise_error_if_no_host_available(mocker):
    persist = mocker.stub(name="dummy_persist")
    persist.directory = Path()
    persist.format = lambda: CacheFormat.PYTABLES
    persist.version = lambda _: None

    remote = mocker.stub(name="stub_remote_source")
    remote.available = lambda _x, _y, _z: None
    pf = _PullFrame(persist, remote, client, 0.0)

    with pytest.raises(NoResourceAvailable) as e:
        pf._sync(_dummy_demand())
    assert str(e.value).startswith("No host available for the demand")


def test_sync_raise_error_if_all_sync_failed(mocker):
    persist = mocker.stub(name="stub_persist")
    persist.directory = Path()
    persist.format = lambda: CacheFormat.PYTABLES
    persist.version = lambda _: 0
    persist.exists = lambda _: True

    remote = mocker.stub(name="stub_remote_source")
    node = Node(directory="", host="localhost")
    remote.available = lambda _x, _y, _z: Resource(
        nodes=[node], version=0, last_idx=datetime(2020, 1, 1)
    )

    client = mocker.stub(name="stub_client")
    client.post = lambda _: 1 / 0
    pf = _PullFrame(persist, remote, client, 0.0)

    with pytest.raises(AllSyncFailed) as e:
        pf._sync(_dummy_demand())
    assert str(e.value).startswith("All sync failed")


@pytest.mark.parametrize("create_persist", PERSIST.values())
def test_sync_from_node(tmpdir, create_persist, mocker):
    df = sample_df()
    temp_directory = Path(tmpdir)

    local_dir = temp_directory / "local"
    remote_dir = temp_directory / "remote"

    local_persist = create_persist.on(local_dir)
    remote_persist = create_persist.on(remote_dir)

    remote_persist.save("fake", df)

    node = Node(directory=str(remote_dir), host="localhost")
    resource = Resource(nodes=[node], version=0, last_idx=df.index[-1])
    remote = mocker.stub(name="stub_remote_source")
    remote.available = lambda _x, _y, _z: resource

    pf = _PullFrame(local_persist, remote, client, 60.0)
    loaded = pf.load("fake")
    pd.testing.assert_frame_equal(loaded, df)


@pytest.mark.parametrize("create_persist", PERSIST.values())
def test_sync_update_from_node(tmpdir, create_persist, mocker):
    local_df = to_df(
        [
            "          , 1 , 2 ",
            "2020-01-01,1.0,2.0",
            "2020-01-02,1.0,2.0",
            "2020-01-05,1.0,2.0",
        ]
    )

    remote_df = to_df(
        [
            "          , 1 , 2 ",
            "2020-01-01,1.0,2.0",
            "2020-01-02,1.0,2.0",
            "2020-01-05,2.0,3.0",  # version should be different in real
            "2020-01-06,3.0,3.0",
        ]
    )

    expected = to_df(
        [
            "          , 1 , 2 ",
            "2020-01-01,1.0,2.0",
            "2020-01-02,1.0,2.0",
            "2020-01-05,1.0,2.0",
            "2020-01-06,3.0,3.0",
        ]
    )

    temp_directory = Path(tmpdir)

    local_dir = temp_directory / "local"
    local_persist = create_persist.on(local_dir)

    remote_dir = temp_directory / "remote"
    remote_persist = create_persist.on(remote_dir)
    remote_persist.save("fake", remote_df)

    index = remote_df.index
    node = Node(directory=str(remote_dir), host="localhost")
    resource = Resource(nodes=[node], version=0, last_idx=index[-1])
    remote = mocker.stub(name="stub_remote_source")
    remote.available = lambda _x, _y, _z: resource
    remote.version = lambda _: 0

    pf = _PullFrame(local_persist, remote, client, 60.0)
    pf.save("fake", local_df)

    loaded = pf.load("fake", None, datetime(2020, 1, 6))
    pd.testing.assert_frame_equal(loaded, expected)


def _dummy_demand() -> Demand:
    return Demand(
        cache_format=CacheFormat.PYTABLES,
        name="fake",
        start=datetime.now(),
        end=datetime.now(),
    )
