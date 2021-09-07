import json
from pathlib import Path
from random import choice, randint
from datetime import datetime

from lin.utils.requests import get_json


data_file = Path(__file__).parent / "data.json"
API_URL = [
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/a.json",
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/b.json",
    "https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/sentences/c.json",
]


async def bottle_generator() -> dict:
    result = await get_json(choice(API_URL))
    data = {
        "msg": result[randint(0, len(result) - 1)]["hitokoto"],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    return data


def load_bottles() -> list:
    try:
        data = json.loads(data_file.read_bytes())
    except:
        data = []
        with open(data_file, "w")as f:
            f.write(json.dumps(data, indent=4))
    return data


def save_bottles(data: list) -> None:
    with open(data_file, "w")as f:
        f.write(json.dumps(data, indent=4))