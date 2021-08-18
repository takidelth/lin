import shutil
import nonebot
from pydantic.errors import DecimalError

from lin.log import logger
from lin.service import SERVICES_DIR, ServiceManager as sv

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

    # 保存 block_list 信息
    sv.save_block_list()

@driver.on_startup
async def _startup() -> None:
    pass