import os
import sys
from dataclasses import dataclass
from typing import TextIO

from app.core.exec_cache import check_executable_exists


@dataclass(frozen=True)
class ShellContext:
    stdout_target: TextIO
    stderr_target: TextIO
    exec_cache: dict[str, str]


def handle_exit(args: list[str], context: ShellContext) -> None:
    sys.exit(0)


def handle_echo(args: list[str] | None, context: ShellContext) -> None:
    # empty raw string from cmd would be None, which should be ok to print newline
    if args is None:
        print(file=context.stdout_target)
    else:
        print(" ".join(args), file=context.stdout_target)


def handle_type(args: list[str], context: ShellContext) -> None:
    # currently will not handle multiple args or missing args, just assume the good case
    if args[0] in BUILTIN_COMMANDS or args[0] == "exit":
        print(f"{args[0]} is a shell builtin", file=context.stdout_target)
        return
    exe_exist, exe_path = check_executable_exists(
        args[0],
        context.exec_cache,
    )
    if exe_exist:
        print(f"{args[0]} is {exe_path}", file=context.stdout_target)
    else:
        print(f"{args[0]}: not found", file=context.stderr_target)


def handle_pwd(args: list[str], context: ShellContext) -> None:
    print(os.getcwd(), file=context.stdout_target)


def handle_cd(args: list[str], context: ShellContext) -> None:
    expanded_path = os.path.expanduser(args[0])
    try:
        os.chdir(expanded_path)
    except FileNotFoundError:
        print(f"cd: {expanded_path}: No such file or directory", file=context.stderr_target)


BUILTIN_COMMANDS = {
    "exit": handle_exit,
    "echo": handle_echo,
    "type": handle_type,
    "pwd": handle_pwd,
    "cd": handle_cd,
}
