from logging import LogRecord, log
import traceback
from loguru import logger
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.plugin import on_command
from nonebot.rule import to_me

from lin.exceptions import ApiException

test = on_command("test", aliases={"测试"}, priority=5)

@test.handle()
async def first_handle_receive(bot : Bot, event : Event, state: dict):
    logger.error("报错!!!!!!!!!!")
    a = "asda" + 100
    logger.info(a)
    raise ApiException("报错！！！！！")

