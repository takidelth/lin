from pathlib import Path
import re
import aiofiles


def get_id(msg: str) -> str:
    result = re.search("[0-9]+", msg)
    
    if result:
        return result.group()
    else:
        return ""


def find_flag_id(string: str) -> str:
    result = re.search("[0-9]+", string)

    if result:
        return result.group()
    else:
        return ""


async def write_text(file: Path, content: str) -> int:
    async with aiofiles.open(file, "w")as f:
        return await f.write(content)


def get_time(msg: str) -> int:
    sec = 0

    result = re.search("([0-9]+)天", msg)
    if result:
        sec += int(result.group(1)) * 86400
    
    result = re.search("([0-9]+)小时", msg)
    if result:
        sec += int(result.group(1)) * 3600

    result = re.search("([0-9]+)分钟", msg)
    if result:
        sec += int(result.group(1)) * 60

    return sec