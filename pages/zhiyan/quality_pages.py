"""智言客服Agent - 质检中心 + VOC洞察分析 + 数据概览（2026-10-16 探测确认）。"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import MODAL_CANCEL, MODAL_OK


class AiQualityPage(BasePage):
    """AI 质检 /ai-quality-inspection（查询类）"""
    PATH = "/ai-quality-inspection"
    SEARCH_INPUT = "input[placeholder='请输入买家昵称搜索']"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    QUERY_BUTTON = "button:has-text('查 询')"


class ServiceQualityPage(BasePage):
    """客服质检 /quality-inspection"""
    PATH = "/quality-inspection"
    SEARCH_INPUT = "input[placeholder='请输入买家昵称搜索']"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    RESET_BUTTON = "button:has-text('重 置')"
    QUERY_BUTTON = "button:has-text('查 询')"
    DETAIL_LINK = "text=查看详情"   # 跳详情页


class QualityInsightPage(BasePage):
    """质检洞察分析 /quality-inspection-insight（数据页）"""
    PATH = "/quality-inspection-insight"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    QUERY_BUTTON = "button:has-text('查 询')"


class ConsultInsightPage(BasePage):
    """咨询洞察分析 /consult-insight（数据页）"""
    PATH = "/consult-insight"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    QUERY_BUTTON = "button:has-text('查 询')"


class DashboardPage(BasePage):
    """仪表盘 /dashboard"""
    PATH = "/dashboard"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    FLOW_BUTTON = "button:has-text('智言AI客服接待流程')"
    QUERY_BUTTON = "button:has-text('查询')"
    FLOW_MODAL = ".ant-modal:has-text('智言AI客服接待流程')"


class StatsPage(BasePage):
    """统计分析 /stats（7 个子页签，2026-10-16 补测全部可点击，无独有按钮）

    每个子页签均显示：开始日期/结束日期 + 1 个表格
    """
    PATH = "/stats"
    DATE_START = "input[placeholder='开始日期']"
    DATE_END = "input[placeholder='结束日期']"
    # 7 个页签（带 overflow，部分需 scroll_into_view_if_needed）
    TAB_CONSULT = "[role=tab]:has-text('咨询统计')"
    TAB_KNOWLEDGE = "[role=tab]:has-text('知识统计')"
    TAB_PRODUCT = "[role=tab]:has-text('商品统计')"
    TAB_TRANSFER = "[role=tab]:has-text('转接统计')"
    TAB_DAILY = "[role=tab]:has-text('每日接待统计')"
    TAB_SHOP = "[role=tab]:has-text('店铺接待统计')"
    TAB_AGENT = "[role=tab]:has-text('客服接待统计')"
