"""B1回归的固定环境/店铺边界；与原有只读冒烟互相独立。"""
from urllib.parse import urlsplit

BASE_URL = "https://dev.zhiyan.chat"
SHOP = "UI货品回归店铺B1_20260831_01"
PRODUCT = "9102026102001"
STOCK = "UIAUTO_20261020_STOCK01"
READ_PATHS = frozenset({"/product-config", "/stock-config", "/stock-knowledge", "/product-group", "/variables", "/replace-word"})


def validate_environment(base_url, shop):
    if base_url != BASE_URL or shop != SHOP:
        raise ValueError("B1回归仅允许固定开发站和B1测试店铺")


def validate_page(url, shop, platform):
    parts = urlsplit(url)
    if (parts.scheme, parts.netloc) != ("https", "dev.zhiyan.chat"):
        raise ValueError("页面已离开开发站")
    if parts.path not in READ_PATHS | {"/dashboard"}:
        raise ValueError("页面不在B1回归允许范围")
    if shop != SHOP or platform != "/platformLogo/tmall.png":
        raise ValueError("店铺或平台不匹配，停止B1回归")
