import shutil
import nonebot
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import (
    MessageEvent,
    GroupMessageEvent
)
from nonebot.message import run_preprocessor

from lin.log import logger
from lin.service import SERVICES_DIR, ServiceManager as sv
from lin.exceptions import IgnoreException, PluginDisableException

PLUGIN_INFO_DIR = SERVICES_DIR

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