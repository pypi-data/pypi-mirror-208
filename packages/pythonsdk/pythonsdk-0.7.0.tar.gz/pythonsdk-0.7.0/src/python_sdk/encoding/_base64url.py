import base64


def b64url_encode(s: bytes) -> bytes:
    return base64.urlsafe_b64encode(s=s).rstrip(b"=")


# TODO: add validation
def b64url_decode(s: bytes | str) -> bytes:
    if isinstance(s, bytes):
        return _b64url_decode_bytes(s)
    return _b64url_decode_string(s)


def _b64url_decode_bytes(s: bytes) -> bytes:
    padding = (len(s) % 4) * b"="
    padded = s + padding
    return base64.urlsafe_b64decode(padded)


def _b64url_decode_string(s: str) -> bytes:
    padding = (len(s) % 4) * "="
    padded = s + padding
    return base64.urlsafe_b64decode(padded)
