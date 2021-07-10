import traceback
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import Message
from nonebot.rule import to_me
from nonebot.plugin import on_command, on_message
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.mirai.message import MessageSegment

import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.77 '
}  # 请求header
BaiDuWiKi = 'https://baike.baidu.com/item/'

baidu = on_command("百度", aliases={"百度百科", "度娘"}, rule=to_me())

@baidu.handle()
async def handle_first_receive(bot : Bot, event : MessageEvent, state : T_State):
    url = BaiDuWiKi + event.message
    # try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await baidu.finish("不好意思...网络请求出现错误啦， 哎嘿~")
        response.raise_for_status()
    html = response.text
    ans = BeautifulSoup(html, "html.parser").find_all(class_='para')[0].get_text() + '\n' + url
    await baidu.finish(ans)
    # except:
    #     print(response.text)


douban = on_command("豆瓣", priority=5, rule=to_me())
DouBanWiKi = "https://www.douban.com/search?q="

@douban.handle()
async def first_receive(bot: Bot, event: MessageEvent, state: T_State):
    msg = event.get_message()
    url = DouBanWiKi + msg
    reply = ""
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup(class_="result")[0](class_="content")[0]
        mType = content(class_="title")[0].h3.span.string
        title = content(class_="title")[0].h3.a.string
        score = content(class_="rating_nums")[0].string
        subject = content(class_="subject-cast")[0].string
        text = content.p.string

        reply = f"片名:{title}\n类型:{mType}\n导演:{subject}\n豆瓣评分:{score}\n{text}"
    except:
        reply = "俺找不到（理直气壮）"
        reply += "[CQ:image,file=cdeb755a74bfdfacc99b54b2c8ce7bb0.image,url=https://gchat.qpic.cn/gchatpic_new/2929028892/483796300-2503789967-CDEB755A74BFDFACC99B54B2C8CE7BB0/0?term=3]"
        await douban.finish(Message(reply))

    await douban.finish(reply)