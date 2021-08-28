from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment, Message
from nonebot.typing import T_State

from lin.log import logger
from lin.service import ServiceManager as sv

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
