from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.message import Message
from nonebot.plugin import on_message, on_command
from nonebot.rule import to_me
import requests
from bs4 import BeautifulSoup

scold = on_command("骂我", priority=5, rule=to_me())

scoldUrl = "https://zuanbot.com/api.php?level=min&lang=zh_cn"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "referer": "https://zuanbot.com/"
}

# 找骂
@scold.handle()
async def first_receive(bot: Bot, event: Event):
    responnse = requests.get(scoldUrl, headers=headers)
    reply = f"[CQ:at,qq={event.get_user_id()}]{responnse.text}"
    # print(reply)
    await scold.finish(Message(reply))

# 彩虹屁
caiHongPiUrl = "https://chp.shadiao.app/api.php"
pi = on_command("彩虹屁", rule=to_me(), priority=5)

@pi.handle()
async def first_receive(bot: Bot, event: Event):
    responnse = requests.get(caiHongPiUrl, headers=headers)
    reply = f"[CQ:at,qq={event.get_user_id()}]{responnse.text}"
    # print(reply)
    await scold.finish(Message(reply))


netEaseSaidUrl = "http://www.yduanzi.com/?utm_source=shadiao.app"
netEaseSaid = on_command("网易云段子", aliases={"网易云", "到点"}, priority=5, rule=to_me())

@netEaseSaid.handle()
async def first_receive(bot: Bot, event: Event):
    responnse = requests.get(netEaseSaidUrl, headers=headers)
    soup = BeautifulSoup(responnse.text, "html.parser")
    txt = soup(id="duanzi-text")[0].string
    reply = f"{txt}"
    # print(reply)
    await scold.finish(Message(reply))