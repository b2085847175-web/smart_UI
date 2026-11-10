"""智言客服Agent - 策略管理分组（2026-10-16 探测确认）。"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import (
    MODAL_CANCEL, MODAL_OK, MODAL_SAVE, POPCONFIRM_CANCEL,
    ROW_EDIT, ROW_DELETE,
)


class GreetingPage(BasePage):
    """进店欢迎语 /greeting"""
    PATH = "/greeting"
    SORT_BUTTON = "button:has-text('欢迎语排序')"
    ADD_BUTTON = "button:has-text('新增欢迎语')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    SORT_MODAL = ".ant-modal:has-text('欢迎语排序')"
    GREETING_MODAL = ".ant-modal:has-text('新增欢迎语'), .ant-modal:has-text('编辑欢迎语')"
    NAME_INPUT = "input[placeholder='请输入欢迎语名称']"
    DELETE_POPCONFIRM_TEXT = "确认删除这条欢迎语?"


class VariablesPage(BasePage):
    """自定义变量 /variables"""
    PATH = "/variables"
    SEARCH_INPUT = "input[placeholder='请输入变量名称或内容搜索']"
    IMPORT_BUTTON = "button:has-text('导入')"
    LOG_BUTTON = "button:has-text('操作日志')"
    ADD_BUTTON = "button:has-text('新增变量')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    IMPORT_MODAL = ".ant-modal:has-text('导入变量')"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    ADD_MODAL = ".ant-modal:has-text('新增变量')"
    EDIT_MODAL = ".ant-modal:has-text('编辑变量')"
    DELETE_MODAL = ".ant-modal:has-text('确认删除')"
    NAME_INPUT = "input[placeholder='请输入变量名称']"
    CONTENT_INPUT = "input[placeholder='请输入变量内容']"


class FilterWordsPage(BasePage):
    """屏蔽词管理 /filter-words（文本区+按钮，无表格）"""
    PATH = "/filter-words"
    SEARCH_INPUT = "input[placeholder='输入关键词搜索屏蔽词']"
    COPY_ALL_BUTTON = "button:has-text('复制全部')"
    CLEAR_ALL_BUTTON = "button:has-text('清空全部')"
    ADD_BUTTON = "button:has-text('添加屏蔽词')"
    CLEAR_MODAL = ".ant-modal:has-text('确认清空')"
    ADD_MODAL = ".ant-modal:has-text('添加屏蔽词')"
    WORDS_INPUT = "input[placeholder='输入屏蔽词，多个词可用逗号或空格分隔']"


class ReplaceWordPage(BasePage):
    """替换词管理 /replace-word"""
    PATH = "/replace-word"
    SEARCH_INPUT = "input[placeholder='请输入关键词搜索']"
    ADD_BUTTON = "button:has-text('添加替换词')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    ADD_MODAL = ".ant-modal:has-text('添加替换词规则')"
    EDIT_MODAL = ".ant-modal:has-text('编辑替换词规则')"
    SOURCE_INPUT = "input[placeholder='请输入被替换的关键词']"
    DELETE_POPCONFIRM_TEXT = "确认删除删除后该替换规则将不再生效，是否继续？"


class CommonStrategyPage(BasePage):
    """通用策略 /strategy（纯配置页，无明显按钮，以配置项形式呈现）

    2026-10-16 补测：表单无 .ant-form-item-label，配置项以"标题文字 + 开关（radio 实现）+ 输入框"形式：
    - 客服基础信息：如何称呼买家
    - 重复问答策略：完全相同的答案出现 N 秒内 N 次直接转接人工
    - 采纳相同知识
    - 历史消息记忆量：生成回复时将参考最近 N 句历史聊天记录
    - 订单售后周期：N 天内有有效订单
    """
    PATH = "/strategy"
    # 11 个输入框（具体 N 值）+ 1 个下拉（单位选择）
    CONFIG_INPUTS = "input:visible"
    CONFIG_SELECT = ".ant-select:visible"
