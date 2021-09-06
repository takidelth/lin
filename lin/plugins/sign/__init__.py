from random import randint
from datetime import date, datetime

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.service import ServiceManager as sv

from .data_source import load_data, save_data


sign_lst: dict = load_data()


__doc__ = """
签到功能
"""


sign = sv.on_command("签到", docs=__doc__)


@sign.handle()
async def _sign_handle(bot: Bot, event: MessageEvent) -> None:
    user_id = str(event.user_id)

    try:
        data = sign_lst[user_id]
    except KeyError:
        sign_lst[user_id] = {}
        data = {
            "count": 1,
            "level": randint(0, 3),
            "score": randint(50, 200),
            "date": datetime.now().strftime("%Y %m %d")
        }
    
    if data["count"] > 1:
        if (date.today() - date(*map(int, data["date"].split(" ")))).days >= 1:
            data["count"] += 1
            level = randint(0, 3)
            data["level"] = 100 if (data["level"] + level) >= 100 else data["level"] + level
            data["score"] += randint(50, 200)
            data["date"] = datetime.now().strftime("%Y %m %d")
        else:
            await sign.finish("阁下今天已经签到过啦awa")
    else:
        if sign_lst.get(user_id):
            await sign.finish("阁下今天已经签到过啦awa")
            
    sign_lst[user_id] = data
    await save_data(sign_lst)

    msg = (
        f"签到成功\n"
        f"累计签到: {data['count']}\n"
        f"当前积分: {data['score']}\n"
        f"好感度: {data['level']}"
    )
    msg = MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={str(user_id)}&s=4") + msg
    await sign.finish(msg)