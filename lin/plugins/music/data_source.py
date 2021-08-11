from os import link
import re
from typing import Union, Optional
import requests

headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class MusicParse:
    """处理 Music 链接"""
    
    API_ADDR: str = "http://api.takidelth.cn/meting/"
    lnk: str = ""
    flag: bool = False


    @staticmethod
    def get_type_and_id(string: str, server_type: str) -> Union[str, str] or None:
        """ on_regex("(song|playlist|songid|details).*?id=([0-9a-zA-Z]+|[0-9]+)") """
        if server_type == "netease":
            pattern = "(song|playlist).*?id=([0-9]+)"
        elif server_type == "tencent":
            pattern = "(songid|details).*?id=([0-9a-zA-Z]+)"
        result = re.findall(pattern, string)
        return [
            "single" if result[0][0] in ["song", "songid"] else "playlist",
            result[0][1]
        ] if result else None
    
    
    @staticmethod
    def get_server_type(link: str) -> str:
        if "music.163.com" in link:
            return "netease"
        elif "y.qq.com" in link:
            return "tencent"


    @property
    def link(self) -> str:
        return self.lnk

    
    @link.setter
    def link(self, value: str) -> None:
        server_type = self.get_server_type(value)
        result = self.get_type_and_id(value, server_type)
        if result:
            self.tp, self.id = result
            self.flag = True
            self.server_type = server_type


    def get_link_type(self) -> str:
        return self.tp


    @property
    def get_id(self) -> str:
        return self.id
    

    def _generate_full_api_url(self, link_type: str, song_id: str) -> str:
        return self.API_ADDR + f"?server={self.server_type}&type={self.tp}&id={song_id}"


    @property
    def content(self) -> dict or list or ...:
        url = self._generate_full_api_url(self.tp, self.id)
        data = requests.get(url, headers=headers).json()
        print(url)
        if isinstance(data, dict):
            return data if not data.get("error", None) else None
        elif isinstance(data, list):
            return data if data != [] else None
    

    @property
    def ok(self) -> bool:
        return self.flag


if __name__ == "__main__":
    MusicParser = MusicParse()
    MusicParser.link = "https://i.y.qq.com/n2/m/share/details/taoge.html?platform=11&amp;appshare=android_qq&amp;appversion=10150009&amp;hosteuin=oKni7ivP7i-57z**&amp;id=2917966132&amp;ADTAG=qfshare"
    print(MusicParser.content)