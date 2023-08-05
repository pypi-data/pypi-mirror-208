import logging
import sys


class STDOut(logging.StreamHandler):
    TYPE: str = "STDOUT"

    def __init__(self) -> None:
        super().__init__(stream=sys.stdout)
