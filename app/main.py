import shlex
import sys

from app.core.cli import handle_redirection, parse_redirection_cli, setup_autocompletion
from app.core.exec_cache import get_exec_cache
from app.core.execute import execute_command


def main():
    exec_cache = get_exec_cache()

    setup_autocompletion(exec_cache)

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

        execute_command(command, command_args, stdout_target, stderr_target, exec_cache)

        if stdout_target is not sys.stdout:
            stdout_target.close()
        if stderr_target is not sys.stderr:
            stderr_target.close()


if __name__ == "__main__":
    main()
