import json
from pathlib import Path
import aiofiles


data_file = Path(__file__).parent / "data.json"


def load_data() -> dict:
    try:
        data = json.loads(data_file.read_bytes())
    except:
        data = {}
        with open(data_file, "w")as f:
            f.write(json.dumps(data, indent=4))
    return data


async def save_data(data: dict) -> None:
    async with aiofiles.open(data_file, "w")as f:
        await f.write(json.dumps(data, indent=4))