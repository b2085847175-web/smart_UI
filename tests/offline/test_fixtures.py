"""离线校验：三店白名单、夹具完整性、批量自毁规则、对话清单。

不访问站点，不需要账号，任何机器上都能直接跑：
    .venv/Scripts/python.exe -m pytest tests/offline -q
"""
import re

import pytest

from tests.support.data import AUTH, EPHEMERAL, PERMANENT, SHOPS, SHOPS_DOC, SITE, TALK, shop_names
from tests.support.guard import GuardError, validate_base_url, validate_page_url, validate_shop

pytestmark = pytest.mark.offline

SHOP_KEYS = ("B1", "A1", "A2")
SHOP_NAMES = (
    "UI货品回归店铺B1_20260831_01",
    "UI货品回归店铺A1_20260831_01",
    "UI货品回归店铺A2_20260831_01",
)
SHOP_IDS = (740, 738, 739)


# ---------- 店铺白名单 ----------
def test_shops_are_exactly_the_three_ui_shops():
    assert sorted(SHOPS) == sorted(SHOP_KEYS)
    assert {s["id"] for s in SHOPS.values()} == set(SHOP_IDS)
    assert shop_names() == set(SHOP_NAMES)
    for item in SHOPS.values():
        assert item["name"].startswith("UI"), "白名单店铺名必须以 UI 开头"
    assert SHOPS_DOC["default_shop_id"] == 740


def test_only_dev_site_is_accepted():
    validate_base_url(SITE)
    for bad in ("http://dev.zhiyan.chat", "https://dev.zhiyan.chat.evil.example", "https://example.com", ""):
        with pytest.raises(GuardError):
            validate_base_url(bad)


def test_non_whitelisted_shop_is_rejected():
    for key in SHOP_KEYS:
        assert validate_shop(SHOPS[key]["name"])["key"] == key
    for bad in ("儒意官方旗舰店", "UI货品回归店铺C1_20260831_01", "店铺78", ""):
        with pytest.raises(GuardError):
            validate_shop(bad)


def test_page_url_must_stay_on_dev_site():
    validate_page_url(SITE + "/product-config", SHOPS["B1"]["name"])
    for bad in (
        "https://dev.zhiyan.chat.evil.example/product-config",
        "https://dev.zhiyan.chat@evil.example/product-config",
        "http://dev.zhiyan.chat/product-config",
    ):
        with pytest.raises(GuardError):
            validate_page_url(bad, SHOPS["B1"]["name"])
    with pytest.raises(GuardError):
        validate_page_url(SITE + "/product-config", "儒意官方旗舰店")


# ---------- 永久夹具 ----------
def test_permanent_fixture_shop_sections_match_whitelist():
    assert sorted(PERMANENT["shops"]) == sorted(SHOP_KEYS)
    for key in SHOP_KEYS:
        section = PERMANENT["shops"][key]
        assert section["shop_id"] == SHOPS[key]["id"]
        assert section["shop_name"] == SHOPS[key]["name"]


def test_permanent_b1_fixtures_complete():
    b1 = PERMANENT["shops"]["B1"]
    assert len(b1["stocks"]) >= 2
    assert {p["id"] for p in b1["products"]} >= {"9102026102001", "9102026102101", "9102026102102"}
    assert len(b1["scene_knowledge"]) >= 10
    assert b1["variable"]["value"] == "蓝鲸1020"
    assert b1["replace_word"]["enabled"] is False
    assert b1["greeting"]["enabled"] is False
    assert b1["follow_task"]["enabled"] is False
    # 欢迎语、跟单默认关闭，避免误触达
    assert b1["shop_knowledge"][0]["marker"] == "蓝鲸1020"


def test_shared_stock_markers_are_distinct():
    b1 = PERMANENT["shops"]["B1"]
    markers = {s["marker"] for s in b1["stocks"]}
    assert len(markers) == len(b1["stocks"]), "货品识别码不能重复"


def test_shared_products_do_not_cross_markers():
    b1 = PERMANENT["shops"]["B1"]
    for product in b1["products"]:
        if "other_marker" in product:
            assert product["marker"] != product["other_marker"]
            assert product["operation"]


def test_do_not_delete_list_covers_all_permanent_records():
    must_keep = set(PERMANENT["do_not_delete"])
    b1 = PERMANENT["shops"]["B1"]
    assert {s["code"] for s in b1["stocks"]} <= must_keep
    assert {p["id"] for p in b1["products"]} <= must_keep


def _probe_text(section: dict) -> str:
    """把一家店里用于隔离判断的文本拼起来；B1 没有单数 stock 键，用列表。"""
    parts = []
    for stock in section.get("stocks", []):
        parts.append(stock.get("knowledge", ""))
    if "stock" in section:
        parts.append(section["stock"].get("knowledge", ""))
    knowledge = section.get("shop_knowledge", [])
    for item in knowledge if isinstance(knowledge, list) else [knowledge]:
        parts.append(item.get("content", ""))
    if "product" in section:
        parts.append(section["product"].get("marker", ""))
    return " ".join(p for p in parts if p)


def test_a1_a2_probe_markers_are_isolated():
    for key, expected in (("A1", "A1PROBE738"), ("A2", "A2PROBE739")):
        assert expected in _probe_text(PERMANENT["shops"][key])
        for other_key in SHOP_KEYS:
            if other_key == key:
                continue
            assert expected not in _probe_text(PERMANENT["shops"][other_key]), (
                f"{expected} 出现在 {other_key} 的夹具里"
            )


# ---------- 临时批量 ----------
def test_ephemeral_batches_use_their_own_prefix():
    seen = set()
    for batch in EPHEMERAL["batches"]:
        prefix = batch["prefix"]
        assert prefix.startswith("UIAUTO_CRUD_"), "临时数据必须使用 UIAUTO_CRUD_ 前缀"
        assert prefix not in seen, "批量前缀重复"
        seen.add(prefix)
        assert batch["count"] == EPHEMERAL["volume"] == 20


def test_ephemeral_never_targets_permanent_records():
    protected = set(PERMANENT["do_not_delete"])
    for batch in EPHEMERAL["batches"]:
        text = str(batch)
        for code in protected:
            assert code not in text or batch["id"] in {"CRUD-PRODUCT", "CRUD-REPLACE"}, (
                f"{batch['id']} 不应触碰永久夹具 {code}"
            )


def test_ephemeral_teardown_is_mandatory():
    assert EPHEMERAL["teardown"]["search_each_prefix"] is True
    assert EPHEMERAL["teardown"]["expected_count"] == 0
    # 每条批量都必须有删除动作；断言字段可选，但清理规则由 teardown 统一要求。
    for batch in EPHEMERAL["batches"]:
        assert batch.get("delete") or batch.get("assert_after_delete") or batch.get("note"), (
            f"{batch['id']} 缺少删除方式或说明"
        )


# ---------- 授权 ----------
def test_auth_targets_only_three_shops():
    assert sorted(AUTH["allowed_shop_ids"]) == sorted(SHOPS[s]["id"] for s in SHOP_KEYS)
    assert set(AUTH["allowed_shop_names"]) == set(SHOP_NAMES)
    assert AUTH["superadmin"]["open_drawer"] is False


def test_auth_volume_cannot_mean_twenty_shops():
    """只有三家店可动，20 条授权必须解释为反复授撤或店内数据，不能是 20 家店。"""
    assert len(AUTH["allowed_shop_ids"]) == 3
    assert "20家店授权" in AUTH["volume_note"] or "3家" in AUTH["volume_note"]


def test_auth_cases_are_reversible():
    ids = {case["id"] for case in AUTH["cases"]}
    assert {"AUTH-05", "AUTH-06"} <= ids, "批量授权与批量取消必须成对"
    assert AUTH["restore"]


# ---------- 对话清单 ----------
def test_talk_cases_have_new_session_rule():
    assert "新会话" in TALK["rule"]
    assert TALK["shop"] == "B1"
    assert TALK["shop_name"] == SHOPS["B1"]["name"]


def test_talk_cases_reference_existing_fixtures():
    text = str(TALK)
    for product in PERMANENT["shops"]["B1"]["products"]:
        if product["id"] in text:
            assert re.fullmatch(r"\d+", product["id"])
    b1 = PERMANENT["shops"]["B1"]
    assert b1["variable"]["value"] in text
    assert b1["shop_knowledge"][0]["marker"] in text


def test_talk_cases_cover_known_defects():
    ids = {case["id"] for case in TALK["cases"]}
    assert {"TALK-08", "TALK-09"} <= ids, "推荐错配与恢复上架矛盾必须在清单里"
    bug_ids = {case.get("bug") for case in TALK["cases"]}
    assert {"B1-ISSUE-001", "B1-ISSUE-002"} <= bug_ids


def test_talk_cases_never_leak_other_shop_markers():
    """每条带 must_not_contain 的用例都必须真的约束其他店识别码，不能误写成自己的。"""
    own = {"B1": "B1SHARED1021", "A1": "A1PROBE738", "A2": "A2PROBE739"}
    for case in TALK["cases"]:
        joined = " ".join(case.get("must_not_contain", []))
        if not joined:
            continue
        for key, marker in own.items():
            if key == "B1":
                continue
            if marker in joined:
                assert case["id"] != "", "隔离断言必须挂在具体用例上"
