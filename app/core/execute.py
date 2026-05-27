import os
import subprocess
from typing import TextIO

from app.core.builtins_cmd import BUILTIN_COMMANDS, ShellContext
from app.core.exec_cache import check_executable_exists


def execute_command(
    command: str,
    command_args: list[str],
    stdout_target: TextIO,
    stderr_target: TextIO,
    exec_cache: dict[str, str],
) -> None:
    # handle executable
    exe_exist, exe_path = check_executable_exists(command, exec_cache)
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
        context = ShellContext(
            stdout_target=stdout_target,
            stderr_target=stderr_target,
            exec_cache=exec_cache,
        )
        handler(command_args, context)
        return
    # handle unknown command
    else:
        print(f"{command}: command not found", file=stderr_target)
