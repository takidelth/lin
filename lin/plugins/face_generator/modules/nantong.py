from io import BytesIO
from PIL.Image import Image

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.utils.image import CreateImg
from lin.utils.api import get_qq_avatar
from lin.service import ServiceManager as sv
from lin.log import logger


async def gay_generator(qqid: int) -> str:
    ava = CreateImg(100, 100, background=BytesIO(await get_qq_avatar(qqid)))
    ava.circle()
    text = CreateImg(200, 30, font_size=30)
    text.text((0, 0), "男同")
    A = CreateImg(300, 150, font_size=25, color="white")
    A.paste(ava, (30, 25), True)
    A.paste(text, (150, 40))
    A.text((150, 85), "关注了你", (125, 125, 125))
    return A.pic2bs4()


gay = sv.on_regex("男同.*?qq=([0-9]{5,11}).*?关注了你")


@gay.handle()
async def _gay_handle(bot: Bot, event: Event, state: T_State) -> None:
    qqid = state["_matched_groups"][0]
    
    bs4 = await gay_generator(int(qqid))
    repo = MessageSegment.image(f"base64://{bs4}")
    await gay.finish(repo)