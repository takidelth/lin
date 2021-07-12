from nonebot.adapters.cqhttp.event import Event, NoticeEvent
from nonebot.adapters.cqhttp.message import Message
from nonebot.plugin import  on_notice
from nonebot.adapters.cqhttp import Bot
from nonebot.typing import T_State
import random 

stamp = on_notice(priority=5)

words = [
    "戳我干嘛?", 
    "再戳我可生气了昂()", 
    "爬！",
    "[CQ:image,file=cdeb755a74bfdfacc99b54b2c8ce7bb0.image,url=https://gchat.qpic.cn/gchatpic_new/2929028892/483796300-2503789967-CDEB755A74BFDFACC99B54B2C8CE7BB0/0?term=3]"    
]

@stamp.handle()
async def first_handle(bot: Bot, event: NoticeEvent, state: T_State):
    dInfo = event.dict()

    if (event.get_event_name() == 'notice.notify.poke') and dInfo.get("target_id") == int(bot.self_id):
        # sender_id = event.get_user_id()
        msg = Message(words[random.randint(0, len(words))-1])
        await bot.send(
            event=event,
            message=msg,
            at_sender=True
        )