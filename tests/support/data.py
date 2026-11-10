"""加载 data/ 下的测试数据定义；所有用例只从这里取店铺、夹具和对话清单。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def _load(relative: str) -> dict:
    path = DATA / relative
    if not path.is_file():
        raise FileNotFoundError(f"缺少测试数据文件: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


SHOPS_DOC = _load("shops.json")
PERMANENT = _load("fixtures/permanent.json")
EPHEMERAL = _load("fixtures/ephemeral.json")
AUTH = _load("fixtures/auth.json")
TALK = _load("fixtures/talk-cases.json")

SITE = SHOPS_DOC["site"]
SHOPS = {shop["key"]: shop for shop in SHOPS_DOC["shops"]}
DEFAULT_SHOP = next(k for k, v in SHOPS.items() if v["id"] == SHOPS_DOC["default_shop_id"])


def shop(key: str) -> dict:
    try:
        return SHOPS[key]
    except KeyError:
        raise ValueError(f"未知店铺代号: {key}") from None


def shop_names() -> set:
    return {item["name"] for item in SHOPS.values()}
