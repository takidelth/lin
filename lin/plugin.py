from logging import log
import os
import re
import json
from typing import Set, List, Type, Tuple, Union, Optional, TYPE_CHECKING
from pathlib import Path
from loguru import logger
from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent
from nonebot.adapters import Bot, Event

from nonebot.matcher import Matcher
from nonebot.handler import Handler
from nonebot.message import run_preprocessor
from nonebot.permission import Permission
from nonebot.typing import T_State, T_Handler, T_RuleChecker
from nonebot.rule import Rule, startswith, endswith, keyword, command, shell_command, ArgumentParser, regex
from pydantic.tools import T

from lin.exceptions import IgnoreException

SERVICE_DIR = Path(".") / "lin" / "data" / "services"
SERVICES_DIR = SERVICE_DIR / "services"
os.makedirs(SERVICE_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)


def _load_block_list() -> dict:
    """
    :说明:
        
        读取被禁止使用的用户和群组

    """

    file = SERVICE_DIR / "ban.json"
    try:
        data = json.loads(file.read_bytes())
    except Exception:
        data = {"user":{}, "group":{}}
        with open(file, "w")as f:
            f.write(json.dumps(data, indent=4))
    return data


def _save_block_list(data: dict) -> None:
    """
    :说明:
        
        保存被禁止使用的用户和群组
    """

    file = SERVICE_DIR / "ban.json"
    with open(file, "w")as f:
        f.write(json.dumps(data, indent=4))


def _load_service_config(service: str, docs: str) -> dict:
    file = SERVICES_DIR / (service.replace("/", "") + ".json")
    try:
        data = json.loads(file.read_bytes())
    except Exception:
        data = {
            "command": service,
            "docs": docs,
            "enable": True,
            "disable_user": {},
            "disable_group": {}
        }
        with open(file, "w")as f:
            f.write(json.dumps(data, indent=4))
    return data


def _save_service_config(service: str, data: dict) -> None:
    file = SERVICES_DIR / (service.replace("/", "") + ".json")
    with open(file, "w")as f:
        f.write(json.dumps(data, indent=4))


def on_message(rule: Optional[Union[Rule, T_RuleChecker]] = None,
               permission: Optional[Permission] = None,
               *,
               handlers: Optional[List[Union[T_Handler, Handler]]] = None,
               temp: bool = False,
               priority: int = 1,
               block: bool = True,
               state: Optional[T_State] = None,
               ) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器。

    :参数:

      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    matcher = Matcher.new("message",
                          Rule() & rule,
                          permission or Permission(),
                          temp=temp,
                          priority=priority,
                          block=block,
                          handlers=handlers,
                          default_state=state,
        )
    
    return matcher


def on_notice(rule: Optional[Union[Rule, T_RuleChecker]] = None,
              *,
              handlers: Optional[List[Union[T_Handler, Handler]]] = None,
              temp: bool = False,
              priority: int = 1,
              block: bool = False,
              state: Optional[T_State] = None,
              ) -> Type[Matcher]:
    """
    :说明:

      注册一个通知事件响应器。

    :参数:

      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    matcher = Matcher.new("notice",
                          Rule() & rule,
                          Permission(),
                          temp=temp,
                          priority=priority,
                          block=block,
                          handlers=handlers,
                          default_state=state,
                          )
    
    return matcher


def on_request(rule: Optional[Union[Rule, T_RuleChecker]] = None,
               *,
               handlers: Optional[List[Union[T_Handler, Handler]]] = None,
               temp: bool = False,
               priority: int = 1,
               block: bool = False,
               state: Optional[T_State] = None,
               ) -> Type[Matcher]:
    """
    :说明:

      注册一个请求事件响应器。

    :参数:

      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    matcher = Matcher.new("request",
                          Rule() & rule,
                          Permission(),
                          temp=temp,
                          priority=priority,
                          block=block,
                          handlers=handlers,
                          default_state=state,
                          )
    
    return matcher


def on_startswith(msg: str,
                  rule: Optional[Optional[Union[Rule, T_RuleChecker]]] = None,
                  **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器，并且当消息的**文本部分**以指定内容开头时响应。

    :参数:

      * ``msg: str``: 指定消息开头内容
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    return on_message(startswith(msg) & rule, **kwargs)


def on_endswith(msg: str,
                rule: Optional[Optional[Union[Rule, T_RuleChecker]]] = None,
                **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器，并且当消息的**文本部分**以指定内容结尾时响应。

    :参数:

      * ``msg: str``: 指定消息结尾内容
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    return on_message(endswith(msg) & rule, **kwargs)


def on_keyword(keywords: Set[str],
               rule: Optional[Union[Rule, T_RuleChecker]] = None,
               **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器，并且当消息纯文本部分包含关键词时响应。

    :参数:

      * ``keywords: Set[str]``: 关键词列表
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    return on_message(keyword(*keywords) & rule, **kwargs)


def on_command(cmd: Union[str, Tuple[str, ...]],
               docs: Optional[str] = None,
               rule: Optional[Union[Rule, T_RuleChecker]] = None,
               aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
               **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器，并且当消息以指定命令开头时响应。

      命令匹配规则参考: `命令形式匹配 <rule.html#command-command>`_

    :参数:

      * ``cmd: Union[str, Tuple[str, ...]]``: 指定命令内容
      * ``docs: Optional[str]``: 插件说明
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``aliases: Optional[Set[Union[str, Tuple[str, ...]]]]``: 命令别名
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """

    async def _strip_cmd(bot: "Bot", event: "Event", state: T_State):
        message = event.get_message()
        segment = message.pop(0)
        new_message = message.__class__(
            str(segment).lstrip()[len(state["_prefix"]["raw_command"]):].lstrip()
        )  # type: ignore
        for new_segment in reversed(new_message):
            message.insert(0, new_segment)

    handlers = kwargs.pop("handlers", [])
    handlers.insert(0, _strip_cmd)

    commands = set([cmd]) | (aliases or set())
    _load_service_config(str(cmd), docs)
    return on_message(command(*commands) & rule, handlers=handlers, **kwargs)


def on_shell_command(cmd: Union[str, Tuple[str, ...]],
                     rule: Optional[Union[Rule, T_RuleChecker]] = None,
                     aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
                     parser: Optional[ArgumentParser] = None,
                     **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个支持 ``shell_like`` 解析参数的命令消息事件响应器。

      与普通的 ``on_command`` 不同的是，在添加 ``parser`` 参数时, 响应器会自动处理消息。

      并将用户输入的原始参数列表保存在 ``state["argv"]``, ``parser`` 处理的参数保存在 ``state["args"]`` 中

    :参数:

      * ``cmd: Union[str, Tuple[str, ...]]``: 指定命令内容
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``aliases: Optional[Set[Union[str, Tuple[str, ...]]]]``: 命令别名
      * ``parser: Optional[ArgumentParser]``: ``nonebot.rule.ArgumentParser`` 对象
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """

    async def _strip_cmd(bot: "Bot", event: "Event", state: T_State):
        message = event.get_message()
        segment = message.pop(0)
        new_message = message.__class__(
            str(segment)
            [len(state["_prefix"]["raw_command"]):].strip())  # type: ignore
        for new_segment in reversed(new_message):
            message.insert(0, new_segment)

    handlers = kwargs.pop("handlers", [])
    handlers.insert(0, _strip_cmd)

    commands = set([cmd]) | (aliases or set())
    return on_message(shell_command(*commands, parser=parser) & rule,
                      handlers=handlers,
                      **kwargs)


def on_regex(pattern: str,
             flags: Union[int, re.RegexFlag] = 0,
             rule: Optional[Union[Rule, T_RuleChecker]] = None,
             **kwargs) -> Type[Matcher]:
    """
    :说明:

      注册一个消息事件响应器，并且当消息匹配正则表达式时响应。

      命令匹配规则参考: `正则匹配 <rule.html#regex-regex-flags-0>`_

    :参数:

      * ``pattern: str``: 正则表达式
      * ``flags: Union[int, re.RegexFlag]``: 正则匹配标志
      * ``rule: Optional[Union[Rule, T_RuleChecker]]``: 事件响应规则
      * ``permission: Optional[Permission]``: 事件响应权限
      * ``handlers: Optional[List[Union[T_Handler, Handler]]]``: 事件处理函数列表
      * ``temp: bool``: 是否为临时事件响应器（仅执行一次）
      * ``priority: int``: 事件响应器优先级
      * ``block: bool``: 是否阻止事件向更低优先级传递
      * ``state: Optional[T_State]``: 默认 state


    :返回:

      - ``Type[Matcher]``
    """
    return on_message(regex(pattern, flags) & rule, **kwargs)

@run_preprocessor
async def _check_block(
    matcher: Matcher,
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    ) -> None:
    data = _load_block_list()
    user_id = event.get_user_id()
    
    if user_id in data["user"]:
        logger.info(f"Ignore user: {user_id}")
        raise IgnoreException(f"Ignore user: {user_id}")
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        if group_id in data["group"]:
            logger.info(f"Ignore group: {group_id}")
            raise IgnoreException(f"Ignore group: {group_id}")
    logger.info("ckeck block finished")