import subprocess
from typing import NamedTuple


class Command(NamedTuple):
    stdout: bytes
    stderr: bytes
    return_code: int


def remove_last_line_break(data: str) -> str:
    last_line_break = data.rfind("\n")
    if last_line_break == -1:
        return data
    else:
        return data[:last_line_break]


def _decode(data: bytes) -> str:
    data = data.decode("utf-8")
    return remove_last_line_break(data=data)


def run_command(command: str) -> Command:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    return_code = process.returncode
    stdout = _decode(data=stdout)
    stderr = _decode(data=stderr)
    return Command(
        stdout,
        stderr,
        return_code,
    )
