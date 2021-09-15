from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.exception import ActionFailed

from lin.service import ServiceManager as sv

from ._data_source import get_id


__doc__ = """
设置管理员 （解除|设置）
"""
set_group_admin = sv.on_command("设置管理员", docs=__doc__, permission=SUPERUSER)


@set_group_admin.handle()
async def _handle_set_group_admin(bot: Bot, event: GroupMessageEvent) -> None:
    msg = str(event.message).strip()
    
    target_id = get_id(msg)
    if target_id == "":
        await set_group_admin.finish("说清楚是谁啊喂")

    enable = True
    if "解除" in msg:
        enable = False

    target_id = int(target_id)
    try:
        await bot.set_group_admin(
                            group_id=event.group_id,
                            user_id=target_id,
                            enable=enable
                        )
    except ActionFailed:
        await set_group_admin.finish("权限不足")
    else:
        await set_group_admin.finish("操作成功")


__doc__ = """
群组踢人
"""
group_kick = sv.on_command(
    "踢人", aliases={"机票"}, docs=__doc__, permission=SUPERUSER 
)


@group_kick.handle()
async def _handle_group_kick(bot: Bot, event: GroupMessageEvent) -> None:
    msg = str(event.message).strip()
    
    target_id = get_id(msg)
    if target_id == "":
        await group_kick.finish("无效的id")

    target_id = int(target_id)

    try:
        await bot.set_group_kick(
                            group_id=event.group_id,
                            user_id=target_id,
                            reject_add_request=True     # 拒绝此人的请求
                        )
    except ActionFailed:
        await group_kick.finish("权限不足")
    else:
        await group_kick.finish("操作成功")


    # bot.set_group_card
    # bot.set_group_name
    # bot.set_group_leave
    # bot.set_group_special_title
    # bot.set_group_leave