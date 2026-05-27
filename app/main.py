import os
import shlex
import subprocess
import sys
from typing import TextIO


def handle_echo(args: list[str] | None, stream: TextIO) -> None:
    # empty raw string from cmd would be None, which should be ok to print newline
    if args is None:
        print(file=stream)
    else:
        print(" ".join(args), file=stream)


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


def handle_type(args: list[str], stream: TextIO) -> None:
    # currently will not handle multiple args or missing args, just assume the good case
    if args[0] in BUILTIN_COMMANDS or args[0] == "exit":
        print(f"{args[0]} is a shell builtin", file=stream)
        return
    exe_exist, exe_path = check_executable_exists(args[0])
    if exe_exist:
        print(f"{args[0]} is {exe_path}", file=stream)
    else:
        print(f"{args[0]}: not found", file=stream)


def handle_pwd(args: list[str], stream: TextIO) -> None:
    print(os.getcwd(), file=stream)


def handle_cd(args: list[str], stream: TextIO) -> None:
    expanded_path = os.path.expanduser(args[0])
    try:
        os.chdir(expanded_path)
    except FileNotFoundError:
        print(f"cd: {expanded_path}: No such file or directory", file=stream)


def execute_command(command: str, command_args: list[str], output_target: TextIO) -> None:
    # handle executable
    exe_exist, exe_path = check_executable_exists(command)
    if exe_exist:
        subprocess.run(
            [os.path.basename(exe_path)] + command_args,
            stdout=output_target,
            # stderr=output_target,
        )
        return

    # handle builtins
    if command in BUILTIN_COMMANDS:
        handler = BUILTIN_COMMANDS[command]
        handler(command_args, output_target)
        return
    # handle unknown command
    else:
        print(f"{command}: command not found", file=output_target)


def handle_redirection(redirection_op: str | None, file: str | None) -> TextIO:
    if redirection_op is None or file is None:
        return sys.stdout
    mode = "w" if redirection_op in {">", "1>", "!>", "2>"} else "a"
    return open(file, mode, encoding="utf-8")


BUILTIN_COMMANDS = {"echo": handle_echo, "type": handle_type, "pwd": handle_pwd, "cd": handle_cd}
REDIRECTION_OPERATORS = {">", ">>", "1>", "1>>", "!>", "!>>", "2>", "2>>"}


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()

        # handle exit
        if command == "exit":
            break

        command_split = shlex.split(command)
        command = command_split[0]

        # Check if there's redirection
        redirection_op = None
        file = None
        if len(command_split) >= 3:
            # possible redirection, check the last two tokens
            # TODO: stdout/stderr chain redirection, e.g. cmd > out.txt 2>&1
            if command_split[-2] in REDIRECTION_OPERATORS:
                redirection_op = command_split[-2]
                file = command_split[-1]
                command_args = command_split[1:-2]
            else:
                command_args = command_split[1:]
        else:
            command_args = command_split[1:]

        output_target = handle_redirection(redirection_op, file)

        execute_command(command, command_args, output_target)

        if output_target is not sys.stdout:
            output_target.close()


if __name__ == "__main__":
    main()
