import contextlib
import dataclasses
import pathlib
import typing


@dataclasses.dataclass
class FileStats:
    file: pathlib.Path
    exists_after: bool = False
    exists_before: bool = False
    contents_after: bytes = b""
    contents_before: bytes = b""

    @property
    def has_changed(self) -> bool:
        return self.contents_after != self.contents_before


@contextlib.contextmanager
def file_watcher(file: pathlib.Path) -> typing.Generator[FileStats, None, None]:
    results = FileStats(file=file)

    try:
        if file.exists():
            results.exists_before = True
            results.contents_before = file.read_bytes()
        yield results

    finally:
        if file.exists():
            results.exists_after = True
            results.contents_after = file.read_bytes()
