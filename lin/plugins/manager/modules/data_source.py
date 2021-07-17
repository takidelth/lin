import re


def get_id(msg: str) -> str:
    result = re.search("[0-9]+", msg)
    
    if result:
        return result.group()
    else:
        return ""