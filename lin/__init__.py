import nonebot
from nonebot.adapters.gocq import Bot as LINGBot

from .config import RUNTIME_CONFIG
from .log import logger

def asgi():
    return nonebot.get_asgi()


def driver():
    return nonebot.get_driver()


def init():    
    nonebot.init(**RUNTIME_CONFIG)
    driver().register_adapter("gocq", LINGBot)
    nonebot.load_plugins("lin/plugins")
    nonebot.load_from_toml("pyproject.toml")
    if RUNTIME_CONFIG["debug"]:
        nonebot.load_plugin("nonebot_plugin_test")
    logger.info(f"Now running: lin")

def run(app):
    nonebot.run(app=app)
    