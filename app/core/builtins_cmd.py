import os
import sys
from typing import TextIO


def handle_exit(args: list[str], stdout: TextIO, stderr: TextIO) -> None:
    sys.exit(0)


def handle_echo(args: list[str] | None, stdout: TextIO, stderr: TextIO) -> None:
    # empty raw string from cmd would be None, which should be ok to print newline
    if args is None:
        print(file=stdout)
    else:
        print(" ".join(args), file=stdout)


def check_executable_exists(command: str) -> tuple[bool, str]:
    for path in os.getenv("PATH", "").split(os.pathsep):
        executable_path = os.path.join(path, command)
        if (
            os.path.isfile(executable_path)
            and os.access(executable_path, os.X_OK)
            and command == os.path.basename(executable_path)
        ):
            return True, executable_path
        else:
            continue
    return False, ""


def handle_type(args: list[str], stdout: TextIO, stderr: TextIO) -> None:
    # currently will not handle multiple args or missing args, just assume the good case
    if args[0] in BUILTIN_COMMANDS or args[0] == "exit":
        print(f"{args[0]} is a shell builtin", file=stdout)
        return
    exe_exist, exe_path = check_executable_exists(args[0])
    if exe_exist:
        print(f"{args[0]} is {exe_path}", file=stdout)
    else:
        print(f"{args[0]}: not found", file=stderr)


def handle_pwd(args: list[str], stdout: TextIO, stderr: TextIO) -> None:
    print(os.getcwd(), file=stdout)


def handle_cd(args: list[str], stdout: TextIO, stderr: TextIO) -> None:
    expanded_path = os.path.expanduser(args[0])
    try:
        os.chdir(expanded_path)
    except FileNotFoundError:
        print(f"cd: {expanded_path}: No such file or directory", file=stderr)


BUILTIN_COMMANDS = {
    "exit": handle_exit,
    "echo": handle_echo,
    "type": handle_type,
    "pwd": handle_pwd,
    "cd": handle_cd,
}
