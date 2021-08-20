from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import (
    GroupRequestEvent,
    GroupMessageEvent,
    GroupUploadNoticeEvent,
    GroupRecallNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupAdminNoticeEvent,
    GroupBanNoticeEvent
)

from lin.service import ServiceManager as sv


sv.on_notice()