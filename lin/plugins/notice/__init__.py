import traceback
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent
from nonebot.adapters.cqhttp.event import Event, Sender
from nonebot.rule import to_me
from lin.plugin import on_command, on_message
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
import asyncio

notice = on_command("公告", permission=SUPERUSER, rule=to_me())

@notice.handle()
async def handle_first_receive(bot : Bot, event: GroupMessageEvent, state: dict):
    msg = event.get_message()
    
    # msg.append(MessageSegment.image(path="C:\\Users\\wh103\\Desktop\\temp\\lin\\src\\plugins\\notice\\face.png"))
    groupid = event.group_id
    memberlist = await bot.get_group_member_list(self_id=bot.self_id, group_id=groupid)
    for item in memberlist:
        try:
            await bot.send_msg(user_id=item['user_id'],
                message=msg,
                auto_escape=True,
                self_id=bot.self_id
            )
            await asyncio.sleep(3)
        except:
            pass
    await notice.finish("消息已经送达")