import json
from os import stat
from pathlib import Path

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from lin.service import ServiceManager as sv

from ._data_source import find_flag_id, write_text


DATA_DIR = Path(".") / "lin" / "data" / "essential"


__doc__ = """
处理好友请求(私聊触发)
使用:
    查看所有请求
    > 好友请求 list
    
    同意请求
    > 好友请求 accept <flag_id>
    
    拒绝请求
    > 好友请求 refuse <flag_id>

"""
handle_friend_request = sv.on_command("好友请求", docs=__doc__, permission=SUPERUSER)


@handle_friend_request.handle()
async def _handle_group_request(bot: Bot, event: PrivateMessageEvent, state: T_State) -> None:
    msg = str(event.message).strip()
    
    if msg == "list":
        await _handle_show_list(bot, event)
    elif "accept" in msg:
        flag_id = find_flag_id(msg)
        if flag_id:
            await _handle_accept(bot, event, flag_id)
    elif "refuse" in msg:
        flag_id = find_flag_id(msg)
        if flag_id:
            await _handle_refuse(bot, event, flag_id)


async def _handle_show_list(bot: Bot, event: MessageEvent) -> None:
    file = DATA_DIR / "request_friend.json"
    try:
        data: dict = json.loads(file.read_bytes())
    except:
        await handle_friend_request.finish("目前没有好友申请哦")
    for flag, info in data.items():
        repo = (
            f"时间: {info['time']}\n"
            f"发起者: {info['nickname']}({info['user_id']})\n"
            f"备注信息: {info['comment']}\n"
            f"请求编号: {flag}"
        )
        await handle_friend_request.send(repo)


async def _handle_accept(bot: Bot, event: MessageEvent, flag: str) -> None:
    file = DATA_DIR / "request_friend.json"
    try:
        data: dict = json.loads(file.read_bytes())
    except:
        await handle_friend_request.finish("目前没有好友申请哦")
    
    if not data.get(flag):
        await handle_friend_request.finish("无效的 flag_id")
    
    await bot.set_friend_add_request(
                            flag=flag,
                            sub_type=data[flag]["sub_type"],
                            approve=True
                        )
    # 更新文件
    data.pop(flag)
    await write_text(file, json.dumps(data, indent=4))
    
    await handle_friend_request.finish(f"{flag} 请求已经接受")


async def _handle_refuse(bot: Bot, event: MessageEvent, flag: str) -> None:
    file = DATA_DIR / "request_friend.json"
    try:
        data: dict = json.loads(file.read_bytes())
    except:
        await handle_friend_request.finish("目前没有好友申请哦")
    
    if not data.get(flag):
        await handle_friend_request.finish("无效的 flag_id")

    await bot.set_friend_add_request(
                            flag=flag,
                            sub_type=data[flag]["sub_type"],
                            approve=False
                            # TODO 回复备注消息
                        )
    # 更新文件
    data.pop(flag)
    await write_text(file, json.dumps(data, indent=4))
    
    await handle_friend_request.finish(f"{flag} 请求已经拒绝")