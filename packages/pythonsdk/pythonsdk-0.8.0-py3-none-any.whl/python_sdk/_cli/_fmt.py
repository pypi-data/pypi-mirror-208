import sys

from python_sdk import bin


def fmt(target: str, check: bool) -> None:
    if check:
        try:
            bin.call("black", "--line-length", "120", "--check", target, stream_output=True)
        except bin.CalledProcessError as e:
            sys.exit(e.exit_code)

        try:
            bin.call(
                "isort",
                "--line-length",
                "120",
                "--force-single-line-imports",
                "--force-sort-within-sections",
                "--profile",
                "black",
                "--check",
                target,
                stream_output=True,
            )
        except bin.CalledProcessError as e:
            sys.exit(e.exit_code)

    else:
        try:
            bin.call("black", "--line-length", "120", target, stream_output=True)
        except bin.CalledProcessError as e:
            sys.exit(e.exit_code)

        try:
            bin.call(
                "isort",
                "--line-length",
                "120",
                "--force-single-line-imports",
                "--force-sort-within-sections",
                "--profile",
                "black",
                target,
                stream_output=True,
            )
        except bin.CalledProcessError as e:
            sys.exit(e.exit_code)
