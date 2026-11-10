"""智言客服Agent - AI智能中心分组（2026-10-16 探测确认）。"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import (
    MODAL_CANCEL, MODAL_OK, MODAL_SAVE, POPCONFIRM_CANCEL,
    ROW_EDIT, ROW_DELETE,
)


class AiAgentPage(BasePage):
    """AI智能体 /ai-agent（卡片 + 配置入口）"""
    PATH = "/ai-agent"
    CONFIG_BUTTON = "button:has-text('配 置')"
    SALES_REP_BUTTON = "button:has-text('销冠客服')"
    SALES_REVIEW_LINK = "text=销冠知识审核"
    SALES_REP_MODAL = ".ant-modal:has-text('销冠客服')"


class IntelligentFollowPage(BasePage):
    """智能跟单 /intelligent-follow（含第1/2/3轮页签）"""
    PATH = "/intelligent-follow"
    TAB_1 = "[role=tab]:has-text('第1轮')"
    TAB_2 = "[role=tab]:has-text('第2轮')"
    TAB_3 = "[role=tab]:has-text('第3轮')"
    SORT_BUTTON = "button:has-text('任务排序')"
    ADD_TASK_BUTTON = "button:has-text('新增任务')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    SORT_MODAL = ".ant-modal:has-text('任务排序')"
    TASK_MODAL = ".ant-modal:has-text('新增任务'), .ant-modal:has-text('编辑任务')"
    TASK_NAME_INPUT = "input[placeholder='请输入话术名称']"
    DELETE_POPCONFIRM_TEXT = "确认删除这个话术?"


class TransferPage(BasePage):
    """智能转接 /transfer"""
    PATH = "/transfer"
    LOG_BUTTON = "button:has-text('操作日志')"
    ROW_EDIT = ROW_EDIT
    STRATEGY_LINK = "text=转接策略"  # 跳到 /transfer/strate
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    EDIT_MODAL = ".ant-modal:has-text('转接配置')"
    DEFAULT_GROUP_INPUT = "input[placeholder='请输入默认客服分组名称']"


class WorkOrderPage(BasePage):
    """智能工单 /work-order（查询类，无弹层）"""
    PATH = "/work-order"
    SEARCH_INPUT = "input[placeholder='买家昵称/工单标题/编号/订单号']"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    EXPORT_BUTTON = "button:has-text('导出')"


class SmartSizePage(BasePage):
    """智能尺码推荐 /smart-size"""
    PATH = "/smart-size"
    SEARCH_INPUT = "input[placeholder='请输入尺码表名称']"
    ADD_BUTTON = "button:has-text('新增尺码表')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    ADD_MODAL = ".ant-modal:has-text('新建尺码表')"
    EDIT_MODAL = ".ant-modal:has-text('编辑尺码表')"
    NAME_INPUT = "input[placeholder='请输入尺码表名称']"
    DELETE_POPCONFIRM_TEXT = "确定要删除这个尺码表吗？"


class KnowledgeReviewPage(BasePage):
    """销冠知识审核 /knowledge-review"""
    PATH = "/knowledge-review"
    SEARCH_BUYER_INPUT = "input[placeholder='搜索买家昵称']"
    SEARCH_PRODUCT_INPUT = "input[placeholder='搜索商品ID或标题']"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    EDIT_KNOWLEDGE_BUTTON = "button:has-text('编辑知识')"
    EDIT_MODAL = ".ant-modal:has-text('知识审核')"
    NAME_INPUT = "input[placeholder='请输入知识名称']"
    ACCEPT_BUTTON = "button:has-text('采 纳')"
    REJECT_BUTTON = "button:has-text('不采纳')"
