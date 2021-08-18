from itertools import product
from typing import Union, Tuple, TYPE_CHECKING

from nonebot.rule import Rule
from nonebot import get_driver
from nonebot.rule import TrieRule
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event


def to_bot() -> Rule:
    async def _to_bot(bot: Bot, event: Event, state: T_State):
        return event.is_tome()

    return Rule(_to_bot)


def command(service_name: str, *cmds: Union[str, Tuple[str, ...]]) -> Rule:
    r"""
    :说明:

      命令形式匹配，根据配置里提供的 ``command_start``, ``command_sep`` 判断消息是否为命令。

      可以通过 ``state["_prefix"]["command"]`` 获取匹配成功的命令（例：``("test",)``），通过 ``state["_prefix"]["raw_command"]`` 获取匹配成功的原始命令文本（例：``"/test"``）。
      
      通过 ``state["_prefix"]["_service_name"]`` 获取 service_name 进一步判断插件状态

    :参数:

      * ``*cmds: Union[str, Tuple[str, ...]]``: 命令内容

    :示例:

      使用默认 ``command_start``, ``command_sep`` 配置

      命令 ``("test",)`` 可以匹配：``/test`` 开头的消息
      命令 ``("test", "sub")`` 可以匹配”``/test.sub`` 开头的消息

    \:\:\:tip 提示
    命令内容与后续消息间无需空格！
    \:\:\:
    """

    config = get_driver().config
    command_start = config.command_start
    command_sep = config.command_sep
    commands = list(cmds)
    for index, command in enumerate(commands):
        if isinstance(command, str):
            commands[index] = command = (command,)
        if len(command) == 1:
            for start in command_start:
                TrieRule.add_prefix(f"{start}{command[0]}", command)
        else:
            for start, sep in product(command_start, command_sep):
                TrieRule.add_prefix(f"{start}{sep.join(command)}", command)
    async def _command(bot: "Bot", event: "Event", state: T_State) -> bool:
        state["_service_name"] = service_name
        return state["_prefix"]["command"] in commands

    return Rule(_command)