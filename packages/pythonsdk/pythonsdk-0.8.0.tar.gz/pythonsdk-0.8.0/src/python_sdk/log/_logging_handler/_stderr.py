import logging
import sys


class STDErr(logging.StreamHandler):
    TYPE: str = "STDERR"

    def __init__(self) -> None:
        super().__init__(stream=sys.stderr)
