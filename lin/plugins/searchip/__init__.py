import re
import json

from nonebot.typing import T_State
from nonebot.adapters.gocq import Bot, MessageEvent
from pydantic.types import Json

from lin.rule import to_bot
from lin.service import on_command
from lin.utils import requests
from lin.log import logger
from lin.exceptions import ApiException

API_URL = "https://ip.taobao.com/outGetIpInfo"

__doc__ = """
ip 查询
使用:
  /ip <target_ip>
  查询ip <target_ip>
  ip地址 <target_ip>
"""
ip_serch = on_command(
    cmd="/ip", docs=__doc__, aliases={"查询ip", "ip地址"}, rule=to_bot()
)


@ip_serch.args_parser
async def _get_ip(bot : Bot, event : MessageEvent, state : T_State) -> None:
    msg = str(event.message).strip()

    quit_list = ["算了", "算了算了", "罢了", "取消", "不下了"]
    if msg in quit_list:
        ip_serch.finish("好吧")

    if msg:
        state["ip"] = msg
    else:
        ip_serch.reject("发我 ip 啊喂")
        

@ip_serch.handle()
async def handle_first_receive(bot : Bot, event : MessageEvent, state : T_State) -> None:
    msg = str(event.message).strip()
    if msg:
        state["ip"] = msg


@ip_serch.got("ip", prompt="要把ip发给凌，才能帮你搜索喔")
async def _handle(bot : Bot, event : MessageEvent, state : T_State) -> None:
    msg = state["ip"]
    result = re.search('[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', str(msg))
    if result:
        # 校验ip 是否有效
        result = result.group()
        for split in [int(i) for i in result.split(".")]:
            if split > 255:
                ip_serch.reject("无效IP...（")
        
        data = {"ip": result, "accessKey": "alibaba-inc"}
        try:
            res_data = await requests.post_bytes(url=API_URL, data=data)
        except:
            logger.warning("IP 搜索接口返回异常")
            raise ApiException("IP 搜索接口返回异常")

        res_data = json.loads(res_data)["data"]
        repo = (
            f"ip: {res_data.get('ip')}\n"
            f"country: {res_data.get('country')}\n"
            f"city: {res_data.get('city')}\n"
            f"isp: {res_data.get('isp')}"
        )
        logger.info(str(res_data))
        await ip_serch.finish(repo)