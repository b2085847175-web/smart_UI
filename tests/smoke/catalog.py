"""30个既有页面入口 + 2026-11-10新登记页面入口和经证据筛选的功能链；不自动点击未知控件。"""
import re

from .catalog_knowledge import SCENARIOS as KNOWLEDGE
from .catalog_business import SCENARIOS as BUSINESS
from .catalog_support import SCENARIOS as SUPPORT
from .catalog_extras import SCENARIOS as EXTRAS
from .specs import Scenario, inspect


PAGES = (
    ("product-config", "商品管理"), ("product-knowledge", "商品知识库"),
    ("product-group", "商品分组"), ("stock-config", "货品管理"),
    ("stock-knowledge", "货品知识库"), ("shop-knowledge", "店铺知识库"),
    ("scene", "场景知识库"), ("keyword", "自定义知识库"),
    ("ai-agent", "AI智能体"), ("intelligent-follow", "智能跟单"),
    ("transfer", "智能转接"), ("work-order", "智能工单"),
    ("smart-size", "智能尺码推荐"), ("knowledge-review", "销冠知识审核"),
    ("greeting", "进店欢迎语"), ("variables", "自定义变量"),
    ("filter-words", "屏蔽词管理"), ("replace-word", "替换词管理"),
    ("strategy", "通用策略"), ("quality-inspection", "客服质检"),
    ("ai-quality-inspection", "会话洞察分析"), ("quality-inspection-insight", "质检洞察分析"),
    ("consult-insight", "咨询洞察分析"), ("dashboard", "仪表盘"),
    ("stats", "统计分析"), ("sync", "跨店同步"),
    ("service-account", "客服账号管理"), ("yanzhi", "我的言值"),
    ("yanzhi-consume-detail", "言值消耗明细"), ("contact-us", "关于我们"),
)
# 2026-11-10实测新登记；B1清单继续只按PAGES校验观察覆盖，时效管理未开发暂不登记。
EXTRA_PAGES = (
    ("harness", "智言 Harness"), ("tag", "标签管理"),
    ("accounts", "账号管理"), ("brands", "品牌管理"),
    ("shops", "店铺管理"), ("shop-group", "店铺分组"),
)
OVERVIEWS = tuple(
    Scenario("nav-" + path, "页面入口", "/" + path, title + "页面入口",
             (inspect("页面主要内容可见并记录结构计数"),),
             "按登记路由进入页面；侧栏折叠菜单本身的全部导航组合不在此验证。")
    for path, title in PAGES + EXTRA_PAGES
)
SCENARIOS = OVERVIEWS + KNOWLEDGE + BUSINESS + SUPPORT + EXTRAS


def validate_catalog():
    """清单配置校验不是业务断言，任何缺项均阻止用例收集。"""
    seen = set()
    known_paths = {"/" + path for path, _ in PAGES + EXTRA_PAGES}
    actions = {"click", "open", "inspect", "menu", "search", "popup", "limited", "date"}
    for case in SCENARIOS:
        if case.id in seen or not re.fullmatch(r"[a-z0-9-]+", case.id):
            raise ValueError("重复或非法功能ID: " + case.id)
        seen.add(case.id)
        if case.path not in known_paths or not case.steps:
            raise ValueError("未知路由或空功能链: " + case.id)
        for step in case.steps:
            if step.action not in actions:
                raise ValueError("未支持的冒烟动作: " + step.action)
            if step.action not in {"inspect", "limited"} and not step.target:
                raise ValueError("缺少动作定位: " + case.id)
            for target in (step.target, step.wait):
                if target and (target.scope not in {"main", "overlay", "page"}
                               or target.kind not in {"css", "button", "tab", "text", "placeholder", "link"}):
                    raise ValueError("非法定位定义: " + case.id)


validate_catalog()
