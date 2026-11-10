"""智言客服Agent - 商品管理页 /product-config（知识库管理 > 商品管理）

页面元素（2026-10-16 探测确认，以商品 855353284512 为样本）：
- 列表：商品表格 + 搜索框（商品ID/标题、货品编码）+ 批量操作/新增商品
- 行内操作：编辑、添加话术、商品属性、图片管理、删除
- 编辑 -> .ant-modal「编辑商品信息」：商品ID/货品编码/商品标题/商品名称输入框，
  商品状态/是否推荐（radio+下拉），取消/确定
- 添加话术 -> 弹层「商品知识」：页签 已配置知识/未配置知识，
  搜索框（请输入商品知识名称搜索），按钮 清空商品知识，1 个下拉
- 商品属性 -> 弹层「商品属性」：属性名搜索框，按钮 添加属性/编辑/删除，1 个下拉
- 图片管理 -> 弹层「商品图片管理」：内容搜索框，按钮 智能识别，2 个下拉
- 删除 -> .ant-popconfirm 气泡确认「确认删除/确定要删除这个商品吗？」，取消/确认
  （注意：删除是真实删除，用例中默认只点取消）
- 批量操作（右上角下拉）：导入属性 / 导出属性 / 导入商品状态 / 导出商品状态
- 新增商品（右上角）-> .ant-modal「新增商品信息」：表单字段与编辑弹窗一致
  （商品ID/货品编码/商品标题/商品名称/商品状态/是否推荐），取消/确定
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductConfigPage(BasePage):
    PATH = "/product-config"

    # ---------- 列表页 ----------
    SEARCH_PRODUCT_INPUT = "input[placeholder='请输入商品ID、商品标题搜索']"
    SEARCH_STOCK_INPUT = "input[placeholder='请输入货品编码搜索']"
    BATCH_BUTTON = "button:has-text('批量操作')"
    ADD_PRODUCT_BUTTON = "button:has-text('新增商品')"

    # ---------- 批量操作下拉项 ----------
    BATCH_MENU_ITEM = ".ant-dropdown-menu-item:visible:has-text('{name}')"
    BATCH_IMPORT_ATTR = "导入属性"
    BATCH_EXPORT_ATTR = "导出属性"
    BATCH_IMPORT_STATUS = "导入商品状态"
    BATCH_EXPORT_STATUS = "导出商品状态"

    # ---------- 新增商品弹窗（字段与编辑弹窗相同，复用 EDIT_* 输入框） ----------
    ADD_MODAL = ".ant-modal:has-text('新增商品信息')"

    # ---------- 行内操作按钮（配合 row_by_id 使用） ----------
    ROW_EDIT = "text=编辑"
    ROW_ADD_SCRIPT = "text=添加话术"
    ROW_ATTR = "text=商品属性"
    ROW_IMAGE = "text=图片管理"
    ROW_DELETE = "text=删除"

    # ---------- 编辑商品弹窗 ----------
    EDIT_MODAL = ".ant-modal:has-text('编辑商品信息')"
    EDIT_PRODUCT_ID_INPUT = "input[placeholder='请输入商品ID']"
    EDIT_TITLE_INPUT = "input[placeholder='请输入商品标题']"
    EDIT_NAME_INPUT = "input[placeholder='请输入商品名称']"
    MODAL_OK = "button:has-text('确 定')"
    MODAL_CANCEL = "button:has-text('取 消')"

    # ---------- 添加话术弹层（商品知识） ----------
    SCRIPT_MODAL = ":visible:has-text('商品知识')"
    SCRIPT_TAB_CONFIGURED = "[role=tab]:has-text('已配置知识')"
    SCRIPT_TAB_UNCONFIGURED = "[role=tab]:has-text('未配置知识')"
    SCRIPT_SEARCH_INPUT = "input[placeholder='请输入商品知识名称搜索']"
    SCRIPT_CLEAR_BUTTON = "button:has-text('清空商品知识')"

    # ---------- 商品属性弹层 ----------
    ATTR_MODAL = ":visible:has-text('商品属性')"
    ATTR_SEARCH_INPUT = "input[placeholder='属性名搜索']"
    ATTR_ADD_BUTTON = "button:has-text('添加属性')"

    # ---------- 图片管理弹层 ----------
    IMAGE_MODAL = ":visible:has-text('商品图片管理')"
    IMAGE_SEARCH_INPUT = "input[placeholder='内容搜索']"
    IMAGE_AI_RECOG_BUTTON = "button:has-text('智能识别')"

    # ---------- 删除气泡确认框 ----------
    DELETE_POPCONFIRM = ".ant-popconfirm:visible"
    DELETE_CONFIRM_TEXT = "确定要删除这个商品吗？"
    DELETE_CANCEL = ".ant-popconfirm button:has-text('取 消')"
    DELETE_OK = ".ant-popconfirm button:has-text('确 认')"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ---------- 导航 ----------
    def open(self):
        """需先展开「知识库管理」父菜单再进入。"""
        menu = self.page.locator("[class*=menu] >> text=知识库管理").last
        try:
            menu.click(timeout=3000)
            self.page.wait_for_timeout(800)
        except Exception:
            pass
        self.page.locator(f"a[href='{self.PATH}']").first.click()

    # ---------- 行定位 ----------
    def row_by_id(self, product_id: str):
        return self.page.locator(f"tr:has-text('{product_id}')").first

    # ---------- 搜索 ----------
    def search_product(self, keyword: str):
        self.fill(self.SEARCH_PRODUCT_INPUT, keyword)
        self.page.keyboard.press("Enter")

    # ---------- 批量操作 ----------
    def open_batch_menu(self):
        self.click(self.BATCH_BUTTON)

    def click_batch_item(self, name: str):
        """name 为 BATCH_* 常量之一，如 BATCH_IMPORT_ATTR。"""
        self.open_batch_menu()
        self.page.locator(self.BATCH_MENU_ITEM.format(name=name)).click()

    # ---------- 新增商品 ----------
    def open_add_modal(self):
        self.click(self.ADD_PRODUCT_BUTTON)

    def fill_product_form(self, product_id: str = "", title: str = "", name: str = ""):
        """新增/编辑弹窗共用表单。"""
        if product_id:
            self.fill(self.EDIT_PRODUCT_ID_INPUT, product_id)
        if title:
            self.fill(self.EDIT_TITLE_INPUT, title)
        if name:
            self.fill(self.EDIT_NAME_INPUT, name)

    # ---------- 行内操作 ----------
    def click_row_action(self, product_id: str, action: str):
        """action 为 ROW_* 常量之一。"""
        self.row_by_id(product_id).locator(action).first.click()

    # ---------- 弹层通用 ----------
    def cancel_modal(self):
        self.page.locator(self.MODAL_CANCEL).first.click()

    def cancel_delete(self):
        self.page.locator(self.DELETE_CANCEL).first.click()

    # ---------- 断言 ----------
    def should_have_product(self, product_id: str):
        self.should_be_visible(f"tr:has-text('{product_id}')")
