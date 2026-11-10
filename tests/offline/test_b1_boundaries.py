"""离线验证跨站/跨店保护、危险请求拦截和证据完整性。"""
from copy import deepcopy
import pytest

from tests.b1.catalog import load_catalog, validate_catalog
from tests.b1.guard import BASE_URL, SHOP, validate_environment, validate_page
from tests.smoke.safety import ReadOnlyPolicy


def test_catalog_is_traceable():
    data = load_catalog()
    observed = [c for c in data["scenarios"] if c["status"] != "planned"]
    assert len({c["ledger_record"] for c in observed}) == len(observed)
    for c in data["scenarios"]:
        if c["automation"] != "manual_only":
            assert "本次未运行浏览器自动化" in c["automation"]


@pytest.mark.parametrize("url", ["http://dev.zhiyan.chat", "https://dev.zhiyan.chat.evil.example", "https://other.example", BASE_URL + "/"])
def test_wrong_environment_stops_before_login(url):
    with pytest.raises(ValueError):
        validate_environment(url, SHOP)


@pytest.mark.parametrize("url,shop,platform", [
    ("https://dev.zhiyan.chat.evil.example/product-config", SHOP, "/platformLogo/tmall.png"),
    ("https://dev.zhiyan.chat@evil.example/product-config", SHOP, "/platformLogo/tmall.png"),
    (BASE_URL + "/product-config", "其他店铺", "/platformLogo/tmall.png"),
    (BASE_URL + "/product-config", SHOP, "/platformLogo/jd.png"),
    (BASE_URL + "/login", SHOP, "/platformLogo/tmall.png"),
    (BASE_URL + "/sync", SHOP, "/platformLogo/tmall.png"),
])
def test_wrong_page_shop_or_platform_is_rejected(url, shop, platform):
    with pytest.raises(ValueError):
        validate_page(url, shop, platform)


@pytest.mark.parametrize("path", ["/dashboard", "/product-config", "/stock-config", "/stock-knowledge",
    "/product-group", "/variables", "/replace-word"])
def test_allowed_b1_page(path):
    validate_environment(BASE_URL, SHOP)
    validate_page(BASE_URL + path, SHOP, "/platformLogo/tmall.png")


@pytest.mark.parametrize("method,path", [("POST", "/api/product"), ("DELETE", "/api/product/1"),
    ("GET", "/api/product/delete"), ("GET", "/api/product?operation=delete"), ("POST", "/api/replace-word/update")])
def test_business_writes_are_still_blocked(method, path):
    allowed, _ = ReadOnlyPolicy(BASE_URL).permits(method, BASE_URL + path)
    assert allowed is False


def test_catalog_rejects_invented_execution():
    data = deepcopy(load_catalog())
    case = next(c for c in data["scenarios"] if c["status"] == "planned")
    case["actual"] = "已通过"
    with pytest.raises(ValueError, match="不能带已执行结论"):
        validate_catalog(data)


def test_catalog_rejects_evidence_escape():
    data = deepcopy(load_catalog())
    data["scenarios"][0]["evidence"] = ["../../pytest.ini"]
    with pytest.raises(ValueError, match="证据文件缺失或越界"):
        validate_catalog(data)
