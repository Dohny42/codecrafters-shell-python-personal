import os
import subprocess
import sys


def handle_echo(args: list[str] | None) -> None:
    # empty raw string from cmd would be None, which should be ok to print newline
    if args is None:
        print()
    else:
        print(" ".join(args))


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


def handle_type(args: list[str]) -> None:
    # currently will not handle multiple args or missing args, just assume the good case
    if args[0] in BUILTIN_COMMANDS or args[0] == "exit":
        print(f"{args[0]} is a shell builtin")
        return
    exe_exist, exe_path = check_executable_exists(args[0])
    if exe_exist:
        print(f"{args[0]} is {exe_path}")
    else:
        print(f"{args[0]}: not found")


def handle_pwd(args: list[str]) -> None:
    print(os.getcwd())


BUILTIN_COMMANDS = {"echo": handle_echo, "type": handle_type, "pwd": handle_pwd}


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()

        # handle exit
        if command == "exit":
            break

        command_split = command.split(" ")

        # handle executable
        exe_exist, exe_path = check_executable_exists(command_split[0])
        if exe_exist:
            subprocess.run(
                [os.path.basename(exe_path)] + command_split[1:], check=True
            )  # avoid passing the full exe
            continue

        # handle builtins
        if command_split[0] in BUILTIN_COMMANDS:
            handler = BUILTIN_COMMANDS[command_split[0]]
            handler(command_split[1:])
            continue
        # handle unknown command
        else:
            print(f"{command_split[0]}: command not found")


if __name__ == "__main__":
    main()
