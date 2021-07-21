import re
from re import Match


def _replace(object: Match) -> str:
    return chr(int(object.group(1)))


def format_code(code: str) -> None:
    return re.sub("&#([1-9][0-9]*);", _replace, code)
