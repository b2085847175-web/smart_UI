"""策略、设置及账务页面的显式只读流程。"""
from .specs import Scenario, Step, button, click, css, field, gap, inspect, menu, opened, search, text


SCENARIOS = (
    Scenario("support-greeting-add", "策略管理", "/greeting", "新增欢迎语表单",
             (opened("新增欢迎语", button("新增欢迎语")), inspect("名称字段", field("请输入欢迎语名称", "overlay"))),
             "只打开，不填写或保存。"),
    Scenario("support-greeting-edit", "策略管理", "/greeting", "代表欢迎语编辑",
             (opened("代表欢迎语编辑", text("编辑", sample=True, data=True)), inspect("表单", field("请输入欢迎语名称", "overlay")))),
    Scenario("support-greeting-sort", "策略管理", "/greeting", "欢迎语排序入口",
             (opened("查看排序", button("欢迎语排序")), inspect("排序区域", css(".ant-modal:visible", "page"))),
             "仅一条记录时控件禁用，记录受限；不拖动或保存。"),
    Scenario("support-variables-search", "策略管理", "/variables", "变量查询",
             (search("查询变量", "请输入变量名称或内容搜索", "店铺"), inspect("查询区域"))),
    Scenario("support-variables-add", "策略管理", "/variables", "新增变量表单",
             (opened("新增变量", button("新增变量")), inspect("名称字段", field("请输入变量名称", "overlay")))),
    Scenario("support-variables-edit", "策略管理", "/variables", "代表变量编辑",
             (opened("代表变量编辑", text("编辑", sample=True, data=True)), inspect("表单", css("input", "overlay")))),
    Scenario("support-variables-import", "策略管理", "/variables", "变量导入规则",
             (opened("查看导入说明", button("导入")), inspect("导入弹层", css(".ant-modal:visible", "page"))),
             "不下载模板，不上传，不提交。"),
    Scenario("support-variables-log", "策略管理", "/variables", "变量日志及代表详情",
             (opened("操作日志", button("操作日志")),
              opened("代表日志详情", text("查看详情", "overlay", sample=True, data=True)),
              inspect("日志详情", text("操作详情", "overlay")))),
    Scenario("support-filter-search", "策略管理", "/filter-words", "屏蔽词查询",
             (search("查询屏蔽词", "输入关键词搜索屏蔽词", "测试"), inspect("查询区域"))),
    Scenario("support-filter-add", "策略管理", "/filter-words", "添加屏蔽词入口",
             (opened("添加屏蔽词", button("添加屏蔽词")), inspect("词条输入框", field("输入屏蔽词，多个词可用逗号或空格分隔", "overlay")))),
    Scenario("support-replace-search", "策略管理", "/replace-word", "替换词查询",
             (search("查询替换词", "请输入关键词搜索", "测试"), inspect("查询区域"))),
    Scenario("support-replace-add", "策略管理", "/replace-word", "添加替换词表单",
             (opened("添加替换词", button("添加替换词")), inspect("来源词字段", field("请输入被替换的关键词", "overlay")))),
    Scenario("support-replace-edit", "策略管理", "/replace-word", "代表替换规则编辑",
             (opened("编辑代表规则", text("编辑", sample=True, data=True)), inspect("规则表单", css("input", "overlay")))),
    Scenario("support-strategy-fields", "策略管理", "/strategy", "通用策略只读配置区域",
             tuple(inspect(name, css(f':is(h1,h2,h3,h4):text-is("{name}")')) for name in ("客服基础信息", "重复问答策略", "历史消息记忆量", "订单售后周期"))
             + (inspect("只观察输入框数量", css("input")),), "可能自动保存，禁止填写或切换。"),
    Scenario("support-sync-entry", "设置", "/sync", "跨店同步选择步骤",
             (opened("同步选择入口", css('button:has([aria-label="file-text"]):has-text("跨店同步")')),
              inspect("同步选择表单", text("同步至其他店铺", "overlay"))),
             "不勾选模块、目标、同步方式，不提交。"),
    Scenario("support-sync-log", "设置", "/sync", "同步操作日志",
             (opened("同步操作日志", button("操作日志")), inspect("日志区域", field("请输入店铺名称,同步模块", "overlay")))),
    Scenario("support-account-edit", "设置", "/service-account", "代表客服账号编辑",
             (opened("代表账号编辑", text("编辑", sample=True, data=True)), inspect("账号表单", field("请输入AI员工名称", "overlay")), inspect("账号信息", text("账号信息", "overlay"))),
             "不修改账号名称、状态或关联店铺。"),
    Scenario("support-billing-records", "言值", "/yanzhi", "充值记录只读展示",
             (inspect("充值记录入口", text("言值充值记录")),), "不发起充值支付。"),
    Scenario("support-billing-date", "言值", "/yanzhi-consume-detail", "消耗明细日期面板",
             (Step("只打开开始日期", "date", field("开始日期")), inspect("消耗明细")),
             "不改变店铺、类型或日期范围，不导出。"),
    Scenario("support-help", "全局", "/contact-us", "帮助入口展示",
             (inspect("帮助页面区域"),), "不访问外部官网、不扫码、不咨询。"),
)

SCENARIOS += tuple(
    Scenario(f"support-greeting-{suffix}", "策略管理", "/greeting", f"欢迎语{label}工具",
             (opened("新增欢迎语表单", button("新增欢迎语")), action),
             "不选择或插入内容，不保存。")
    for suffix, label, action in (
        ("variables", "变量", menu("变量候选", button("变量", "overlay", sample=True), candidates=".ant-table tbody tr[data-row-key]")),
        ("video", "视频", opened("视频弹层", button("视频", "overlay", sample=True))),
        ("emoji-gap", "图片及表情边界", gap("图片及表情未执行", "不触发文件选择器；表情浮层历史未成功打开，保留未覆盖。")),
    )
)
