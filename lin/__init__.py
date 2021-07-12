import nonebot
from nonebot.adapters.cqhttp import Bot as LINGBot
from nonebot.log import logger

from .config import RUNTIME_CONFIG


def asgi():
    return nonebot.get_asgi()


def driver():
    return nonebot.get_driver()


def init():    
    nonebot.init(**RUNTIME_CONFIG)
    driver().register_adapter("cqhttp", LINGBot)
    nonebot.load_plugins("lin/plugins")
    nonebot.load_from_toml("pyproject.toml")
    if RUNTIME_CONFIG["debug"]:
        nonebot.load_plugin("nonebot_plugin_test")
    logger.info(f"""Now running: lin

            \033[31m▏\033[0mn
            █▏ ､⺍
            █▏⺰ʷʷｨ
            █◣▄██◣
            \033[31m◥██████▋
            　◥████ █▎
            　　███▉ █▎
            　◢████◣\033[0m⌠ₘ℩
            　　██◥█◣\≫
            　　██　◥█◣
            　　█▉　　█▊
            　　█▊　　█▊
            　　█▊　　█▋
            　　 █▏　　█▙

""")

def run(app):
    nonebot.run(app=app)
    