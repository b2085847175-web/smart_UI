"""智言客服Agent - 智言 Harness 对话助手 https://dev.zhiyan.chat/harness

2026-11-10 探测确认。对话式 AI 助手：分析真实对话、解释知识来源、优化知识库、分析数据。
发送消息会产生会话数据；页面对象只登记定位，只读流程不得调用发送。
"""
from pages.base_page import BasePage


class HarnessPage(BasePage):
    """智言 Harness /harness"""
    PATH = "/harness"

    # ---------- 会话列表 ----------
    NEW_SESSION_BUTTON = "button:has-text('新对话')"
    SEARCH_SESSION_BUTTON = "button:has-text('搜索会话')"
    SESSION_SEARCH_INPUT = "input[placeholder='搜索会话标题']"
    SESSION_LIST = ".ant-conversations"
    SESSION_ITEM = ".ant-conversations-item"
    # 会话项 hover 出现的更多菜单，含"删除"
    SESSION_MORE = ".ant-conversations-item .anticon-ellipsis"
    SESSION_DELETE_ITEM = ".ant-dropdown :text('删除')"
    SESSION_DELETE_CONFIRM = ".ant-modal-confirm:has-text('删除会话')"
    SESSION_DELETE_CONFIRM_TEXT = "删除后该会话及其聊天记录将被清除，且无法恢复"
    SESSION_DELETE_OK = ".ant-modal-confirm button:has-text('删 除')"

    # ---------- 首页快捷任务 ----------
    WELCOME_HEADING = "text=今天需要帮你做什么？"
    QUICK_ANALYZE = "text=分析对话"
    QUICK_MODIFY_KNOWLEDGE = "text=添加/修改知识"
    QUICK_OPTIMIZE_KNOWLEDGE = "text=优化知识库"
    QUICK_ANALYZE_DATA = "text=分析数据"
    # 点击快捷任务仅向输入框预填提示词，不自动发送
    QUICK_PREFILL_HINT = "可以帮你分析真实对话、解释知识来源、优化知识库内容、分析数据"

    # ---------- 输入与上下文 ----------
    CONTEXT_ADD_BUTTON = "button:has-text('添加上下文')"
    CONTEXT_MENU = ".ant-dropdown:visible, [role='menu']"
    # 添加上下文 9 类候选（实测顺序）
    CONTEXT_ITEMS = ("添加图片或文件", "自定义知识库", "场景知识库", "店铺知识库",
                     "商品知识库", "货品知识库", "自定义变量", "AI智能体", "客服质检会话")
    CONTEXT_SESSION_ITEM = ".ant-dropdown :text('客服质检会话')"
    INPUT_BOX = "textarea[placeholder*='描述你想让 Harness 做什么']"
    SEND_BUTTON = "button:has(.anticon-arrow-up)"

    # ---------- 客服质检会话选择弹窗 ----------
    SESSION_PICKER = ".ant-modal:has-text('选择会话'), .ant-modal:has-text('客服质检')"
    SESSION_PICKER_DATE_FROM = "input[placeholder='开始日期'], input[aria-label='开始日期']"
    SESSION_PICKER_BUYER_INPUT = "input[placeholder='请输入买家昵称搜索']"
    SESSION_PICKER_EMPTY = "text=没有匹配的会话"
    SESSION_PICKER_OK = ".ant-modal button:has-text('确 定')"
    SESSION_PICKER_CANCEL = ".ant-modal button:has-text('取 消')"
