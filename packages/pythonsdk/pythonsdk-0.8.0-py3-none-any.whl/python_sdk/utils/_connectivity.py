import contextlib
import socket

_CLOUDFLARE_DNS_IPV4 = "1.1.1.1"
_DNS_PORT = 53


def is_connected() -> bool:
    with contextlib.suppress(OSError):
        socket.create_connection((_CLOUDFLARE_DNS_IPV4, _DNS_PORT))
        return True
    return False
