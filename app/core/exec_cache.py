import os


def get_exec_cache() -> dict[str, str]:
    exec_cache = {}
    for path in os.getenv("PATH", "").split(os.pathsep):
        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                    exec_cache[file] = file_path
    return exec_cache


def check_executable_exists(command: str, exec_cache: dict[str, str]) -> tuple[bool, str]:
    # check cache
    cached = exec_cache.get(command)
    if cached and os.path.isfile(cached) and os.access(cached, os.X_OK):
        return True, cached

    # not in cache (maybe new file added after cache generated), check PATH again
    for path in os.getenv("PATH", "").split(os.pathsep):
        executable_path = os.path.join(path, command)
        if (
            os.path.isfile(executable_path)
            and os.access(executable_path, os.X_OK)
            and command == os.path.basename(executable_path)
        ):
            exec_cache[command] = executable_path  # update cache for future use
            return True, executable_path
        else:
            continue

    # stale cache
    if command in exec_cache:
        del exec_cache[command]

    return False, ""
