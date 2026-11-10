"""智言客服Agent - 登录页 https://dev.zhiyan.chat/login

页面元素（2026-10-16 探测确认）：
- 账号输入框  #login_username  placeholder=账号
- 密码输入框  #login_password  placeholder=密码
- 登录按钮    button[type=submit]  文本"登 录"
页面无：记住我、忘记密码、扫码登录等额外元素。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class ZhiYanLoginPage(BasePage):
    # ---------- 元素定位器 ----------
    USERNAME_INPUT = "#login_username"
    PASSWORD_INPUT = "#login_password"
    LOGIN_BUTTON = "button[type=submit]"

    PATH = "/login"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ---------- 页面动作 ----------
    def open(self):
        self.goto(self.PATH)

    def login(self, username: str, password: str):
        # BasePage.fill会记录输入值；认证字段直接填充，避免凭据进入日志。
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.click(self.LOGIN_BUTTON)

    # ---------- 页面断言 ----------
    def should_be_on_login_page(self):
        self.should_have_url(self.PATH)
        self.should_be_visible(self.LOGIN_BUTTON)
