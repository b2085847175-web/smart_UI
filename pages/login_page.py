"""示例页面对象：SauceDemo 登录页。"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    # 定位器集中管理，页面变了只改这里
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    def open(self):
        self.goto("/")

    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)
