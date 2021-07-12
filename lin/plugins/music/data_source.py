from os import link
import re
from typing import Union, Optional
import requests

headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_type_and_id(string: str) -> tuple or None:
    result = re.findall("(song|playlist).*?id=([0-9]+)", string)
    return result[0] if result else None


class MusicParse:
    """处理 Music 链接"""
    
    lnk: str = ""
    flag: bool = False


    @property
    def link(self) -> str:
        return self.lnk

    
    @link.setter
    def link(self, value: str) -> None:
        result = get_type_and_id(value)
        if result:
            self.tp, self.id = result
            self.flag = True


    @property
    def get_type(self) -> str:
        return self.tp


    @property
    def get_id(self) -> str:
        return self.id
    
    
    @property
    def content(self) -> dict or list or ...:
        url = f"http://api.takidelth.cn/meting/?type={'single' if self.tp == 'song' else 'playlist'}&id={self.id}"
        data = requests.get(url, headers=headers).json()
        if isinstance(data, dict):
            return data if not data.get("error", None) else None
        elif isinstance(data, list):
            return data if data != [] else None
    
    def is_ok(self) -> bool:
        return self.flag


MusicParser = MusicParse()

if __name__ == "__main__":
    MusicParser.link = "https://api.injahow.cn/meting/?type=song&id=591321"
    print(MusicParser.target_link)