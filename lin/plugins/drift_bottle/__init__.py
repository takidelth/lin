from random import randint
from datetime import datetime
from copy import deepcopy

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import Message
from nonebot.typing import T_State

from lin.service import ServiceManager as sv

from .data_source import bottle_generator, load_bottles, save_bottles


bottles: list = load_bottles()


__doc__ = """
收漂流瓶
"""
bottle_recv = sv.on_command("收漂流瓶", docs=__doc__)


@bottle_recv.handle()
async def _handle_bottle(bot: Bot, event: MessageEvent) -> None:
    if len(bottles) == 0:
        data = await bottle_generator()
    else:
        index = randint(0, len(bottles) - 1)
        data = bottles[index]
        bottles.pop(index)
        save_bottles(bottles)
    
    # TODO 内容以图片发送
    repo = (
        f"时间: {data['date']}\n"
        f"内容:\n{data['msg']}"
    )
    await bottle_recv.finish(Message(repo))


__doc__ = """
收漂流瓶
"""
bottle_send = sv.on_command("发漂流瓶", docs=__doc__)


@bottle_send.handle()
async def _send_bottle(bot: Bot, event: MessageEvent) -> None:
    msg = str(event.message).strip()
    
    if not msg:
        await bottle_send.reject("阁下想要写点什么呢")
    else:
        data = {
            "msg": msg,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        bottles.append(data)
        save_bottles(bottles)
    await bottle_send.finish("阁下的漂流瓶已经投到大海里了哦")