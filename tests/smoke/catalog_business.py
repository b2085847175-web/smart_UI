"""基于已留存实测证据的业务功能只读遍历；不保存配置或记录正文。"""
from .specs import (
    Scenario, Step, Target, button, text, tab, css, field,
    click, opened, inspect, menu, search, popup, gap,
)


def _ai_config(name):
    # 实测证明卡片内有精确标题文本，未证明使用 ant-card-head-title。
    return css(
        f'.ant-card:has(:text-is("{name}")) '
        'button:has-text("配 置")'
    )


_AI = (
    Scenario("biz-ai-product-generate", "AI智能体", "/ai-agent", "商品知识生成配置入口", (
        opened("从商品知识生成卡片进入商品管理", _ai_config("商品知识生成"), "/product-config"),
        inspect("查看商品管理布局及表格计数"),
    )),
    Scenario("biz-ai-product-learn", "AI智能体", "/ai-agent", "商品知识学习配置", (
        opened("打开商品知识学习配置", _ai_config("商品知识学习")),
        inspect("查看自动学习模式，不切换模式", text("商品知识学习", "overlay")),
        inspect("查看学习配置字段计数", css("input, textarea", "overlay")),
    )),
    Scenario("biz-ai-product-answer", "AI智能体", "/ai-agent", "智能商品应答配置", (
        opened("打开智能商品应答配置", _ai_config("智能商品应答")),
        inspect("查看匹配度与低匹配处理字段", css("input, textarea", "overlay")),
        gap("未显示分支不强制展开", "不切换低匹配处理策略；只记录当前可见字段，其他策略字段未覆盖。"),
    )),
    Scenario("biz-ai-product-recommend", "AI智能体", "/ai-agent", "智能推荐商品配置", (
        opened("打开智能推荐商品配置", _ai_config("智能推荐商品")),
        inspect("查看推荐策略字段，不填写策略", css("textarea", "overlay")),
        gap("推荐策略权限限制", "推荐策略标注仅超管可配置；不切换推荐模式，不尝试越权编辑。"),
    )),
    Scenario("biz-ai-selling-points", "AI智能体", "/ai-agent", "商品卖点介绍配置", (
        opened("打开商品卖点介绍配置", _ai_config("商品卖点介绍")),
        inspect("查看收到商品链接后的回复模式", text("收到商品链接", "overlay")),
    )),
    Scenario("biz-ai-transfer", "AI智能体", "/ai-agent", "智能转接配置入口", (
        opened("从智能转接卡片进入转接配置", _ai_config("智能转接"), "/transfer"),
        inspect("查看转接场景表格计数", css("tbody tr[data-row-key]", data=True)),
    )),
    Scenario("biz-ai-follow", "AI智能体", "/ai-agent", "智能跟单配置入口", (
        opened("从智能跟单卡片进入跟单", _ai_config("智能跟单"), "/intelligent-follow"),
        inspect("查看跟单轮次与任务布局"),
    )),
    Scenario("biz-ai-express-note", "AI智能体", "/ai-agent", "智能快递备注配置", (
        opened("打开智能快递备注配置", _ai_config("智能快递备注")),
        inspect("查看快递及插旗配置，不勾选", text("已选择快递", "overlay")),
    )),
    Scenario("biz-ai-service-style", "AI智能体", "/ai-agent", "客服风格定制配置", (
        opened("打开客服风格定制配置", _ai_config("客服风格定制")),
        inspect("查看预设风格，不切换风格", text("风格类型", "overlay")),
        gap("自定义风格分支未切换", "自定义人设仅定位入口，不切换单选项，因此隐藏的自定义字段不认定已覆盖。"),
    )),
    Scenario("biz-ai-detail-image-answer", "AI智能体", "/ai-agent", "商详图智能应答配置", (
        opened("打开商详图智能应答配置", _ai_config("商详图智能应答")),
        inspect("查看回复来源配置，不切换模式", text("商详图智能应答", "overlay")),
    )),
    Scenario("biz-ai-attribute-learn", "AI智能体", "/ai-agent", "商品属性学习配置", (
        opened("打开商品属性学习配置", _ai_config("商品属性学习")),
        inspect("查看不学习属性区域，不删除或选择属性", text("AI将不学习以下商品属性", "overlay")),
    )),
    Scenario("biz-ai-size-recommend", "AI智能体", "/ai-agent", "智能尺码推荐配置入口", (
        opened("从智能尺码推荐卡片进入尺码表", _ai_config("智能尺码推荐"), "/smart-size"),
        inspect("查看尺码表样本数量", css("tbody tr[data-row-key]", data=True)),
    )),
    Scenario("biz-ai-order-note", "AI智能体", "/ai-agent", "智能订单备注配置", (
        opened("打开智能订单备注配置", _ai_config("智能订单备注")),
        inspect("查看订单备注编辑区域数量，不读取或编辑策略", css('[contenteditable="true"]', "overlay")),
        gap("备注策略权限限制", "策略标注仅超管可配置；不编辑备注、不选择插旗。"),
    )),
    Scenario("biz-ai-conversation-insight", "AI智能体", "/ai-agent", "会话洞察分析配置", (
        opened("打开会话洞察分析配置", _ai_config("会话洞察分析")),
        inspect("查看分析会话数量及分析内容配置", text("每日分析会话数", "overlay")),
        gap("自定义会话数隐藏字段", "不切换全部会话与自定义会话数；仅查看当前展示字段，不认定隐藏数量字段已覆盖。"),
    )),
    Scenario("biz-ai-top-service", "AI智能体", "/ai-agent", "销冠客服账号配置查看", (
        opened("打开销冠客服账号抽屉", button("销冠客服")),
        inspect("查看账号配置表格计数，不记录账号值", css("table", "overlay")),
    )),
    Scenario("biz-ai-review-entry", "AI智能体", "/ai-agent", "销冠知识审核入口", (
        opened("进入销冠知识审核", button("销冠知识审核"), "/knowledge-review"),
        inspect("查看审核布局，不记录客户与知识正文"),
    )),
)


# 四个业务场景及各轮次均来自实测，不从运行时页面自动生成计划。
# 历史样本中已付款第3轮、已发货第3/4轮无任务；本链仅遍历列表，不推断当前空态。
_FOLLOW_ROUNDS = tuple(
    Scenario(
        f"biz-follow-{key}-round-{round_number}", "智能跟单", "/intelligent-follow",
        f"{scene} / 第{round_number}轮时间与任务查看",
        (
            click("切换跟单场景", text(scene), wait=tab(f"第{round_number}轮")),
            click("切换独立轮次", tab(f"第{round_number}轮"), wait=css('[aria-label="跟单等待时长"]')),
            inspect("查看等待时长字段，不读取或更改值", css('[aria-label="跟单等待时长"]')),
            inspect("查看当前轮次任务与时间布局，不存话术正文"),
        ),
    )
    for key, scene, count in (
        ("consult-unordered", "咨询未下单", 3),
        ("ordered-unpaid", "下单未付款", 3),
        ("paid", "已付款", 3),
        ("shipped", "已发货", 5),
    )
    for round_number in range(1, count + 1)
)

_FOLLOW_FORMS = tuple(
    Scenario(
        f"biz-follow-{key}-{mode}", "智能跟单", "/intelligent-follow",
        f"{scene} / {entry}表单只读查看",
        (
            click("切换跟单场景", text(scene), wait=tab("第1轮")),
            click("选择有实测样本的第1轮", tab("第1轮")),
            opened("打开任务表单，不提交", button(entry, sample=mode == "edit", data=mode == "edit")),
            inspect("查看任务名称与关联配置字段", field("请输入话术名称", "overlay")),
            inspect("查看可见任务表单布局，不存话术正文", css("form", "overlay")),
            gap("任务隐藏分支未切换", "不切换启用状态、商品关联、有效期或跟单方式；隐藏分支未覆盖。"),
        ),
    )
    for key, scene in (
        ("consult-unordered", "咨询未下单"), ("ordered-unpaid", "下单未付款"),
        ("paid", "已付款"), ("shipped", "已发货"),
    )
    for mode, entry in (("add", "新增任务"), ("edit", "编辑"))
)

_FOLLOW_TOOLS = (
    Scenario("biz-follow-sort", "智能跟单", "/intelligent-follow", "任务排序只读查看", (
        opened("打开任务排序，不拖动排序行", button("任务排序")),
        inspect("查看排序表格计数，不记录话术正文", css("table", "overlay")),
    )),
    Scenario("biz-follow-rich-video", "智能跟单", "/intelligent-follow", "新增任务视频面板", (
        opened("打开新增任务表单", button("新增任务")),
        opened("打开视频链接面板，不填链接", button("视频", "overlay")),
        inspect("查看视频面板布局，不上传、不预览远端链接", text("视频链接:", "overlay")),
    )),
    Scenario("biz-follow-rich-variables", "智能跟单", "/intelligent-follow", "新增任务变量候选", (
        opened("打开新增任务表单", button("新增任务")),
        menu("展开变量候选，不插入变量", button("变量", "overlay"), candidates=".ant-table tbody tr[data-row-key]"),
    )),
    Scenario("biz-follow-rich-limits", "智能跟单", "/intelligent-follow", "任务表情和图片入口限制", (
        opened("打开新增任务表单", button("新增任务")),
        inspect("定位图片按钮，不触发文件选择器", button("图片", "overlay")),
        inspect("定位表情按钮", css('button:has([aria-label="smile"])', "overlay", sample=True)),
        gap("表情与图片覆盖受限", "多次实测未捕获独立表情浮层，仅定位入口；图片按钮触发文件选择器，因此不点击、不选文件、不上传，两个流程均不认定已覆盖。"),
    )),
)


_TRANSFER = tuple(
    Scenario(
        f"biz-transfer-{key}-edit", "智能转接", "/transfer", f"{scene}转接配置查看",
        (
            opened("打开场景行的编辑抽屉", text("编辑", row=scene)),
            inspect("查看默认分组和时间段字段", text("按时间段转接 注：时间段不可重叠", "overlay")),
            inspect("查看已显示时间段表格计数", css("table", "overlay")),
            inspect("查看转接及失败话术区域布局，不记录正文", css("input, textarea, table", "overlay")),
            gap("转接配置不增改", "不添加时间段或话术，不切换分组；未显示的配置分支不认定已覆盖。"),
        ),
    )
    for key, scene in (("pre-sales", "售前问题"), ("after-sales", "售后问题"), ("logistics", "物流问题"), ("complaint", "客诉问题"))
) + tuple(
    Scenario(
        f"biz-transfer-{key}-strategy", "智能转接", "/transfer", f"{scene}转接策略入口及新建表单",
        (
            opened("进入场景策略页", text("转接策略", row=scene), "/transfer/strate"),
            inspect("查看策略列表布局"),
            opened("打开新增策略表单，不保存", button("新增策略")),
            inspect("查看策略表单字段", css("input, textarea", "overlay")),
            menu("展开可添加限定条件，不选择条件", css('button:has([aria-label="plus"]):has-text("添加")', "overlay"), candidates=".ant-popover-inner-content .ant-space-item > button"),
        ) + (
            (gap("已有策略编辑链未覆盖", "历史样本该场景策略为空；此链仅覆盖策略列表与新增表单，当前即使存在策略仍需专门已有策略编辑链。"),)
            if key != "pre-sales" else ()
        ),
    )
    for key, scene in (("pre-sales", "售前问题"), ("after-sales", "售后问题"), ("logistics", "物流问题"), ("complaint", "客诉问题"))
) + (
    Scenario("biz-transfer-strategy-edit", "智能转接", "/transfer", "售前已有策略代表样本编辑查看", (
        opened("进入售前策略页", text("转接策略", row="售前问题"), "/transfer/strate"),
        opened("选取已有策略编辑样本，不保存", button("编辑", sample=True, data=True)),
        inspect("查看已有策略限定条件字段，不记录策略内容", css("input, textarea", "overlay")),
        menu("展开可添加限定条件，不选择", css('button:has([aria-label="plus"]):has-text("添加")', "overlay"), candidates=".ant-popover-inner-content .ant-space-item > button"),
    )),
    Scenario("biz-transfer-log", "智能转接", "/transfer", "转接操作日志及变更详情", (
        opened("打开操作日志", button("操作日志")),
        inspect("查看操作日志行计数，不存人员信息", css("tbody tr[data-row-key]", "overlay", data=True)),
        opened("打开一条日志详情", text("查看详情", "overlay", sample=True, data=True)),
        inspect("查看变更详情布局，不记录字段值", text("操作详情", "overlay")),
    )),
    Scenario("biz-transfer-log-search", "智能转接", "/transfer", "操作日志搜索字段查看", (
        opened("打开操作日志", button("操作日志")),
        inspect("查看触发场景搜索入口", field("请输入触发场景搜索", "overlay")),
    )),
)


_SIZE = (
    Scenario("biz-size-search", "智能尺码推荐", "/smart-size", "尺码表名称查询", (
        search("查询无隐私的固定尺码表名称", "请输入尺码表名称", "只读冒烟不存在的尺码表"),
        inspect("查看查询后的表格布局，不创建样本"),
    )),
    Scenario("biz-size-add", "智能尺码推荐", "/smart-size", "新增尺码表表单查看", (
        opened("打开新建尺码表", button("新增尺码表")),
        inspect("查看尺码表名称字段", field("请输入尺码表名称", "overlay")),
        inspect("查看主尺码表布局，不添加尺码值", text("主尺码表", "overlay")),
        gap("尺码图不上传", "不操作文件输入，不上传尺码图；不切换商品关联模式，因此隐藏分支未覆盖。"),
    )),
    Scenario("biz-size-edit", "智能尺码推荐", "/smart-size", "已有尺码表样本编辑查看", (
        opened("打开一个尺码表样本，不保存", button("编辑", sample=True, data=True)),
        inspect("查看已有尺码表名称字段，不记录值", field("请输入尺码表名称", "overlay")),
        inspect("查看已有尺码表布局，不存尺码内容", text("主尺码表", "overlay")),
    )),
) + tuple(
    Scenario(
        f"biz-size-{mode}-{axis}", "智能尺码推荐", "/smart-size", f"{entry} / {label}候选查看",
        (
            opened("打开尺码表配置表单", button(entry, sample=mode == "edit", data=mode == "edit")),
            inspect("查看尺码维度选择控件数量，不依据历史顺序点击", css(".ant-select", "overlay")),
            gap("维度候选定位受限", "实测仅留存横纵轴下拉顺序；缺少稳定语义定位，不以历史位置打开维度菜单。"),
        ),
        limitation="当前只定位维度控件，候选菜单未覆盖；缺少稳定语义定位，不按历史位置点击。",
    )
    for mode, entry in (("add", "新增尺码表"), ("edit", "编辑"))
    for axis, label in (("horizontal", "横轴维度"), ("vertical", "纵轴维度"))
)

_REVIEW = (
    Scenario("biz-review-query", "销冠知识审核", "/knowledge-review", "审核当前条件查询", (
        inspect("定位买家昵称查询字段，不填写身份", field("搜索买家昵称")),
        inspect("定位商品查询字段", field("搜索商品ID或标题")),
        click("查询当前条件", button("查询")),
        inspect("查看买家列表与学习结果布局，不记录身份或正文"),
        gap("聊天内容链未覆盖", "历史样本无聊天记录；此链仅覆盖查询与布局，不论当前是否有记录均未实现聊天内容遍历。"),
    )),
    Scenario("biz-review-edit", "销冠知识审核", "/knowledge-review", "审核知识编辑抽屉只读查看", (
        opened("打开一个审核知识样本", button("编辑知识", sample=True, data=True)),
        inspect("查看知识名称字段，不记录知识值", field("请输入知识名称", "overlay")),
        inspect("查看审核表单布局，不读取知识正文", css("form", "overlay")),
        gap("审核仅查看", "不点击采纳、不采纳，不切换生效或关联模式；隐藏条件与时间字段不认定已覆盖。"),
    )),
)


_INSPECTION = (
    Scenario("biz-work-order-empty", "智能工单", "/work-order", "工单数据与搜索入口限制", (
        inspect("定位工单多字段搜索入口", field("买家昵称/工单标题/编号/订单号")),
        inspect("查看工单列表布局，不导出数据"),
        gap("工单详情链未覆盖", "历史保护修正版样本为空，未取得详情入口证据；此链只覆盖列表，当前即使有数据仍需专门详情链，不造工单或变更状态。"),
    )),
    Scenario("biz-quality-query", "客服质检", "/quality-inspection", "客服质检当前条件查询", (
        inspect("定位买家查询字段，不填写身份", field("请输入买家昵称搜索")),
        click("查询当前条件", button("查询")),
        inspect("查看查询后质检列表布局，不存会话数据"),
        gap("常规入口详情链未覆盖", "历史常规入口无详情样本；此链仅覆盖查询及列表，当前有数据仍不自动进入详情。统计转接新页另有样本详情链。"),
    )),
    Scenario("biz-quality-reset", "客服质检", "/quality-inspection", "客服质检筛选重置", (
        click("重置本页查询条件，不变更业务数据", button("重置")),
        inspect("查看重置后的筛选字段布局"),
    )),
    Scenario("biz-quality-advanced", "客服质检", "/quality-inspection", "客服质检高级条件展开", (
        click("展开六项高级条件", text("展开(6)"), wait=text("收起")),
        inspect("查看高级筛选字段数量", css("form input")),
        inspect("定位转接原因搜索字段", field("请输入转接原因搜索")),
    )),
    Scenario("biz-ai-quality-query", "会话洞察分析", "/ai-quality-inspection", "会话洞察当前条件查询", (
        inspect("定位买家昵称搜索字段，不填写身份", field("请输入买家昵称搜索")),
        click("查询当前条件", button("查询")),
        inspect("查看查询后的洞察记录布局"),
        gap("会话洞察详情链未覆盖", "历史保护修正版样本无质检记录；此链只覆盖查询及列表，当前有数据仍需专门详情链。不造会话、不标记复检。"),
    )),
    Scenario("biz-quality-insight-query", "质检洞察分析", "/quality-inspection-insight", "质检洞察查询及统计区域", (
        click("查询当前店铺与日期条件", button("查询")),
        inspect("查看重点变化区域", text("重点变化")),
        inspect("查看平台分布区域", text("平台检出分布")),
        inspect("查看检出排行区域", text("检出数 TOP20")),
        inspect("查看质检明细布局", text("质检检出明细")),
        gap("质检洞察下钻链未覆盖", "历史平台、标签及检出明细样本均为空；此链仅覆盖统计区域布局，当前存在明细仍需另实现下钻链，不猜测按钮。"),
    )),
    Scenario("biz-consult-insight-query", "咨询洞察分析", "/consult-insight", "咨询洞察查询及统计区域", (
        click("查询当前店铺与日期条件", button("查询")),
        inspect("查看重点变化区域", text("重点变化")),
        inspect("查看平台分布区域", text("平台检出分布")),
        inspect("查看咨询热点排行区域", text("咨询热点TOP20")),
        inspect("查看咨询热点明细布局", text("咨询热点明细")),
        gap("咨询热点下钻链未覆盖", "历史咨询热点及明细样本为空；此链仅覆盖统计区域布局，当前存在明细仍需专门下钻链，不造数据或猜测入口。"),
    )),
    Scenario("biz-dashboard-query", "仪表盘", "/dashboard", "仪表盘查询及趋势区域", (
        click("查询当前店铺与日期条件", button("查询")),
        inspect("查看重点变化布局", text("重点变化")),
        inspect("查看接待趋势区域", text("接待人数趋势")),
        inspect("查看转接趋势区域", text("转接人数趋势")),
        inspect("查看商品热度区域", text("商品热度TOP20")),
        inspect("查看场景热度区域", text("场景热度TOP20")),
    )),
    Scenario("biz-dashboard-flow", "仪表盘", "/dashboard", "AI客服接待流程说明", (
        opened("打开客服接待流程说明", button("智言AI客服接待流程")),
        inspect("查看流程说明区域", text("买家进线", "overlay")),
    )),
)


_STATS = tuple(
    Scenario(
        f"biz-stats-{key}", "统计分析", "/stats", f"{category}主类查看",
        (
            click("切换统计主类", tab(category)),
            inspect("查看当前统计主类图表与明细布局，不存具体数值"),
        ),
    )
    for key, category in (("consult", "咨询统计"), ("knowledge", "知识统计"), ("product", "商品统计"), ("transfer", "转接统计"))
) + tuple(
    Scenario(
        f"biz-stats-consult-{key}", "统计分析", "/stats", f"咨询统计 / {child}",
        (
            click("切换咨询统计", tab("咨询统计"), wait=tab(child)),
            click("切换咨询子类", tab(child)),
            inspect("查看咨询统计表格计数，不存客户或账号信息", css("table")),
        ),
    )
    for key, child in (("daily", "每日接待统计"), ("shop", "店铺接待统计"), ("service", "客服接待统计"))
) + tuple(
    Scenario(
        f"biz-stats-knowledge-{key}", "统计分析", "/stats", f"知识统计 / {child}",
        (
            click("切换知识统计", tab("知识统计"), wait=tab(child)),
            click("切换知识子类", tab(child)),
            inspect("查看知识统计当前图表与明细布局"),
        ) + (
            (gap("自定义知识统计明细链未覆盖", "历史子类样本无统计明细表；此链仅覆盖子类布局，当前有明细仍需单独遍历链，不伪造明细或会话入口。"),)
            if key == "custom" else ()
        ),
    )
    for key, child in (("scene", "场景知识库"), ("product", "商品知识"), ("custom", "自定义知识库"))
) + tuple(
    Scenario(
        f"biz-stats-product-detail-{key}", "统计分析", "/stats", f"商品统计详情 / {category}",
        (
            click("切换商品统计", tab("商品统计")),
            opened("选取商品统计样本并打开抽屉", button("查看", sample=True, data=True)),
            click("切换抽屉内知识分类按钮", button(category, "overlay")),
            inspect("查看当前分类明细布局，不存商品知识正文", css("button", "overlay")),
        ),
    )
    for key, category in (("product", "商品知识"), ("scene", "场景知识库"), ("custom", "自定义知识库"))
) + (
    Scenario("biz-stats-transfer-session-detail", "统计分析", "/stats", "转接统计新页会话及有数据详情", (
        click("切换转接统计", tab("转接统计")),
        popup("打开一个转接原因的会话新页", button("查看会话", sample=True, data=True), "/quality-inspection"),
        inspect("查看新页会话列表计数，不记录身份或正文", css("tbody tr[data-row-key]", data=True)),
        opened("打开一条有数据的会话详情", text("查看详情", sample=True, data=True), "/quality-inspection/"),
        inspect("查看详情布局，不读取会话正文，不点击已检或复检"),
    ), limitation="样本由当前转接统计数据决定；没有样本按数据受限记录，不硬编码客户或会话ID。"),
)


# 只使用实测默认文案、稳定业务ID或表单标签；不把历史全局索引当定位契约。
_FILTERS = tuple(
    Scenario(
        f"biz-filter-{key}-{field_key}", module, path, f"{label}筛选候选查看",
        (menu(
            "展开语义明确的筛选候选，不选择", target,
            candidates=".ant-checkbox-wrapper" if key == "ai-quality" and field_key in {"hotspot", "point"} else "",
        ),),
        limitation="只查看当前渲染候选，不切换店铺或勾选选项；入口不唯一时由执行器显式报错。",
    )
    for key, module, path, fields in (
        ("follow", "智能跟单", "/intelligent-follow", (("unit", "等待时长单位", css('.ant-select:has(:text-is("分钟"))')),)),
        ("work-order", "智能工单", "/work-order", (
            ("scene", "场景", css('.ant-select:has(:text-is("全部场景"))')),
            ("handler", "处理人", css('.ant-select:has(:text-is("全部处理人"))')),
            ("state", "工单状态", css('.ant-select:has(:text-is("全部"))')),
        )),
        ("review", "销冠知识审核", "/knowledge-review", (("state", "审核状态", css('.ant-select:has(#status)')),)),
        ("quality", "客服质检", "/quality-inspection", (
            ("keyword", "关键词类型", css('.ant-form-item:has(label:text-is("关键词")) .ant-select')),
            ("shop", "店铺", css('.ant-form-item:has(label:text-is("店铺")) .ant-select')),
        )),
        ("ai-quality", "会话洞察分析", "/ai-quality-inspection", (
            ("shop", "店铺", css('#ai-quality-shop[role="combobox"]')),
            ("hotspot", "咨询热点", css('.ant-select:has(:text-is("请选择咨询热点"))')),
            ("point", "质检点", css('.ant-select:has(:text-is("请选择质检点"))')),
            ("result", "质检结果", css('.ant-select:has(:text-is("全部质检结果"))')),
            ("recheck", "复检情况", css('.ant-select:has(:text-is("全部复检情况"))')),
        )),
        ("stats", "统计分析", "/stats", (("shop-range", "统计店铺范围", css('.ant-select:has(:text-is("当前店铺"))')),)),
    )
    for field_key, label, target in fields
) + tuple(
    Scenario(
        f"biz-filter-{key}-unlocated", module, path, "缺少稳定语义的筛选入口限制",
        (
            inspect("只查看当前筛选控件数量，不点击全局店铺或历史索引", css(".ant-select")),
            gap("筛选候选定位受限", reason),
        ),
    )
    for key, module, path, reason in (
        ("work-order", "智能工单", "/work-order", "品牌及店铺只留存全局位置与当前账号文案，缺少稳定字段标签；不按历史索引展开。"),
        ("quality-insight", "质检洞察分析", "/quality-inspection-insight", "店铺下拉仅留存全局位置，缺少稳定语义定位；不按历史位置或账号名称点击。"),
        ("consult-insight", "咨询洞察分析", "/consult-insight", "店铺下拉仅留存全局位置，缺少稳定语义定位；不按历史位置或账号名称点击。"),
        ("dashboard", "仪表盘", "/dashboard", "店铺下拉仅留存全局位置，缺少稳定语义定位；不按历史位置或账号名称点击。"),
    )
) + tuple(
    Scenario(
        f"biz-quality-advanced-filter-{key}", "客服质检", "/quality-inspection", f"高级查询 / {label}候选",
        (
            click("展开高级条件", text("展开(6)"), wait=text("收起")),
            menu("按已实测表单标签展开候选，不选择", css(f'.ant-form-item:has(label:text-is("{label}")) .ant-select')),
        ),
    )
    for key, label in (("brand", "品牌"), ("type", "问题类型"), ("category", "问题分类"), ("state", "质检情况"), ("scene", "转接场景"))
)

_DATES = tuple(
    Scenario(
        f"biz-date-{key}", module, path, "日期范围面板只读查看",
        (Step("展开开始日期面板，不选日期", "date", field("开始日期")),),
    )
    for key, module, path in (
        ("work-order", "智能工单", "/work-order"),
        ("review", "销冠知识审核", "/knowledge-review"),
        ("quality", "客服质检", "/quality-inspection"),
        ("ai-quality", "会话洞察分析", "/ai-quality-inspection"),
        ("quality-insight", "质检洞察分析", "/quality-inspection-insight"),
        ("consult-insight", "咨询洞察分析", "/consult-insight"),
        ("dashboard", "仪表盘", "/dashboard"),
        ("stats", "统计分析", "/stats"),
    )
)

SCENARIOS: tuple[Scenario, ...] = (
    _AI + _FOLLOW_ROUNDS + _FOLLOW_FORMS + _FOLLOW_TOOLS + _TRANSFER
    + _SIZE + _REVIEW + _INSPECTION + _STATS + _FILTERS + _DATES
)
