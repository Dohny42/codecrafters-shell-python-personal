import os
import shlex
import subprocess
import sys
from typing import TextIO

from app.core.builtins_cmd import BUILTIN_COMMANDS, check_executable_exists
from app.core.cli import handle_redirection, parse_redirection_cli, setup_autocompletion


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


def main():
    setup_autocompletion()

    while True:
        sys.stdout.write("$ ")
        command = input()

        command_split = shlex.split(command)
        command = command_split[0]

        command_args, stdout_op, stdout_file, stderr_op, stderr_file = parse_redirection_cli(
            command_split
        )

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
