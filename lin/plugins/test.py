from typing import NoReturn
from nonebot.typing import T_State
import requests_async as requests

from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.adapters.cqhttp.message import Message, MessageSegment

from lin.log import logger
from lin.service import on_command, on_regex, regex
from lin.exceptions import ApiException
from lin.service import GocqhttpApiServer as hs

__doc__ = """
功能测试插件:
  此插件是主人用来测试功能的哦
"""

class testing:
    # test = on_regex("(song|playlist|songid|details).*?id=([0-9a-zA-Z]+|[0-9]+)")
    test = on_command("test", docs=__doc__)

    @test.handle()
    async def _(bot: Bot, event: Event, state: T_State) -> None:
        """
        print(state["_matched"])
        print(state["_matched_groups"])
        print(state["_matched_dict"])

        song?id=1449406576
        ('song', '1449406576')
        {}
        """
        await testing.test.finish(MessageSegment.image("file:///home/taki/item/lin/Ling/lin/plugins/facecreator/modules/img/bdkBpCSo14.png", type_=40000))