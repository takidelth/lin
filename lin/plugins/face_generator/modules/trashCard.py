# from https://github.com/djkcyl/trashCard
import os
import json
from io import BytesIO
from pathlib import Path
from datetime import datetime
from typing import Dict, Union
from PIL import Image, ImageFont, ImageDraw

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event, MessageEvent, GroupMessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.rule import to_bot
from lin.service import ServiceManager as sv
from lin.utils.api import get_qq_avatar
from lin.log import logger

SRC_PATH = Path(__file__).parent / "src"
IMG_PATH = Path(__file__).parent / "img/card"
os.makedirs(IMG_PATH, exist_ok=True)
DAT_PATH = IMG_PATH / "data.json"

__doc__ = """
废物证生成, 我是个fw 5555
此功能基于 A60佬 的源码基础进行了修改 
源项目地址： https://github.com/djkcyl/trashCard
使用：
    trashcard
    tc
    废物证
    
    换新:
    trashcard 换新
    tc 换新
    废物证 换新

""" + str(MessageSegment.image(f"file://{str(IMG_PATH / 'temp.png')}"))


class TrashCard:
    

    def loadCardList() -> Dict[int, Dict[Union[str, int], Union[str, int]]]:
        try:
            data = json.loads(DAT_PATH.read_bytes())
        except:
            data = dict()
            with open(DAT_PATH, "w")as f:
                f.write(json.dumps(data, indent=4))
        return data


    @classmethod
    def saveCard(cls,
                    qqid: str, 
                    qqnick: str, 
                    id: int, 
                    time: str,
                    groupname: str = ""
                ) -> None:

        cls.cardList[qqid] = {
            "qqnick": qqnick,
            "groupname": groupname,
            "id": id,
            "time": time
        }
        with open(DAT_PATH, "w")as f:
            f.write(json.dumps(cls.cardList, indent=4))


    @classmethod
    def cardIsExists(cls, qqid: str) -> bool:
        if cls.cardList.get(qqid, None):
            return True
        else:
            return False 


    @classmethod
    async def drawCard(cls, qqid: str, qqnick: str, groupname: str, id: int, time: str) -> None:
        """默认存储在 ``./img/`` 目录下"""
        # 打开模板图
        template = Image.open(str(SRC_PATH / 'template.png'))
        # 设置字体
        msyhbdFont60 = ImageFont.truetype(str(SRC_PATH / 'msyhbd.ttc'), 60)
        FZDBSJWFont34 = ImageFont.truetype(str(SRC_PATH / 'FZDBSJW.TTF'), 34)
        JetBrainsMonoExtraBoldFont68 = ImageFont.truetype(str(SRC_PATH / 'JetBrainsMono-ExtraBold.ttf'), 68)
        JetBrainsMonoExtraBoldFont64 = ImageFont.truetype(str(SRC_PATH / 'JetBrainsMono-ExtraBold.ttf'), 64)
        JetBrainsMonoExtraBoldFont32 = ImageFont.truetype(str(SRC_PATH / 'JetBrainsMono-ExtraBold.ttf'), 32)
        # 填入头像
        avatarContent = await get_qq_avatar(qqid)
        avatarBio = BytesIO()
        avatarBio.write(avatarContent)
        avatarImg = Image.open(avatarBio)
        avatarImg180 = avatarImg.resize((180, 180))
        avatarBox = (80, 80)
        template.paste(avatarImg180, avatarBox)
        # 填入文字
        qqnick = await cls.getCutStr(qqnick, 11)
        groupname = await cls.getCutStr(groupname, 10)
        draw = ImageDraw.Draw(template)
        draw.text((180, 510), str(id).rjust(10, "0"), font=JetBrainsMonoExtraBoldFont68, fill='black')
        draw.text((332, 88), qqid, font=JetBrainsMonoExtraBoldFont64, fill='black')
        draw.text((330, 172), qqnick, font=msyhbdFont60, fill='black')
        draw.text((625, 318), groupname, font=FZDBSJWFont34, fill="black")
        draw.text((625, 368), time, font=JetBrainsMonoExtraBoldFont32, fill='black')
        template.save(str(IMG_PATH / f'{id}.png'))
        return


    @classmethod
    async def getCutStr(cls, string: str, cut: str) -> str:
        si = 0
        i = 0
        cutStr = ""
        for s in string:
            if '\u4e00' <= s <= '\u9fff':
                si += 1.5
            else:
                si += 1
            i += 1
            if si > cut:
                cutStr = string[:i] + '....'
                break
            else:
                cutStr = string
        
        return cutStr
    
    
    @classmethod
    async def sendCard(cls, qqid: str) -> None:
        cardPath = IMG_PATH / f"{cls.cardList[qqid]['id']}.png"
        await TrashCard.trashCard.send(MessageSegment.image(f"file://{str(cardPath)}"))


    @classmethod
    async def drawCardToSendProc(cls, bot: Bot, event: MessageEvent, is_first: bool = True) -> None:
        qqid: str = str(event.user_id)
        qqnick: str = event.sender.nickname
        groupname: str = ""
        if isinstance(event, GroupMessageEvent):
            groupname: str = (await bot.get_group_info(group_id=event.group_id, no_cache=True))["group_name"]
        id: int = len(cls.cardList.keys()) + 1 if is_first else cls.cardList[qqid]['id']
        time: str = datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")

        cls.saveCard(qqid, qqnick, id, time, groupname)

        # draw
        await TrashCard.drawCard(qqid, qqnick, groupname, id, time)
        # send
        await TrashCard.sendCard(qqid)
        

    cardList = loadCardList()
    trashCard = sv.on_command(cmd="trashcard", aliases={"tc", "废物证"})    


    @trashCard.handle()
    async def _handle(bot: Bot, event: MessageEvent) -> None:
        qqid: str = str(event.user_id)
        msg = str(event.message).strip()

        if TrashCard.cardIsExists(qqid) and "换新" in msg:
            await TrashCard.drawCardToSendProc(bot, event, is_first=False)
            await TrashCard.trashCard.finish("呐, 这是阁下新的废物证， 好好保存哦")
        elif TrashCard.cardIsExists(qqid):
            await TrashCard.sendCard(qqid)
            await TrashCard.trashCard.finish("阁下已经有一张了， 如果想要重新生成可以回复 '废物证 换新'")
        elif (not TrashCard.cardIsExists(qqid)) and "换新" in msg:
            await TrashCard.trashCard.reject("阁下暂时还没有废物证，回复 '是' 凌可以为你生成一张哦")
        else:
            await TrashCard.drawCardToSendProc(bot, event)