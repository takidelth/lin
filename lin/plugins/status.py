import psutil

from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent

from lin.log import logger
from lin.rule import to_bot
from lin.utils.apscheduler import scheduler
from lin.service import GocqhttpApiServer as hs
from lin.service import ServiceManager as sv


__doc__ = """
检测服务器状态
使用:
    @凌 state
"""
state = sv.on_command("state", docs=__doc__, rule=to_bot())


@state.handle()
async def _state_handle(bot: Bot, event: MessageEvent) -> None:
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    net_sent = psutil.net_io_counters().bytes_sent / 1000000
    net_recv = psutil.net_io_counters().bytes_recv / 1000000
    
    repo = (
        f"\nCpu: {cpu}%\n"
        f"Mem: {mem}%\n"
        f"Disk: {disk}%\n"
        f"NetSent: {net_sent:.2f}MB\n"
        f"NetRecv: {net_recv:.2f}MB"
    )
    await state.finish(repo)


@scheduler.scheduled_job("interval", minutes=20)
async def _() -> None:
    
    logger.info("开始检测服务状态")

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    net_sent = psutil.net_io_counters().bytes_sent / 1000000
    net_recv = psutil.net_io_counters().bytes_recv / 1000000

    msg = ""
    if cpu >= 80:
        msg += "有点累了"
    elif mem >= 80:
        msg += "快要记不下东西了"
    elif disk >= 80:
        msg += "要被塞满了"
    else:
        return

    msg += (
        f"\nCpu: {cpu}%\n"
        f"Mem: {mem}%\n"
        f"Disk: {disk}%\n"
        f"NetSent: {net_sent:.2f}MB\n"
        f"NetRecv: {net_recv:.2f}MB"
    )
    await hs.send_private_msg(user_id=1037447217, message=msg)