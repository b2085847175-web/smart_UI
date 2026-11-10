"""在线：授权授/撤与批量。授权对象只允许三家 UI 店。

前置：UI_TEST_EMPLOYEE_USERNAME / UI_TEST_EMPLOYEE_PASSWORD 为普通员工或质检员账号。
超管没有授权抽屉，不能用于本文件。
"""
import os
import re

import pytest
from playwright.sync_api import expect

from tests.support.data import AUTH, SHOPS

pytestmark = pytest.mark.online

DRAWER = ".ant-drawer-content:visible"


@pytest.fixture(scope="module")
def employee_page(browser, config, browser_context_args):
    username = os.getenv("UI_TEST_EMPLOYEE_USERNAME", "")
    password = os.getenv("UI_TEST_EMPLOYEE_PASSWORD", "")
    if not username or not password:
        pytest.skip("缺少 UI_TEST_EMPLOYEE_USERNAME / UI_TEST_EMPLOYEE_PASSWORD，跳过授权用例")
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    base = config["base_url"].rstrip("/")
    page.goto(base + "/login", wait_until="domcontentloaded")
    page.locator("#login_username").fill(username)
    page.locator("#login_password").fill(password)
    page.locator("button[type=submit]").click()
    page.wait_for_url(base + "/", timeout=30000)
    yield page
    context.close()


def _open_auth_drawer(page, account: str):
    page.goto(page.url.split("/login")[0] + "/accounts", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    row = page.get_by_role("row").filter(has_text=account).first
    row.get_by_text("店铺授权", exact=True).first.click()
    drawer = page.locator(DRAWER).first
    expect(drawer).to_be_visible()
    hint = page.get_by_text("超级管理员已拥有所有店铺的授权", exact=True)
    if hint.count():
        pytest.skip("当前账号是超管，没有可操作的授权抽屉")
    return drawer


def _tab(drawer, name: str):
    drawer.get_by_role("tab", name=re.compile(name)).first.click()
    return drawer


def _shop_rows(drawer, shop_name: str):
    return drawer.get_by_role("row").filter(has_text=shop_name)


@pytest.mark.parametrize("key", ["B1", "A1", "A2"])
def test_grant_then_revoke_single_shop(employee_page, key):
    """未授权→授权→回到未授权，逐店验证，断言页签迁移。"""
    shop = SHOPS[key]
    page = employee_page
    drawer = _open_auth_drawer(page, os.getenv("UI_TEST_EMPLOYEE_ACCOUNT", ""))
    _tab(drawer, "未授权店铺")
    rows = _shop_rows(drawer, shop["name"])
    if rows.count() == 0:
        # 已授权时先撤销，保证能走通“未授权→授权”
        _tab(drawer, "已授权店铺")
        _shop_rows(drawer, shop["name"]).first.get_by_text("取消授权", exact=True).first.click()
        page.wait_for_timeout(800)
        _tab(drawer, "未授权店铺")
        rows = _shop_rows(drawer, shop["name"])
    expect(rows).to_have_count(1)
    rows.first.get_by_text("授权", exact=True).first.click()
    page.wait_for_timeout(1000)

    _tab(drawer, "已授权店铺")
    expect(_shop_rows(drawer, shop["name"])).to_have_count(1)

    _tab(drawer, "未授权店铺")
    expect(_shop_rows(drawer, shop["name"])).to_have_count(0)


def test_batch_grant_and_batch_revoke_three_shops(employee_page):
    """批量授权/取消只勾这三家；不允许勾选白名单以外的店。"""
    page = employee_page
    drawer = _open_auth_drawer(page, os.getenv("UI_TEST_EMPLOYEE_ACCOUNT", ""))
    _tab(drawer, "未授权店铺")

    granted = 0
    for key in ("B1", "A1", "A2"):
        rows = _shop_rows(drawer, SHOPS[key]["name"])
        if rows.count() == 0:
            continue
        rows.first.locator("input[type=checkbox]").first.check()
        granted += 1
    assert granted > 0, "三家店都已在已授权，无法验证批量授权"

    drawer.get_by_role("button", name=re.compile("批量授权")).first.click()
    page.wait_for_timeout(1200)

    _tab(drawer, "已授权店铺")
    for key in ("B1", "A1", "A2"):
        expect(_shop_rows(drawer, SHOPS[key]["name"])).to_have_count(1)

    revoked = 0
    for key in ("B1", "A1", "A2"):
        rows = _shop_rows(drawer, SHOPS[key]["name"])
        if rows.count() == 0:
            continue
        rows.first.locator("input[type=checkbox]").first.check()
        revoked += 1
    drawer.get_by_role("button", name=re.compile("批量取消授权")).first.click()
    page.wait_for_timeout(1200)

    _tab(drawer, "未授权店铺")
    for key in ("B1", "A1", "A2"):
        expect(_shop_rows(drawer, SHOPS[key]["name"])).to_have_count(1)
