import sys

VALID_COMMANDS = ["exit", "echo", "type"]


def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # handle exit
        if user_input == "exit":
            break
        # handle echo
        user_input_split = user_input.split(" ", maxsplit=1)
        if user_input_split[0] == "echo":
            if len(user_input_split) > 1:
                print(user_input_split[1])
            else:
                print()
            continue
        # handle type
        if user_input_split[0] == "type":
            # currently will not handle multiple args or missing args, just assume the good case
            if user_input_split[1] in VALID_COMMANDS:
                print(f"{user_input_split[1]} is a shell builtin")
                continue
            else:
                print(f"{user_input_split[1]}: command not found")
                continue
        # handle unknown command
        print(f"{user_input}: command not found")


if __name__ == "__main__":
    main()
