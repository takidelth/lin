import random
import os


def save_code(code: str, filename: str, path) -> str:
    abs_path = os.path.join(path, filename)
    with open(abs_path, "w",encoding="utf8")as file:
        file.write(code)
    return abs_path


def random_filename(type: str = "py") -> str:
    if type not in ["cpp", "CPP", "py", "java"]:
        raise Exception
    filename = "".join(random.choices(
        "abcdefghijklmnopqrstuvwxyz123456789", k=20))+"."+type
    if os.path.exists(os.path.join(__file__, filename)):
        filename = "".join(random.choices(
            "abcdefghijklmnopqrstuvwxyz123456789", k=20))+"."+type
    return filename


def check_code_type(string: str) -> str:
    for tp in ['#include', 'cpp', 'c']:
        if tp in string:
            return 'cpp'
    for tp in ['py', 'python', 'Python', 'PY']:
        if tp in string:
            return 'py'

    return 'unknow'
