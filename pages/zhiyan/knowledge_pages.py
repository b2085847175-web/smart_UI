"""智言客服Agent - 知识库管理分组（不含商品管理，已在 product_config_page.py）

2026-10-16 探测确认。Page 内定位器均为探测时实际命中的选择器。
"""
from pages.base_page import BasePage
from pages.zhiyan._mixins import (  # 共用常量见 _mixins
    MODAL_CANCEL, MODAL_OK, MODAL_SAVE,
    POPCONFIRM_CANCEL, ROW_DELETE, ROW_EDIT, ROW_ADD_SCRIPT, ROW_ATTR, ROW_IMAGE,
    SEARCH_SHOP, NOOP_PROBE,
)


class ProductKnowledgePage(BasePage):
    """商品知识库 /product-knowledge"""
    PATH = "/product-knowledge"
    SEARCH_INPUT = "input[placeholder='请输入商品知识名称']"
    BATCH_IMPORT_BUTTON = "button:has-text('导入知识库')"
    BATCH_EXPORT_BUTTON = "button:has-text('导出知识库')"
    LOG_BUTTON = "button:has-text('操作日志')"
    ADD_SCRIPT_BUTTON = "button:has-text('添加话术')"
    # 行内
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    # 弹层
    IMPORT_MODAL = ".ant-modal:has-text('批量导入商品知识')"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    SCRIPT_MODAL = ".ant-modal:has-text('编辑商品知识话术')"


class ProductGroupPage(BasePage):
    """商品分组 /product-group"""
    PATH = "/product-group"
    SEARCH_INPUT = "input[placeholder='请输入分组名称/商品ID']"
    ADD_BUTTON = "button:has-text('新增分组')"
    GROUP_MODAL = ".ant-modal:has-text('分组')"
    GROUP_NAME_INPUT = "input[placeholder='请输入分组名称']"
    GROUP_PRODUCT_INPUT = "input[placeholder='请输入商品ID']"
    GROUP_TITLE_INPUT = "input[placeholder='请输入商品标题']"
    GROUP_POPCONFIRM = ".ant-popconfirm:visible"
    GROUP_POPCONFIRM_TEXT = "您确定要删除此分组吗？"


class StockConfigPage(BasePage):
    """货品管理 /stock-config"""
    PATH = "/stock-config"
    SEARCH_INPUT = "input[placeholder='请输入货品编码或名称']"
    ADD_BUTTON = "button:has-text('新增货品')"
    ADD_MODAL = ".ant-modal:has-text('新增货品')"
    EDIT_MODAL = ".ant-modal:has-text('货品配置信息')"
    STOCK_CODE_INPUT = "input[placeholder='请输入货品编码']"
    STOCK_TITLE_INPUT = "input[placeholder='请输入货品标题']"
    DELETE_MODAL = ".ant-modal:has-text('确认删除')"


class StockKnowledgePage(BasePage):
    """货品知识库 /stock-knowledge"""
    PATH = "/stock-knowledge"
    SEARCH_INPUT = "input[placeholder='请输入货品知识名称']"
    BATCH_IMPORT_BUTTON = "button:has-text('导入知识库')"
    BATCH_EXPORT_BUTTON = "button:has-text('导出知识库')"
    LOG_BUTTON = "button:has-text('操作日志')"
    ADD_SCRIPT_BUTTON = "button:has-text('添加话术')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    IMPORT_MODAL = ".ant-modal:has-text('批量导入货品知识')"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    SCRIPT_MODAL = ".ant-modal:has-text('编辑货品知识话术')"


class ShopKnowledgePage(BasePage):
    """店铺知识库 /shop-knowledge"""
    PATH = "/shop-knowledge"
    SEARCH_INPUT = "input[placeholder='请输入知识名称、内容或商品ID']"
    ADD_BUTTON = "button:has-text('新增知识')"
    LOG_BUTTON = "button:has-text('操作日志')"
    SYNC_BUTTON = "button:has-text('同步')"
    ROW_EDIT = ROW_EDIT
    ROW_DELETE = ROW_DELETE
    # 弹层
    ADD_MODAL = ".ant-modal:has-text('新增知识')"
    EDIT_MODAL = ".ant-modal:has-text('编辑知识')"
    SYNC_MODAL = ".ant-modal:has-text('同步知识至其他店铺')"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    NAME_INPUT = "input[placeholder='请输入知识名称']"
    SYNC_SEARCH_INPUT = "input[placeholder='请输入店铺名称']"


class SceneKnowledgePage(BasePage):
    """场景知识库 /scene（卡片式，非表格）"""
    PATH = "/scene"
    SEARCH_INPUT = "input[placeholder='请输入内容']"
    LOG_BUTTON = "button:has-text('操作日志')"
    SUBSCRIBE_BUTTON = "button:has-text('订阅行业包')"
    # 卡片行内操作：编辑/删除是 <button class="ant-btn-link"> 包 span
    CARD_EDIT = "button:has-text('编辑')"
    CARD_DELETE = "button:has-text('删除')"
    CARD_SWITCH = "[role=switch]"
    SWITCH_POPCONFIRM = ".ant-popconfirm:visible"
    SWITCH_POPCONFIRM_TEXT = "确认禁用该知识吗？"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    SUBSCRIBE_MODAL = ".ant-modal:has-text('订阅行业包')"
    SUBSCRIBE_SEARCH_INPUT = "input[placeholder='请输入行业包名称搜索']"
    # 卡片「编辑/新增知识」弹层（2026-10-16 补测确认）
    KNOWLEDGE_MODAL = ".ant-modal:has-text('知识名称')"
    KNOWLEDGE_NAME_INPUT = "input[placeholder='请输入知识名称']"
    # 弹层内的工具按钮
    ADD_KNOWLEDGE_BTN = "button:has-text('新增知识')"
    ADD_NEXT_BTN = "button:has-text('添加第')"  # 添加第N次知识内容
    TOOL_EMOJI = "button:has-text('表情')"
    TOOL_IMAGE = "button:has-text('图片')"
    TOOL_VIDEO = "button:has-text('视频')"
    TOOL_VARIABLE = "button:has-text('变量')"
    TOOL_PRODUCT_KNOW = "button:has-text('商品知识')"
    TOOL_SEPARATOR = "button:has-text('分隔线')"


class CustomKnowledgePage(BasePage):
    """自定义知识库 /keyword（卡片式）"""
    PATH = "/keyword"
    SEARCH_INPUT = "input[placeholder='请输入内容']"
    LOG_BUTTON = "button:has-text('操作日志')"
    ADD_SCENE_BUTTON = "button:has-text('添加关键词场景')"
    ADD_KNOWLEDGE_BUTTON = "button:has-text('新增知识')"
    CARD_EDIT = "span:has-text('编辑')"
    CARD_DELETE = "span:has-text('删除')"
    CARD_SWITCH = "[role=switch]"
    SWITCH_POPCONFIRM = ".ant-popconfirm:visible"
    SWITCH_POPCONFIRM_TEXT = "确认禁用该知识吗？"
    DELETE_POPCONFIRM = ".ant-popconfirm:visible"
    DELETE_POPCONFIRM_TEXT = "删除后已配置的条件与知识内容均会删除，不可恢复，确认删除吗？"
    LOG_MODAL = ".ant-modal:has-text('操作日志')"
    ADD_SCENE_MODAL = ".ant-modal:has-text('添加关键词场景')"
    KNOWLEDGE_MODAL = ".ant-modal:has-text('请输入知识名称')"
    KNOWLEDGE_NAME_INPUT = "input[placeholder='请输入知识名称']"
