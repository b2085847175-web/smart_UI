"""在线会话：登录、按白名单选店、逐页校验当前店铺、提供行与测试窗操作。"""
import os
import re

import pytest
from playwright.sync_api import expect

from .data import SITE, SHOPS
from .guard import validate_base_url, validate_shop

DEFAULT_TIMEOUT = 30000


def credentials() -> tuple:
    username = os.getenv("UI_TEST_USERNAME", "")
    password = os.getenv("UI_TEST_PASSWORD", "")
    return username, password


def require_credentials() -> tuple:
    username, password = credentials()
    if not username or not password:
        pytest.skip("缺少 UI_TEST_USERNAME / UI_TEST_PASSWORD，未访问业务站点", allow_module_level=False)
    return username, password


class Session:
    """一个已登录并选定店铺的浏览器会话。"""

    def __init__(self, page, shop: dict):
        self.page = page
        self.shop = shop
        self.timeout = DEFAULT_TIMEOUT

    # ---------- 店铺 ----------
    def assert_shop(self) -> None:
        """只读顶栏用户区，避免把页面内的店铺筛选误当成当前登录店。"""
        selection = self.page.locator(".header-actions .user-info .ant-select-selection-item")
        expect(selection).to_have_count(1)
        text = selection.inner_text().strip()
        validate_shop(text)
        assert text == self.shop["name"], f"当前店铺不是预期：{text} != {self.shop['name']}"

    def goto(self, path: str) -> None:
        self.assert_shop()
        self.page.goto(SITE + path, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        self.assert_shop()

    # ---------- 通用 ----------
    def search(self, placeholder: str, value: str) -> None:
        box = self.page.get_by_placeholder(placeholder, exact=True).first
        box.fill(value)
        box.press("Enter")
        self.page.wait_for_timeout(800)

    def rows(self):
        return self.page.locator("tbody tr[data-row-key], .ant-table-tbody tr.ant-table-row")

    def row(self, text: str):
        """按可见文本精确定位唯一表格行；不唯一直接失败，避免点错数据。"""
        row = self.page.get_by_role("row").filter(has=self.page.get_by_text(text, exact=True))
        expect(row).to_have_count(1)
        return row

    def visible_count(self, text: str) -> int:
        return self.page.get_by_text(text, exact=True).count()

    # ---------- 测试窗 ----------
    def open_test_window(self) -> None:
        self.page.get_by_text("测试窗", exact=True).first.click()
        expect(self.page.get_by_text("客服测试", exact=True).first).to_be_visible()

    def new_conversation(self) -> None:
        self.page.get_by_role("radio", name="plus").click()
        self.page.wait_for_timeout(800)

    def send_message(self, text: str) -> None:
        box = self.page.get_by_placeholder("输入消息...").first
        box.fill(text)
        self.page.get_by_role("button", name=re.compile("发送$")).first.click()
        self.wait_for_reply()

    def wait_for_reply(self, timeout: int = 60000) -> None:
        """等待 AI 回复气泡出现：测试窗回复前有“正在输入”态，这里以发送按钮恢复可用为准。"""
        self.page.wait_for_timeout(1200)
        deadline = timeout
        endpoint = f"locator('.ant-spin-spinning')"
        while deadline > 0:
            if self.page.locator(endpoint).count() == 0:
                self.page.wait_for_timeout(1500)
                return
            self.page.wait_for_timeout(500)
            deadline -= 500
        raise AssertionError("等待测试窗回复超时")

    def last_reply_text(self) -> str:
        bubbles = self.page.locator("div").filter(has=self.page.locator("button:has-text('知识来源')"))
        return bubbles.last.inner_text()

    def open_knowledge_source(self) -> str:
        self.page.locator("button:has-text('知识来源')").last.click()
        self.page.wait_for_timeout(600)
        panel = self.page.locator(".ant-drawer-content:visible, .ant-modal:visible").first
        try:
            return panel.inner_text()
        except Exception:
            return ""


@pytest.fixture(scope="session")
def online_session(request, browser, config, browser_context_args):
    """登录并选 B1；缺少凭据或环境不匹配时整体跳过，不启动业务访问。"""
    if not request.config.getoption("--run-online"):
        pytest.skip("在线用例需 --run-online 显式启用")
    validate_base_url(config["base_url"])
    username, password = require_credentials()
    shop = SHOPS["B1"]
    context = browser.new_context(**{**browser_context_args, "service_workers": "block"})
    context.set_default_timeout(DEFAULT_TIMEOUT)
    page = context.new_page()
    try:
        page.goto(SITE + "/login", wait_until="domcontentloaded")
        page.locator("#login_username").fill(username)
        page.locator("#login_password").fill(password)
        page.locator("button[type=submit]").click()
        page.wait_for_url(SITE + "/", timeout=DEFAULT_TIMEOUT)
        page.get_by_placeholder("输入店铺名称搜索", exact=True).fill(shop["name"])
        card = page.locator("div").filter(has=page.get_by_text(shop["name"], exact=True)).first
        expect(card).to_be_visible()
        card.click()
        page.wait_for_url(SITE + "/dashboard", timeout=DEFAULT_TIMEOUT)
        session = Session(page, shop)
        session.assert_shop()
        yield session
    finally:
        context.close()
