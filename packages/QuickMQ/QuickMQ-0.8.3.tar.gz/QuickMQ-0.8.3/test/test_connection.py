import json
import subprocess
import threading

import pytest

import quickmq
from quickmq.api import _CURRENT_SESSION
from quickmq.connection import ConnectionPool, ReconnectConnection, ServerConnection
from quickmq.exceptions import NotAuthenticatedError


@pytest.fixture
def disconnect_rabbitmq():
    def disconnect():
        stop_proc = subprocess.Popen(["make", "stop_rabbitmq"])
        stop_proc.wait()

    return disconnect


@pytest.fixture
def restart_rabbitmq():
    def reconnect():
        start_proc = subprocess.Popen(["make", "start_rabbitmq"])
        start_proc.wait()

    return reconnect


def test_connection_creation():
    new_connect = ReconnectConnection("localhost")
    assert new_connect.vhost == "/"
    assert new_connect.port == quickmq.configure("rabbitmq_port")
    new_connect.close()


def test_incorrect_credentials():
    with pytest.raises(NotAuthenticatedError):
        quickmq.connect("localhost", auth=("wrong_user", "wrong_password"))


def test_wrong_server():
    with pytest.raises(ConnectionError):
        quickmq.connect("not_host")


def test_callback():
    evnt = threading.Event()

    def callback():
        evnt.set()
    connection = ServerConnection('localhost')
    connection.start()
    connection.add_callback(callback)
    evnt.wait()


def test_reconnect(disconnect_rabbitmq, restart_rabbitmq):
    quickmq.connect("localhost")
    assert len(_CURRENT_SESSION.pool.connections) == 1
    disconnect_rabbitmq()
    restart_rabbitmq()
    assert len(_CURRENT_SESSION.pool.connections) == 1
    quickmq.disconnect()


@pytest.mark.parametrize("exchange", ["amq.fanout"])
def pub_after_disconnect(create_listener, disconnect_rabbitmq, restart_rabbitmq):
    msg = "Hello World!"
    quickmq.connect("localhost")
    disconnect_rabbitmq()
    quickmq.publish(msg, exchange="amq.fanout")
    restart_rabbitmq()
    rcvd_bytes = create_listener.get_message(block=True)
    assert json.loads(rcvd_bytes) == msg
    quickmq.disconnect()


def test_connection_pool():
    event = threading.Event()

    def callbck(_connection):
        event.set()

    pool = ConnectionPool()
    con = ReconnectConnection("localhost")
    con.start()
    pool.add_connection(con)
    assert len(pool) == 1
    pool.add_callback(callbck)
    event.wait(2.0)
    assert event.is_set()
    pool.remove_all()


@pytest.mark.skip
def test_close_on_error(disconnect_rabbitmq, restart_rabbitmq, capsys):
    con = ServerConnection("localhost")
    con.start()
    assert con.connected
    try:
        disconnect_rabbitmq()
        assert not con.connected
    finally:
        restart_rabbitmq()
        assert not con.connected
