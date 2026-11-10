"""页面对象基类：封装通用操作，所有 Page 继承此类。"""
import re

from playwright.sync_api import Page, expect

from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.log = get_logger(self.__class__.__name__)

    # ---------- 导航 ----------
    def goto(self, path: str = ""):
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path
        self.log.info("打开页面: %s", url)
        self.page.goto(url)

    # ---------- 元素操作 ----------
    def click(self, selector: str):
        self.log.info("点击: %s", selector)
        self.page.click(selector)

    def fill(self, selector: str, value: str):
        self.log.info("输入: %s = %s", selector, value)
        self.page.fill(selector, value)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    # ---------- 断言 ----------
    def should_have_text(self, selector: str, text: str):
        expect(self.page.locator(selector)).to_have_text(text)

    def should_have_url(self, url_part: str):
        expect(self.page).to_have_url(re.compile(re.escape(url_part)))

    def should_be_visible(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible()

    # ---------- 工具 ----------
    def screenshot(self, name: str) -> str:
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path, full_page=True)
        self.log.info("截图已保存: %s", path)
        return path

    def wait_for(self, selector: str, state: str = "visible"):
        self.page.wait_for_selector(selector, state=state)
