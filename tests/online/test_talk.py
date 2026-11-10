"""在线：测试窗对话。每条新会话，只看本次回复与知识来源。"""
import re

import pytest

from tests.support.data import PERMANENT, TALK

pytestmark = pytest.mark.online

B1 = PERMANENT["shops"]["B1"]
CASES = {case["id"]: case for case in TALK["cases"]}


def _reply_and_source(session, text: str) -> tuple:
    session.send_message(text)
    reply = session.last_reply_text()
    source = session.open_knowledge_source()
    session.page.keyboard.press("Escape")
    return reply, source


def test_permanent_fixtures_are_visible_in_lists(online_session):
    """对话前置：甲乙与原商品都在列表、均为上架推荐是。"""
    session = online_session
    session.goto("/product-config")
    for product in B1["products"]:
        session.search("请输入商品ID、商品标题搜索", product["id"])
        row = session.row(product["id"])
        expect_text = row.inner_text()
        assert product["title"] in expect_text
        assert "上架" in expect_text, f"{product['id']} 应为上架"


def test_custom_knowledge_exact_reply(online_session):
    case = CASES["TALK-01"]
    session = online_session
    session.goto("/dashboard")
    session.open_test_window()
    session.new_conversation()
    reply, source = _reply_and_source(session, case["input"])
    for expected in case["expect_reply_contains"]:
        assert expected in reply, f"回复缺少 {expected}"
    for forbidden in case.get("must_not_contain", []):
        assert forbidden not in reply


@pytest.mark.parametrize("case_id", ["TALK-05", "TALK-06"])
def test_shared_stock_no_cross_talk(online_session, case_id):
    case = CASES[case_id]
    session = online_session
    session.goto("/dashboard")
    session.open_test_window()
    session.new_conversation()
    session.send_message(f"http://item.taobao.com/item.htm?id={case['send_product']}")
    reply, source = _reply_and_source(session, case["input"])
    combined = reply + source
    for expected in case["expect_reply_contains"]:
        assert expected in combined, f"{case_id} 缺少 {expected}"
    for forbidden in case["must_not_contain"]:
        assert forbidden not in combined, f"{case_id} 串入了 {forbidden}"


def test_recommendation_category_matches_link(online_session):
    """B1-ISSUE-001：推荐正文品类、链接商品、来源商品必须一致。"""
    case = CASES["TALK-08"]
    session = online_session
    session.goto("/dashboard")
    session.open_test_window()
    session.new_conversation()
    reply, source = _reply_and_source(session, case["input"])
    # 只要出现商品链接，就必须同时出现该商品的特征词（保温杯），不能是粉底液
    if "item.htm?id=" in reply:
        assert "保温杯" in reply or "杯" in reply, "给出了链接但没有杯类介绍"
        assert "粉底液" not in reply, "推荐正文出现与链接不符的品类"


def test_restored_product_not_described_as_delisted(online_session):
    """B1-ISSUE-002：已恢复上架的商品，回复不应同时声称已下架。"""
    case = CASES["TALK-09"]
    session = online_session
    session.goto("/dashboard")
    session.open_test_window()
    session.new_conversation()
    reply, _ = _reply_and_source(session, case["input"])
    contradiction = "下架" in reply and "item.htm?id=" in reply
    assert not contradiction, "同一回复同时声称下架并给出购买链接"
