from _typeshed import WriteableBuffer
import os
import json
from re import sub
import shutil
import nonebot
from pathlib import Path
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import (
    MessageEvent,
    LuckyKingNotifyEvent,
    GroupMessageEvent,
    GroupRequestEvent,
    GroupUploadNoticeEvent,
    GroupRecallNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupAdminNoticeEvent,
    GroupBanNoticeEvent,
    FriendRequestEvent
)
from nonebot.message import run_preprocessor

from lin.log import logger
from lin.config import BotSelfConfig
from lin.service import SERVICES_DIR, ServiceManager as sv
from lin.service import GocqhttpApiServer as gh
from lin.exceptions import (
    IgnoreException, 
    PluginDisableException, 
    WriteError
)

PLUGIN_INFO_DIR = SERVICES_DIR
ESSENTIAL_DIR = Path(".") / "lin" / "data" / "essential"
os.makedirs(ESSENTIAL_DIR, exist_ok=True)


driver = nonebot.get_driver()


@driver.on_startup
async def _startup() -> None:
    # 初始化 插件管理
    sv.init()


@driver.on_shutdown
async def _shutdown() -> None:
    # 删除 插件信息
    logger.info("Thanks for using.")
    logger.debug("Bot 已经停止, 正在清理插件信息...")
    try:
        shutil.rmtree(PLUGIN_INFO_DIR)
        logger.debug("插件信息清理完毕")
    except:
        logger.error("插件清理失败")
        repo = "插件信息清理失败请前往 /lin/data/services/ 目录手动清理"
        raise Exception(repo)

    # 保存 block_list 信息
    sv.end()


@run_preprocessor
async def _check_block(
    matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State,
) -> None:
    user_id = event.get_user_id()
    
    if sv.Auth.auth_user(user_id):
        logger.info(f"Ignore user: {user_id}")
        raise IgnoreException(f"Ignore user: {user_id}")
    
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        if sv.Auth.auth_group(group_id):
            logger.info(f"Ignore group: {group_id}")
            raise IgnoreException(f"Ignore group: {group_id}")


@run_preprocessor
async def _check_enable(
    matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State
) -> None:
    service_name = state["_service_name"]
    if not sv.Status.check_status(service_name):
        logger.error(f"插件 {service_name} 已被禁用 可能是正在维护中哦")
        raise PluginDisableException(f"插件 {service_name} 已被禁用 可能是正在维护中哦")


request_friend_event = sv.on_request()


@request_friend_event.handle()
async def _request_friend_event(bot: Bot, event: FriendRequestEvent) -> None:
    file = ESSENTIAL_DIR / "request_friend.json"
    try:
        data = json.loads(file.read_bytes())
    except:
        data = dict()
    data[event.flag] = {"user_id": event.user_id, "comment": event.comment}
    
    try:
        with open(file, "w")as f:
            f.write(json.dumps(data, indent=4))
    except WriteError:
        raise WriteError("request_friend.json write failed")

    repo = (
        f"收到一个好友请求主人快来看下\n"
        f"发送者: {event.user_id}\n"
        f"消息内容: {event.comment}\n"
        f"请求编号: {event.flag}"
    )
    for superuser in BotSelfConfig.superusers:
        await gh.send_private_msg(user_id=superuser, message=repo)


request_group_event = sv.on_request()


@request_group_event.handle()
async def _request_group_event(bot: Bot, event: GroupRequestEvent) -> None:
    file = ESSENTIAL_DIR / "request_group.json"
    try:
        data = json.loads(file.read_bytes())
    except:
        data = dict()
    sub_type = "加群" if event.sub_type == "add" else "被邀请加群" 
    data[event.flag] = {
        "group_id": event.group_id,
        "user_id": event.user_id,
        "comment": event.comment,
        "sub_type": sub_type
    }
    try:
        with open(file, "w")as f:
            f.write(json.dumps(data, indent=4))
    except WriteError:
        raise WriteError("request_group.json write failed")
    repo = (
        f"主人收到一条{sub_type}请求 快来看看\n"
        f"发送者: {event.user_id}\n",
        f"目标群组: {event.group_id}\n"
        f"请求编号: {event.flag}"
    )
    for superuser in BotSelfConfig.superusers:
        await gh.send_private_msg(user_id=superuser, message=repo)