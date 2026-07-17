import socket

import pytest
from hypothesis import settings

settings.register_profile("ci", max_examples=40, derandomize=True, deadline=1000)
settings.load_profile("ci")


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deny common direct Python socket connection and datagram APIs.

    This does not provide subprocess, native-extension, container, or operating-system-level
    network isolation.
    """

    def deny(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access is forbidden in tests")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket.socket, "sendto", deny)
    if hasattr(socket.socket, "sendmsg"):
        monkeypatch.setattr(socket.socket, "sendmsg", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
