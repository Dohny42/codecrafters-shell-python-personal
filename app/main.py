import os
import sys


def handle_echo(args: str):
    if len(args) > 1:
        print(args[1])
    else:
        print()


def check_executable_exists(command: str) -> tuple[bool, str]:
    for path in sys.path:
        print(f"checking {path=}")
        executable_path = os.path.join(path, command)
        print(f"Checking {executable_path=}")
        if (
            os.path.isfile(executable_path)
            and os.access(executable_path, os.X_OK)
            and command == os.path.basename(executable_path)
        ):
            return True, executable_path
        else:
            continue
    return False, ""


def handle_type(args: str):
    # currently will not handle multiple args or missing args, just assume the good case
    if args in BUILTIN_COMMAND_HANDLER_MAP or args == "exit":
        print(f"{args} is a shell builtin")
    exe_exist, full_path = check_executable_exists(args)
    if exe_exist:
        print(f"{args} is {full_path}")
    else:
        print(f"{args}: not found")


BUILTIN_COMMAND_HANDLER_MAP = {"echo": handle_echo, "type": handle_type}


def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # handle exit
        if user_input == "exit":
            break
        # handle builtins
        user_input_split = user_input.split(" ", maxsplit=1)
        if user_input_split[0] in BUILTIN_COMMAND_HANDLER_MAP:
            handler = BUILTIN_COMMAND_HANDLER_MAP[user_input_split[0]]
            handler(user_input_split[1])
            continue
        # handle unknown command
        else:
            print(f"{user_input}: command not found")


if __name__ == "__main__":
    main()
