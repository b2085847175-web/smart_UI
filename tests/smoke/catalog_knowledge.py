"""八个知识库模块的显式安全链路；每个场景均由执行器从 path 重新导航。"""
from .specs import (
    Scenario,
    Step,
    button,
    click,
    css,
    field,
    gap,
    inspect,
    menu,
    opened,
    search,
    text,
)


_PRODUCT = "680483637921"
_STOCK = "RY-50834"
_KNOWLEDGE_EDIT = 'button.ant-btn-link:has([aria-label="edit"])'
_PRODUCT_QUERY = "请输入商品ID、商品标题搜索"
_STOCK_QUERY = "请输入货品编码或名称"


SCENARIOS = (
    Scenario(
        "kb-product-search", "商品管理", "/product-config", "按已知商品ID查询",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            inspect("代表商品行可见", css("td", row=_PRODUCT, data=True)),
        ),
    ),
    Scenario(
        "kb-product-stock-search", "商品管理", "/product-config", "按已知货品编码查询商品",
        (
            search("查询关联货品编码", "请输入货品编码搜索", _STOCK),
            inspect("查询结果表格", css(".ant-table")),
        ),
    ),
    Scenario(
        "kb-product-status-menu", "商品管理", "/product-config", "商品状态筛选候选",
        (menu("只展开商品状态候选", css('.ant-select:has-text("全部")')),),
        "只展开候选，不选择上架或下架，不改变商品状态。",
    ),
    Scenario(
        "kb-product-add", "商品管理", "/product-config", "新增商品表单",
        (
            opened("打开新增商品", button("新增商品")),
            inspect("商品ID字段", field("请输入商品ID", "overlay")),
        ),
        "仅打开已实测表单，不填写、不确认。",
    ),
    Scenario(
        "kb-product-add-stock-menu", "商品管理", "/product-config", "新增商品的货品编码候选",
        (
            opened("打开新增商品", button("新增商品")),
            menu("只展开货品编码候选", css('.ant-select:has-text("请输入货品编码查询")', "overlay")),
        ),
        "候选可能为空；不输入或绑定货品。",
    ),
    Scenario(
        "kb-product-add-status-menu", "商品管理", "/product-config", "新增商品的商品状态候选",
        (
            opened("打开新增商品", button("新增商品")),
            menu("只展开表单商品状态", css('.ant-select:has-text("上架")', "overlay")),
        ),
        "不选择候选、不切换推荐状态、不确认。",
    ),
    Scenario(
        "kb-product-edit", "商品管理", "/product-config", "代表商品编辑表单",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开代表商品编辑", text("编辑", row=_PRODUCT, data=True)),
            inspect("商品ID字段", field("请输入商品ID", "overlay")),
        ),
        "仅打开既有商品信息，不填写、不保存。",
    ),
    Scenario(
        "kb-product-script", "商品管理", "/product-config", "代表商品的话术入口",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品知识", text("添加话术", row=_PRODUCT, data=True)),
            inspect("商品知识搜索入口", field("请输入商品知识名称搜索", "overlay")),
            gap("商品知识数据完整性", "旧探测的商品知识读取POST被保护拦截；打开抽屉不代表内部知识数据完整。"),
        ),
    ),
    Scenario(
        "kb-product-attributes", "商品管理", "/product-config", "代表商品属性列表",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品属性", text("商品属性", row=_PRODUCT, data=True)),
            inspect("属性查询入口", field("属性名搜索", "overlay")),
        ),
    ),
    Scenario(
        "kb-product-attribute-add", "商品管理", "/product-config", "添加属性的行内表单",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品属性", text("商品属性", row=_PRODUCT, data=True)),
            click("打开新增属性行", button("添加属性", "overlay"), wait=field("请输入属性名", "overlay")),
            inspect("新增属性值字段", field("请输入属性值", "overlay")),
        ),
        "行内新增只展示空表单，不填写、不保存。",
    ),
    Scenario(
        "kb-product-attribute-edit", "商品管理", "/product-config", "品牌属性的行内编辑",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品属性", text("商品属性", row=_PRODUCT, data=True)),
            click("打开品牌属性编辑", button("编辑", "overlay", row="品牌", data=True), wait=field("请输入属性名", "overlay")),
            inspect("属性值字段", field("请输入属性值", "overlay")),
        ),
        "只打开指定品牌属性，不修改、不保存。",
    ),
    Scenario(
        "kb-product-images", "商品管理", "/product-config", "代表商品图片管理",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品图片管理", text("图片管理", row=_PRODUCT, data=True)),
            inspect("图片内容查询入口", field("内容搜索", "overlay")),
        ),
        "不点击智能识别，不上传或删除图片。",
    ),
    Scenario(
        "kb-product-image-types", "商品管理", "/product-config", "商品图片类型候选",
        (
            search("查询代表商品", _PRODUCT_QUERY, _PRODUCT),
            opened("打开商品图片管理", text("图片管理", row=_PRODUCT, data=True)),
            menu("只展开自绘图片类型筛选", text("全部", "overlay")),
        ),
        "已实测为自绘按钮，不按 Ant Select 猜测；不选择类型。",
    ),
    Scenario(
        "kb-group-search", "商品分组", "/product-group", "商品分组只读查询",
        (
            search("按已知商品ID查询分组", "请输入分组名称/商品ID", _PRODUCT),
            inspect("查询结果表格", css(".ant-table")),
        ),
    ),
    Scenario(
        "kb-group-add", "商品分组", "/product-group", "新增分组表单及绑定入口",
        (
            opened("打开新增分组", button("新增分组")),
            inspect("分组名称字段", field("请输入分组名称", "overlay")),
            inspect("绑定商品入口", text("绑定商品", "overlay")),
            gap("绑定商品后续分支", "不切换绑定商品开关，不选择或增删绑定商品。"),
        ),
    ),
    Scenario(
        "kb-group-edit", "商品分组", "/product-group", "代表分组编辑表单",
        (
            opened("打开首个代表分组编辑", button("编辑", sample=True, data=True)),
            inspect("既有分组名称字段", field("请输入分组名称", "overlay")),
        ),
        "明确只取首个代表分组，不遍历全部分组，不修改绑定条件或保存。",
    ),
    Scenario(
        "kb-stock-search", "货品管理", "/stock-config", "按已知货品编码查询",
        (
            search("查询代表货品", _STOCK_QUERY, _STOCK),
            inspect("代表货品行可见", css("td", row=_STOCK, data=True)),
        ),
    ),
    Scenario(
        "kb-stock-add", "货品管理", "/stock-config", "新增货品表单",
        (
            opened("打开新增货品", button("新增货品")),
            inspect("货品编码字段", field("请输入货品编码", "overlay")),
            inspect("货品标题字段", field("请输入货品标题", "overlay")),
        ),
        "只打开表单，不填写、不保存。",
    ),
    Scenario(
        "kb-stock-edit", "货品管理", "/stock-config", "代表货品配置信息",
        (
            search("查询代表货品", _STOCK_QUERY, _STOCK),
            opened("打开货品配置信息", button("编辑", row=_STOCK, data=True)),
            inspect("货品知识区域", text("货品知识", "overlay")),
        ),
        "不触发AI生成、清空知识或货品信息修改。",
    ),
    Scenario(
        "kb-shop-search", "店铺知识库", "/shop-knowledge", "店铺知识只读查询",
        (
            search("查询知识名称", "请输入知识名称、内容或商品ID", "运费"),
            inspect("知识查询结果", css(".ant-table")),
        ),
    ),
    Scenario(
        "kb-shop-add", "店铺知识库", "/shop-knowledge", "新增店铺知识表单",
        (
            opened("打开新增知识", button("新增知识")),
            inspect("知识名称字段", field("请输入知识名称", "overlay")),
            inspect("关联商品条件", text("关联商品", "overlay")),
            inspect("生效时间条件", text("生效时间", "overlay")),
        ),
        "不填写正文，不添加内容段落，不切换商品、分组或时间模式，不保存。",
    ),
    Scenario(
        "kb-shop-edit", "店铺知识库", "/shop-knowledge", "代表店铺知识及既有多段内容",
        (
            search("查询代表知识", "请输入知识名称、内容或商品ID", "运费"),
            opened("打开运费知识编辑", button("编辑", row="运费", data=True)),
            inspect("知识名称字段", field("请输入知识名称", "overlay")),
            inspect("既有正文输入区域数量", css("textarea", "overlay")),
        ),
        "只记录既有正文区域数量，不保存正文，不增删段落或切换条件。",
    ),
    Scenario(
        "kb-shop-product-view", "店铺知识库", "/shop-knowledge", "切换商品视图",
        (
            click("切换到商品视图", text("商品视图"), wait=css(".ant-table")),
            inspect("商品视图表格", css(".ant-table")),
        ),
        "只切换已知只读视图，不修改知识配置。",
    ),
    Scenario(
        "kb-shop-knowledge-view", "店铺知识库", "/shop-knowledge", "从商品视图切回知识视图",
        (
            click("切换到商品视图", text("商品视图"), wait=css(".ant-table")),
            click("切回知识视图", text("知识视图"), wait=button("新增知识")),
            inspect("知识视图列表", css(".ant-table")),
        ),
    ),
    Scenario(
        "kb-scene-search", "场景知识库", "/scene", "场景知识内容查询",
        (
            search("按当前已知搜索类型查询", "请输入内容", "使用"),
            inspect("查询后内容区域"),
        ),
        "只在默认模拟问法类型下查询，不切换搜索类型或业务配置。",
    ),
    Scenario(
        "kb-scene-search-types", "场景知识库", "/scene", "场景知识搜索类型候选",
        (menu("只展开搜索类型", css('.ant-select:has-text("模拟问法")')),),
        "不选择其他搜索类型。",
    ),
    Scenario(
        "kb-scene-industry", "场景知识库", "/scene", "行业包订阅说明",
        (
            opened("打开行业包列表", button("订阅行业包")),
            inspect("行业包浮层", css(".ant-modal:visible", "page")),
        ),
        "只打开，不订阅或取消订阅，不点击任何行业项。",
    ),
    Scenario(
        "kb-scene-edit", "场景知识库", "/scene", "代表知识条目编辑及当前回复条件",
        (
            opened("打开首个代表知识条目", css(_KNOWLEDGE_EDIT, sample=True, data=True)),
            inspect("知识名称字段", field("请输入知识名称", "overlay")),
            inspect("关联商品条件", text("关联商品", "overlay")),
            inspect("订单状态条件", text("订单状态", "overlay")),
            inspect("生效时间条件", text("生效时间", "overlay")),
        ),
        "用知识链接按钮而非场景标题编辑；只查看当前轮次、回复方式及条件，不切换、不添加轮次、不保存。",
    ),
    Scenario(
        "kb-keyword-search", "自定义知识库", "/keyword", "关键词查询",
        (
            search("按当前关键词类型查询", "请输入内容", "使用"),
            inspect("查询后内容区域"),
        ),
    ),
    Scenario(
        "kb-keyword-search-types", "自定义知识库", "/keyword", "关键词搜索类型候选",
        (menu("只展开搜索类型", css('.ant-select:has-text("关键词")')),),
        "不选择其他类型。",
    ),
    Scenario(
        "kb-keyword-scene-add", "自定义知识库", "/keyword", "添加关键词场景规则说明",
        (
            opened("打开添加关键词场景", button("添加关键词场景")),
            inspect("关键词规则表单", css(".ant-modal:visible", "page")),
        ),
        "只查看同场景AND、跨场景OR、15字/50场景规则；不输入关键词、不添加场景、不保存。",
    ),
    Scenario(
        "kb-keyword-scene-edit", "自定义知识库", "/keyword", "代表关键词场景标题编辑",
        (
            opened(
                "打开首个代表场景标题编辑",
                css('button:not(.ant-btn-link):has-text("编 辑")', sample=True, data=True),
                wait=text("编辑关键词场景", "overlay"),
            ),
            inspect("关键词场景编辑表单", css(".ant-modal:visible", "page")),
        ),
        "该入口专门编辑关键词场景，不与知识条目编辑混用；不修改关键词或保存。",
    ),
    Scenario(
        "kb-keyword-knowledge-add", "自定义知识库", "/keyword", "代表场景新增知识表单",
        (
            opened("打开首个代表场景新增知识", button("新增知识", sample=True, data=True)),
            inspect("知识名称字段", field("请输入知识名称", "overlay")),
            inspect("关联商品条件", text("关联商品", "overlay")),
        ),
        "明确只取首个代表场景，不填写、不增删轮次、不切换条件、不保存。",
    ),
    Scenario(
        "kb-keyword-knowledge-edit", "自定义知识库", "/keyword", "代表知识条目编辑",
        (
            opened("打开首个代表知识条目", css(_KNOWLEDGE_EDIT, sample=True, data=True)),
            inspect("知识名称字段", field("请输入知识名称", "overlay")),
            inspect("订单状态条件", text("订单状态", "overlay")),
            inspect("生效时间条件", text("生效时间", "overlay")),
        ),
        "知识条目与关键词场景标题独立；只查看当前多轮内容与条件，不切换或保存。",
    ),
)


# 下面是已知入口的显式参数矩阵，不从页面内容推导或自动点击功能。
SCENARIOS += tuple(
    Scenario(
        f"kb-product-import-{suffix}", "商品管理", "/product-config", f"批量{label}说明",
        (
            Step("展开批量操作菜单", "menu", button("批量操作"), destination="keep"),
            opened(
                f"打开{label}说明",
                css(f'.ant-dropdown:visible .ant-dropdown-menu-item:has(:text-is("{label}"))', "page"),
            ),
            inspect("导入说明弹层", css(".ant-modal:visible", "page")),
        ),
        "只查看说明，不下载模板、不选择文件、不上传、不提交。",
    )
    for suffix, label in (("attributes", "导入属性"), ("status", "导入商品状态"))
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-script-{suffix}", module, path, f"代表{kind}的{label}页签",
        (
            search(f"查询代表{kind}", placeholder, key),
            opened(f"打开{kind}知识", text(entry, row=key, data=True) if prefix == "product" else button(entry, row=key, data=True)),
            click(
                f"切换{label}页签",
                css(f'[role="tab"]:has-text("{label}")', "overlay"),
                wait=css(f'[role="tab"][aria-selected="true"]:has-text("{label}")', "overlay"),
            ),
            inspect("当前知识页签区域", css('[role="tabpanel"]:visible', "overlay")),
        ),
        "只切换已实测知识页签；空列表是允许的数据态，不生成、不清空、不保存。"
        + ("商品知识读取曾被保护拦截，抽屉数据完整性不作通过保证。" if prefix == "product" else ""),
    )
    for prefix, module, path, kind, placeholder, key, entry in (
        ("product", "商品管理", "/product-config", "商品", _PRODUCT_QUERY, _PRODUCT, "添加话术"),
        ("stock", "货品管理", "/stock-config", "货品", _STOCK_QUERY, _STOCK, "编辑"),
    )
    for suffix, label in (("configured", "已配置知识"), ("unconfigured", "未配置知识"))
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-knowledge-search", module, path, "按已知知识名称查询",
        (
            search("查询使用方法知识", placeholder, "使用方法"),
            inspect("使用方法知识行", text("使用方法", data=True)),
        ),
    )
    for prefix, module, path, placeholder in (
        ("product", "商品知识库", "/product-knowledge", "请输入商品知识名称"),
        ("stock", "货品知识库", "/stock-knowledge", "请输入货品知识名称"),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-knowledge-import", module, path, "导入知识库说明",
        (
            opened("打开知识库导入说明", button("导入知识库")),
            inspect("导入说明弹层", css(".ant-modal:visible", "page")),
        ),
        "只查看规则，不下载模板、不上传、不提交、不导出。",
    )
    for prefix, module, path in (
        ("product", "商品知识库", "/product-knowledge"),
        ("stock", "货品知识库", "/stock-knowledge"),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-knowledge-content", module, path, "使用方法的代表话术明细",
        (
            opened("打开使用方法话术明细", button("添加话术", row="使用方法", data=True)),
            inspect("已知代表条目", css("td", "overlay", row=key, data=True)),
        ),
        "只查看使用方法，不遍历全部知识类型或商品/货品。",
    )
    for prefix, module, path, key in (
        ("product", "商品知识库", "/product-knowledge", _PRODUCT),
        ("stock", "货品知识库", "/stock-knowledge", _STOCK),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-knowledge-inline-edit", module, path, "使用方法的指定样本正文行内编辑",
        (
            opened("打开使用方法话术明细", button("添加话术", row="使用方法", data=True)),
            click(
                "打开指定样本正文行内编辑",
                css('button:has([aria-label="edit"])', "overlay", row=key, data=True),
                wait=css('[contenteditable="true"]', "overlay", row=key, data=True),
            ),
            inspect("正文编辑区域", css('[contenteditable="true"]', "overlay", row=key, data=True)),
        ),
        "指定商品/货品行定位；这是既有抽屉内行内编辑，不等待新弹层，不输入、不保存。",
    )
    for prefix, module, path, key in (
        ("product", "商品知识库", "/product-knowledge", _PRODUCT),
        ("stock", "货品知识库", "/stock-knowledge", _STOCK),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-log-detail", module, path, "操作日志及首条代表变更详情",
        (
            opened("打开操作日志", button("操作日志")),
            inspect("日志表格", css(".ant-table", "overlay")),
            opened("打开首条代表日志详情", text("查看详情", "overlay", sample=True, data=True)),
            inspect("详情弹层内容区域结构，不记录知识正文", css(".ant-modal-body, .ant-drawer-body", "overlay")),
        ),
        "明确仅选首条代表日志；无日志时按空数据受限，不保存操作人、时间及变更正文。",
    )
    for prefix, module, path in (
        ("product", "商品知识库", "/product-knowledge"),
        ("stock", "货品知识库", "/stock-knowledge"),
        ("shop", "店铺知识库", "/shop-knowledge"),
        ("scene", "场景知识库", "/scene"),
        ("keyword", "自定义知识库", "/keyword"),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-page-size", module, path, "分页条数候选",
        (menu("只展开分页条数候选", css(".ant-pagination-options .ant-select")),),
        "只展开，不选择或翻页。",
    )
    for prefix, module, path in (
        ("product", "商品管理", "/product-config"),
        ("product-knowledge", "商品知识库", "/product-knowledge"),
        ("group", "商品分组", "/product-group"),
        ("stock", "货品管理", "/stock-config"),
        ("stock-knowledge", "货品知识库", "/stock-knowledge"),
        ("shop", "店铺知识库", "/shop-knowledge"),
        ("scene", "场景知识库", "/scene"),
        ("keyword", "自定义知识库", "/keyword"),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-rich-{suffix}", module, path, f"代表知识首段的{tool}工具",
        (
            opened("打开代表知识表单", parent),
            menu(
                f"只展开首段{tool}候选", button(tool, "overlay", sample=True),
                candidates=".ant-table tbody tr[data-row-key]" if suffix == "variables" else ".ant-list-item",
            ),
        ),
        "多轮知识明确仅取首段代表工具，不点击菜单候选、不插入内容、不保存。",
    )
    for prefix, module, path, parent in (
        ("scene", "场景知识库", "/scene", css(_KNOWLEDGE_EDIT, sample=True, data=True)),
        ("keyword", "自定义知识库", "/keyword", button("新增知识", sample=True, data=True)),
    )
    for suffix, tool in (("variables", "变量"), ("product-knowledge", "商品知识"))
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-rich-video", module, path, "代表知识首段视频说明弹层",
        (
            opened("打开代表知识表单", parent),
            opened("打开首段视频工具", button("视频", "overlay", sample=True)),
            inspect("视频弹层", css(".ant-modal:visible", "page")),
        ),
        "只打开视频面板，不输入地址、不上传、不插入、不保存。",
    )
    for prefix, module, path, parent in (
        ("scene", "场景知识库", "/scene", css(_KNOWLEDGE_EDIT, sample=True, data=True)),
        ("keyword", "自定义知识库", "/keyword", button("新增知识", sample=True, data=True)),
    )
)

SCENARIOS += tuple(
    Scenario(
        f"kb-{prefix}-rich-gaps", module, path, "图片与表情工具覆盖边界",
        (
            opened("打开代表知识表单", parent),
            gap(
                "图片文件入口与表情浮层",
                "图片历史只观察到文件选择器；本链不触发系统文件选择，不选择文件、不上传。"
                "表情旧探测未成功捕获独立面板，不能认定已覆盖；不强制事件、不插入表情。",
            ),
        ),
    )
    for prefix, module, path, parent in (
        ("scene", "场景知识库", "/scene", css(_KNOWLEDGE_EDIT, sample=True, data=True)),
        ("keyword", "自定义知识库", "/keyword", button("新增知识", sample=True, data=True)),
    )
)
