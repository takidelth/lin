from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.permission import SUPERUSER

from lin.service import ServiceManager as sv


__doc__ = """
禁用插件
"""
disable = sv.on_command("disable", docs=__doc__, permission=SUPERUSER)


@disable.handle()
async def _disable_handle(bot: Bot, event: MessageEvent) -> None:
    pass