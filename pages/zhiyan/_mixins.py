"""Page Object 复用常量：弹层按钮、行内操作通用选择器。"""

# 弹层通用
MODAL_CANCEL = "button:has-text('取 消')"
MODAL_OK = "button:has-text('确 定'), button:has-text('确 认')"
MODAL_SAVE = "button:has-text('保 存')"
POPCONFIRM_CANCEL = ".ant-popconfirm:visible button:has-text('取 消')"

# 行内通用（按文本）
ROW_EDIT = "text=编辑"
ROW_DELETE = "text=删除"
ROW_ADD_SCRIPT = "text=添加话术"
ROW_ATTR = "text=商品属性"
ROW_IMAGE = "text=图片管理"

# 列表外搜索
SEARCH_SHOP = "input[placeholder='输入店铺名称搜索']"

# 仅占位（prober 中使用，不导出给 Page）
NOOP_PROBE = None
