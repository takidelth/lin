from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from lin.service import on_command, Service as sv
from lin.log import logger

from .data_source import get_id

__doc__ = """
封禁用户
权限组:
  管理员
使用:
  封禁用户 <用户QQ>
"""
block_user = on_command("封禁用户", __doc__, permission=SUPERUSER)


@block_user.args_parser
async def _get_target_id(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()

    quit_list = ["算了", "算了算了", "罢了", "取消"]
    if msg in quit_list:
        await block_user.finish("好吧")

    if msg:
        state["qq"] = msg
    else:
        await block_user.reject("是谁呢?（直勾勾的看着你")


@block_user.handle()
async def _handle_target_id(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()

    if msg:
        state["qq"] = msg


@block_user.got("qq", prompt="是谁呢?")
async def _handle(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = state["qq"]
    qq_id = get_id(msg)
    sv.block_user(qq_id)
    await block_user.finish(f"用户: {qq_id} 已被禁用")
    logger.info(f"qq: {qq_id}")
    


__doc__ = """
解封用户
权限组:
  管理员
使用:
  解封用户 <用户QQ>
"""
unblock_user = on_command("解封用户", __doc__, permission=SUPERUSER)


@unblock_user.args_parser
async def _get_target_id(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()

    quit_list = ["算了", "算了算了", "罢了", "取消"]
    if msg in quit_list:
        await block_user.finish("好吧")

    if msg:
        state["qq"] = msg
    else:
        await block_user.reject("是谁呢?（直勾勾的看着你")


@unblock_user.handle()
async def _handle_target_id(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()

    if msg:
        state["qq"] = msg


@unblock_user.got("qq", prompt="是谁呢?")
async def _handle(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = state["qq"]
    qq_id = get_id(msg)
    sv.unblock_user(qq_id)
    await block_user.finish(f"用户: {qq_id} 已被解除禁用")
    logger.info(f"qq: {qq_id}")