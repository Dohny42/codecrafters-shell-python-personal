import readline
import sys
from typing import TextIO

from app.core.builtins_cmd import BUILTIN_COMMANDS

STDOUT_REDIRECTION_OPERATORS = {">", ">>", "1>", "1>>"}
STDERR_REDIRECTION_OPERATORS = {"!>", "!>>", "2>", "2>>"}


def parse_redirection_cli(
    command_split: list[str],
) -> tuple[list[str], str | None, str | None, str | None, str | None]:
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

    return command_args, stdout_op, stdout_file, stderr_op, stderr_file


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


def make_autocomplete(exec_cache: dict[str, str]):
    last_prefix = ""
    tab_count = 0

    def autocomplete(text: str, state: int) -> str | None:
        nonlocal last_prefix, tab_count
        matches = [cmd for cmd in BUILTIN_COMMANDS.keys() if cmd.startswith(text)]
        matches += [cmd for cmd in exec_cache.keys() if cmd.startswith(text)]
        matches = sorted(set(matches))  # remove duplicates and sort

        if text != last_prefix:
            last_prefix = text
            tab_count = 0

        if state == 0:
            tab_count += 1
            if len(matches) > 1:
                if tab_count == 1:
                    print("\a", end="", flush=True)
                elif tab_count == 2:
                    print("\n" + " ".join(matches))
                    print(f"$ {readline.get_line_buffer()}", end="", flush=True)  # type: ignore (windows)
        if state < len(matches):
            return matches[state] + " "
        return None

    return autocomplete


def display_matches(substitution, matches, longest_match_length):
    print("\n" + " ".join(matches))
    print(f"$ {readline.get_line_buffer()}", end="", flush=True)  # type: ignore (windows)


def setup_autocompletion(exec_cache: dict[str, str]):
    readline.set_completer(make_autocomplete(exec_cache))  # type: ignore (windows)
    readline.parse_and_bind("tab: complete")  # type: ignore (windows)
    readline.set_completion_display_matches_hook(display_matches)  # type: ignore (windows)


if __name__ == "__main__":
    setup_autocompletion({})

    while True:
        input_cmd = input("shell> ")
        if input_cmd.strip() == "exit":
            break
