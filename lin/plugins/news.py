from pathlib import Path

import nonebot
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.service import ServiceManager as sv
from lin.service import GocqhttpApiServer as gh
from lin.utils.requests import get_json, get_bytes
from lin.utils.apscheduler import scheduler
from lin.exceptions import ApiException


driver = nonebot.get_driver()
IMG_PATH = Path(".") / "lin" / "data" / "temp" / "news.jpg"
API_URL = "https://api.iyk0.com/60s/"


async def get_img_url() -> str:
    data = await get_json(API_URL)
    if data["code"] == 200:
        return data["imageUrl"]
    else:
        raise ApiException("news api error")


async def update_img() -> None:
    """
    更新新闻图片
    说明:

        缓存 api 接口图片到本地实现加速
    """
    try:
        img_url = await get_img_url()
    except ApiException as e:
        await gh.send_to_superusers(message="报告主人！ news 插件的 api 返回异常")
        return
    data = await get_bytes(img_url)
    IMG_PATH.write_bytes(data)
    await gh.send_to_superusers(message="news 插件的图片已经预先缓存到本地了哦")


@driver.on_startup
async def _update_img() -> None:
    await update_img()


@scheduler.scheduled_job("cron", hour="*/6")
async def _update_new_image() -> None:
    await update_img()


__doc__ = """
60s读世界
使用:
    新闻
    news
    60s读世界
    60s
"""


news = sv.on_command(
    cmd="news", aliases={"新闻", "60s读世界", "60s"}, docs=__doc__
)


@news.handle()
async def _news_handle(bot: Bot, event: MessageEvent) -> None:
    repo = MessageSegment.image(f"file:///{str(IMG_PATH.absolute())}")
    await news.finish(repo)


"""
TODO 手动群发
TODO 定时自动发送 [随机|全部]
"""