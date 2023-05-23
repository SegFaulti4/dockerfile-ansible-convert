import os.path
from typing import Optional


from src.log import globalLog


def path_str_wrapper(path: str, cwd: str, usr: Optional[str], ignore_tilde: bool = False) -> str:

    def custom_strip(s: str, c: str) -> str:
        return s.strip(c) if s.startswith(c) and s.endswith(c) else s

    def strip_quotes(s: str) -> str:
        s = custom_strip(s, "'")
        s = custom_strip(s, '"')
        s = custom_strip(s, "'")
        return s

    # because we don't need any quotes
    path = strip_quotes(path)

    if path.startswith("/"):
        return path
    if path.startswith("~") and not ignore_tilde:
        if usr is None:
            globalLog.info(f"Could not change path string - {path}, usr is None")
            return path
        if usr == "root":
            home = "/root"
        else:
            home = f"/home/{usr}"
        path = path[1:]
        i = 0

        # to handle something like `~/dir`
        # because for some reason os.path.join("/home/usr", "~/") == "/"
        while path[i:] and path[i] == "/":
            i += 1
        path = path[i:]

        if path:
            return os.path.join(home, path)
        return home

    # this is enough for something like `./some_dir/other_dir` or `another_dir/other_dir`
    return os.path.join(cwd, path)
