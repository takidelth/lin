import traceback
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.plugin import on_command
from nonebot.rule import to_me

test = on_command("test", aliases={"测试"}, rule=to_me(), priority=5)

@test.handle()
async def first_handle_receive(bot : Bot, event : Event, state: dict):
    msg = Message("[CQ:image,file=cdeb755a74bfdfacc99b54b2c8ce7bb0.image,url=https://gchat.qpic.cn/gchatpic_new/2929028892/483796300-2503789967-CDEB755A74BFDFACC99B54B2C8CE7BB0/0?term=3]")
    await bot.send(
        event=event,
        message=Message(event.get_session_id())
    )
    await test.finish(msg)



