"""似乎是个用不上的模块呢"""

import aiofiles
from pathlib import Path


async def read_text(path: Path, encoding: str = "utf-8") -> str:
    async with aiofiles.open(path, "r", encoding=encoding)as r:
        data = await r.read()
    return data


async def read_bytes(path: Path) -> bytes:
    async with aiofiles.open(path, "rb")as r:
        data = await r.read()
    return data


async def write_text(path: Path, content: bytes, encoding: str = "utf-8") -> None:
    async with aiofiles.open(path, "w", encoding=encoding)as r:
        return await r.write(content)


async def write_bytes(path: Path, content: bytes, encoding: str = "utf-8") -> None:
    async with aiofiles.open(path, "wb", encoding=encoding)as r:
        return await r.write(content)