"""执行显式功能链；操作异常不吞掉，受限和未执行不冒充完成。"""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from time import monotonic
from urllib.parse import urlsplit

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.zhiyan.smoke_page import (
    AuthenticationLost, OVERLAYS, SmokePage, Unavailable,
)


class RequestBlocked(RuntimeError):
    """只读策略已阻断当前链，禁止继续操作页面。"""


class SmokeRun:
    def __init__(self, context, page, base_url, policy, timeout, redact=()):
        self.context = context
        self.policy = policy
        self.ui = SmokePage(page, base_url, timeout, guard=self._check_policy)
        self.redact = tuple(value for value in redact if value)
        self.events = []
        self.report = None
        self.fatal = False
        self._attach(page)
        context.on("page", self._attach)

    def clean(self, value):
        value = str(value)
        for secret in self.redact:
            value = value.replace(secret, "[redacted]")
        value = re.sub(r"https?://[^\s'\"]+", lambda m: urlsplit(m.group()).path, value)
        return value.split("Call log:", 1)[0].splitlines()[0][:400] if value else ""

    def _attach(self, page):
        page.on("pageerror", lambda error: self.events.append({
            "kind": "pageerror", "message": self.clean(error),
        }))
        page.on("response", lambda response: self._response(response))
        page.on("requestfailed", lambda req: self.events.append({
            "kind": "requestfailed", "path": urlsplit(req.url).path,
            "method": req.method, "resource_type": req.resource_type,
            "message": self.clean(req.failure),
        }))

    def _response(self, response):
        if response.status >= 400:
            if response.status == 401 and urlsplit(response.url).path.startswith("/api/"):
                self.fatal = True
            self.events.append({"kind": "http_error", "path": urlsplit(response.url).path,
                                "status": response.status})

    def _check_policy(self):
        if self.fatal:
            raise AuthenticationLost("接口返回认证失效，停止后续业务遍历")
        if self.policy.blocked:
            raise RequestBlocked("只读保护已拦截请求，停止当前功能链")

    def _menu(self, step):
        ui, page = self.ui, self.ui.page
        element = ui.resolve(step.target)
        self._check_policy()
        ui.validate_action(element, step.target, "menu")
        # 保存节点身份而不是数量，避免把既有无关浮层当作本次菜单。
        before = page.evaluate_handle("""() => [...document.querySelectorAll(
            '.ant-dropdown,.ant-select-dropdown,.ant-popover')].filter(e =>
            e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')""")
        trigger = element.element_handle()
        panel = None
        phase = "展开所属浮层"
        try:
            element.hover()
            self._check_policy()
            find_panel = """({before, trigger}) => {
                const visible = e => e && e.isConnected && e.getClientRects().length &&
                    getComputedStyle(e).visibility !== 'hidden';
                const panels = [...document.querySelectorAll('.ant-dropdown,.ant-select-dropdown,.ant-popover')].filter(visible);
                const ids = [trigger, ...trigger.querySelectorAll('[aria-controls]')]
                    .flatMap(e => (e.getAttribute('aria-controls') || '').split(/\\s+/)).filter(Boolean);
                const linked = panels.filter(p => ids.some(id => {
                    const controlled = document.getElementById(id);
                    return controlled && (p === controlled || p.contains(controlled) || controlled.contains(p));
                }));
                const candidates = linked.length ? linked : panels.filter(p => !before.includes(p));
                return candidates.length === 1 ? candidates[0] : false;
            }"""
            try:
                handle = page.wait_for_function(find_panel, arg={"before": before, "trigger": trigger}, timeout=800)
            except PlaywrightTimeoutError:
                self._check_policy()
                ui.readonly_click(step.target, "menu")
                self._check_policy()
                handle = page.wait_for_function(find_panel, arg={"before": before, "trigger": trigger})
            panel = handle.as_element()
            self._check_policy()
            phase = "等候可见候选"
            selector = step.candidates or '[role=menuitem],[role=option],.ant-select-item-option'
            visible_options = """({panel, selector}) => [...panel.querySelectorAll(selector)].filter(e =>
                e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden').length"""
            # 自绘富文本候选是表格/列表，必须由登记清单显式声明，不泛化任意div为候选。
            page.wait_for_function("args => (" + visible_options + ")(args) > 0", arg={"panel": panel, "selector": selector})
            result = {"visible_options": page.evaluate(visible_options, {"panel": panel, "selector": selector}),
                      "candidate_selector": selector}
            self._check_policy()
            if step.destination != "keep":
                phase = "关闭所属浮层"
                element.press("Escape")
                self._check_policy()
                hidden = """panel => !panel.isConnected || !panel.getClientRects().length ||
                    getComputedStyle(panel).visibility === 'hidden'"""
                try:
                    page.wait_for_function(hidden, arg=panel, timeout=800)
                except PlaywrightTimeoutError:
                    self._check_policy()
                    # 只切换已登记入口，绝不点击候选或被遮罩挡住的背景。
                    ui.validate_action(element, step.target, "menu")
                    element.hover()
                    self._check_policy()
                    ui.readonly_click(step.target, "menu")
                    self._check_policy()
                    page.wait_for_function(hidden, arg=panel)
            return result
        except PlaywrightTimeoutError as error:
            raise PlaywrightTimeoutError(f"菜单阶段[{phase}]: {self.clean(error)}") from error
        finally:
            before.dispose()
            if panel is not None:
                panel.dispose()
            trigger.dispose()

    def _destination(self, path):
        # 新页详情允许动态ID，但禁止跳到其他域或相似拼写路由。
        try:
            self.ui.page.wait_for_url(re.compile(
                re.escape(self.ui.base_url + path) + (r".*" if path.endswith("/") else r"(?:[/?#].*)?$")
            ))
        except PlaywrightTimeoutError:
            if urlsplit(self.ui.page.url).path.rstrip("/") == "/login":
                raise AuthenticationLost("跳转时认证失效") from None
            raise
        self._check_policy()
        self.ui.settle()
        self._check_policy()

    def execute(self, step):
        self._check_policy()
        ui = self.ui
        page = ui.page
        if step.action == "limited":
            raise Unavailable(step.value)
        if step.action == "inspect":
            return ui.inspect(step.target)
        if step.action == "search":
            if step.target.scope != "main" or step.target.kind != "placeholder":
                raise RuntimeError("只允许页面级、明确placeholder的查询字段")
            if not re.search(r"搜索|请输入内容|请输入.*名称|请输入.*编码", step.target.value):
                raise RuntimeError("字段没有已登记的查询语义")
            field = ui.resolve(step.target)
            self._check_policy()
            field.fill(step.value)
            self._check_policy()
            field.press("Enter")
            self._check_policy()
            ui.settle()
            self._check_policy()
            return {"query": "configured sample"}
        if step.action == "popup":
            with self.context.expect_page(timeout=ui.timeout) as popup:
                ui.readonly_click(step.target, "open")
            self._check_policy()
            ui.page = popup.value
            ui.page.set_default_timeout(ui.timeout)
            ui.page.wait_for_load_state("domcontentloaded")
            self._check_policy()
            self._destination(step.destination)
        elif step.action == "open":
            before = page.locator(OVERLAYS).count()
            ui.readonly_click(step.target, "open")
            self._check_policy()
            if step.destination == "overlay":
                page.wait_for_function("""n => [...document.querySelectorAll('.ant-modal,.ant-drawer-content')]
                    .filter(e=>e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden').length > n""", arg=before)
                ui.root("overlay").wait_for(state="visible")
            elif step.destination:
                self._destination(step.destination)
        elif step.action == "menu":
            return self._menu(step)
        elif step.action == "date":
            ui.readonly_click(step.target, "date")
            self._check_policy()
            panel = page.locator(".ant-picker-dropdown:visible")
            panel.wait_for(state="visible")
            self._check_policy()
            page.keyboard.press("Escape")
            panel.wait_for(state="hidden")
        elif step.action == "click":
            ui.readonly_click(step.target)
            self._check_policy()
            if step.target.kind == "tab":
                page.wait_for_function("e => e.getAttribute('aria-selected') === 'true'", arg=ui.resolve(step.target).element_handle())
        else:
            raise ValueError("未知动作: " + step.action)
        self._check_policy()
        ui.settle()
        self._check_policy()
        if self.fatal:
            raise AuthenticationLost("接口返回认证失效，停止后续业务遍历")
        if step.wait:
            ui.resolve(step.wait).wait_for(state="visible")
        return {"path": urlsplit(ui.page.url).path}

    def run(self, scenario):
        started = monotonic()
        self.report = {
            "id": scenario.id, "module": scenario.module, "name": scenario.name,
            "path": scenario.path, "status": "not_run", "steps": [],
            "limitation": scenario.limitation,
            "note": "无业务断言；completed仅表示登记操作完成，不代表业务正确。",
        }
        outcome = self.report
        blocker = None
        try:
            self._check_policy()
            self.ui.goto(scenario.path)
            self._check_policy()
            if self.fatal:
                raise AuthenticationLost("页面加载期间接口认证失效")
            outcome["navigation"] = "completed"
            for step in scenario.steps:
                if self.policy.blocked:
                    blocker = "前置请求被只读保护拦截"
                if blocker:
                    outcome["steps"].append({"name": step.name, "status": "not_run", "reason": blocker})
                    continue
                try:
                    data = self.execute(step)
                    self._check_policy()
                    record = {"name": step.name, "action": step.action, "status": "completed", "observation": data}
                except RequestBlocked as error:
                    record = {"name": step.name, "action": step.action, "status": "blocked", "reason": self.clean(error)}
                    blocker = "前置请求被只读保护拦截"
                except Unavailable as error:
                    record = {"name": step.name, "action": step.action, "status": "limited", "reason": self.clean(error)}
                    blocker = "前置步骤受限"
                except Exception as error:
                    record = {"name": step.name, "action": step.action, "status": "failed",
                              "reason": type(error).__name__ + ": " + self.clean(error),
                              "diagnostic": self.clean(str(error).split("Call log:", 1)[-1].strip())}
                    if isinstance(error, AuthenticationLost):
                        self.fatal = True
                    blocker = "前置步骤失败"
                outcome["steps"].append(record)
        except RequestBlocked as error:
            outcome["navigation"] = "blocked"
            outcome["error"] = self.clean(error)
            outcome["steps"] = [{"name": step.name, "status": "not_run", "reason": "页面进入期间只读保护拦截"}
                                for step in scenario.steps]
        except Exception as error:
            outcome["navigation"] = "failed"
            outcome["error"] = type(error).__name__ + ": " + self.clean(error)
            self.fatal = self.fatal or isinstance(error, AuthenticationLost)
            outcome["steps"] = [{"name": step.name, "status": "not_run", "reason": "页面进入失败"}
                                for step in scenario.steps]
        # 阻断后不再触发Escape或关闭按钮；独立context由fixture销毁。
        if self.policy.blocked:
            outcome["cleanup"] = "not_run"
        else:
            try:
                self.ui.close_overlays()
                self._check_policy()
                outcome["cleanup"] = "completed"
            except RequestBlocked as error:
                outcome["cleanup"] = "blocked"
                outcome["cleanup_error"] = self.clean(error)
            except Exception as error:
                outcome["cleanup"] = "failed"
                outcome["cleanup_error"] = self.clean(error)
                outcome["cleanup_diagnostic"] = self.clean(str(error).split("Call log:", 1)[-1].strip())
        blocked_keys = {(item["method"], urlsplit(item["path"]).path) for item in self.policy.blocked}
        def expected_block(event):
            return (event["kind"] == "requestfailed"
                    and (event.get("method"), event.get("path")) in blocked_keys
                    and re.search(r"BLOCKED|blocked|ERR_FAILED", event.get("message", "")))
        def cancelled_media(event):
            return (event["kind"] == "requestfailed" and event.get("resource_type") == "media"
                    and event.get("message") == "net::ERR_ABORTED")
        outcome["events"] = [event for event in self.events if not expected_block(event) and not cancelled_media(event)]
        outcome["policy_events"] = [event for event in self.events if expected_block(event)]
        outcome["media_cancellations"] = [event for event in self.events if cancelled_media(event)]
        outcome["blocked_requests"] = list(self.policy.blocked)
        outcome["samples"] = list(self.ui.samples)
        statuses = {item["status"] for item in outcome["steps"]}
        operation_failed = outcome["navigation"] == "failed" or "failed" in statuses or outcome["cleanup"] == "failed"
        outcome["infrastructure_failed"] = operation_failed or bool(outcome["events"])
        if self.fatal or operation_failed:
            outcome["status"] = "failed"
        elif self.policy.blocked:
            outcome["status"] = "blocked"
        elif "limited" in statuses or "not_run" in statuses:
            outcome["status"] = "partial"
        elif outcome["events"]:
            outcome["status"] = "completed_with_events"
        else:
            outcome["status"] = "completed"
        outcome["duration_seconds"] = round(monotonic() - started, 3)
        return outcome


def write_summary(directory, planned):
    directory = Path(directory)
    records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("case-*.json"))]
    by_id = {item["id"]: item for item in records}
    for scenario in planned:
        if scenario.id not in by_id:
            records.append({"id": scenario.id, "module": scenario.module, "name": scenario.name,
                            "path": scenario.path, "status": "not_run", "reason": "前置受阻、跳过或执行中断"})
    result = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "scope": "功能级只读冒烟，无业务断言，不提供业务通过率",
              "counts": dict(Counter(item["status"] for item in records)), "records": records}
    path = directory / "summary.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
