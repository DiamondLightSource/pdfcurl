import subprocess
import sys

from pdfcurl import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "pdfcurl", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
