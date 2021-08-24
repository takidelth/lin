# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 22:19:35 2021

@author: ChiliMud
"""

import os
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment

from lin.service import ServiceManager as sv

SRC_PATH = Path(__file__).parent / "src"
IMG_PATH = Path(__file__).parent / "img/ph"
os.makedirs(IMG_PATH, exist_ok=True)

__doc__ = """
ph 风格图片生成
使用:
  ph <text1> <text2>

例子:
  ph pxxx hub

结果:
""" + str(MessageSegment.image(f"file://{str(IMG_PATH / 'temp.png')}"))


def spacing(check_str, font):
    
    # 用pil内置textsize函数获取字符串长度
    testkinter = Image.new('RGBA', (300, 300))
    test = ImageDraw.Draw(testkinter)
    
    return test.textsize(check_str, font=font)[0]


async def ph_generator(text1, text2):
    
    #配置信息
    rectangle_color = (247, 151, 29)  # 橘色矩形配色
    bg_color = (20,20,20) # 背景色
    font_size = 90 # 字号
    
    # 字体
    ph_font = ImageFont.truetype(str(SRC_PATH / 'NotoSansBold.otf'), size=font_size)
    
    len_text1 = spacing(text1, ph_font)
    len_text2 = spacing(text2, ph_font)
    kinter_width = len_text1 + len_text2 + 110
    kinter_height = font_size + 100
    
    # 画布
    im = Image.new('RGBA',(kinter_width, kinter_height), color=bg_color)
    
    drawObject = ImageDraw.Draw(im)
    
    
    # 画矩形
    x, y = len_text1 + 45, 50
    w, h = len_text2+20, font_size
    r = 20
    
    drawObject.ellipse((x,y,x+r,y+r),fill=rectangle_color)    
    drawObject.ellipse((x+w-r,y,x+w,y+r),fill=rectangle_color)    
    drawObject.ellipse((x,y+h-r,x+r,y+h),fill=rectangle_color)    
    drawObject.ellipse((x+w-r,y+h-r,x+w,y+h),fill=rectangle_color)
        
    drawObject.rectangle((x+r/2,y, x+w-(r/2), y+h),fill=rectangle_color)    
    drawObject.rectangle((x,y+r/2, x+w, y+h-(r/2)),fill=rectangle_color)
    
    # 文字
    drawObject.text((25,50), text1, font=ph_font)
    drawObject.text((len_text1+55, 50), text2, font=ph_font, fill=bg_color)
    
    # 保存    
    im.save(str(IMG_PATH / 'ph.png'))


ph = sv.on_command("ph", docs=__doc__)


@ph.handle()
async def _ph_handle(bot: Bot, event: MessageEvent) -> None:
    msg = str(event.message).split(" ")
    if 2 < len(msg) > 2 :
        await ph.finish("非法参数")
        return
    
    await ph_generator(*msg)
    repo = MessageSegment.image(file=f"file://{str(IMG_PATH / 'ph.png')}")
    await ph.finish(repo)
