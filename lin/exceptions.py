import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from random import randint

from nonebot.message import run_postprocessor
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.typing import T_State

from lin.log import logger

ERROR_DIR = Path(".") / "lin" / "data" / "errors"
os.makedirs(ERROR_DIR, exist_ok=True)


class BaseBotException(BaseException):
    
    prompt: Optional[str] = "ignore"


    def __init__(self, prompt: Optional[str]) -> None:
        self.prompt = prompt or self.__class__.prompt or self.__class__.__name__
        
        super().__init__(self.prompt)


class ApiException(BaseBotException):
    prompt = "API 异常"


@run_postprocessor
async def _track_error(
    matcher: Matcher,
    exception: Optional[Exception],
    bot: Bot,
    event: Event,
    state: T_State
) -> None:
    if exception is None:
        return

    try:
        raise exception
    except BaseBotException as e:
        prompt = e.prompt or e.__class__.__name__
    except Exception as e:
        prompt = "Unknown ERROR->" + e.__class__.__name__
    
    logger.debug(f"A bug has been fix, datetime: {datetime.now().strftime('%Y%m%d-%H')}")
    # [图片] 第一时间赶到现场嘲笑
    notice_msg = [
        "笨蛋上线干活了喂...你该不会在睡觉吧？可真是个懒鬼",
        "哎呀...主人的屎山又出交通事故了哦，赶紧去修复吧（嘲笑",
        "阿哲， 你写的什么屎山啊事故率真高"
    ]
    await bot.send_private_msg(user_id=1037447217, message=notice_msg[randint(0, len(notice_msg) - 1)])
    msg = "[WARNING]发生了意料之外的错误 >_<"
    await bot.send(event, msg)