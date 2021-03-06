from nonebot.adapters.cqhttp import Bot, MessageEvent

from lin.service import ServiceManager as sv
from lin.utils.requests import get_text, get_ua
from lin.exceptions import ApiException

API_URL = "https://zuanbot.com/api.php?level=min&lang=zh_cn"
HEADERS = {"user-agent": get_ua()}

__doc__ = """
嘴臭一下
说明:
    此命令可能骂的很难听， 请不要不识抬举
"""
smelly = sv.on_command("嘴臭一下", docs=__doc__)


@smelly.handle()
async def _smelly(bot: Bot, event: MessageEvent) -> None:
    result = await get_text(API_URL, headers=HEADERS)
    if not result:
        raise ApiException("嘴臭一下 API 返回异常")
    await smelly.finish(result)