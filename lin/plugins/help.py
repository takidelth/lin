import os
import json
from pathlib import Path

from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from lin.service import SERVICES_DIR, on_command
from lin.log import logger
from lin.rule import to_bot

__doc__ = """
帮助
使用:
  /help
  /help list 获取命令列表
  /help info <帮助主体>
"""

help = on_command("/help", __doc__, aliases={"帮助", "usage", "帮帮俺"}, rule=to_bot())


@help.handle()
async def _help_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().split(" ")
    if msg[0] == "":
        repo = (
            # TODO 添加默认 help 帮助消息
            "迷路啦？\n"
            "这是帮助命令的调用方法:\n"
            f"{__doc__}\n"
        )
        await help.finish(repo)

    elif msg[0] == "list":
        repo = ""
        for _, _, files in os.walk(SERVICES_DIR):
            for file in files:
                repo += f"『{file.split('.')[0]}』\n"
        repo = "凌能做的事情如下\n" + repo + "没有反应可能是没有权限或者属于不可触发的命令"
        await help.finish(repo)

    elif msg[0] == "info":
        cmd = msg[1]
        cmd_file = SERVICES_DIR / f"{cmd}.json"
        
        if not cmd_file.exists():
            await help.finish("未找到相关命令")
        
        data = json.loads(cmd_file.read_bytes())
        repo = (
            f"{cmd} INFO:\n"
            f"enable: {data['enable']}\n"
            f"docs: {data['docs']}"
        )
        await help.finish(repo)
    
    else:
        help.finish("未找到相关命令")
