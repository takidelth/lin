from random import randint, choice

from nonebot.adapters.gocq import Bot, GroupMessageEvent
from nonebot.adapters.gocq.message import MessageSegment, Message

from lin.log import logger
from lin.service import on_message

msg_list = dict() # group_id: "last_msg"
face_url = [
    "https://cdn.jsdelivr.net/gh/takidelth/takidelth/imgcache/face/a1.bmp",
    "https://cdn.jsdelivr.net/gh/takidelth/takidelth/imgcache/face/a2.jpg",
    "https://cdn.jsdelivr.net/gh/takidelth/takidelth/imgcache/face/a3.gif",
    "https://cdn.jsdelivr.net/gh/takidelth/takidelth/imgcache/face/a4.png"
]

interrupt_repeat = on_message()


@interrupt_repeat.handle()
async def _pia_(bot: Bot, event: GroupMessageEvent) -> None:
    group_id = event.group_id
    msg = str(event.message)[:30]
    
    if msg != msg_list.get(group_id, None):
        msg_list[group_id] = msg[:30]
        return
    
    is_run = True if randint(0, 3) == 1 else False   # 1/4 的概率触发
    if is_run:
        await interrupt_repeat.send(MessageSegment.image(choice(face_url)))
        await interrupt_repeat.finish("哎嘿" if msg == "打断复读~" else "打断复读")
        msg_list[group_id] = "打断复读~"
