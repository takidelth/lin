import traceback
from typing import Dict

from nonebot.adapters.mirai import Bot, GroupMessage, MessageEvent
from nonebot.adapters.mirai.event import message
from nonebot.rule import to_me
from nonebot.plugin import on_command, on_message
from nonebot.typing import T_State
import nonebot

import os
from .function import random_filename, save_code, check_code_type

bot_cfg = nonebot.get_driver().config

runner = on_command("运行", rule=to_me())

@runner.handle()
async def handle_first_receive(bot : Bot, event : MessageEvent, state: T_State):
    msg = event.message_chain
    
    await runner.finish(run(str(msg)))
    pass


def run(code: str) -> str:
    cType = check_code_type(code)
    path = bot_cfg.code_path
    socSavePath = os.path.join(path, cType)
    if cType == 'unknow':
        return "暂不支持此语言"

    filename = random_filename(cType)
    socPath = save_code(code, filename, socSavePath)
    if cType == 'py':
        return filename + "\n" + str(socPath)
    elif cType  == 'cpp':
        # os.popen("g++ ")
        excFileName = filename.split('.')[0]
        excFilePath = os.path.join(socSavePath, excFileName)
        command = f"g++ {socPath} -o {excFilePath} && " \
                + f"{excFilePath} 2> {os.path.join(path, 'err.log')} > {os.path.join(path, 'output.log')} & " \
                + f"sleep 5 && " \
                + f"pkill {excFileName}"
        return filename + "\n" + str(socPath) + "\n" + command
    pass