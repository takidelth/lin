from pathlib import Path
from ipaddress import IPv4Address
from datetime import timedelta
from .utils.yaml import load_yml

CONFIG_PATH = Path(".") / "config.yml"
config = load_yml(CONFIG_PATH)

class BotSelfConfig:
    config: dict = config["BotSelfConfig"]
    
    host: IPv4Address = IPv4Address(config.get("host", "127.0.0.1"))
    port: int = int(config.get("port", 8080))
    debug: bool = bool(config.get("debug", False))
    superusers: set = set(config.get("superusers", ["1234567890"]))
    nickname: set = set(config.get("nickname", ["凌"]))
    command_start: set = set(config.get("command_start", [""]))
    command_sep: set = set(config.get("command_sep", ["."]))
    session_expire_timeout: timedelta = timedelta(
        seconds=config.get("session_expire_timeout", 60)
    )


class OtherPluginsConfig:
    config: dict = config["OtherPluginsConfig"]
    
    plugin_ipypreter_image: str = config.get("your_docker_image_tag", "latest") 


RUNTIME_CONFIG = {
    "host": BotSelfConfig.host,
    "port": BotSelfConfig.port,
    "debug": BotSelfConfig.debug,
    "superusers": BotSelfConfig.superusers,
    "nickname": BotSelfConfig.nickname,
    "command_start": BotSelfConfig.command_start,
    "command_sep": BotSelfConfig.command_sep,
    "session_expire_timeout": BotSelfConfig.session_expire_timeout,
    "PLUGIN_IPYPRETER_IMAGE": OtherPluginsConfig.plugin_ipypreter_image
}