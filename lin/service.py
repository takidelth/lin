import os
import re
import json
from datetime import datetime
from types import FunctionType
from typing import Any, Dict, Set, List, Type, Tuple, Union, Optional, TYPE_CHECKING
from pathlib import Path
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.handler import Handler
from nonebot.message import run_preprocessor
from nonebot.permission import Permission, SUPERUSER
from nonebot.typing import T_State, T_Handler, T_RuleChecker
from nonebot.rule import Rule, startswith, endswith, keyword, shell_command, ArgumentParser, regex

from lin.log import logger
from lin.exceptions import IgnoreException, GroupIdInvalidException, FriendIdInvalidException
from lin.config import GocqhttpApiConfig
from lin.utils.requests import post_bytes
from lin.rule import command

SERVICE_DIR = Path(".") / "lin" / "data" / "services"
SERVICES_DIR = SERVICE_DIR / "services"
os.makedirs(SERVICE_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)


class ServiceManager:
    """一个集成的服务类"""
    
    _ban_file: Path = SERVICE_DIR / "ban.json"

    _block_list: dict


    @classmethod
    def init(cls) -> None:
        # 加载 block_list
        cls._block_list = cls.Auth._load_block_list()
        

    @classmethod
    def end(cls) -> None:
        # 保存 block_list
        cls.Auth._save_block_list()


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
        # 保存 各插件状态
        if server_type != "admin_":
            ServiceManager.Status._plugins_status[(data["command"]).replace("/", "")] = data["enable"]
        # 返回插件信息
        return data


    class Status:
        """ 插件状态管理 """
        
        _plugins_status: dict = dict()


        @classmethod
        def set_plugin_status(cls, serivce: str, enable: bool) -> None:
            # 从 plugin_status 中确认 status
            if cls._plugins_status.get(serivce, None) == None and cls._plugins_status.get(serivce) == enable:
                return
            # 找到 插件信息 文件更新 enable 
            file = SERVICES_DIR / f"{serivce}.json"
            data = json.loads(file.read_bytes())
            data["enable"] = enable
            with open(file, "w")as f:
                f.write(json.dumps(data, indent=4))

            cls._plugins_status[serivce] = enable


        @classmethod
        def check_status(cls, service: str) -> bool:
            # 暂未处理 没有这个服务的情况
            return cls._plugins_status.get(service, True)


        @classmethod
        def enable(cls, service: str) -> None:
            cls.set_plugin_status(service, True)

        
        @classmethod
        def disable(cls, service: str) -> None:
            cls.set_plugin_status(service, False)
    

    class Auth:
        """ 权限管理 """
        def _save_block_list() -> None:
            logger.info("正在保存 block_list...")
            with open(ServiceManager._ban_file, "w")as f:
                f.write(json.dumps(ServiceManager._block_list, indent=4))
            logger.info("block_list 保存完成")

        
        @staticmethod
        def _load_block_list() -> Dict[str, Dict[str, str]]:
            try:
                data = json.loads(ServiceManager._ban_file.read_bytes())
            except Exception:
                data = {"user":{}, "group":{}}
                with open(ServiceManager._ban_file, "w")as f:
                    f.write(json.dumps(data, indent=4))
            return data


        def check_id(func: FunctionType) -> FunctionType:
            """检查 id 是否存在于 block_list 中的装饰器"""
            def wapper(*args, **kwargs) -> None:
                target_type = func.__name__.split("_")
                target_id = args[0]
                # 检查 id 是否已经存在
                print(ServiceManager.Status._plugins_status)
                if target_type == "group" and ServiceManager.Auth.auth_group(target_id):
                    raise GroupIdInvalidException()
                elif target_type == "user" and ServiceManager.Auth.auth_user(target_id):
                    raise FriendIdInvalidException()
                # TODO 检查 id 是否存在
                func(*args, **kwargs)
            return wapper


        # TODO 检查 群组 和 用户 是否存在
        def auth_user(user_id: str) -> bool:
            return user_id in ServiceManager._block_list["user"]
        

        def auth_group(group_id: str) -> bool:
            return group_id in ServiceManager._block_list["group"]


        @check_id
        def block_user(user_id: str) -> None:
            ServiceManager._block_list["user"][user_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        @check_id
        def unblock_user(user_id: str) -> None:
            ServiceManager._block_list["user"].pop(user_id)


        @check_id
        def block_group(group_id: str) -> None:
            ServiceManager._block_list["group"][group_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        @check_id
        def unblock_group(group_id: str) -> None:
            ServiceManager._block_list["group"].pop(group_id)


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
        ServiceManager._load_service_config(str(cmd), docs, kwargs.get("permission"))
        # 给 state 注入 service_name 方便运行前检查 enable
        return ServiceManager.on_message(command(cmd.replace("/", ""), *commands) & rule, handlers=handlers, **kwargs)


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
