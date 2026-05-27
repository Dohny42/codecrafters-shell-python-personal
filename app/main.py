import os
import shlex
import subprocess
import sys
from typing import TextIO


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


def execute_command(
    command: str, command_args: list[str], stdout_target: TextIO, stderr_target: TextIO
) -> None:
    # handle executable
    exe_exist, exe_path = check_executable_exists(command)
    if exe_exist:
        subprocess.run(
            [os.path.basename(exe_path)] + command_args,
            stdout=stdout_target,
            stderr=stderr_target,
        )
        return

    # handle builtins
    if command in BUILTIN_COMMANDS:
        handler = BUILTIN_COMMANDS[command]
        handler(command_args, stdout_target, stderr_target)
        return
    # handle unknown command
    else:
        print(f"{command}: command not found", file=stderr_target)


def handle_redirection(
    stdout_op: str | None, stdout_file: str | None, stderr_op: str | None, stderr_file: str | None
) -> tuple[TextIO, TextIO]:
    if stdout_op is None or stdout_file is None:
        stdout_target = sys.stdout
    else:
        mode = "w" if stdout_op in {">", "1>"} else "a"  # ! explicit check for "a" would be safer
        stdout_target = open(stdout_file, mode, encoding="utf-8")

    if stderr_op is None or stderr_file is None:
        stderr_target = sys.stderr
    else:
        mode = "w" if stderr_op in {"!>", "2>"} else "a"
        stderr_target = open(stderr_file, mode, encoding="utf-8")

    return stdout_target, stderr_target


BUILTIN_COMMANDS = {"echo": handle_echo, "type": handle_type, "pwd": handle_pwd, "cd": handle_cd}
STDOUT_REDIRECTION_OPERATORS = {">", ">>", "1>", "1>>"}
STDERR_REDIRECTION_OPERATORS = {"!>", "!>>", "2>", "2>>"}


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()

        # handle exit
        if command == "exit":
            break

        command_split = shlex.split(command)
        command = command_split[0]

        # redirection check (for now assume: cmd [args] [stdout_op file] [stderr_op file])
        # TODO: try to implement referenced file descriptor redirect (e.g. cmd > out.txt 2>&1)
        stdout_op = None
        stderr_op = None
        stdout_file = None
        stderr_file = None
        command_args = command_split[1:]  # default case

        # handle redirection for all combinations
        # loop from the end to parse redirection operators and files
        i = len(command_split) - 2
        while i >= 1:
            op = command_split[i]
            file = command_split[i + 1] if i + 1 < len(command_split) else None
            if op in STDOUT_REDIRECTION_OPERATORS and stdout_op is None and file is not None:
                stdout_op = op
                stdout_file = file
                command_args = command_args[: i - 1]
                i -= 2
                continue
            elif op in STDERR_REDIRECTION_OPERATORS and stderr_op is None and file is not None:
                stderr_op = op
                stderr_file = file
                command_args = command_args[: i - 1]
                i -= 2
                continue
            i -= 1

        stdout_target, stderr_target = handle_redirection(
            stdout_op, stdout_file, stderr_op, stderr_file
        )

        execute_command(command, command_args, stdout_target, stderr_target)

        if stdout_target is not sys.stdout:
            stdout_target.close()
        if stderr_target is not sys.stderr:
            stderr_target.close()


if __name__ == "__main__":
    main()
