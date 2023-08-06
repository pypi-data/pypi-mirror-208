from typing import Optional

import pync
from rich.console import Console
from rich.syntax import Syntax

Error = Optional[str]


def notify(message, title, sound=True):
    if sound:
        pync.notify(message, title=title, sound='Ping')
    else:
        pync.notify(message, title=title)


def print_error_body(err: str):
    syntax = Syntax(err, "text", theme="paraiso-dark", line_numbers=False)
    Console().print(syntax)


def clean_stderr(s: str):
    if s is None:
        return ""
    s = s.split("\n")
    o = []
    for l in s:
        if "direnv" in l:
            continue
        o.append(l)

    if len(o) == 0:
        return ""
    return "\n".join(o)


def get_latest_version() -> str:
    try:
        import requests

        package = 'pbsrollout'
        response = requests.get(f'https://pypi.org/pypi/{package}/json')
        return response.json()['info']['version']
    except:
        return ""


def is_dev() -> bool:
    from os import getenv
    if getenv('DEV', '').lower() == 'true':
        return True
    import pathlib
    ret = pathlib.Path(__file__).parent.resolve()
    return 'pbsrollout/pbsrollout' in str(ret)
