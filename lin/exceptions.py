import json
import os
import string
from pathlib import Path
from typing import Optional
from datetime import datetime
from random import randint
from random import sample
from datetime import datetime
from traceback import format_exc

from nonebot.message import run_postprocessor
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.typing import T_State

from lin.log import logger

ERROR_DIR = Path(".") / "lin" / "data" / "errors"
os.makedirs(ERROR_DIR, exist_ok=True)


def _save_error(prompt: str, content: str) -> str:
    track_id = "".join(sample(string.ascii_letters + string.digits, 8))
    data = {
        "track_id": track_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "content": content
    }
    file = ERROR_DIR / f"{track_id}.json"
    with open(file, "w")as f:
        f.write(json.dumps(data, indent=4))
    return track_id


def _load_error(track_id: str) -> dict:
    file = ERROR_DIR / f"{track_id}.json"
    try:
        data = json.loads(file.read_bytes())
    except:
        data = dict()
    return data


class BaseBotException(BaseException):
    
    prompt: Optional[str] = "ignore"


    def __init__(self, prompt: Optional[str]) -> None:
        self.prompt = prompt or self.__class__.prompt or self.__class__.__name__
        self.track_id = _save_error(prompt, format_exc())
        super().__init__(self.prompt)


class ApiException(BaseBotException):
    prompt = "API 异常"


class IgnoreException(BaseBotException):
    prompt = "对象不在服务范围内"


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
        track_id = e.track_id
    except Exception as e:
        prompt = "Unknown ERROR->" + e.__class__.__name__
        track_id = _save_error(prompt, format_exc())
    
    logger.debug(f"A bug has been fix, datetime: {datetime.now().strftime('%Y%m%d-%H')}")
    # [图片] 第一时间赶到现场嘲笑
    notice_msg = [
        "笨蛋上线干活了喂...什么？你该不会在睡觉吧？可真是个懒鬼",
        "哎呀...主人的屎山又出交通事故了哦，赶紧去修复吧（嘲笑",
        "阿哲， 你写的什么屎山啊事故率真高"
    ]
    hitokoto = notice_msg[randint(0, len(notice_msg) - 1)]
    repo = (
        f"{hitokoto}\n"
        f"追踪ID: {track_id}\n"
        f"报错原因: {prompt}\n"
    )
    await bot.send_private_msg(user_id=1037447217, message=repo)
    msg = (
        "[WARNING]发生了意料之外的错误 >_<\n"
        "不用担心，我已经通知主人啦\n"
        f"追踪ID: {track_id}\n"
        f"报错原因: {prompt}\n"
        f"请耐心等待主人修复"
    )
    await bot.send(event, msg)