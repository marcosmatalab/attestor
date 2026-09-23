"""Run the test suite with outbound network connections blocked.

The README claims the whole suite runs with no network. That claim is easy to make and
easy to break: one test that quietly reaches a real timestamping authority would pass on
a developer machine, pass in CI, and fail for the person who cloned the repository on a
train - and the failure would look like a bug in the ledger rather than a broken promise.

So this makes the claim executable. Every connection to anything that is not loopback
raises, and then pytest runs normally:

    python scripts/run_offline.py

Loopback is deliberately still allowed. asyncio on Windows wakes its event loop through a
local socket pair, and `TestClient` drives the ASGI app through it, so forbidding
127.0.0.1 would not be a stricter test - it would be a test of asyncio's internals. The
claim is that nothing leaves the machine, and that is exactly what is enforced here.
"""

import socket
import sys
from typing import Any

import pytest

LOOPBACK = frozenset({"127.0.0.1", "::1", "localhost", ""})

_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex
_real_create_connection = socket.create_connection


def host_of(address: Any) -> str:
    return str(address[0]) if isinstance(address, tuple) and address else ""


def refuse(address: Any) -> None:
    host = host_of(address)
    if host not in LOOPBACK:
        raise OSError(
            f"outbound connection to {host} refused: this run is offline by construction. "
            "A test that needs the network is a test that will fail on a clean clone."
        )


def guarded_connect(self: socket.socket, address: Any) -> None:
    refuse(address)
    _real_connect(self, address)


def guarded_connect_ex(self: socket.socket, address: Any) -> int:
    refuse(address)
    return int(_real_connect_ex(self, address))


def guarded_create_connection(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
    refuse(address)
    return _real_create_connection(address, *args, **kwargs)


def main(argv: list[str]) -> int:
    socket.socket.connect = guarded_connect  # type: ignore[method-assign]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[method-assign]
    socket.create_connection = guarded_create_connection  # type: ignore[assignment]
    print("[offline] outbound connections are blocked; loopback is allowed", flush=True)
    return int(pytest.main(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
