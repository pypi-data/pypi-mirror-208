import kivalu
import pytest

import helixd


@pytest.fixture(scope="module")
def server():
    with kivalu.TestServer() as server:
        yield server


LXD_STACK = """
---
storage-pools:
- name: test-storage-pool
  driver: dir

volumes:
- name: test-volume
  parent: test-storage-pool

networks:
- name: test-network
  config:
    ipv4.address: 10.42.254.1/24
    ipv4.nat: true
    ipv6.address: none
    dns.mode: dynamic
    dns.domain: test

profiles:
- name: test-profile
  devices:
    root:
      type: disk
      path: /
      pool: test-storage-pool
    eth0:
      type: nic
      nictype: bridged
      parent: test-network

instances:
- name: test-instance
  profiles:
  - test-profile
  source:
    type: image
    mode: pull
    server: https://images.linuxcontainers.org
    protocol: simplestreams
    alias: ubuntu/20.04
  devices:
    mnt:
      type: disk
      path: /mnt
      pool: test-storage-pool
      source: test-volume
""".lstrip()

OK_OUTPUT1 = """
checking existence /1.0/storage-pools/test-storage-pool
creating /1.0/storage-pools/test-storage-pool
checking existence /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
creating /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
checking existence /1.0/networks/test-network
creating /1.0/networks/test-network
checking existence /1.0/profiles/test-profile
creating /1.0/profiles/test-profile
checking existence /1.0/instances/test-instance
creating /1.0/instances/test-instance
""".lstrip()

OK_OUTPUT2 = """
checking status /1.0/instances/test-instance
starting /1.0/instances/test-instance
""".lstrip()

OK_OUTPUT3 = """
checking existence /1.0/instances/test-instance
checking status /1.0/instances/test-instance
stopping /1.0/instances/test-instance
""".lstrip()

OK_OUTPUT4 = """
checking existence /1.0/instances/test-instance
deleting /1.0/instances/test-instance
checking existence /1.0/profiles/test-profile
deleting /1.0/profiles/test-profile
checking existence /1.0/networks/test-network
deleting /1.0/networks/test-network
checking existence /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
deleting /1.0/storage-pools/test-storage-pool/volumes/custom/test-volume
checking existence /1.0/storage-pools/test-storage-pool
deleting /1.0/storage-pools/test-storage-pool
""".lstrip()


def test_ok(server, capsys):
    server.data = {"lxd-stack": LXD_STACK}

    helixd.main("create -u http://localhost:8000".split())
    assert capsys.readouterr().out == OK_OUTPUT1

    helixd.main("start -u http://localhost:8000".split())
    assert capsys.readouterr().out == OK_OUTPUT2

    helixd.main("stop -u http://localhost:8000".split())
    assert capsys.readouterr().out == OK_OUTPUT3

    helixd.main("delete -u http://localhost:8000".split())
    assert capsys.readouterr().out == OK_OUTPUT4


def test_ko_key_not_found(server, capsys):
    server.data = {}

    with pytest.raises(SystemExit) as e:
        helixd.main("create -u http://localhost:8000".split())
    assert e.value.code == 1
    assert capsys.readouterr().out == "key 'lxd-stack' not found on server http://localhost:8000\n"


def test_ko_not_a_stack(server, capsys):
    server.data = {"lxd-stack": "not a stack"}

    with pytest.raises(SystemExit) as e:
        helixd.main("create -u http://localhost:8000".split())
    assert e.value.code == 1
    assert capsys.readouterr().out == "key 'lxd-stack' on server http://localhost:8000 is not a proper yaml or json dictionary\n"
