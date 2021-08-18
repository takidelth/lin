"""似乎是个用不上的模块呢"""

import io
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


class Path_async(Path):
    
    
    async def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        if self._closed:
            self._raise_closed()
        return aiofiles.open(self, mode, buffering, encoding, errors, newline,
                       opener=self._opener)

    async def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        async with self.open(mode='rb') as f:
            return await f.read()

    async def read_text(self, encoding=None, errors=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode='r', encoding=encoding, errors=errors) as f:
            return await f.read()

    async def write_bytes(self, data):
        """
        Open the file in bytes mode, write to it, and close the file.
        """
        # type-check for the buffer interface before truncating the file
        view = memoryview(data)
        with self.open(mode='wb') as f:
            return await f.write(view)

    async def write_text(self, data, encoding=None, errors=None):
        """
        Open the file in text mode, write to it, and close the file.
        """
        if not isinstance(data, str):
            raise TypeError('data must be str, not %s' %
                            data.__class__.__name__)
        with self.open(mode='w', encoding=encoding, errors=errors) as f:
            return await f.write(data)