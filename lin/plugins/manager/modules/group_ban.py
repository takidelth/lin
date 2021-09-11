from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent
from nonebot.permission import SUPERUSER

from lin.service import ServiceManager as sv

from ._data_source import get_id, get_time


__doc__ = """
禁言群成员
"""
group_ban = sv.on_command("禁言", docs=__doc__, permission=SUPERUSER)


@group_ban.handle()
async def _handle_group_ban(bot: Bot, event: GroupMessageEvent) -> None:
    msg = str(event.message).strip()

    target_id = get_id(msg)
    if target_id == "":
        await group_ban.finish("阁下要禁言谁先说清楚鸭")

    time = get_time(msg)
    if time == 0:
        await group_ban.finish("无效的时间")

    await bot.set_group_ban(
                    group_id=event.group_id,
                    user_id=int(target_id),
                    duration=time
                )


__doc__ = """
解除禁言
"""
group_disban = sv.on_command("解除禁言", docs=__doc__, permission=SUPERUSER)


@group_disban.handle()
async def _handle_group_disban(bot: Bot, event: GroupMessageEvent) -> None:
    msg = str(event.message).strip()

    target_id = get_id(msg)
    if target_id == "":
        await group_disban.finish("阁下要解除谁先说清楚鸭")

    await bot.set_group_ban(
                    group_id=event.group_id,
                    user_id=int(target_id),
                    duration=0
                )


__doc__ = """
全体禁言 (解除)
"""
group_ban_all = sv.on_command("全体禁言", docs=__doc__, permission=SUPERUSER)


@group_ban_all.handle()
async def _handle_group_ban_all(bot: Bot, event: MessageEvent) -> None:
    # 完全没有考虑 主人不是管理员的情况（doge保命
    msg = str(event.message).strip()
    
    enable = True
    if "解除" in enable:
        enable = False

    await bot.set_group_whole_ban(
                            group_id=event.group_id,
                            enable=enable
                        )
    # bot.set_group_admin
    # bot.set_group_card
    # bot.set_group_kick
    # bot.set_group_name
    # bot.set_group_leave
    # bot.set_group_special_title
    # bot.set_group_leave
