"""2026-11-10 新登记页面的显式只读流程；只打开表单与列表，不保存、不删除、不发送。"""
from .specs import (
    Scenario, button, click, css, field, gap, inspect, menu, opened, search, text,
)


SCENARIOS = (
    # ---------- 智言 Harness ----------
    Scenario("harness-context-menu", "智言Harness", "/harness", "添加上下文候选", (
        menu("上下文菜单候选", button("添加上下文")),
        gap("会话选择弹窗未进入", "菜单候选按只读策略禁止点击；客服质检会话选择弹窗暂不覆盖。"),
    ), "只观察9类上下文候选，不选择、不发送。"),
    Scenario("harness-quick-tasks", "智言Harness", "/harness", "快捷任务提示词预填", (
        click("预填分析对话", text("分析对话")),
        inspect("输入区存在", css("textarea")),
    ), "预填仅进入输入框，不发送消息。"),
    Scenario("harness-session-search", "智言Harness", "/harness", "会话标题搜索入口", (
        click("打开会话搜索", button("搜索会话")),
        inspect("标题搜索字段", field("搜索会话标题", "page")),
    ), "只打开搜索面板，不输入不切换会话。"),

    # ---------- 标签管理 ----------
    Scenario("tag-category-add", "标签管理", "/tag", "新增分类表单", (
        opened("新增分类", button("新增分类")),
        inspect("分类名称字段", field("请输入分类名称", "overlay")),
    ), "分类名限15字；只打开不填写不保存。"),
    Scenario("tag-item-add", "标签管理", "/tag", "新增标签表单", (
        opened("新增标签", button("新增标签")),
        inspect("标签名称字段", field("请输入标签名称", "overlay")),
        inspect("描述字段", field("请输入描述", "overlay")),
    ), "判断标准限100字；只打开不填写不保存。"),
    Scenario("tag-official-view", "标签管理", "/tag", "官方标签只读详情", (
        opened("查看官方标签", text("查看", sample=True, data=True)),
        inspect("只读详情字段", css("input[disabled], textarea[disabled]", "overlay")),
    ), "官方标签详情只读，不编辑不切换状态。"),
    Scenario("tag-search", "标签管理", "/tag", "标签名称查询", (
        search("查询标签", "搜索标签名称", "测试"),
        inspect("查询结果区域"),
    )),

    # ---------- 账号管理 ----------
    Scenario("admin-account-add", "平台管理", "/accounts", "新增账号表单", (
        opened("新增账号", button("新增账号")),
        inspect("账号字段", field("请输入账号", "overlay")),
        inspect("角色与接待模式控件", css(".ant-modal .ant-select", "overlay")),
    ), "角色三选一、接待模式三复选；只打开不填写不保存。"),
    Scenario("admin-account-edit", "平台管理", "/accounts", "代表账号编辑", (
        opened("代表账号编辑", text("编辑", sample=True, data=True)),
        inspect("新密码留空提示", field("请输入新密码（留空不修改）", "overlay")),
    ), "不修改账号、姓名、角色、接待模式。"),
    Scenario("admin-account-search", "平台管理", "/accounts", "账号或姓名查询", (
        search("查询账号", "请输入账号或姓名搜索", "test"),
        inspect("查询结果区域"),
    )),
    Scenario("admin-account-auth", "平台管理", "/accounts", "普通员工店铺授权抽屉", (
        opened("打开店铺授权抽屉", text("店铺授权", row="codex_test_20260721", data=True)),
        inspect("授权双页签", css("[role=tab]", "overlay")),
    ), "只打开抽屉观察页签，不授权不取消授权；行样本缺失按受限记录。"),

    # ---------- 品牌管理 ----------
    Scenario("admin-brand-add", "平台管理", "/brands", "新增品牌表单", (
        opened("新增品牌", button("新增品牌")),
        inspect("品牌表单字段", css("input", "overlay")),
    ), "只打开不填写不保存。"),
    Scenario("admin-brand-edit", "平台管理", "/brands", "代表品牌编辑", (
        opened("代表品牌编辑", text("编辑", sample=True, data=True)),
        inspect("品牌表单字段", css("input", "overlay")),
    ), "不修改品牌名称或状态。"),
    Scenario("admin-brand-search", "平台管理", "/brands", "品牌名称查询", (
        search("查询品牌", "请输入品牌名称搜索", "UI"),
        inspect("查询结果区域"),
    )),

    # ---------- 店铺管理 ----------
    Scenario("admin-shop-add", "平台管理", "/shops", "新增店铺表单", (
        opened("新增店铺", button("新增店铺")),
        inspect("店铺名称字段", field("请输入店铺名称（必须与电商平台的店铺名称保持一致）", "overlay")),
    ), "电商平台、所属行业、品牌不选择；只打开不填写不保存。"),
    Scenario("admin-shop-edit", "平台管理", "/shops", "代表店铺编辑", (
        opened("代表店铺编辑", text("编辑", sample=True, data=True)),
        inspect("店铺表单字段", css("input", "overlay")),
    ), "不修改店铺名称、平台、行业或品牌。"),
    Scenario("admin-shop-search", "平台管理", "/shops", "店铺名称查询", (
        search("查询店铺", "请输入店铺名称搜索", "儒意"),
        inspect("查询结果区域"),
    )),

    # ---------- 店铺分组 ----------
    Scenario("admin-group-add", "平台管理", "/shop-group", "新增分组表单", (
        opened("新增分组", button("新增分组")),
        inspect("分组名称字段", field("请输入分组名称", "overlay")),
    ), "分组名限30字，不选择店铺；只打开不填写不保存。"),
    Scenario("admin-group-edit", "平台管理", "/shop-group", "代表分组编辑", (
        opened("代表分组编辑", text("编辑", sample=True, data=True)),
        inspect("分组名称字段", field("请输入分组名称", "overlay")),
    ), "不修改分组名称与店铺集合。"),
)
