"""
    [√]TODO 权限 和 插件 的动态管理
    [√]TODO 重构 部分插件代码
    [ ]TODO 重写 Code Runner 插件
    [√]TODO 整合 plugin 内部函数
    [ ]TODO 添加 定时任务模块
    [ ]TODO 添加 hitokoto(一言) 插件
    [ ]TODO 修改 music 插件 以正则触发
"""
import shutil
import nonebot

from lin.log import logger
from lin.service import SERVICES_DIR, _update_block_list, _load_block_list

PLUGIN_INFO_DIR = SERVICES_DIR

driver = nonebot.get_driver()


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


@driver.on_startup
async def _startup() -> None:
    # load block list
    logger.info("正在加载 block_list...")
    _update_block_list(_load_block_list())
    logger.debug("block_list 加载完成")
