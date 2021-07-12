from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.event import Sender
from nonebot.rule import to_me
from nonebot.plugin import on_command
import requests

answerUrl = "http://cx.icodef.com/wyn-nb?v=2"
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
}

ans = on_command("问", aliases={"答案", "ans", "题库"}, rule=to_me(), priority=5)

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
    # except:
    #     await ans.finish("网络请求出错啦， 请稍后再试")
        