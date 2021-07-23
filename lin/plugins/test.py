from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.bot import Bot

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
    await hs.send_private_msg(user_id=1037447217, message="test")

