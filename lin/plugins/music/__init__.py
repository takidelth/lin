from typing import Optional

from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment, Message
from nonebot.typing import T_State

from lin.log import logger
from lin.service import ServiceManager as sv
from lin.utils.requests import get_json

from .data_source import MusicParse


__doc__ = """
音乐解析插件:
    目前支持网易和QQ音乐解析
使用方式：
    发送指令: music <你的音乐链接>
或者
    发送命令: music 后再向机器人分享你的链接

说明:
    链接可以是 歌单 也可以是 单曲
"""


music = sv.on_command("music", __doc__)


@music.args_parser
async def _wait_link(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()
    quit_list = ["算了", "算了算了", "罢了", "取消", "不下了"]
    if msg in quit_list:
        await music.finish("好吧")
    
    if not msg:
        await music.reject("发链接, gkdgkd")
    else:
        state["link_str"] = msg


@music.handle()
async def _find_link(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()
    if msg:
        state["link_str"] = msg


@music.got("link_str", prompt="上链接!")
async def _handle_event(bot: Bot, event: MessageEvent, state: T_State) -> None:
    link_str = state["link_str"]
    if not ("music.163.com" in link_str or "y.qq.com" in link_str):
        await music.reject("目前只支持网易云音乐和QQ音乐喔, 换个链接重试一下吧")
    
    MusicParser = MusicParse()
    MusicParser.link = link_str
    if MusicParser.ok:
        await music.send("链接已确认，正在解析稍等一会哦")
    else:
        # 对不起我只是菜了一点
        await music.send(Message("[CQ:image,file=4a0d0ac0e92958b534969ee401537e4c.image,url=https://c2cpicdw.qpic.cn/offpic_new/1037447217//1037447217-1189060299-4A0D0AC0E92958B534969EE401537E4C/0?term=3]"))
        await music.reject("hmmmm...俺只可以解析单曲和歌单啦...")

    # 针对单曲和歌单实现两种不同的处理方式
    content = MusicParser.content

    if MusicParser.get_link_type() == "single" and content:
        cover = MessageSegment.image(content['cover'])
        repo = cover + Message(
            f"\n来源：{MusicParser.server_type}\n"
            f"歌名：{content['name']}\n"
            f"歌手：{content['artist']}\n"
            f"歌曲下载链接：{content['url']}\n"
            f"歌词下载链接：{content['lrc']}\n"
            )
        await music.send(repo)
        await music.finish("凌酱任务完成 (鼓掌")

    elif MusicParser.get_link_type() == "playlist":
        await music.finish(f"主人还在摸鱼(疯狂暗示")
    else:
        logger.error("API 请求返回数据失败")
        await music.finish(f"咦...好像失败了，这...这绝对不是我的问题！不信你换一个试试")


async def search_music(song_name: str, author: Optional[str] = None) -> int:
    API_URL = "https://api.obfs.dev/api/netease/search?s=" + song_name
    result = (await get_json(API_URL))["result"]
    if result["songCount"] == 0:
        return -1
    
    if author:
        for item in result["songs"]:
            for author_info in item["ar"]:
                author_names = [author_info["name"]] + author_info["tns"] + author_info["alias"]
                if author in author_names:
                    return item["id"]
        return -1
    else:
        return result["songs"][0]["id"]


__doc__ = """
点歌插件
使用:
    点歌 [歌手] <歌名>
"""
share_music = sv.on_command("点歌", docs=__doc__)


@share_music.handle()
async def _handle_share(bot: Bot, event: MessageEvent) -> T_State:
    msg = str(event.message).split(" ")
    
    param_count = len(msg)
    if param_count == 2:
        author, song_name = msg
        song_id = await search_music(song_name, author)
    elif param_count == 1:
        song_name = msg[0]
        song_id = await search_music(song_name)
    else:
        await share_music.finish("非法参数")
    
    if song_id == -1:
        await share_music.finish("没有找到>_<")
    repo = MessageSegment.music(type_="163", id_=song_id)

    await share_music.finish(repo)