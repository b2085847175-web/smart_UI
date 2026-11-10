"""智言客服Agent - 标签管理 https://dev.zhiyan.chat/tag

2026-11-10 探测确认（天猫/儒意官方旗舰店）。
官方分类与官方标签只读，自定义分类/标签支持增删改；判断标准限100字，分类名限15字。
"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import MODAL_CANCEL, MODAL_OK, MODAL_SAVE, ROW_EDIT, ROW_DELETE


class TagPage(BasePage):
    """标签管理 /tag"""
    PATH = "/tag"

    # ---------- 左侧分类树 ----------
    ADD_CATEGORY_BUTTON = "button:has-text('新增分类')"
    CATEGORY_SEARCH_INPUT = "input[placeholder='搜索标签分类']"
    CATEGORY_TREE = ".ant-tree"
    CATEGORY_NODE = ".ant-tree-treenode:has-text('{name}')"
    # 树节点操作按钮 hover 显示，aria-label 带分类全名
    CATEGORY_EDIT = "button[aria-label='编辑{name}']"
    CATEGORY_DELETE = "button[aria-label='删除{name}']"
    CATEGORY_ADD_MODAL = ".ant-modal:has-text('新增分类'), .ant-modal:has-text('编辑分类')"
    CATEGORY_NAME_INPUT = "input[placeholder='请输入分类名称']"
    CATEGORY_NAME_LIMIT = ".ant-modal .ant-typography:has-text('15')"

    # ---------- 右侧标签列表 ----------
    ADD_TAG_BUTTON = "button:has-text('新增标签')"
    TAG_SEARCH_INPUT = "input[placeholder='搜索标签名称']"
    TAG_TABLE = ".ant-table"
    TAG_ROW_EDIT = ROW_EDIT
    TAG_ROW_DELETE = ROW_DELETE
    TAG_ROW_VIEW = "text=查看"
    TAG_SWITCH = "button[role='switch']"
    OFFICIAL_BADGE = "img[alt='官方']"

    # ---------- 新增/编辑标签弹窗 ----------
    TAG_MODAL = ".ant-modal:has-text('新增标签'), .ant-modal:has-text('编辑标签')"
    TAG_NAME_INPUT = "input[placeholder='请输入标签名称']"
    TAG_CATEGORY_SELECT = ".ant-modal .ant-select:has-text('分类')"
    TAG_DESC_INPUT = "input[placeholder='请输入描述']"
    TAG_CRITERIA_INPUT = "textarea[placeholder*='反问质疑客户']"  # 判断标准，占位含格式示例
    TAG_STATUS_SWITCH = ".ant-modal [role='switch']"
    TAG_SAVE_BUTTON = MODAL_SAVE
    TAG_CANCEL_BUTTON = MODAL_CANCEL

    # ---------- 官方标签查看（只读） ----------
    VIEW_FIELDS = ".ant-modal input[disabled], .ant-modal textarea[disabled]"
    VIEW_CLOSE_BUTTON = ".ant-modal button:has-text('关 闭')"

    # ---------- 删除确认 ----------
    DELETE_TAG_CONFIRM = ".ant-popover:has-text('确认删除该标签')"
    DELETE_TAG_CONFIRM_TEXT = "确认删除该标签？ 删除后不可恢复"
    DELETE_CATEGORY_CONFIRM = ".ant-popover:has-text('确认删除该分类')"
    DELETE_CATEGORY_CONFIRM_TEXT = "分类下仍有子分类或标签时无法删除"
    CONFIRM_BUTTON = MODAL_OK

    # ---------- 状态筛选 ----------
    STATUS_FILTER = ".ant-select-selection-item:has-text('全部')"
    STATUS_OPTIONS = ("全部", "启用", "禁用")
