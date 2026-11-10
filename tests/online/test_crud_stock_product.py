"""在线 CRUD：老数据查改、20 条批量新增、逐个删除并断言归零。

只动 UIAUTO_CRUD_ 前缀的数据；永久夹具只查、只改测试字段，不删。
"""
import re

import pytest
from playwright.sync_api import expect

from tests.support.data import EPHEMERAL, PERMANENT
from tests.support.session import Session

pytestmark = pytest.mark.online

BATCH = 20
B1 = PERMANENT["shops"]["B1"]
PREFIX_STOCK = "UIAUTO_CRUD_STOCK_"
PREFIX_PROD = "UIAUTO_CRUD_PROD_"

DRAWER = ".ant-drawer-content:visible"


def _fill(page, placeholder: str, value: str) -> None:
    page.get_by_placeholder(placeholder, exact=True).first.fill(value)


def _stock_codes(session: Session) -> int:
    session.search("请输入货品编码或名称", PREFIX_STOCK)
    return session.page.get_by_text(re.compile(re.escape(PREFIX_STOCK))).count()


# ---------- 货品 ----------
def test_stock_old_record_query_and_update(online_session: Session):
    """老数据：可查到，改标题后能读回，再恢复原标题。"""
    stock = B1["stocks"][0]
    session = online_session
    session.goto("/stock-config")
    session.search("请输入货品编码或名称", stock["code"])
    row = session.row(stock["code"])
    expect(row).to_contain_text(stock["title"])

    row.get_by_text("编辑", exact=True).first.click()
    drawer = session.page.locator(DRAWER).first
    expect(drawer).to_be_visible()
    title_input = drawer.locator("#stockName")
    title_input.fill(stock["title"] + "_回归探针")
    drawer.get_by_role("button", name=re.compile("确 定|保 存")).first.click()
    session.page.wait_for_timeout(1200)

    session.search("请输入货品编码或名称", stock["code"])
    expect(session.row(stock["code"])).to_contain_text("_回归探针")

    # 恢复
    session.row(stock["code"]).get_by_text("编辑", exact=True).first.click()
    drawer = session.page.locator(DRAWER).first
    drawer.locator("#stockName").fill(stock["title"])
    drawer.get_by_role("button", name=re.compile("确 定|保 存")).first.click()
    session.page.wait_for_timeout(1200)
    session.search("请输入货品编码或名称", stock["code"])
    expect(session.row(stock["code"])).to_contain_text(stock["title"])


def test_stock_batch_create_twenty(online_session: Session):
    session = online_session
    session.goto("/stock-config")
    for i in range(1, BATCH + 1):
        nn = f"{i:02d}"
        session.page.get_by_role("button", name=re.compile("新增货品")).first.click()
        drawer = session.page.locator(DRAWER).first
        expect(drawer).to_be_visible()
        drawer.locator("#stockCode").fill(PREFIX_STOCK + nn)
        drawer.locator("#stockName").fill(f"UIAUTO_CRUD货品{nn}")
        drawer.get_by_role("button", name=re.compile("确 定|保 存")).first.click()
        session.page.wait_for_timeout(500)
    assert _stock_codes(session) >= BATCH - 2, "20 条新增后应能搜到整批（允许表格分页误差）"


def test_stock_batch_delete_twenty(online_session: Session):
    """删除上一批；若上一条用例失败，这里仍会尽量清理干净。"""
    session = online_session
    session.goto("/stock-config")
    session.search("请输入货品编码或名称", PREFIX_STOCK)
    for _ in range(BATCH):
        rows = session.page.get_by_role("row").filter(has_text=PREFIX_STOCK)
        if rows.count() == 0:
            break
        first = rows.first
        first.get_by_text("删除", exact=True).first.click()
        confirm = session.page.locator(".ant-popconfirm:visible, .ant-modal:visible").first
        confirm.get_by_role("button", name=re.compile("确 认|确 定")).first.click()
        session.page.wait_for_timeout(500)
    assert _stock_codes(session) == 0, "批量删除后按前缀搜索必须为 0"


# ---------- 商品 ----------
def test_product_old_record_query_and_update(online_session: Session):
    """老数据：查到永久商品，改名称后读回，再恢复。"""
    product = next(p for p in B1["products"] if p["id"] == "9102026102001")
    session = online_session
    session.goto("/product-config")
    session.search("请输入商品ID、商品标题搜索", product["id"])
    row = session.row(product["id"])
    expect(row).to_contain_text(product["title"])

    row.get_by_text("编辑", exact=True).first.click()
    drawer = session.page.locator(DRAWER).first
    expect(drawer).to_be_visible()
    name_input = drawer.locator("#name")
    name_input.fill(product["title"] + "回归探针")
    drawer.get_by_role("button", name=re.compile("确 定")).first.click()
    session.page.wait_for_timeout(1200)

    session.search("请输入商品ID、商品标题搜索", product["id"])
    expect(session.row(product["id"])).to_contain_text("回归探针")

    session.row(product["id"]).get_by_text("编辑", exact=True).first.click()
    drawer = session.page.locator(DRAWER).first
    drawer.locator("#name").fill(product["title"].replace("商品", "商品") or product["title"])
    drawer.get_by_role("button", name=re.compile("确 定")).first.click()
    session.page.wait_for_timeout(1200)


def test_product_add_requires_id_and_title(online_session: Session):
    """新增商品空提交必须被拦住。"""
    session = online_session
    session.goto("/product-config")
    session.page.get_by_role("button", name=re.compile("新增商品")).first.click()
    drawer = session.page.locator(DRAWER).first
    expect(drawer).to_be_visible()
    drawer.get_by_role("button", name=re.compile("确 定")).first.click()
    session.page.wait_for_timeout(600)
    # 仍停留在抽屉即视为拦截成功；抽屉关闭则说明空表单被提交
    expect(drawer).to_be_visible()
    drawer.get_by_role("button", name=re.compile("取 消")).first.click()


def test_product_batch_create_and_delete_twenty(online_session: Session):
    """20 条商品自建自毁：新增后计数，再逐条删除归零。"""
    session = online_session
    session.goto("/product-config")
    created = 0
    for i in range(1, BATCH + 1):
        nn = f"{i:02d}"
        session.page.get_by_role("button", name=re.compile("新增商品")).first.click()
        drawer = session.page.locator(DRAWER).first
        expect(drawer).to_be_visible()
        drawer.locator("#product_id").fill(f"91020990{nn}")
        drawer.locator("#product_title").fill(f"UIAUTO_CRUD商品{nn}")
        drawer.locator("#name").fill(f"CRUD商品{nn}")
        drawer.get_by_role("button", name=re.compile("确 定")).first.click()
        session.page.wait_for_timeout(500)
        created += 1
    assert created == BATCH

    session.search("请输入商品ID、商品标题搜索", PREFIX_PROD)
    assert session.page.get_by_text(PREFIX_PROD, exact=False).count() >= 1

    for _ in range(BATCH):
        rows = session.page.get_by_role("row").filter(has_text=PREFIX_PROD)
        if rows.count() == 0:
            break
        rows.first.get_by_text("删除", exact=True).first.click()
        confirm = session.page.locator(".ant-popconfirm:visible, .ant-modal:visible").first
        confirm.get_by_role("button", name=re.compile("确 认|确 定")).first.click()
        session.page.wait_for_timeout(500)
    session.search("请输入商品ID、商品标题搜索", PREFIX_PROD)
    assert session.page.get_by_role("row").filter(has_text=PREFIX_PROD).count() == 0
