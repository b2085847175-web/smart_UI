"""环境与店铺护栏：只允许开发站与三家 UI 店，越界立即报错，不访问页面。"""
from urllib.parse import urlsplit

from .data import SITE, SHOPS, shop_names


class GuardError(RuntimeError):
    pass


def validate_base_url(url: str) -> None:
    if url.rstrip("/") != SITE:
        raise GuardError(f"只允许 {SITE}，当前为 {url}")


def validate_shop(name: str) -> dict:
    name = (name or "").strip()
    for shop in SHOPS.values():
        if shop["name"] == name:
            return shop
    raise GuardError(f"店铺不在三家 UI 白名单内: {name!r}")


def validate_page_url(url: str, shop_name: str) -> None:
    parts = urlsplit(url)
    if (parts.scheme, parts.netloc) != ("https", "dev.zhiyan.chat"):
        raise GuardError(f"页面已离开开发站: {url}")
    validate_shop(shop_name)


def shop_label_ok(label: str) -> bool:
    return label in shop_names()
