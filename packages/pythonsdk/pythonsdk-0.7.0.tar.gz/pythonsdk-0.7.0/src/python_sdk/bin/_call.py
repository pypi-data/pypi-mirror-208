import dataclasses
import functools
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import typing


class BinaryNotInstalled(Exception):
    message: str
    binary: str

    def __init__(self, binary: str, message: str = "Binary not installed.") -> None:
        super().__init__(message, binary)
        self.message = message
        self.binary = binary

    def __str__(self) -> str:
        return self.binary


class CalledProcessError(Exception):
    message: str
    output: str
    exit_code: int

    def __init__(self, output: str, exit_code: int, message: str = "Called process failure.") -> None:
        super().__init__(message, output, exit_code)
        self.message = message
        self.output = output
        self.exit_code = exit_code

    def __str__(self) -> str:
        return f"{self.exit_code}\n{self.output}"


def call(
    *args: typing.Any,
    sudo: bool = False,
    sudo_binary: str = "sudo",
    environment_variables: dict[str, str] | None = None,
    stream_output: bool = False,
    stream_printer: typing.Callable[[str], None] = functools.partial(print, end="", file=sys.stderr, flush=True),
    force_arch: typing.Literal["amd64", "x86_64"] | None = None,
    stdin: typing.TextIO | None = None,
    cwd: pathlib.Path | None = None,
) -> str:
    """
    Raises:
        BinaryNotInstalled: binary not installed
    """
    env = environment_variables if environment_variables is not None else dict(os.environ)
    arguments = [str(argument) for argument in args]

    if args[0] == "arch":
        # Caller supplied arch in args, instead of the force_arch argument. Let's pull it out.
        force_arch = args[1]
        arguments = list(args[2:])

    if args[0].endswith("sudo"):
        # Caller supplied sudo in args, instead of the sudo argument. Let's pull it out.
        sudo = True
        sudo_binary = args[0]
        arguments = list(args[1:])

    if sudo:
        path_to_sudo = shutil.which(sudo_binary)
        if not path_to_sudo:
            raise BinaryNotInstalled(binary=sudo_binary)
        sudo_full_path = pathlib.Path(path_to_sudo)
        if not sudo_full_path.exists():
            raise BinaryNotInstalled(binary=str(sudo_full_path))
        if not os.access(sudo_full_path, os.EX_OK):
            raise PermissionError(f"{sudo_full_path} is not executable.")

    binary: str = args[0]
    arguments = list(args[1:])

    path_to_binary = shutil.which(binary)
    if not path_to_binary:
        raise BinaryNotInstalled(binary=binary)
    binary_full_path = pathlib.Path(path_to_binary)
    if not binary_full_path.exists():
        raise BinaryNotInstalled(binary=str(binary_full_path))
    if not os.access(binary_full_path, os.EX_OK):
        raise PermissionError(f"{binary_full_path} is not executable.")

    command: list[str | pathlib.Path] = [binary_full_path] + arguments
    if sudo:
        command.insert(0, sudo_full_path)
    if force_arch:
        command.insert(0, "arch")
        command.insert(1, f"-{force_arch}")

    logging.debug(f"Calling command. binary={binary_full_path} {command=}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=stdin,
        text=True,
        env=env,
        cwd=cwd,
    )

    output = ""
    for char in iter(functools.partial(process.stdout.read, 1), ""):  # type: ignore
        output += char
        if stream_output:
            stream_printer(char)

    logging.debug(
        f"Called command output. binary={binary_full_path} {command=} {output=} exit_code={process.returncode}"
    )

    process.wait()

    if process.returncode:
        raise CalledProcessError(output=output, exit_code=process.returncode)

    return output.strip()
