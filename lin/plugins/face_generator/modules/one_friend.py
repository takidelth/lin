from io import BytesIO
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent, MessageEvent
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.log import logger
from lin.service import ServiceManager as sv
from lin.utils.image import CreateImg
from lin.utils.api import get_qq_avatar

async def img_generator(qqid: int, nikename: str, msg: str) -> str:
    ava = CreateImg(100, 100, background=BytesIO(await get_qq_avatar(qqid)))
    ava.circle()
    text = CreateImg(300, 30, font_size=30)
    text.text((0, 0), nikename)
    A = CreateImg(700, 150, font_size=25, color="white")
    A.paste(ava, (30, 25), True)
    A.paste(text, (150, 40))
    A.text((150, 85), msg, (125, 125, 125))
    return A.pic2bs4()
    


friend = sv.on_regex("我朋友.*?qq=([0-9]{5,11}).*?说(.+)")


@friend.handle()
async def _friend_handle(bot: Bot, event: Event, state: T_State) -> None:
    try:
        qqid, msg = state["_matched_groups"]
    except ValueError as e:
        return 
    
    qqid = int(qqid)
    msg = msg.replace("他", "我").replace("她", "我").replace("它", "我")
    if isinstance(event, GroupMessageEvent):
        nikename = (await bot.get_group_member_info(group_id=event.group_id, user_id=qqid))["nickname"]
    elif isinstance(event, MessageEvent):
        nikename = "朋友"
    bs4 = await img_generator(qqid, nikename, msg)
    repo = MessageSegment.image(f"base64://{bs4}")
    await friend.finish(repo)