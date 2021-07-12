from nonebot.adapters.cqhttp import message
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment, Message
from nonebot.typing import T_State
from nonebot.log import logger

from .data_source import MusicParse
from lin.utils import requests


music = on_command("music", aliases={"音乐", "音乐下载"}, priority=5)


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
        # 对不起我只是太菜了
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
        await music.finish(f"咦...好像失败了，这...这绝对不是我的问题！不信你换一个试试")