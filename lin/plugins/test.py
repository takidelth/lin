from logging import LogRecord, log
import traceback
from loguru import logger
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from lin.service import on_command
from nonebot.rule import to_me

from lin.exceptions import ApiException

__doc__ = """
功能测试插件:
  此插件是主人用来测试功能的哦
"""

test = on_command("test", __doc__)

@test.handle()
async def first_handle_receive(bot : Bot, event : Event, state: dict):
    logger.error("报错!!!!!!!!!!")
    a = "asda" + 100
    logger.info(a)
    raise ApiException("报错！！！！！")

