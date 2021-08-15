from .requests import get_bytes


async def qq_avatar(qqid: int, size:int = 5) -> bytes:
    """ 
    获取 qq 头像
    
    :说明:

      ``size``  ------>     ``PX``
      * `1`     ------>     40 x 40
      * `2`	    ------>     40 x 40
      * `3`	    ------>     100 x100
      * `4`	    ------>     140 x140
      * `5`	    ------>     640 x 640
      * `40`    ------>     40 x 40
      * `100`   ------>	    100 x100
    """
    return await get_bytes(f"https://q1.qlogo.cn/g?b=qq&nk={str(qqid)}&s=5")