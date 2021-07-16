from nonebot.rule import Rule
from nonebot.typing import T_State
from typing import TYPE_CHECKING
from nonebot.adapters import Bot, Event


def to_bot() -> Rule:
    async def _to_bot(bot: Bot, event: Event, state: T_State):
        return event.is_tome()

    return Rule(_to_bot)