"""智言客服Agent - 首页/主框架 https://dev.zhiyan.chat/

页面元素（2026-10-16 探测确认）：
- 左侧菜单：账号管理/品牌管理/店铺管理/店铺分组/关于我们（a[href]），我的言值（纯展示，无路由）
- 主内容区：充值按钮、店铺名称搜索框
- 右上角：用户下拉（.user-dropdown，hover 展开）：返回选择页、修改密码、退出
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class ZhiYanHomePage(BasePage):
    # ---------- 左侧导航菜单 ----------
    MENU_ACCOUNTS = "a[href='/accounts']"      # 账号管理
    MENU_BRANDS = "a[href='/brands']"          # 品牌管理
    MENU_SHOPS = "a[href='/shops']"            # 店铺管理
    MENU_SHOP_GROUP = "a[href='/shop-group']"  # 店铺分组
    MENU_CONTACT_US = "a[href='/contact-us']"  # 关于我们
    MENU_YANZHI = "span:has-text('我的言值')"   # 我的言值（纯展示，点击不跳转）

    # ---------- 主内容区 ----------
    RECHARGE_BUTTON = "button:has-text('充值')"
    SHOP_SEARCH_INPUT = "input[placeholder='输入店铺名称搜索']"

    # ---------- 右上角用户区 ----------
    USER_AVATAR = ".user-dropdown"                          # hover 展开下拉
    USER_DROPDOWN_BACK = ".ant-dropdown :text('返回选择页')"
    USER_DROPDOWN_CHANGE_PWD = ".ant-dropdown :text('修改密码')"
    USER_DROPDOWN_LOGOUT = ".ant-dropdown li:text('退出'), .ant-dropdown :text('退出')"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ---------- 菜单导航 ----------
    def goto_accounts(self):
        self.click(self.MENU_ACCOUNTS)

    def goto_brands(self):
        self.click(self.MENU_BRANDS)

    def goto_shops(self):
        self.click(self.MENU_SHOPS)

    def goto_shop_group(self):
        self.click(self.MENU_SHOP_GROUP)

    def goto_contact_us(self):
        self.click(self.MENU_CONTACT_US)

    # ---------- 主内容区动作 ----------
    def search_shop(self, keyword: str):
        self.fill(self.SHOP_SEARCH_INPUT, keyword)

    def click_recharge(self):
        self.click(self.RECHARGE_BUTTON)

    # ---------- 用户下拉 ----------
    def open_user_dropdown(self):
        self.page.locator(self.USER_AVATAR).first.hover()

    def logout(self):
        self.open_user_dropdown()
        self.page.locator(self.USER_DROPDOWN_LOGOUT).first.click()

    # ---------- 页面断言 ----------
    def should_be_logged_in(self):
        self.should_be_visible(self.MENU_SHOPS)
        self.should_be_visible(self.USER_AVATAR)
