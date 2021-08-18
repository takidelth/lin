import os
import re
import json
from datetime import datetime
from types import FunctionType
from typing import Any, Dict, Set, List, Type, Tuple, Union, Optional, TYPE_CHECKING
from pathlib import Path
from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.handler import Handler
from nonebot.message import run_preprocessor
from nonebot.permission import Permission, SUPERUSER
from nonebot.typing import T_State, T_Handler, T_RuleChecker
from nonebot.rule import Rule, startswith, endswith, keyword, command, shell_command, ArgumentParser, regex

from lin.log import logger
from lin.exceptions import IgnoreException, GroupIdInvalidException, FriendIdInvalidException
from lin.config import GocqhttpApiConfig
from lin.utils.requests import post_bytes

SERVICE_DIR = Path(".") / "lin" / "data" / "services"
SERVICES_DIR = SERVICE_DIR / "services"
os.makedirs(SERVICE_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)


def _load_service_config(service: str, docs: str, permission: Permission) -> dict:
    server_type = "admin_" if permission == SUPERUSER else ""
    file = SERVICES_DIR / (server_type + service.replace("/", "") + ".json")
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


class ServiceManager:
    """一个集成的服务类"""


    def __init__(self) -> None:
        
        self._ban_file: Path = SERVICE_DIR / "ban.json"

        self._block_list: dict = self._load_block_list()
    

    def save_block_list(self) -> None:
        logger.info("正在保存 block_list...")
        with open(self._ban_file, "w")as f:
            f.write(json.dumps(self._block_list, indent=4))
        logger.info("block_list 保存完成")


    def _load_block_list(self) -> Dict[str, Dict[str, str]]:
        try:
            data = json.loads(self._ban_file.read_bytes())
        except Exception:
            data = {"user":{}, "group":{}}
            with open(self._ban_file, "w")as f:
                f.write(json.dumps(data, indent=4))
        return data


    def check_id(func: FunctionType) -> FunctionType:
        def wapper(*args, **kwargs) -> None:
            target_type = func.__name__.split("_")
            self: ServiceManager = args[0]
            target_id = args[1]
            # 检查 id 是否已经存在
            if target_type == "group" and self.auth_group(target_id):
                raise GroupIdInvalidException()
            elif target_type == "user" and self.auth_user(target_id):
                raise FriendIdInvalidException()
            func(*args, **kwargs)
        return wapper


    # TODO 检查 群组 和 用户 是否存在
    def auth_user(self, user_id: str) -> bool:
        return user_id in self._block_list["user"]
    

    def auth_group(self, group_id: str) -> bool:
        return group_id in self._block_list["group"]


    @check_id
    def block_user(self, user_id: str) -> None:
        self._block_list["user"][user_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    @check_id
    def unblock_user(self, user_id: str) -> None:
        self._block_list["user"].pop(user_id)


    @check_id
    def block_group(self, group_id: str) -> None:
        self._block_list["group"][group_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    @check_id
    def unblock_group(self, group_id: str) -> None:
        self._block_list["group"].pop(group_id)

    
    @run_preprocessor
    async def _check_block(
        matcher: Matcher,
        bot: Bot,
        event: MessageEvent,
        state: T_State,
        ) -> None:
        user_id = event.get_user_id()
        print(service_manager._block_list)
        if service_manager.auth_user(user_id):
            logger.info(f"Ignore user: {user_id}")
            raise IgnoreException(f"Ignore user: {user_id}")
      
        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group_id)
            if service_manager.auth_group(group_id):
                logger.info(f"Ignore group: {group_id}")
                raise IgnoreException(f"Ignore group: {group_id}")
    

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
        return ServiceManager.on_message(startswith(msg) & rule, **kwargs)


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
        return ServiceManager.on_message(endswith(msg) & rule, **kwargs)


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
        return ServiceManager.on_message(keyword(*keywords) & rule, **kwargs)


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
        _load_service_config(str(cmd), docs, kwargs.get("permission"))
        return ServiceManager.on_message(command(*commands) & rule, handlers=handlers, **kwargs)


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
        return ServiceManager.on_message(shell_command(*commands, parser=parser) & rule,
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
        return ServiceManager.on_message(regex(pattern, flags) & rule, **kwargs)


# ServiceManager 的实例化
service_manager = ServiceManager()


class GocqhttpApiServer:
    """一个 gocqhttp HTTP API 的封装"""

    API_ADDR: str = f"http://{GocqhttpApiConfig.host}:{GocqhttpApiConfig.port}"

    @classmethod
    async def send_private_msg(
        cls,
        user_id: Optional[int] = None, 
        group_id: Optional[int] = None, 
        message=Union[str],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        return await cls.send_msg(message_type="private",
                            user_id=user_id, 
                            group_id=group_id,
                            message=message, 
                            auto_escape=auto_escape
                )
    

    @classmethod
    async def send_group_msg(
        cls,
        user_id: Optional[int] = None, 
        group_id: Optional[int] = None, 
        message=Union[str],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        return await cls.send_msg(message_type="private",
                            user_id=user_id, 
                            group_id=group_id,
                            message=message, 
                            auto_escape=auto_escape
                )


    @classmethod
    async def send_msg(
        cls,
        message_type: Optional[str] = "", 
        user_id: Optional[int] = None, 
        group_id: Optional[int] = None, 
        message=Union[str],
        auto_escape: bool = False
    ) -> Dict[str, Any]:
        url = cls.API_ADDR + "/send_msg?"
        if (not message_type) and group_id != None:
            message_type = "group"
        elif (not message_type) and user_id != None:
            message_type = "private"
        params = {
            "message_type": message_type,
            "user_id": str(user_id),
            "group_id": str(group_id),
            "message": message,
            "auto_escape": str(auto_escape)
        }
        result = json.loads(await post_bytes(url, params=params))
        logger.debug(result)
        return result
