import requests_async as requests

from nonebot.adapters.gocq import Event
from nonebot.adapters.gocq.bot import Bot
from nonebot.adapters.gocq.event import GroupMessageEvent
from nonebot.adapters.gocq.message import Message, MessageSegment

from lin.log import logger
from lin.service import on_command
from lin.exceptions import ApiException
from lin.service import GocqhttpApiServer as hs

__doc__ = """
功能测试插件:
  此插件是主人用来测试功能的哦
"""

test = on_command("test", __doc__)

@test.handle()
async def first_handle_receive(bot : Bot, event : Event, state: dict):
    
    msg = Message(f'[CQ:tts,text={str(event.get_message())}]')
    await test.finish(msg)