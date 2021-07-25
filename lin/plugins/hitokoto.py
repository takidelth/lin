from random import choice

from nonebot.adapters.cqhttp import Bot, MessageEvent

from lin.service import on_command
from lin.utils.requests import get_json

URL = [
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/a.json",
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/b.json",
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/c.json",
]

__doc__ = """
一言
使用:
  hitokoto
  一言
"""
hitokoto = on_command(
    cmd="一言", aliases={"hitokoto"}, docs=__doc__
)


@hitokoto.handle()
async def _hitokoto(bot: Bot, event: MessageEvent) -> None:
    data = get_json(choice(URL))
    repo = data.get("hitokoto")
    hitokoto.finish(repo)