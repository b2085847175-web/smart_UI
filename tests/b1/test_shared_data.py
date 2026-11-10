"""共享货品样本的只读断言；在线执行需显式启用，不发送测试消息。"""
import json
import re

import pytest
from playwright.sync_api import expect

from .catalog import ROOT

SAMPLES = json.loads((ROOT / "data/b1/shared-fixtures.json").read_text(encoding="utf-8"))
pytestmark = [pytest.mark.regression, pytest.mark.b1_regression]


def shared_product_row(b1, sample):
    b1.goto("/product-config")
    search = b1.page.get_by_placeholder("请输入商品ID、商品标题搜索", exact=True)
    search.fill(sample["id"])
    search.press("Enter")
    return b1.row(sample["id"])


@pytest.mark.parametrize("sample", SAMPLES["products"], ids=lambda item: item["id"])
def test_shared_stock_link_persisted(b1, sample):
    row = shared_product_row(b1, sample)
    expect(row).to_contain_text(sample["title"])
    expect(row.get_by_text(SAMPLES["stock"]["code"], exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="上架", exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="是", exact=True)).to_be_visible()


@pytest.mark.parametrize("sample", SAMPLES["products"], ids=lambda item: item["id"])
def test_own_product_knowledge_persisted(b1, sample):
    shared_product_row(b1, sample).get_by_role("button", name=re.compile("添加话术$")).click()
    dialog = b1.page.locator('[role="dialog"]:visible').filter(has_text="商品知识")
    expect(dialog).to_have_count(1)
    expect(dialog).to_contain_text(sample["id"])
    dialog.get_by_role("tab", name=re.compile("已配置知识")).click()
    row = b1.row("使用方法", dialog)
    expect(row).to_contain_text(sample["marker"])
    expect(row).to_contain_text(sample["operation"])
    expect(row).not_to_contain_text(sample["other_marker"])
    dialog.get_by_role("button", name="关闭", exact=True).click()
    expect(dialog).to_have_count(0)


def test_shared_stock_knowledge_restored(b1):
    """只打开知识查看抽屉，检查临时更新已恢复；不进入正文编辑。"""
    b1.goto("/stock-knowledge")
    b1.row("使用方法").get_by_role("button", name=re.compile("添加话术$")).click()
    dialog = b1.page.get_by_role("dialog", name="编辑货品知识话术", exact=True)
    expect(dialog).to_be_visible()
    search = dialog.get_by_role("searchbox", name="货品标题/编码", exact=True)
    search.fill(SAMPLES["stock"]["code"])
    search.press("Enter")
    row = dialog.get_by_role("row").filter(
        has=b1.page.get_by_text("货品编码：" + SAMPLES["stock"]["code"], exact=True)
    )
    expect(row).to_have_count(1)
    expect(row).to_contain_text(SAMPLES["stock"]["title"])
    expect(row.get_by_text(SAMPLES["stock"]["knowledge"], exact=True)).to_be_visible()
    expect(row).not_to_contain_text("B1SHAREDUPDATE1021")
    expect(row).not_to_contain_text("五分钟")
    dialog.get_by_role("button", name="关闭", exact=True).click()
    expect(dialog).not_to_be_visible()
