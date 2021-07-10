import traceback
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.rule import to_me
from nonebot.plugin import on_command, on_message
from nonebot.typing import T_State
import re
import requests

ipfinder = on_command("查询ip", aliases={"ip"}, rule=to_me())

@ipfinder.handle()
async def handle_first_receive(bot : Bot, event : MessageEvent, state : T_State):
    msg = event.message
    result = re.search('[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', str(msg))
    receive = None
    if result:
        # 校验ip 是否有效
        result = result.group()
        for split in [int(i) for i in result.split(".")]:
            if split > 255:
                receive = "无效ip, 请重新尝试"
        
        if not receive:
            url = "https://ip.taobao.com/outGetIpInfo"
            data = {
                "ip": result,
                "accessKey": "alibaba-inc"
            }
            response = requests.post(url=url, data=data)
            if response.status_code == 200:
                res_data: dict = response.json()['data']
                receive = f"ip: {res_data.get('ip')}\n" \
                        + f"country: {res_data.get('country')}\n" \
                        + f"city: {res_data.get('city')}\n" \
                        + f"isp: {res_data.get('isp')}"
                # print(res_data)
            else:
                receive = "请求错误"
    else:
        receive = "无效ip, 请重新输入"
    # a = MessageSegment.image(path="C:\\Users\\wh103\\Desktop\\temp\\a.jpg")
    # await bot.send(event=event, message=a)
    await ipfinder.finish(receive)