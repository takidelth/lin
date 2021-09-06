import os
import json
import shutil
import nonebot
from pathlib import Path
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import (
    MessageEvent,
    FriendRecallNoticeEvent,
    LuckyKingNotifyEvent,
    GroupMessageEvent,
    GroupRequestEvent,
    GroupRecallNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupBanNoticeEvent,
    FriendRequestEvent
)
from nonebot.message import run_preprocessor
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.log import logger
from lin.service import SERVICES_DIR, ServiceManager as sv
from lin.service import GocqhttpApiServer as gh
from lin.exceptions import (
    IgnoreException, 
    PluginDisableException, 
    WriteError
)


TEMP_DIR = Path(".") / "lin" / "data" / "temp" 
PLUGIN_INFO_DIR = SERVICES_DIR
ESSENTIAL_DIR = Path(".") / "lin" / "data" / "essential"
os.makedirs(ESSENTIAL_DIR, exist_ok=True)


start_card = MessageSegment.xml("""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<msg serviceID="1" templateID="-1" action="web" brief="QQ Bot 已启动" sourceMsgId="0" url="" flag="0" adverSign="0" multiMsgFlag="0">
    <item layout="2" advertiser_id="0" aid="0">
        <picture cover="https://c2cpicdw.qpic.cn/offpic_new/1037447217//1037447217-1512954484-5BA3B82C3E4E0E3C35D794F143E788EC/0?term=3" w="0" h="0" />
        <title size="25" color="#000000">『凌』已加入该会话</title>
        <summary color="#000000">『凌』开始接受指令执行</summary>
    </item>
    <source name="QQ Bot 已启动，可以开始执行指令" icon="" action="" appid="0" />
</msg>""")


driver = nonebot.get_driver()


@driver.on_startup
async def _startup() -> None:
    # 初始化 插件管理
    sv.init()
    # TODO 向群聊发送 xml 
    pass


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

    # 清理 data/temp 目录
    logger.info("数据清理中...")
    try:
        shutil.rmtree(TEMP_DIR)
        logger.info("数据清理完成")
    except:
        logger.error("数据清理失败")
        repo = "数据清理失败请前往 /lin/data/temp/ 目录手动清理"
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
    service_name = state.get("_service_name")
    if service_name and not sv.Status.check_status(service_name):
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
    await gh.send_to_superusers(repo)


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
    await gh.send_to_superusers(repo)


group_recall_event = sv.on_notice()


@group_recall_event.handle()
async def _group_recall_event(bot: Bot, event: GroupRecallNoticeEvent) -> None:
    # 暂时不做存储
    msg_id = event.message_id
    msg = await bot.get_msg(message_id=msg_id)
    group_name = (await bot.get_group_info(group_id=event.group_id))["group_name"]
    user_nike = (await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id))["nickname"]
    repo = (
        f"主人主人我收到一条好康的消息发给你\n"
        f"message_id: {msg_id}\n"
        f"time: {msg['time']}:\n"
        f"from: {group_name}({event.group_id}) --> {user_nike}({event.user_id})\n"
        f"msg：{msg['raw_message']}"
    )
    await gh.send_to_superusers(repo)


friend_recall_event = sv.on_notice()


@friend_recall_event.handle()
async def _friend_recall_event(bot: Bot, event: FriendRecallNoticeEvent) -> None:
    # 暂时不做存储
    msg_id = event.message_id
    msg = await bot.get_msg(message_id=msg_id)
    repo = (
        f"主人主人我收到一条好康的消息发给你\n"
        f"message_id: {msg_id}\n"
        f"time: {msg['time']}:\n"
        f"from: {event.user_id}\n"
        f"msg：{msg['raw_message']}"
    )
    await gh.send_to_superusers(repo)


group_ban_event = sv.on_notice()


@group_ban_event.handle()
async def _group_ban_event(bot: Bot, event: GroupBanNoticeEvent) -> None:
    if not event.is_tome():
        return
    group_id = event.group_id
    group_name = (await bot.get_group_info(group_id=group_id))["group_name"]
    repo = (
        f"主人我在 {group_name}({group_id})被口球了 TvT"
    )
    await gh.send_to_superusers(repo)


group_decrease_event = sv.on_notice()


@group_decrease_event.handle()
async def _group_decrease_event(bot: Bot, event: GroupDecreaseNoticeEvent) -> None:
    user_nike = (await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id))["nickname"]
    await group_decrease_event.finish(f"{user_nike} 离开了")


group_increase_event = sv.on_notice()


@group_increase_event.handle()
async def _group_increase_event(bot: Bot, event: GroupIncreaseNoticeEvent) -> None:
    # TODO 暂时不考虑欢迎消息追加 头像
    repo = "欢迎新人 " + MessageSegment.at(event.user_id)
    await group_increase_event.finish(repo)