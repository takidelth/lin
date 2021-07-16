from nonebot.adapters.cqhttp import Bot, Event

from lin.rule import to_bot
from lin.plugin import on_command
import requests

from lin.exceptions import ApiException

answerUrl = "http://cx.icodef.com/wyn-nb?v=2"
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
}

__doc__ = """
说明:
  获取网课答案
使用:
  /ans <网课题目内容>
"""

ans = on_command("/ans",__doc__, rule=to_bot())

@ans.handle()
async def first_handle(bot: Bot, event: Event):
    msg = str(event.get_message()).strip()
    data = {
        "question": msg
    }   
    # try:
    response = requests.post(answerUrl, headers=headers, data=data)
    response.raise_for_status()
    if response.status_code == 200:
        res_data = response.json()
        if res_data['code'] != -1:
            ans_data = res_data['data']
            # print(msg)
            # print(res_data)
            await bot.send(
                event=event,
                message=f"{ans_data}",
                at_sender=True
            )
        else:
            await bot.send(
                event=event,
                message="没有找到此题答案喔",
                at_sender=True
            )
    else:
        await ans.finish("网络请求出错啦， 请稍后再试QAQ")    
        