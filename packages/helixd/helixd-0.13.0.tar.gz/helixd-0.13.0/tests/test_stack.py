import pytest

from helixd import ResourceType, Client

CREATE, START, STOP, DELETE = "create", "start", "stop", "delete"


@pytest.fixture
def mock_client(monkeypatch):
    """
    Monkeypatches the client to mock the functions directly interacting with the LXD API.
    Replaces them by a log system to trace the calls.

    :return: the log list
    """

    log = []

    def build_mock(string):
        def mock(_, *args):
            log.append((string, *args))

        return mock

    for function in [CREATE, START, STOP, DELETE]:
        monkeypatch.setattr(Client, function, build_mock(function))

    return log


STORAGE_POOL_CONFIG = {"name": "test-storage-pool", "driver": "dir"}
NETWORK_CONFIG = {"name": "test-network"}
PROFILE_CONFIG = {"name": "test-profile"}
INSTANCE_A_CONFIG = {"name": "test-instance-a", "source": {"type": "none"}}
INSTANCE_B_CONFIG = {"name": "test-instance-b", "source": {"type": "none"}}

LXD_STACK = {
    "storage-pools": [STORAGE_POOL_CONFIG],
    "networks": [NETWORK_CONFIG],
    "profiles": [PROFILE_CONFIG],
    "instances": [INSTANCE_A_CONFIG, INSTANCE_B_CONFIG]
}


def test_create_stack(client, mock_client):
    client.create_stack(LXD_STACK)

    assert mock_client == [(CREATE, STORAGE_POOL_CONFIG, ResourceType.STORAGE_POOLS),
                           (CREATE, NETWORK_CONFIG, ResourceType.NETWORKS),
                           (CREATE, PROFILE_CONFIG, ResourceType.PROFILES),
                           (CREATE, INSTANCE_A_CONFIG, ResourceType.INSTANCES),
                           (CREATE, INSTANCE_B_CONFIG, ResourceType.INSTANCES)]


def test_start_stack(client, mock_client):
    client.start_stack(LXD_STACK)

    assert mock_client == [(START, INSTANCE_A_CONFIG, ResourceType.INSTANCES),
                           (START, INSTANCE_B_CONFIG, ResourceType.INSTANCES)]


def test_stop_stack(client, mock_client):
    client.stop_stack(LXD_STACK)

    assert mock_client == [(STOP, INSTANCE_A_CONFIG, ResourceType.INSTANCES),
                           (STOP, INSTANCE_B_CONFIG, ResourceType.INSTANCES)]


def test_delete_stack(client, mock_client):
    client.delete_stack(LXD_STACK)

    assert mock_client == [(DELETE, INSTANCE_A_CONFIG, ResourceType.INSTANCES),
                           (DELETE, INSTANCE_B_CONFIG, ResourceType.INSTANCES),
                           (DELETE, PROFILE_CONFIG, ResourceType.PROFILES),
                           (DELETE, NETWORK_CONFIG, ResourceType.NETWORKS),
                           (DELETE, STORAGE_POOL_CONFIG, ResourceType.STORAGE_POOLS)]


def test_empty(client, mock_client):
    client.create_stack({})
    client.start_stack({})
    client.stop_stack({})
    client.delete_stack({})

    assert mock_client == []
