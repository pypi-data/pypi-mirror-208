import hashlib
import pathlib

_BUFFER_SIZE = 65536  # 64kb


def get_file_sha1(file: pathlib.Path) -> str:
    sha1 = hashlib.sha1()

    with open(file, "rb") as f:
        while True:
            if data := f.read(_BUFFER_SIZE):
                sha1.update(data)

            else:
                break
    return sha1.hexdigest()
