"""显式启用、只查询保留样本；无创建/删除/测试窗发消息动作。"""
import os
import re

import pytest
from playwright.sync_api import expect

from tests.smoke.safety import ReadOnlyPolicy
from .guard import BASE_URL, SHOP, READ_PATHS, validate_environment, validate_page


def pytest_collection_modifyitems(config, items):
    selected = [item for item in items if "b1_regression" in item.keywords]
    if not selected:
        return
    if not config.getoption("--run-b1-regression"):
        for item in selected:
            item.add_marker(pytest.mark.skip(reason="B1在线回归需--run-b1-regression"))
    elif (config.getoption("numprocesses", default=None) not in (None, 0, "0")
          or config.getoption("reruns", default=0)):
        raise pytest.UsageError("B1在线回归不允许并行或自动重试")


class B1Run:
    def __init__(self, page, policy):
        self.page = page
        self.policy = policy

    def assert_shop(self):
        # 只检查顶栏，避免把仪表盘的局部店铺筛选误当当前登录店。
        selection = self.page.locator(".header-actions .user-info .ant-select-selection-item")
        expect(selection).to_have_count(1)
        expect(selection).to_have_text(SHOP)
        logo = selection.locator("img")
        expect(logo).to_have_count(1)
        validate_page(self.page.url, selection.inner_text().strip(), logo.get_attribute("src"))
        if self.policy.blocked:
            pytest.fail("只读保护拦截请求；本次不能记为业务通过", pytrace=False)

    def goto(self, path):
        if path not in READ_PATHS:
            raise ValueError("未登记的B1回归路由")
        self.assert_shop()
        self.page.goto(BASE_URL + path, wait_until="domcontentloaded")
        expect(self.page).to_have_url(BASE_URL + path)
        self.assert_shop()

    def row(self, exact_text, scope=None):
        scope = scope if scope is not None else self.page
        row = scope.get_by_role("row").filter(has=self.page.get_by_text(exact_text, exact=True))
        expect(row).to_have_count(1)
        expect(row).to_be_visible()
        return row


@pytest.fixture(scope="session")
def b1_session(request, config, browser_context_args):
    # 动态获取browser：缺少配置/凭据时不会先启动浏览器。
    if not request.config.getoption("--run-b1-regression"):
        pytest.skip("B1在线回归未启用")
    try:
        validate_environment(config["base_url"], SHOP)
    except ValueError as error:
        raise pytest.UsageError(str(error)) from None
    username, password = os.getenv("UI_TEST_USERNAME", ""), os.getenv("UI_TEST_PASSWORD", "")
    if not username or not password:
        raise pytest.UsageError("缺少UI_TEST_USERNAME/UI_TEST_PASSWORD，尚未访问站点")
    browser = request.getfixturevalue("browser")
    context = browser.new_context(**{**browser_context_args, "service_workers": "block", "accept_downloads": False})
    context.set_default_timeout(int(config.get("timeout", {}).get("default", 30000)))
    policy = ReadOnlyPolicy(BASE_URL)
    policy.install(context)
    page = context.new_page()
    run = B1Run(page, policy)
    try:
        try:
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            # 不调用会记录输入值的BasePage.fill；不记录认证截图/trace/storage_state。
            page.locator("#login_username").fill(username)
            page.locator("#login_password").fill(password)
            policy.begin_login(username, password)
            page.locator("button[type=submit]").click()
            page.wait_for_url(BASE_URL + "/")
            policy.end_login()
            page.get_by_placeholder("输入店铺名称搜索", exact=True).fill(SHOP)
            card = page.locator('div:has(> img[src*="tmall"])').filter(has_text=SHOP)
            expect(card).to_have_count(1)
            expect(card.get_by_text(SHOP, exact=True)).to_be_visible()
            card.click()
            page.wait_for_url(BASE_URL + "/dashboard")
            run.assert_shop()
        except Exception:
            # Playwright的fill错误可能包含输入值；认证错误不直接输出原始异常。
            pytest.fail("B1登录或选店失败，请检查凭据、环境和店铺；认证细节不写报告", pytrace=False)
        finally:
            policy.end_login()
        yield run
    finally:
        context.close()


@pytest.fixture
def b1(b1_session):
    b1_session.assert_shop()
    yield b1_session
    b1_session.assert_shop()
