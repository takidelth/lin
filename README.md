
<div align="center">

# QQBot lin

![maven](https://img.shields.io/badge/python-3.8%2B-blue?logo=appveyor&style=for-the-badge)
![maven](https://img.shields.io/badge/nonebot-2.0.0-yellow?logo=appveyor&style=for-the-badge)
![maven](https://img.shields.io/badge/go--cqhttp-v1.0.0--beta5-red?logo=appveyor&style=for-the-badge)

</div>


<br>


## 简介
一个基于 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 和 [nonebot2](https://github.com/nonebot/nonebot2) 的 QQ 姬气人


<br>


## 注意
本项插件目录下的所有插件均可移植, `ServiceManager` 只是方便用于管管理控制插件, 插件的注册方式改成 `nonebot` 自带的函数依然可以正常运行（大概[/doge保命]）

<br>


## 项目特色

~~那当然是毫无特色~~，本项目未经过严格的测试尚有很多的 `BUG` （裂开）


<br>


## 快速上手

<details>
<summary>启动</summary>

~~先这样这样然后再那样那样~~


<br>


## 1. 拉取这个仓库
```sh
git clone https://github.com/takidelth/lin
```

> 加速镜像: 

  - `https://github.com.cnpmjs.org/takidelth/lin`
  - `https://hub.fastgit.org/takidelth/lin`



## 2. 安装环境

1. 进入目录 `cd lin`

2. 安装运行必须的包 `pip install -r requirements.txt`

3. 运行 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

   > 务必开启 http 设置， [此项目配置说明](#配置文件说明)

4. 运行 **lin** `python main.py` 或 `python3 main.py` 



</details>


<details>
<summary>配置文件说明</summary>

## 配置文件说明

```yml
BotSelfConfig:
  host: "127.0.0.1"
  port: 8765        # 监听端口 和 gocqhttp 保持一致
  debug: false      # debug 模式
  superusers: ["1037447217"]    # 管理员 qq 号列表可添加多个账号
  nickname: ["凌", "ling", "lin"]   # 昵称
  command_start: [""]       # 命令起始字符
  command_sep: ["."]        # 命令分隔符
  session_expire_timeout: 60

OtherPluginsConfig:
  plugin_ipypreter_image: "latest"      # ipypreter 插件配置 暂时可以忽略

GocqhttpApiConfig:
  host: "127.0.0.1"     # gocqhttp 运行的地址 （默认本机）
  port: 5700            # gocqhttp http 模式运行的端口

```

</details>


<br>


## 声明
此项目仅用于学习交流， 请勿用于非法用途


<br>


## 功能列表

<details>
<summary>已实现的功能</summary>

### 常用功能
- [x] 运行代码 目前支持 `cpp` `c` `py2` `py3` `R` `kotlin` `java`
- [x] 网易 & QQ 音乐 单曲 『封面』 『歌词』 『歌手』 和部分 『音乐资源』 获取
- [x] 搜索 ip 
- [x] 搜索网课答案
- [x] 获取帮助
- [x] 检查服务器状态
- [x] 一言 (hitokoto)
- [x] 黑白图片生成 （gface）
- [x] gface 灰白图必选 -> 可选
- [x] 废物证生成 [trashCard](https://github.com/djkcyl/trashCard)
- [x] ph_generator 风格图片 生成 (搬运自群友的插件)
- [x] 加群通知
- [x] 添加好友通知 
- [x] 转发撤回的 **好友** 或 **群** 消息给管理员康♂康
- [x] 被**禁言**时通知管理员
- [x] 有群员退出时发送群消息
- [x] 入群欢迎
- [x] 男同关注了你
- [x] 我朋友想...
- [x] news 功能
- [x] 每日签到
- [x] 漂流瓶功能
- [x] 天气查询


<br>


### 管理员功能
- [x] 拉黑 & 解除拉黑 （用户 | 群组） 使其不能再使用任何插件
- [x] 打开 & 关闭 插件
- [x] 处理入群请求
- [x] 处理好友请求
- [x] 群禁言 (单人|全体)
- [x] 设置管理员
- [x] 群组踢人


</details>


<br>


## TODO

 - [ ] setu （待定...）
 - [ ] 回复指定消息撤回
 - [ ] 鲁迅说 （from [HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot)）
 - [ ] pixiv 日榜
 - [ ] 插件订阅
 - [ ] 自动复读 （自动打断待定）
 - [ ] 点歌
 - [ ] 部分插件发送内容调整为图片
 - [ ] 铭感词汇消息过滤（撤回）
 - [ ] Epic 白嫖助手
 - [ ] 积分可用于自助设置群头衔
 - [-] 图片美图分类上传功能 （有空传两张积累自己的图库）暂时鸽了


<br>


## 感谢
 - [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
 - [NoneBot/NoneBot2](https://github.com/nonebot/nonebot2)
 - [Kyomotoi/ATRI](https://github.com/Kyomotoi/ATRI)
 - [djkcyl/trashCard](https://github.com/djkcyl/trashCard)
 - [HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot)
 - [Quan666/ELFChatBot](https://github.com/Quan666/ELFChatBot)
 - [monsterxcn/nonebot_plugin_epicfree](https://github.com/monsterxcn/nonebot_plugin_epicfree)


<br>


## 更新日志


<br>


### 2021-9-16

 - 增加 被风控提示


<br>


### 2021-9-15

 - 修复 群组管理 权限不足报错 `BUG`


<br>


### 2021-9-12

 - 增加 **天气查询**
 - 修复 **全体禁言**逻辑 `BUG`


<br>


### 2021-9-11

 - 增加 **群禁言**
 - 增加 **设置管理员**
 - 增加 **群组踢人**
 - 增加 **好友请求处理**
 - 修复 **废物证**插件回复 `BUG`


<br>


### 2021-9-9

 - 修改 **gface** 插件图片灰白成为可选项


<br>


### 2021-9-8

 - 修复 **block** `BUG`
 - 修复 **签到** `BUG`


<br>


### 2021-9-7

 - 增加 **漂流瓶功能**功能
 - 增加 **入群请求处理**功能
 - 增加 入群请求通知 **时间** & **群昵称**
 - 增加 好友请求通知 **时间** & **好友昵称**
 - 修复 退群通知报错 `BUG`


<br>


### 2021-9-6

 - 增加 **签到**功能
 - 增加 发送上线 `xml 卡片` 功能


<br>


### 2021-9-2

 - 修复 `news` 插件 bug

<br>


### 2021-9-1

 - 增加 `news` 插件: 发送 60s读世界 图片
 - 增加 `requirements.txt` 文件


<br>


### 2021-8-28

 - 调整 插件目录下单个 `__init__.py` 文件构成的插件移动至 `plugins` 目录下 
 - 调整 部分插件 `User-Agent` 获取方式 
 - 调整 部分插件**使用说明**


<br>


### 2021-8-25

 - 增加 我的朋友... 图片生成


<br>


### 2021-8-24

 - 增加 "男同关注了你" 图片生成


<br>


### 2021-8-22

 - 增加 转发撤回的 **好友** 或 **群** 消息给管理员康♂康
 - 增加 被**禁言**时通知管理员
 - 增加 有群员退出时发送退群消息
 - 增加 新的消息群发管理员 API
 - 增加 入群欢迎


<br>


### 2021-8-20
 - 增加 入群请求和邀请入群请求通知自动通知**管理员**
 - 增加 好友请求自动通知**管理员**
 - 增加 主动触发发送服务器状态


<br>


### 2021-8-18

 - 增加 权限插件的**权限管理**和插件**状态管理**


<br>


### 2021-11-24

 - 增加 闲聊功能 (from: https://github.com/Quan666/ELFChatBot)
 - 修改 `news` 插件：更新缓存发送消息 <font color="green">-></font> <font color="yellow">不发送</font>


<br>


### 2021-12-7

 - 增加 `epic` 免费游戏提醒 (fron: https://github.com/monsterxcn/nonebot_plugin_epicfree)
 - 修复 `exceptions.py` 报错群发管理员功能
 - 修改 `config.py` 配置文件
 - 发现 项目过于拉跨准备重构
