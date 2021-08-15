"""
    :说明:
      此插件使用的 ``API`` 是 Tampermonkey 的 "超星王珂住手(改)(查题可用)" 脚本的接口
      https://bbs.tampermonkey.net.cn/forum.php?mod=viewthread&tid=15
"""

from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.message import Message

from lin.rule import to_bot
from lin.utils import requests
from lin.service import on_command
from lin.exceptions import ApiException
from lin.log import logger

API_URL = "http://cx.icodef.com/wyn-nb?v=2"
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Content-type": "application/x-www-form-urlencoded",
    "Authorization": ""
}

__doc__ = """
说明:
  获取 超星网课 答案
使用:
  /ans <网课题目内容>
"""

ans = on_command("/ans",__doc__, rule=to_bot())


@ans.args_parser
async def _get_args(bot: Bot, event: Event, state: T_State) -> None:
    msg = str(event.get_message()).strip()

    quit_list = ["算了", "算了算了", "罢了", "取消", "不下了"]
    if msg in quit_list:
        ans.finish("好吧")
    
    if not msg:
        await ans.reject("题呢？")
    else:
        state["question"] = msg


@ans.handle()
async def first_handle(bot: Bot, event: Event, state: T_State) -> None:
    msg = str(event.get_message()).strip()
    if msg:
        state["question"] = msg


@ans.got("question", prompt="题目呢?")
async def _reply_question(bot: Bot, event: Event, state: T_State) -> None:
    question = state["question"]
    data = {"question": question}

    try:
        res_data = await requests.post_json(API_URL, headers=headers, data=data)
    except:
        logger.warning("题库 API 请求出错, 请检查接口")
        raise ApiException("题库 API 请求出错")
    
    if res_data['code'] != -1:
        user_id = event.get_user_id()
        ans_data = res_data['data']
        repo = f"[CQ:at,qq={user_id}] {ans_data}"
        await ans.finish(Message(repo))
    else:
        ans.finish("题库中没有找到此题答案")
        