"""7个已保留样本的具体断言；本次只完成收集及离线验证，未运行终端浏览器。"""
import re
import pytest
from playwright.sync_api import expect

from .guard import PRODUCT, STOCK

pytestmark = [pytest.mark.regression, pytest.mark.b1_regression]


def product_row(b1):
    b1.goto("/product-config")
    search = b1.page.get_by_placeholder("请输入商品ID、商品标题搜索", exact=True)
    search.fill(PRODUCT)
    search.press("Enter")
    return b1.row(PRODUCT)


def test_product_links_stock(b1):
    row = product_row(b1)
    expect(row).to_contain_text("UIAUTO_20261020保温杯商品")
    expect(row.get_by_text(STOCK, exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="上架", exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="是", exact=True)).to_be_visible()


def test_product_attribute_persisted(b1):
    product_row(b1).get_by_role("button", name=re.compile("商品属性$")).click()
    dialog = b1.page.locator('[role="dialog"]:visible').filter(has_text="商品属性")
    expect(dialog).to_have_count(1)
    row = b1.row("UIAUTO容量", dialog)
    expect(row).to_contain_text("500毫升；食品级304不锈钢；测试识别码B1ATTR1020")
    dialog.get_by_role("button", name="关闭", exact=True).click()
    expect(dialog).to_have_count(0)


def test_product_knowledge_persisted(b1):
    product_row(b1).get_by_role("button", name=re.compile("添加话术$")).click()
    dialog = b1.page.locator('[role="dialog"]:visible').filter(has_text="商品知识")
    expect(dialog).to_have_count(1)
    dialog.get_by_role("tab", name=re.compile("已配置知识")).click()
    expect(dialog).to_contain_text("使用方法")
    expect(dialog).to_contain_text("B1PRODUCT1020")
    expect(dialog).to_contain_text("禁止放入微波炉")
    dialog.get_by_role("button", name="关闭", exact=True).click()
    expect(dialog).to_have_count(0)


def test_stock_title_persisted(b1):
    b1.goto("/stock-config")
    search = b1.page.get_by_placeholder("请输入货品编码或名称", exact=True)
    search.fill(STOCK)
    search.press("Enter")
    row = b1.page.get_by_role("row").filter(has_text=re.compile(r"货品编码:\s*" + re.escape(STOCK) + r"(?![A-Za-z0-9_])"))
    expect(row).to_have_count(1)
    expect(row).to_contain_text("UIAUTO_20261020保温杯货品_已编辑")


def test_group_has_one_product(b1):
    b1.goto("/product-group")
    row = b1.row("UIAUTO_20261020保温杯分组")
    expect(row.get_by_role("cell", name="1", exact=True)).to_be_visible()
    # 唯一自建分组行的商品数量；不对全店总数作常量断言。


def test_variable_is_shop_scoped(b1):
    b1.goto("/variables")
    row = b1.row("UIAUTO礼盒暗号")
    expect(row.get_by_role("cell", name="蓝鲸1020", exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="当前店铺", exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="全部店铺", exact=True)).to_have_count(0)


def test_replacement_is_disabled(b1):
    b1.goto("/replace-word")
    row = b1.row("B1KEY1020")
    expect(row.get_by_role("cell", name="B1REPLACE1020", exact=True)).to_be_visible()
    expect(row.get_by_role("cell", name="停用", exact=True)).to_be_visible()
    expect(row.get_by_role("button", name="启用", exact=True)).to_be_visible()
    expect(row.get_by_role("button", name="停用", exact=True)).to_have_count(0)
