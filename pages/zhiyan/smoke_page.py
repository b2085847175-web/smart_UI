"""只读冒烟专用页面对象，不复用旧版宽泛定位和带输入日志的fill。"""
import hashlib
import re
from time import monotonic
from urllib.parse import urlsplit

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


OVERLAYS = ".ant-modal:visible, .ant-drawer-content:visible"
FLOATING = ".ant-dropdown:visible, .ant-select-dropdown:visible, .ant-popover:visible"
MAIN = ".ant-pro-page-container-children-content:visible, .ant-pro-page-container-children-container:visible"
FORBIDDEN = re.compile(
    r"删除|清空|保存|确[定认]|启用|停用|禁用|上传|导出|下载|生成|采纳|复检|已检|"
    r"充值|支付|购买|提交|发布|分隔线|同步|订阅|导入"
)


def exact(value):
    return re.compile(r"^\s*" + r"\s*".join(re.escape(c) for c in value.replace(" ", "")) + r"\s*$")


class Unavailable(RuntimeError):
    """空数据、禁用或预先明确的覆盖限制。"""


class AuthenticationLost(RuntimeError):
    pass


class SmokePage:
    def __init__(self, page, base_url, timeout, guard=None):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.samples = []
        self.guard = guard or (lambda: None)

    def settle(self):
        self.guard()
        self.page.locator("body").wait_for(state="visible")
        self.guard()
        self.page.wait_for_function("""() =>
            (window.__smokePending || 0) === 0 &&
            performance.now() - (window.__smokeLastActivity || 0) >= 350 &&
            ![...document.querySelectorAll('.ant-spin-spinning')]
            .some(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')""")
        self.guard()
        if urlsplit(self.page.url).path.rstrip("/") == "/login":
            raise AuthenticationLost("登录会话失效，停止后续业务遍历")

    def goto(self, path):
        parts = urlsplit(path)
        if parts.scheme or parts.netloc or not path.startswith("/") or path.startswith("//"):
            raise ValueError("只允许本站已登记的相对路径")
        self.guard()
        self.page.goto(self.base_url + path, wait_until="domcontentloaded")
        self.guard()
        try:
            self.page.wait_for_url(re.compile(re.escape(self.base_url + parts.path.rstrip("/")) + r"/?(?:[?#].*)?$"))
        except PlaywrightTimeoutError:
            if urlsplit(self.page.url).path.rstrip("/") == "/login":
                raise AuthenticationLost("登录会话失效，停止后续业务遍历") from None
            raise
        self.settle()
        self.root("main").wait_for(state="visible")
        self.page.wait_for_function("""() => {
            const root = document.querySelector('main') || document.querySelector('.ant-pro-page-container') ;
            return !!root && !!root.innerText.trim();
        }""")

    def root(self, scope):
        if scope == "page":
            return self.page.locator("body")
        if scope == "overlay":
            # Ant弹层按DOM挂载顺序堆叠，最后一个可见弹层为当前前景。
            return self.page.locator(OVERLAYS).last
        if scope != "main":
            raise ValueError("未知作用域: " + scope)
        content = self.page.locator(MAIN)
        if content.count():
            return content.last
        main = self.page.locator("main:visible")
        return main if main.count() == 1 else self.page.locator(".ant-pro-page-container:visible")

    def resolve(self, target, many=False):
        self.guard()
        scope = self.root(target.scope)
        scope.wait_for(state="visible")
        if target.row:
            rows = scope.locator("tbody tr[data-row-key]")
            scope = rows.filter(has_text=re.compile(re.escape(target.row)))
            try:
                scope.first.wait_for(state="visible")
            except PlaywrightTimeoutError:
                if target.data:
                    raise Unavailable("当前列表无指定样本: " + target.row) from None
                raise
            if scope.count() != 1:
                raise RuntimeError("指定业务行不唯一: " + target.row)
        if target.kind == "css":
            result = scope.locator(target.value)
        elif target.kind == "placeholder":
            result = scope.get_by_placeholder(target.value, exact=True)
        elif target.kind == "text":
            result = scope.get_by_text(exact(target.value))
        elif target.kind in {"button", "tab", "link"}:
            result = scope.get_by_role(target.kind, name=exact(target.value))
            if target.kind == "button":
                # Ant图标的img名称可能加入无障碍名称，仍要求按钮自身文案完全匹配。
                result = result.or_(scope.locator("button,[role=button]").filter(has_text=exact(target.value)))
        else:
            raise ValueError("未知定位类型: " + target.kind)
        result = result.locator("visible=true")
        try:
            result.first.wait_for(state="visible")
        except PlaywrightTimeoutError:
            if target.data and self.empty_state(scope):
                raise Unavailable("列表为空，无法进入: " + target.value) from None
            raise
        count = result.count()
        if many:
            return result
        if count != 1:
            if not target.sample:
                raise RuntimeError(f"入口不唯一({count}): {target.value}")
            sample = result.nth(0)
            deadline = monotonic() + self.timeout / 1000
            while True:
                self.guard()
                remaining = int((deadline - monotonic()) * 1000)
                if remaining <= 0:
                    raise RuntimeError("代表业务行未稳定，拒绝动态首项点击")
                sample.wait_for(state="visible", timeout=remaining)
                candidate = sample.evaluate("""async e => {
                    const key = () => e.closest('[data-row-key]')?.getAttribute('data-row-key') || '';
                    const before = key();
                    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                    return e.isConnected && e.getClientRects().length &&
                        getComputedStyle(e).visibility !== 'hidden' && key() === before ? {key: before} : null;
                }""")
                if candidate is not None:
                    key = candidate["key"]
                    break
                if monotonic() >= deadline:
                    raise RuntimeError("代表业务行未稳定，拒绝动态首项点击")
            if key:
                row = self.page.evaluate("key => CSS.escape(key)", key)
                result = result.and_(scope.locator(f"[data-row-key={row}], [data-row-key={row}] *"))
                result.first.wait_for(state="visible")
                if result.count() != 1:
                    raise RuntimeError("代表业务行内入口不唯一，拒绝动态首项点击")
            else:
                result = sample
            self.samples.append({"target": target.value, "matches": count, "sample_index": 0,
                                 "row_key_hash": hashlib.sha256(key.encode()).hexdigest()[:12] if key else None})
        self.guard()
        if result.is_disabled():
            raise Unavailable("控件禁用: " + target.value)
        return result

    @staticmethod
    def empty_state(scope):
        tables = scope.locator(".ant-table:visible")
        if tables.count() != 1:
            return False
        table = tables.nth(0)
        data_rows = table.locator("tbody tr[data-row-key]")
        return bool(table.locator(".ant-empty:visible, .ant-table-placeholder:visible").count()) and data_rows.count() == 0

    def validate_action(self, element, target=None, action="click"):
        self.guard()
        danger = element.evaluate("""e => {
            const sensitive = '[role=switch],[role=checkbox],[role=radio],input[type=checkbox],input[type=radio],input[type=file],.ant-checkbox-wrapper,.ant-radio-wrapper,.ant-switch';
            const label = e.closest('label');
            const button = e.closest('button,[role=button]');
            // 普通表单label可把内部button识别为自己的control，只排除这种自关联。
            const unsafeLabel = label && (!button || !label.contains(button) || label.htmlFor ||
                (label.control && label.control !== button) || label.querySelector(sensitive));
            return !!e.closest(sensitive) || !!e.querySelector(sensitive) || !!unsafeLabel ||
                !!e.closest('[role=option],[role=menuitem],.ant-select-item-option');
        }""")
        # 只读导入菜单入口是唯一允许点击的候选项，不允许选择普通下拉候选。
        allowed_import_item = (
            target is not None and action == "open" and target.scope == "page"
            and target.kind == "css" and ".ant-dropdown:visible" in target.value
            and any(label in target.value for label in ("导入属性", "导入商品状态"))
        )
        readonly_view = (
            target is not None and action == "click" and target.kind == "text" and target.scope == "main"
            and target.value in {"商品视图", "知识视图"}
            and urlsplit(self.page.url).path.rstrip("/") == "/shop-knowledge"
            and not self.page.locator(OVERLAYS).count()
        )
        if danger and not (allowed_import_item or readonly_view):
            raise RuntimeError("禁止操作开关、关联label或菜单候选")
        if action == "close":
            if not element.evaluate("e => e.matches('button,[role=button],.ant-modal-close,.ant-drawer-close')"):
                raise RuntimeError("关闭入口必须为按钮或标准关闭节点")
            if element.evaluate("""e => !!e.form && ['submit', 'reset'].includes(e.type)"""):
                raise RuntimeError("关闭入口不得提交或重置表单")
        role = element.get_attribute("role") or ""
        tag = element.evaluate("e => e.tagName.toLowerCase()")
        kind = element.get_attribute("type") or ""
        label = re.sub(r"\s+", "", element.evaluate("""e => {
            const action = e.closest('button,a,[role=button],[role=menuitem]') || e;
            return action.innerText || action.getAttribute('aria-label') || '';
        }"""))
        danger_label = re.sub(r"\s+", "", element.evaluate("""e => {
            const action = e.closest('button,a,[role=button],[role=menuitem]') || e;
            return [action.innerText, action.getAttribute('aria-label'), action.getAttribute('title')]
                .filter(Boolean).join(' ');
        }"""))
        safe_sync_entry = (
            target is not None and action == "open" and urlsplit(self.page.url).path == "/sync"
            and not self.page.locator(OVERLAYS).count()
            and target.kind == "css" and 'file-text' in target.value
            and label == "跨店同步"
        )
        if role in {"switch", "checkbox", "radio"} or kind in {"checkbox", "radio", "file"}:
            raise RuntimeError("禁止修改配置/选择/上传控件")
        if tag in {"input", "textarea", "select"} and action not in {"menu", "date"}:
            raise RuntimeError("输入控件只能通过明确的查询步骤操作")
        industry_entry = (
            target is not None and action == "open" and urlsplit(self.page.url).path == "/scene"
            and target.scope == "main" and label == "订阅行业包"
            and not self.page.locator(OVERLAYS).count()
        )
        select_menu = action == "menu" and element.evaluate("e => e.matches('.ant-select,[role=combobox]')")
        if FORBIDDEN.search(danger_label) and not (safe_sync_entry or industry_entry or select_menu):
            # 导入仅允许已核实的说明入口，禁止文件选择、下一步和提交。
            path = urlsplit(self.page.url).path.rstrip("/")
            no_overlay = not self.page.locator(OVERLAYS).count()
            import_entry = target is not None and action == "open" and no_overlay and (
                (path == "/variables" and target.scope == "main" and target.kind == "button" and label == "导入")
                or (path in {"/product-knowledge", "/stock-knowledge"}
                    and target.scope == "main" and target.kind == "button" and label == "导入知识库")
                or (path == "/product-config" and allowed_import_item and label in {"导入属性", "导入商品状态"})
            )
            if not import_entry:
                raise RuntimeError("动作安全策略拒绝: " + danger_label[:50])
        self.guard()

    def readonly_click(self, target, action="click"):
        element = self.resolve(target)
        self.validate_action(element, target, action)
        element.click()
        self.guard()

    def inspect(self, target=None):
        scope = self.resolve(target, many=True) if target else self.root("main")
        scope.first.wait_for(state="visible")
        # 只读观察允许多元素，点击仍必须唯一或显式声明代表样本。
        return scope.evaluate_all("""items => ({
            matches: items.length,
            buttons: items.reduce((n,e)=>n+e.querySelectorAll('button').length,0),
            tables: items.reduce((n,e)=>n+e.querySelectorAll('table').length,0),
            fields: items.reduce((n,e)=>n+e.querySelectorAll('input,textarea,select').length,0),
            tabs: items.reduce((n,e)=>n+e.querySelectorAll('[role=tab]').length,0)
        })""")

    def close_overlays(self):
        self.guard()
        self.page.keyboard.press("Escape")
        self.guard()
        # Escape可能已触发抽屉关闭，等待退场动画完成再找关闭按钮，避免追逐正在隐藏的控件。
        try:
            self.page.wait_for_function("""() => ![...document.querySelectorAll('.ant-modal,.ant-drawer-content')]
                .some(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')""", timeout=800)
            return
        except PlaywrightTimeoutError:
            pass
        for _ in range(8):
            self.guard()
            overlays = self.page.locator(OVERLAYS)
            if not overlays.count():
                return
            top = overlays.last
            close = top.get_by_role("button", name=exact("取消")).locator("visible=true")
            if close.count() != 1:
                close = top.locator(".ant-modal-close:visible, .ant-drawer-close:visible")
            if close.count() != 1:
                raise RuntimeError("弹层没有唯一安全关闭入口")
            count_before = overlays.count()
            self.validate_action(close, action="close")
            close.click()
            self.guard()
            self.page.wait_for_function("""n => [...document.querySelectorAll('.ant-modal,.ant-drawer-content')]
                .filter(e=>e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden').length < n""", arg=count_before)
        raise RuntimeError("弹层层级超过清理上限")
