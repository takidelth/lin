from os import stat
import jieba
import jieba.posseg as pseg

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from lin.service import ServiceManager as sv
from lin.exceptions import ApiException
from lin.utils.requests import get_json
from lin.log import logger


API_URL = "https://api.iyk0.com/6rtq/?city="


def get_cite(text: str) -> str:
    words = jieba.lcut(text)
    for word in words:
        if len(word) == 1:
            continue
        txt, flag = list(pseg.cut(word))[0]
        if flag == "ns":
            return txt
    return ""


async def get_weather(cite: str) -> dict:
    url = API_URL + cite
    result = await get_json(url)
    
    if result["status"] != 1000:
        raise ApiException("天气查询接口返回异常")
    return result["data"]["yesterday"]


__doc__ = """
天气查询
使用:
    > 天气 [cite]
    > 查询天气 [cite]
    > 天气查询 [cite]
    > 今天天气 [cite]
    或者消息中包含城市名称和关键字[天气]的消息
"""
weather = sv.on_command(
    "天气", aliases={"查询天气", "天气查询", "今天天气"}, docs=__doc__
)


@weather.handle()
async def _handle_weather(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()
    cite = get_cite(msg)
    if not cite:
        return
    
    state["cite"] = cite


@weather.got("cite", prompt="是哪个城市呢?")
async def _get_weather(bot: Bot, event: MessageEvent, state: T_State) -> None:
    yesterday = await get_weather(state["cite"])

    repo = (
        f"今天{state['cite']}天气 {yesterday['type']} {yesterday['fx']}\n"
        f"气温 {yesterday['high'][3:]} - {yesterday['low'][3:]}"
    )
    await weather.finish(repo)


weather_r = sv.on_regex(".*天气.*")


@weather_r.handle()
async def _handle_weather_r(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()
    cite = get_cite(msg)
    if not cite:
        return
    
    yesterday = await get_weather(cite)
    repo = (
        f"今天{cite}天气 {yesterday['type']} {yesterday['fx']}\n"
        f"气温 {yesterday['high'][3:]} - {yesterday['low'][3:]}"
    )
    await weather_r.finish(repo)
