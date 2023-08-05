import shutil
import subprocess


class TestCodeFormatting:
    def test_code_is_formatted(self) -> None:
        black_is_installed: bool = bool(shutil.which("black"))
        assert black_is_installed, """This test requires black (black.readthedocs.io) to be installed.
You can either:
    a. Install testing dependencies using `pip install python-sdk[testing]`
    b. Install cli dependencies using `pip install python-sdk[cli]`
    c. Install black directly using `pip install black`
"""

        code_is_formatted: bool = subprocess.run(["black", "--line-length", "120", "--check", "."]).returncode == 0
        assert code_is_formatted, """black has found code that hasn't been correctly formatted. 
To see which files are not formatted, check the test output in stdout/stderr.
To automatically fix any code formatting issues, run `black --line-length 120 .`"""


class TestImportFormatting:
    def test_imports_are_formatted(self) -> None:
        isort_is_installed: bool = bool(shutil.which("isort"))
        assert isort_is_installed, """This test requires isort (pycqa.github.io/isort) to be installed.
        You can either:
            a. Install testing dependencies using `pip install python-sdk[testing]`
            b. Install cli dependencies using `pip install python-sdk[cli]`
            c. Install isort directly using `pip install isort`
        """

        imports_are_formatted: bool = (
            subprocess.run(
                [
                    "isort",
                    "--line-length",
                    "120",
                    "--force-single-line-imports",
                    "--force-sort-within-sections",
                    "--profile",
                    "black",
                    "--check",
                    ".",
                ]
            ).returncode
            == 0
        )
        assert imports_are_formatted, """isort has found incorrectly sorted imports.
To see which files contain incorrectly sorted inputs, check the test output in stdout/stderr.
To automatically fix any import sorting issues, run `isort --line-length 120 --force-single-line-imports --force-sort-within-sections --profile black .`"""


class TestTyping:
    def test_typing(self) -> None:
        mypy_is_installed: bool = bool(shutil.which("mypy"))
        assert mypy_is_installed, """This test requires mypy (mypy.readthedocs.io) to be installed.
        You can either:
            a. Install testing dependencies using `pip install python-sdk[testing]`
            b. Install mypy directly using `pip install mypy`
        """

        code_is_typed_correctly: bool = subprocess.run(["mypy", "--strict", "--warn-unreachable", "."]).returncode == 0
        assert code_is_typed_correctly, """Mypy has identified typing issues in the code.
To see the identified issues, check the test output in stdout/stderr."""
