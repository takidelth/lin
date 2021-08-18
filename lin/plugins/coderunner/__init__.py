from os import stat
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.log import logger
from lin.utils import requests
from lin.service import ServiceManager as sv
from lin.exceptions import ApiException

from .data_source import format_code

API_URL = "https://tool.runoob.com/compile2.php"

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"}

LANGUAGE = {
    "R": [["R", "r", "R语言", "R 语言"], 80],
    "kt": [["kt", "Kotlin", "kotlin"], 19],
    "java": [["java"], 8],
    "cpp": [["cpp", "c++", "C艹", "c艹"], 7],
    "c": [["c", "c语言"], 7],
    "py3": [["py3", "python3", "python"], 15],
    "py": [["py", "py2", "python2"], 0],
}

__doc__ = """
代码执行
使用:
  ------
  /run <语言>
  [--stdin=] 
  <code>
  ------

  <> 表示必选
  [] 表示可选

支持语言如下:
  『r』
  『kotlin』
  『java』
  『cpp』
  『C』
  『py3』
  『py2』
示例:
  /run cpp
  --stdin=Hello World
  #include <iostream>
  
  int main() {
      char str[12];

      std::cin >> str;
      
      std::cout << str;
      
      return 0; 
  }
"""
runner = sv.on_command("/run", __doc__)


@runner.args_parser
async def _get_code(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = event.message
    
    quit_list = ["算了", "算了算了", "罢了", "不了", "不了不了"]
    if msg in quit_list:
        runner.finish("好吧")

    if msg:
        state["msg"] = msg
    else:
        runner.finish("呐...您这样不说明白凌不知道您要干什么呀, 如果是因为不知道怎么使用这个命令的话请使用 /help info run 命令来查看")


@runner.handle()
async def _get_code_handle(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = event.message
    
    if msg:
        state["msg"] = msg


@runner.got("msg")
async def _run_code(bot: Bot, event: MessageEvent, state: T_State) -> None:
    msg = str(state["msg"])
    
    stdin = ""
    if "--stdin=" in msg:
        language, stdin, code = msg.split("\n", maxsplit=2)
        stdin = stdin.replace("--stdin=", "")
    else:
        language, code = msg.split("\n", maxsplit=1)

    language = language.strip()
    for key, value in LANGUAGE.items():
        if language in value[0]:
            language = value[1]
            fileext = key
            break
    
    if not fileext:
        runner.finish("QAQ 凌无法执行此代码，请重新检查 <语言> 选项")
    
    form_data = {
        "code": format_code(code),
        "token": "4381fe197827ec87cbac9552f14ec62a",
        "stdin": stdin,
        "language": language,
        "fileext": fileext,
    }

    try:
        result = await requests.post_json(API_URL, headers=HEADERS, data=form_data)
    except:
        ApiException("菜鸟在线编辑器 API 请求时发生错误")
    
    if not result.get("errors", "").strip():
        await runner.finish(result["output"])
    else:
        repo = "运行出错了哦 >_<\n" + result["errors"]
        await runner.finish(repo)