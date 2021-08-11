import re
import os
import json
from io import BytesIO
from pathlib import Path
from typing import Optional, Union
from aiohttp.client_exceptions import ServerDisconnectedError
from PIL import Image, ImageFont, ImageDraw
from string import ascii_letters, digits
from random import sample

from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.message import Message, MessageSegment

from lin.log import logger
from lin.service import on_command
from lin.utils.requests import get_bytes
from lin.exceptions import ApiException

SRC_PATH = Path(__file__).parent / "src"
IMG_PATH = Path(__file__).parent / "img/face"
os.makedirs(IMG_PATH, exist_ok=True)

__doc__ = """
黑白表情包生成
使用:
  gface <表情> <底部的文字>

  或者
  
  gface [根据提示发送图片和文字]
  
注: [] 方括号里的内容为提示信息并非参数说明
""" + str(MessageSegment.image(f"file://{str(IMG_PATH / 'temp.png')}"))


class GrayFace:


    @classmethod
    async def translateToJapan(cls, source: str) -> str:
        url = f"http://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl=ja&q={source}"
        data = json.loads(await get_bytes(url))
        return data["sentences"][0]["trans"]


    @classmethod
    async def drawFace(cls, im: Optional[Union[BytesIO, str]], text: str) -> str:
        """默认存放于 ``./img/`` 目录下"""

        if isinstance(im, BytesIO):
            face = Image.open(im)
        face = Image.open(im)
        fWidth, fHeight = face.size
        bgSize = (fWidth, int(fHeight + fHeight*0.18))  # 按比例生成背景层 size
        newFace = Image.new("RGB", size=bgSize, color=(0, 0, 0))

        # 把表情转换成灰图
        face = face.convert("L")
        # 添加到 newFace 
        newFace.paste(face)

        # text 翻译到日语
        try:
            print(text) 
            jpText = await GrayFace.translateToJapan(text)
        except ServerDisconnectedError:
            pass
        except:
            logger.error("Google translate API return result Error")
            raise ApiException("Google translate API return result Error")

        # 创建字体
        fontSize = int((fHeight*0.06))
        ft = ImageFont.truetype(str(SRC_PATH / "msyhbd.ttc"), fontSize)

        # 创建画布 设置文字位置
        draw = ImageDraw.Draw(newFace)
        textStartPos = ((fWidth / 2 - draw.textlength(text, ft) / 2 , fHeight))
        draw.text(textStartPos, text, font=ft)
        textStartPos = ((fWidth / 2 - draw.textlength(jpText, ft) / 2 , fHeight + fontSize + fontSize*0.2))
        draw.text(textStartPos, jpText, font=ft)

        # save 
        filePath = IMG_PATH / f"{text}.png"
        newFace.save(str(filePath))

        return filePath


    @classmethod
    def getImgFileName(cls, msg: str) -> str:
        pattern = re.compile('file=(.+),')
        result = pattern.search(msg)
        if result:
            return result.group(1)
        return None


    gray = on_command(cmd="gface", aliases={"黑白表情包"}, docs=__doc__)


    @gray.args_parser
    async def _getArgs(bot: Bot, event: Event, state: T_State) -> None:
        msg = str(event.get_message()).split(" ")

        if msg[0] in ["罢了", "不要了", "取消"]:
            await GrayFace.gray.finish("好吧")

        imgName = GrayFace.getImgFileName(msg[0])
        if len(msg) == 1:
            if imgName:
                state['img'] = imgName
            else:
                state['txt'] = msg[0]
        else:
            if imgName:
                state['img'] = imgName
            else:
                state['txt'] = msg[1]

    @gray.handle()
    async def _handle(bot: Bot, event: Event, state: T_State) -> None:
        msg = str(event.get_message()).split(" ")
        
        imgName = GrayFace.getImgFileName(msg[0])
        if imgName:
            state['img'] = imgName
        if len(msg) > 1 and msg[1]:
            state['txt'] = msg[1]
        
    
    @gray.got("img", prompt="请发给我需要制作的表情")
    async def _claimImg(bot: Bot, event: Event, state: T_State) -> None:
        pass
        

    @gray.got("txt", prompt="底部要写点什么呢？小可爱")
    async def _claimText(bot: Bot, event: Event, state: T_State) -> None:
        img, txt = state['img'], state['txt']
        imgUrl = (await bot.get_image(file=img))['url']
        imgData = BytesIO(await get_bytes(imgUrl))
        filePath = await GrayFace.drawFace(imgData, txt)
        if filePath.exists():
            repo = MessageSegment.image(f"file://{str(filePath)}")
        else:
            repo = "似乎失败了呢"
        await GrayFace.gray.finish(repo)