"""智言客服Agent - 平台层管理页（选店前后均可访问）

2026-11-10 探测确认。账号/品牌/店铺/店铺分组四页；均无删除的仅品牌、店铺（只有编辑入口）。
店铺授权抽屉：超管提示"已拥有所有店铺的授权"不开抽屉；普通员工/质检员开双 tab 抽屉。
"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import MODAL_CANCEL, MODAL_OK, MODAL_SAVE, ROW_EDIT, ROW_DELETE


class AccountsPage(BasePage):
    """账号管理 /accounts"""
    PATH = "/accounts"
    SEARCH_INPUT = "input[placeholder='请输入账号或姓名搜索']"
    ADD_BUTTON = "button:has-text('新增账号')"
    STATUS_FILTER = ".ant-select:has-text('全部')"
    ROW_EDIT = ROW_EDIT
    ROW_AUTH = "text=店铺授权"
    ROW_DELETE = ROW_DELETE

    # 新增/编辑弹窗（编辑时账号只读、密码变"新密码"）
    ACCOUNT_MODAL = ".ant-modal:has-text('账号信息')"
    ACCOUNT_INPUT = "input[placeholder='请输入账号']"
    NAME_INPUT = "input[placeholder='请输入姓名']"
    PHONE_INPUT = "input[placeholder='请输入电话']"
    PASSWORD_INPUT = "input[placeholder='请输入密码']"
    NEW_PASSWORD_INPUT = "input[placeholder*='新密码']"
    ROLE_SELECT = ".ant-modal .ant-select:has-text('角色')"
    ROLE_OPTIONS = ("超级管理员", "普通员工", "质检员")
    STATUS_SELECT = ".ant-modal .ant-select:has-text('状态')"
    RECEPTION_LABELS = ("全自动接待", "辅助应答", "辅助接待")
    RECEPTION_CHECKBOX = ".ant-modal .ant-checkbox-wrapper:has-text('{name}')"
    SAVE_BUTTON = MODAL_SAVE
    CANCEL_BUTTON = MODAL_CANCEL

    # 店铺授权抽屉（窄视口下 tab 行布局错乱，见 2026-11-10 实测记录）
    AUTH_DRAWER = ".ant-drawer-content:has-text('店铺授权')"
    AUTH_GRANTED_TAB = "[role='tab']:has-text('已授权店铺')"
    AUTH_UNGRANTED_TAB = "[role='tab']:has-text('未授权店铺')"
    AUTH_MORE_TABS = ".ant-tabs-nav-more"
    AUTH_SEARCH_INPUT = ".ant-drawer input[placeholder='请输入店铺名称搜索']"
    AUTH_ROW_GRANT = ".ant-drawer text=授权"
    AUTH_BATCH_CANCEL = "button:has-text('批量取消授权')"
    AUTH_BATCH_GRANT = "button:has-text('批量授权')"
    AUTH_SUPERADMIN_HINT = "超级管理员已拥有所有店铺的授权"

    # 删除确认
    DELETE_MODAL = ".ant-modal:has-text('确认删除')"
    DELETE_MODAL_TEXT = "删除后不可恢复"
    CONFIRM_BUTTON = MODAL_OK


class BrandsPage(BasePage):
    """品牌管理 /brands；只有编辑入口，无删除"""
    PATH = "/brands"
    SEARCH_INPUT = "input[placeholder='请输入品牌名称搜索']"
    ADD_BUTTON = "button:has-text('新增品牌')"
    ROW_EDIT = ROW_EDIT
    BRAND_MODAL = ".ant-modal:has-text('品牌信息')"
    BRAND_NAME_INPUT = ".ant-modal input"
    BRAND_STATUS_TEXT = "启用状态"
    SAVE_BUTTON = MODAL_SAVE
    CANCEL_BUTTON = MODAL_CANCEL


class ShopsPage(BasePage):
    """店铺管理 /shops；只有编辑入口，无删除"""
    PATH = "/shops"
    SEARCH_INPUT = "input[placeholder='请输入店铺名称搜索']"
    PLATFORM_FILTER = ".ant-select:has-text('全部')"          # 电商平台筛选
    LOGIN_FILTER = ".ant-select:has-text('全部登录状态')"
    ADD_BUTTON = "button:has-text('新增店铺')"
    ROW_EDIT = ROW_EDIT

    SHOP_MODAL = ".ant-modal:has-text('店铺信息')"
    SHOP_NAME_INPUT = "input[placeholder*='必须与电商平台的店铺名称保持一致']"
    PLATFORM_SELECT = ".ant-modal .ant-select:has-text('电商平台')"
    INDUSTRY_SELECT = ".ant-modal .ant-select:has-text('所属行业')"
    BRAND_SELECT = ".ant-modal .ant-select:has-text('品牌')"
    BRAND_LINK = ".ant-modal a[href='/brands']"
    STATUS_TEXT = "状态"
    SAVE_BUTTON = MODAL_SAVE
    CANCEL_BUTTON = MODAL_CANCEL
    # 实测可选平台（列表观测值，非下拉全量）
    PLATFORMS = ("淘宝/天猫", "抖音", "京东", "快手", "拼多多")


class ShopGroupPage(BasePage):
    """店铺分组 /shop-group"""
    PATH = "/shop-group"
    SEARCH_INPUT = "input[placeholder='输入店铺分组名称']"
    ADD_BUTTON = "button:has-text('新增分组')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    GROUP_TABLE = ".ant-table"

    # 新增/编辑弹窗（分组名限30字）
    GROUP_MODAL = ".ant-modal:has-text('新增分组'), .ant-modal:has-text('编辑分组')"
    GROUP_NAME_INPUT = "input[placeholder='请输入分组名称']"
    MANAGE_SHOPS_BUTTON = ".ant-modal button:has-text('已添加店铺')"
    SAVE_BUTTON = MODAL_SAVE
    CANCEL_BUTTON = MODAL_CANCEL

    # 管理店铺浮层（已添加/未添加双 tab，含"添加整页"批量）
    MANAGE_PANEL = ".ant-modal:has-text('管理店铺'), .ant-drawer-content:has-text('管理店铺')"
    MANAGE_ADDED_TAB = "[role='tab']:has-text('已添加店铺')"
    MANAGE_UNADDED_TAB = "[role='tab']:has-text('未添加店铺')"
    MANAGE_SHOP_SEARCH_INPUT = "input[placeholder='请输入店铺名称搜索']"
    MANAGE_ADD_ROW = "text=添加"
    MANAGE_ADD_PAGE = "text=添加整页"
    MANAGE_OK = MODAL_OK
    MANAGE_CANCEL = MODAL_CANCEL

    DELETE_CONFIRM = ".ant-popconfirm:visible"
    DELETE_CONFIRM_TEXT = "确定删除该店铺分组吗？"
