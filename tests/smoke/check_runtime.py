"""离线自检：所有请求由内存路由响应，不连接智言，不含业务断言。"""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from pages.zhiyan.smoke_page import SmokePage
from .runner import SmokeRun, write_summary
from .safety import BLOCK_CHANNELS, READINESS, ReadOnlyPolicy
from .specs import Scenario, Step, button, click, css, gap, inspect, menu, opened, popup, search, tab, text


BASE = "https://smoke.invalid"
HTML = r"""<!doctype html><meta charset="utf-8"><aside>侧栏</aside><main>
<h1>离线测试页</h1><input placeholder="请输入商品ID、商品标题搜索">
<button id="add" onclick="show('父弹层')">新增商品</button>
<button onclick="fetch('/api/save',{method:'POST'})">编辑危险请求</button>
<button onclick="window.open('/detail')">查看会话</button>
<button onclick="location.href='/login'">失效跳转</button>
<button onclick="location.href='/login/'">尾斜杠失效跳转</button>
<button role="tab" aria-selected="false" onclick="this.setAttribute('aria-selected','true')">商品统计</button>
<button id="menu" aria-controls="batch-menu" onclick="document.querySelector('#batch-menu').style.display='block'">批量操作</button>
<div id="batch-menu" class="ant-dropdown" style="display:none"><span role="menuitem" onclick="window.candidateClicks=(window.candidateClicks||0)+1;this.parentNode.style.display='none';show('导入说明')">导入属性</span></div>
<button id="unlinked" onclick="void(0)">无关联菜单</button>
<button aria-controls="empty-menu" onclick="document.querySelector('#empty-menu').style.display='block'">空候选菜单</button>
<div id="empty-menu" class="ant-dropdown" style="display:none"><span role="menuitem" style="display:none">隐藏项</span></div>
<button aria-controls="existing-menu" onclick="void(0)">关联既有菜单</button>
<button onclick="document.querySelector('#new-menu').style.display='block'">新挂载菜单</button>
<div id="new-menu" class="ant-dropdown" style="display:none"><span role="menuitem">新候选</span></div>
<div class="ant-checkbox-wrapper"><input type="checkbox"><span id="unsafe">编辑</span></div>
<button>保存</button><button id="unsafe-parent">保存<span id="unsafe-parent-label">编辑</span></button>
<button><span role="img" aria-label="plus"></span>图标新增入口</button>
<div class="ant-empty">暂无数据</div>
<table><tbody><tr data-row-key="known"><td>680483637921</td><td>文本</td></tr></tbody></table>
<script>
function show(title){
const d=document.createElement('div');d.className='ant-modal';
d.innerHTML='<h2>'+title+'</h2><input placeholder="请输入商品ID"><button onclick="show(\'子弹层\')">视频</button><button onclick="this.parentNode.remove()">取消</button>';
d.style.cssText='position:relative;background:white;padding:10px';document.body.appendChild(d);
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.ant-dropdown').forEach(p=>{if(p.id!=='unrelated-menu')p.style.display='none'})});
</script>"""


def check(value, message):
    if not value:
        raise RuntimeError("离线自检失败: " + message)


def check_runner_boundaries():
    from .test_readonly_smoke import test_readonly_function

    checks = 0
    case = Scenario("offline-boundaries", "离线", "/list", "运行边界", (
        inspect("第一步"), inspect("第二步"),
    ))

    def make_runner(blocked=None):
        runner = object.__new__(SmokeRun)
        runner.policy = SimpleNamespace(blocked=list(blocked or []))
        runner.redact, runner.events, runner.fatal = (), [], False
        calls = []
        runner.ui = SimpleNamespace(
            samples=[], goto=lambda path: calls.append("goto"),
            close_overlays=lambda: calls.append("cleanup"),
        )
        runner.execute = lambda step: calls.append(step.name) or {}
        return runner, calls

    runner, calls = make_runner([{"method": "POST", "path": "/api/save", "reason": "已有阻断"}])
    result = runner.run(case)
    check(not calls and result["navigation"] == "blocked" and
          all(step["status"] == "not_run" for step in result["steps"]), "已有阻断不触发导航或清理")
    checks += 1
    runner, calls = make_runner()

    def blocked_navigation(path):
        calls.append("goto")
        runner.policy.blocked.append({"method": "POST", "path": "/api/save", "reason": "导航阻断"})

    runner.ui.goto = blocked_navigation
    result = runner.run(case)
    check(calls == ["goto"] and result["navigation"] == "blocked" and
          all(step["status"] == "not_run" for step in result["steps"]), "导航阻断后停止全部步骤")
    checks += 1
    runner, calls = make_runner()

    class BetweenSteps:
        def __iter__(self):
            yield case.steps[0]
            runner.policy.blocked.append({"method": "POST", "path": "/api/save", "reason": "步骤间阻断"})
            yield case.steps[1]

    result = runner.run(SimpleNamespace(id=case.id, module=case.module, name=case.name,
                                       path=case.path, limitation="", steps=BetweenSteps()))
    check(calls == ["goto", "第一步"] and result["steps"][0]["status"] == "completed" and
          result["steps"][1]["status"] == "not_run", "步骤间已有阻断不执行下一步")
    checks += 1
    runner, calls = make_runner()

    def independent_timeout(step):
        runner.policy.blocked.append({"method": "POST", "path": "/api/save", "reason": "另一个请求被拦截"})
        raise PlaywrightTimeoutError("独立定位失败")

    runner.execute = independent_timeout
    result = runner.run(case)
    check(result["steps"][0]["status"] == "failed" and result["infrastructure_failed"] and
          result["status"] == "failed", "阻断不可改写独立TimeoutError")
    checks += 1
    for kind in ("pageerror", "requestfailed", "http_error"):
        runner, calls = make_runner()
        runner.events = [{"kind": kind}]
        result = runner.run(case)
        check(result["status"] == "completed_with_events" and result["infrastructure_failed"], kind + "标记基础设施异常")
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr("allure.dynamic.feature", lambda value: None)
            patch.setattr("allure.dynamic.story", lambda value: None)
            patch.setattr("allure.attach", lambda *args, **kwargs: None)
            try:
                test_readonly_function(SimpleNamespace(run=lambda scenario: result), case)
            except pytest.fail.Exception as error:
                check("基础设施" in str(error) and kind in str(error), kind + "明确pytest失败原因")
            else:
                raise RuntimeError("离线自检失败: " + kind + "不得pytest绿灯")
        checks += 1
    runner, calls = make_runner()
    runner.events = [{"kind": "requestfailed", "method": "GET", "path": "/media.mp4",
                      "resource_type": "media", "message": "net::ERR_ABORTED"}]
    result = runner.run(case)
    check(result["status"] == "completed" and len(result["media_cancellations"]) == 1
          and not result["events"], "媒体主动取消独立保留，不冒充运行错误")
    checks += 1
    return checks


def check_action_safety(context, page):
    checks = 0
    ui = SmokePage(page, BASE, 1600)

    for markup in (
        '<button onclick="this.parentNode.remove()">取消</button>',
        '<button class="ant-modal-close" onclick="this.parentNode.remove()">关闭</button>',
        '<button class="ant-drawer-close" aria-label="关闭" onclick="this.parentNode.remove()"></button>',
        '<form><button type="button" onclick="this.closest(\'.ant-modal\').remove()">取消</button></form>',
        '<span class="ant-modal-close" onclick="this.parentNode.remove()">关闭</span>',
    ):
        page.goto(BASE + "/list")
        page.evaluate("""markup => {
            const overlay = document.createElement('div'); overlay.className = 'ant-modal';
            overlay.innerHTML = markup; document.body.appendChild(overlay);
        }""", markup)
        ui.close_overlays()
        check(page.locator('.ant-modal:visible').count() == 0, "唯一取消或标准关闭入口正常关闭")
        checks += 1

    for markup in (
        '<button class="ant-modal-close">保存</button>',
        '<button class="ant-modal-close" aria-label="确认"></button>',
        '<button class="ant-modal-close"><input type="file">关闭</button>',
        '<label class="ant-checkbox-wrapper"><input type="checkbox"><button>取消</button></label>',
        '<div role="menuitem"><button>取消</button></div>',
        '<button>取消</button><button>取消</button>',
        '<form><button>取消</button></form>',
        '<form><button type="reset">取消</button></form>',
        '<form id="close-form"></form><button form="close-form">取消</button>',
        '<button class="ant-modal-close" aria-label="保存">取消</button>',
        '<button class="ant-modal-close" title="删除">取消</button>',
    ):
        page.goto(BASE + "/list")
        page.evaluate("""markup => {
            const overlay = document.createElement('div'); overlay.className = 'ant-modal';
            overlay.innerHTML = markup;
            overlay.addEventListener('click', () => window.closeClicks = (window.closeClicks || 0) + 1);
            document.body.appendChild(overlay);
        }""", markup)
        with pytest.raises(RuntimeError):
            ui.close_overlays()
        check(page.evaluate("window.closeClicks || 0") == 0, "危险或不唯一的关闭入口必须在点击前拒绝")
        checks += 1

    page.goto(BASE + "/list")
    page.evaluate("""() => {
        const form = document.createElement('form');
        form.innerHTML = '<button id="query-submit" type="submit">查询</button><div id="plain-close">关闭</div>';
        form.addEventListener('submit', event => { event.preventDefault(); window.querySubmits = (window.querySubmits || 0) + 1; });
        document.querySelector('main').appendChild(form);
    }""")
    ui.readonly_click(css('#query-submit'))
    check(page.evaluate('window.querySubmits') == 1, "普通查询submit维持原有行为")
    with pytest.raises(RuntimeError, match="关闭入口必须"):
        ui.validate_action(page.locator('#plain-close'), action="close")
    checks += 2

    for path, label, target in (
        ("/variables", "导入", button("导入")),
        ("/product-knowledge", "导入知识库", button("导入知识库")),
        ("/stock-knowledge", "导入知识库", button("导入知识库")),
        ("/sync", "跨店同步", css('[data-icon="file-text"]')),
        ("/scene", "订阅行业包", button("订阅行业包")),
    ):
        page.goto(BASE + path)
        page.evaluate("""label => {
            const entry = document.createElement('button'); entry.id = 'business-entry';
            entry.dataset.icon = 'file-text'; entry.textContent = label;
            document.querySelector('main').appendChild(entry);
        }""", label)
        element = page.locator('#business-entry')
        ui.validate_action(element, target, "open")
        for action, candidate in (("close", target), ("close", None), ("open", None)):
            with pytest.raises(RuntimeError, match="动作安全策略拒绝"):
                ui.validate_action(element, candidate, action)
        checks += 1
    ui.validate_action(page.locator('#add'))
    checks += 1
    page.goto(BASE + "/product-config")
    page.evaluate("""() => document.querySelector('#batch-menu').style.display = 'block'""")
    import_target = css('.ant-dropdown:visible [role="menuitem"]:has-text("导入属性")', "page")
    import_item = page.locator('#batch-menu [role="menuitem"]')
    ui.validate_action(import_item, import_target, "open")
    with pytest.raises(RuntimeError, match="禁止操作"):
        ui.validate_action(import_item, import_target, "close")
    with pytest.raises(RuntimeError, match="禁止操作"):
        ui.validate_action(import_item, action="open")
    checks += 1

    for mode in ("escape", "click"):
        page.goto(BASE + "/list")
        page.evaluate("""mode => {
            const lower = document.createElement('div'); lower.className = 'ant-modal';
            lower.innerHTML = '<button onclick="window.lowerClicks=(window.lowerClicks||0)+1;this.parentNode.remove()">取消</button>';
            const top = document.createElement('div'); top.className = 'ant-modal';
            top.innerHTML = '<button>取消</button>'; document.body.append(lower, top);
            const block = () => { window.safetyBlocked = true; top.remove(); };
            if (mode === 'escape') document.addEventListener('keydown', e => {
                if (e.key === 'Escape') block();
            }, {once:true});
            else top.querySelector('button').addEventListener('click', block);
        }""", mode)

        def guard():
            if page.evaluate("!!window.safetyBlocked"):
                raise RuntimeError("离线guard阻断")

        guarded = SmokePage(page, BASE, 1600, guard=guard)
        with pytest.raises(RuntimeError, match="离线guard阻断"):
            guarded.close_overlays()
        check(page.locator('.ant-modal:visible').count() == 1 and
              page.evaluate("window.lowerClicks || 0") == 0,
              mode + "触发阻断后不能继续点击下层弹层")
        checks += 1

    for markup in (
        '<button id="danger-hover">保存</button>',
        '<button>保存<span id="danger-hover">编辑</span></button>',
        '<label class="ant-checkbox-wrapper"><input type="checkbox"><span id="danger-hover">编辑</span></label>',
        '<span id="danger-hover" role="menuitem">查看</span>',
    ):
        page.goto(BASE + "/list")
        page.evaluate("""markup => {
            const container = document.createElement('div'); container.innerHTML = markup;
            document.querySelector('main').appendChild(container);
            document.querySelector('#danger-hover').addEventListener('mouseenter', () => {
                window.dangerHovers = (window.dangerHovers || 0) + 1;
            });
        }""", markup)
        runner = SmokeRun(context, page, BASE, ReadOnlyPolicy(BASE), 1600)
        with pytest.raises(RuntimeError):
            runner.execute(menu("危险菜单不可先hover", css('#danger-hover')))
        check(page.evaluate("window.dangerHovers || 0") == 0, "危险控件在hover事件发生前拒绝")
        checks += 1
    return checks


def check_dynamic_targets(context, page):
    checks = 0
    ui = SmokePage(page, BASE, 1600)
    page.goto(BASE + "/list")
    page.evaluate("""() => {
        const form = document.createElement('div'); form.className = 'ant-form-item-label';
        form.innerHTML = '<label id="ordinary-label"><div><button id="ordinary-button" onclick="window.addClicks=(window.addClicks||0)+1"><span id="ordinary-button-text">添加</span></button><span id="ordinary-text">普通标签</span></div></label>';
        document.querySelector('main').appendChild(form);
    }""")
    ui.readonly_click(css('#ordinary-button'))
    ui.readonly_click(css('#ordinary-button-text'))
    check(page.evaluate('window.addClicks') == 2, "普通无关联表单label内部button及其文字可点击")
    for selector in ('#ordinary-label', '#ordinary-text'):
        with pytest.raises(RuntimeError, match="禁止操作"):
            ui.validate_action(page.locator(selector))
    checks += 1
    for markup in (
        '<input id="linked-control"><label for="linked-control"><button id="linked-button">添加</button></label>',
        '<label><input type="checkbox"><button id="linked-button">添加</button></label>',
        '<label><input type="radio"><button id="linked-button">添加</button></label>',
        '<label><input type="file"><button id="linked-button">添加</button></label>',
        '<label><span role="switch"></span><button id="linked-button">添加</button></label>',
        '<label><button id="linked-button">保存</button></label>',
    ):
        page.goto(BASE + "/list")
        page.evaluate("""markup => {
            const form = document.createElement('div'); form.innerHTML = markup;
            document.querySelector('main').appendChild(form);
        }""", markup)
        with pytest.raises(RuntimeError):
            ui.validate_action(page.locator('#linked-button'))
        checks += 1

    for key in ('中文商品行', '引号"和反斜杠\\行'):
        page.goto(BASE + "/list")
        page.evaluate("""key => {
            const body = document.querySelector('tbody'); body.innerHTML = '';
            for (const value of [key, '另一行']) {
                const row = document.createElement('tr'); row.dataset.rowKey = value;
                row.innerHTML = '<td><button class="sample-entry">查看</button></td>';
                row.querySelector('button').addEventListener('click', () => { window.clickedKey = row.dataset.rowKey; });
                body.appendChild(row);
            }
        }""", key)
        ui.readonly_click(css('.sample-entry', sample=True))
        check(page.evaluate('window.clickedKey') == key, "CSS.escape支持中文、引号与反斜杠行键")
        checks += 1

    page.goto(BASE + "/list")
    page.evaluate("""() => {
        const body = document.querySelector('tbody'); body.innerHTML = '';
        for (const value of ['重复键', '重复键']) {
            const row = document.createElement('tr'); row.dataset.rowKey = value;
            row.innerHTML = '<td><button class="sample-entry">查看</button></td>'; body.appendChild(row);
        }
    }""")
    with pytest.raises(RuntimeError, match="代表业务行内入口不唯一"):
        ui.resolve(css('.sample-entry', sample=True))
    checks += 1

    page.goto(BASE + "/list")
    page.evaluate("""() => {
        const body = document.querySelector('tbody'); body.innerHTML = '';
        for (const value of ['重渲染键', '另一行']) {
            const row = document.createElement('tr'); row.dataset.rowKey = value;
            row.innerHTML = '<td><button class="sample-entry">查看</button></td>'; body.appendChild(row);
        }
        const original = Element.prototype.closest;
        Element.prototype.closest = function(selector) {
            const result = original.call(this, selector);
            if (selector === '[data-row-key]' && this.matches('.sample-entry') && !window.rerendered) {
                window.rerendered = true;
                requestAnimationFrame(() => { body.innerHTML = body.innerHTML; });
            }
            return result;
        };
    }""")
    resolved = ui.resolve(css('.sample-entry', sample=True))
    check(page.evaluate('!!window.rerendered') and
          resolved.evaluate("e => e.closest('[data-row-key]').dataset.rowKey") == '重渲染键',
          "代表样本锁定前等待重渲染后节点稳定")
    checks += 1

    for candidates, markup in (
        ('tbody tr', '<table><tbody><tr><td>变量一</td></tr><tr><td>变量二</td></tr></tbody></table>'),
        ('li', '<ul><li>知识一</li><li>知识二</li></ul>'),
    ):
        page.goto(BASE + "/list")
        page.evaluate("""markup => {
            const container = document.createElement('div');
            container.innerHTML = '<button id="rich-menu-trigger" aria-controls="rich-menu">变量菜单</button><div id="rich-menu" class="ant-popover" style="display:none"></div>';
            document.querySelector('main').appendChild(container);
            const panel = document.querySelector('#rich-menu'); panel.innerHTML = markup;
            document.querySelector('#rich-menu-trigger').addEventListener('mouseenter', () => {
                setTimeout(() => { panel.style.display = 'block'; }, 150);
            });
            panel.addEventListener('click', () => { window.richClicks=(window.richClicks||0)+1; });
            document.addEventListener('keydown', e => { if (e.key === 'Escape') panel.style.display = 'none'; });
        }""", markup)
        runner = SmokeRun(context, page, BASE, ReadOnlyPolicy(BASE), 1600)
        with pytest.raises(PlaywrightTimeoutError):
            runner.execute(menu("未声明富文本候选不得泛化", css('#rich-menu-trigger')))
        check(page.evaluate('window.richClicks || 0') == 0, "未声明富文本候选时不点击")
        page.keyboard.press('Escape')
        page.mouse.move(0, 0)
        observation = runner.execute(menu("显式富文本候选", css('#rich-menu-trigger'), candidates=candidates))
        check(observation['visible_options'] == 2 and observation['candidate_selector'] == candidates and
              not page.locator('#rich-menu').is_visible() and page.evaluate('window.richClicks || 0') == 0,
              "等待hover延迟后观察显式table/list候选并安全关闭")
        checks += 1
    return checks


def main():
    checks = check_runner_boundaries()
    policy = ReadOnlyPolicy(BASE)
    matrix = (
        ("GET", "/api/products", "fetch", True),
        ("POST", "/api/save", "fetch", False),
        ("GET", "/api/save", "image", False),
        ("GET", "/api/saveProduct", "fetch", False),
        ("GET", "/api/products?action=delete", "fetch", False),
        ("POST", "/api/ai-quality-inspection/check", "fetch", False),
        ("POST", "/api/knowledge/product/1", "fetch", False),
        ("POST", "/api/work-order", "fetch", True),
        ("POST", "/api/ai-quality-inspection/list", "fetch", True),
        ("GET", "/api/yanzhi/recharge/records", "fetch", True),
        ("GET", "/assets/sync.js", "script", True),
    )
    for method, path, resource, expected in matrix:
        actual, _ = policy.permits(method, BASE + path, resource)
        check(actual is expected, method + " " + path)
        checks += 1
    policy.begin_login("offline-user", "offline-pass")
    check(not policy.permits("POST", BASE + "/api/auth/update", payload={"account":"offline-user","password":"offline-pass"},frame_url=BASE+"/login")[0], "认证例外不可放行其他接口")
    payload = {"account": "offline-user", "password": "offline-pass"}
    check(policy.permits("POST", BASE + "/api/auth/login", payload=payload,frame_url=BASE+"/login")[0], "单次认证")
    check(not policy.permits("POST", BASE + "/api/auth/login", payload=payload,frame_url=BASE+"/login")[0], "认证不可重复")
    policy.end_login()
    checks += 3
    check(not policy.permits("POST", BASE + "/api/work-order", payload={"action":"delete"})[0], "查询POST拒绝动作请求体")
    check(not policy.permits("GET", "https://other.invalid/api/list")[0], "拒绝跨域API")
    checks += 2
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(service_workers="block", accept_downloads=False)
        context.set_default_timeout(1600)
        context.add_init_script(BLOCK_CHANNELS + READINESS)
        # 路由始终本地fulfill，不会发出任何真实网络请求。
        active = ReadOnlyPolicy(BASE)

        def route(request_route):
            req = request_route.request
            permitted, reason = active.permits(req.method, req.url, req.resource_type)
            if not permitted:
                active.blocked.append({"method":req.method,"path":req.url,"reason":reason})
                request_route.abort()
            elif req.resource_type == "document":
                body = HTML
                if req.url.endswith("/blocked-nav"):
                    body += "<script>fetch('/api/save',{method:'POST'}).catch(()=>{})</script>"
                elif req.url.endswith("/event-pageerror"):
                    body += "<script>throw new Error('offline-pageerror')</script>"
                elif req.url.endswith("/event-requestfailed"):
                    body += "<script>fetch('/api/offline-failure').catch(()=>{})</script>"
                elif req.url.endswith("/event-http"):
                    body += "<script>fetch('/api/offline-http')</script>"
                request_route.fulfill(body=body, content_type="text/html")
            elif req.url.endswith("/api/offline-failure"):
                request_route.abort()
            elif req.url.endswith("/api/offline-http"):
                request_route.fulfill(status=503, body="{}", content_type="application/json")
            else:
                request_route.fulfill(body="{}", content_type="application/json")

        context.route("**/*", route)
        page = context.new_page()
        page.goto(BASE + "/list")
        check(page.evaluate("""() => ['Worker','SharedWorker','WebSocket','EventSource'].every(name => {
            try { new window[name]('https://smoke.invalid/forbidden'); return false; }
            catch (e) { return e.message.includes('Readonly smoke'); }
        })"""), "实时通道与Worker构造均在创建前拒绝")
        checks += 1
        checks += check_action_safety(context, page)
        checks += check_dynamic_targets(context, page)

        def run(case):
            nonlocal active
            active = ReadOnlyPolicy(BASE)
            value = SmokeRun(context, page, BASE, active, 1600).run(case)
            return value

        simple = Scenario("offline-basic", "离线", "/list", "查询、页签、多元素观察", (
            search("搜索", "请输入商品ID、商品标题搜索", "680483637921"),
            click("切页签", tab("商品统计")),
            inspect("同行多列观察", css("td", row="680483637921", data=True)),
        ))
        result = run(simple)
        check(result["status"] == "completed", "基础链路: " + json.dumps(result,ensure_ascii=False))
        checks += 1
        icon_button = Scenario("offline-icon-button", "离线", "/list", "图标不干扰按钮文案", (
            click("精确按钮自身文案", button("图标新增入口")),
        ))
        check(run(icon_button)["status"] == "completed", "图标无障碍名称不影响精确按钮文案")
        unsafe_parent = Scenario("offline-unsafe-parent", "离线", "/list", "拒绝危险祖先按钮", (
            click("拒绝编辑span冒充保存按钮", css("#unsafe-parent-label")),
        ))
        check(run(unsafe_parent)["status"] == "failed", "危险祖先按钮不能由安全子文案绕过")
        checks += 2
        for suffix, kind in (("pageerror", "pageerror"), ("requestfailed", "requestfailed"), ("http", "http_error")):
            event_case = Scenario("offline-event-" + suffix, "离线", "/event-" + suffix, "事件不得通过", (inspect("结构观察"),))
            result = run(event_case)
            check(result["status"] == "completed_with_events" and result["infrastructure_failed"] and
                  any(event["kind"] == kind for event in result["events"]), kind + "真实浏览器事件标记异常")
            checks += 1
        unsafe_save = Scenario("offline-save", "离线", "/list", "拒绝保存", (click("保存不可执行", button("保存")),))
        check(run(unsafe_save)["status"] == "failed", "默认拒绝保存按钮")
        missing_sample = Scenario("offline-missing-row", "离线", "/list", "缺样本受限", (inspect("缺指定样本", css("td",row="not-there",data=True)),))
        check(run(missing_sample)["status"] == "partial", "指定样本缺失按受限")
        checks += 2
        nested = Scenario("offline-nested", "离线", "/list", "嵌套弹层清理", (
            opened("父弹层", button("新增商品")), opened("子弹层", button("视频", "overlay")),
            inspect("子弹层结构", css("input", "overlay")),
        ))
        result = run(nested)
        check(result["status"] == "completed", "嵌套弹层: " + json.dumps(result,ensure_ascii=False))
        checks += 1
        active = ReadOnlyPolicy(BASE)
        runner = SmokeRun(context, page, BASE, active, 1600)
        runner.ui.goto("/list")
        page.evaluate("""() => {
            const drawer = document.createElement('div'); drawer.className = 'ant-drawer-content';
            drawer.innerHTML = '<button class="ant-drawer-close">关闭</button>'; document.body.appendChild(drawer);
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape') setTimeout(() => drawer.remove(), 180);
            }, {once:true});
        }""")
        runner.ui.close_overlays()
        check(page.locator('.ant-drawer-content:visible').count() == 0,
              "Escape触发退场动画后不追逐隐藏的关闭按钮")
        checks += 1
        imports = Scenario("offline-import", "离线", "/product-config", "只读导入说明", (
            Step("保留批量菜单", "menu", button("批量操作"), destination="keep"),
            opened("导入说明", css('.ant-dropdown:visible [role="menuitem"]:has-text("导入属性")', "page")),
            inspect("导入说明表单", css("input", "overlay")),
        ))
        result = run(imports)
        check(result["status"] == "completed", "导入说明: " + json.dumps(result,ensure_ascii=False))
        checks += 1
        menu_case = Scenario("offline-menu", "离线", "/list", "菜单关闭", (menu("展开关闭", button("批量操作")),))
        check(run(menu_case)["status"] == "completed", "菜单展开关闭")
        checks += 1
        unrelated = """() => {
            const p = document.createElement('div'); p.id = 'unrelated-menu'; p.className = 'ant-dropdown';
            p.innerHTML = '<span role="menuitem">无关候选</span>'; document.body.appendChild(p);
        }"""
        for label, expected in (("无关联菜单", "failed"), ("空候选菜单", "failed"),
                                ("新挂载菜单", "completed"), ("批量操作", "completed")):
            active = ReadOnlyPolicy(BASE)
            runner = SmokeRun(context, page, BASE, active, 1600)
            runner.ui.goto("/list")
            page.evaluate(unrelated)
            try:
                observation = runner.execute(menu("菜单归属", button(label)))
            except PlaywrightTimeoutError:
                actual = "failed"
            else:
                actual = "completed"
                check(observation["visible_options"] > 0, "菜单可见候选必须大于0")
            check(actual == expected, label + "必须绑定本次浮层")
            check(page.locator("#unrelated-menu").is_visible(), "不能误关无关既有浮层")
            check(page.evaluate("window.candidateClicks || 0") == 0, "只观察菜单候选不点击")
            checks += 1
        active = ReadOnlyPolicy(BASE)
        runner = SmokeRun(context, page, BASE, active, 1600)
        runner.ui.goto("/list")
        page.evaluate("""() => {
            const p=document.createElement('div');p.id='existing-menu';p.className='ant-dropdown';
            p.innerHTML='<span role="menuitem">关联候选</span>';document.body.appendChild(p);
        }""")
        check(runner.execute(menu("关联菜单", button("关联既有菜单")))["visible_options"] == 1 and
              not page.locator("#existing-menu").is_visible(), "aria-controls可绑定既有浮层并严格关闭")
        checks += 1
        runner.ui.goto("/list")
        page.evaluate(r"""() => {
            const mask=document.createElement('div');mask.style.cssText='position:fixed;inset:0;z-index:10';
            document.body.appendChild(mask);
            const modal=document.createElement('div');modal.className='ant-modal';
            modal.style.cssText='position:fixed;top:30px;left:30px;z-index:11;background:white';
            modal.innerHTML='<button aria-controls="masked-menu" onclick="document.querySelector(\'#masked-menu\').style.display=\'block\'">遮罩菜单</button>' +
                '<div id="masked-menu" class="ant-dropdown" style="display:none"><span role="menuitem">不可点击候选</span></div>';
            document.body.appendChild(modal);
        }""")
        check(runner.execute(menu("遮罩内菜单", button("遮罩菜单", "overlay")))["visible_options"] == 1 and
              not page.locator("#masked-menu").is_visible(), "遮罩不应阻塞菜单关闭且必须隐藏所属浮层")
        checks += 1
        active = ReadOnlyPolicy(BASE)
        runner = SmokeRun(context, page, BASE, active, 1600)
        runner.ui.goto("/shop-knowledge")
        page.evaluate("""() => {
            const form=document.createElement('div');
            form.innerHTML='<label class="ant-radio-wrapper"><input type="radio" name="view">商品视图</label>' +
                '<label class="ant-radio-wrapper"><input type="radio" name="view">知识视图</label>' +
                '<label class="ant-radio-wrapper"><input type="radio">自动保存配置</label>';
            document.querySelector('main').appendChild(form);
        }""")
        runner.ui.readonly_click(text("商品视图"))
        runner.ui.readonly_click(text("知识视图"))
        try:
            runner.ui.readonly_click(text("自动保存配置"))
        except RuntimeError:
            pass
        else:
            raise RuntimeError("离线自检失败: 普通radio不可借只读视图例外放行")
        checks += 1
        limited = Scenario("offline-gap", "离线", "/list", "受限不算完成", (gap("无样本", "预先明确未覆盖"), inspect("依赖步骤")))
        result = run(limited)
        check(result["status"] == "partial" and result["steps"][1]["status"] == "not_run", "受限后跳过依赖")
        checks += 1
        blocked = Scenario("offline-block", "离线", "/list", "请求拦截", (
            click("模拟意外写请求", button("编辑危险请求")), click("禁止后续页签", tab("商品统计")),
        ))
        result = run(blocked)
        check(result["status"] == "blocked" and result["steps"][1]["status"] == "not_run" and
              page.get_by_role("tab").get_attribute("aria-selected") == "false", "写请求阻断后不再点击页签")
        checks += 1
        nav_blocked = Scenario("offline-navigation-block", "离线", "/blocked-nav", "导航请求阻断", (
            click("禁止导航后的页签", tab("商品统计")),
        ))
        result = run(nav_blocked)
        check(result["navigation"] == "blocked" and result["steps"][0]["status"] == "not_run" and
              result["cleanup"] == "not_run" and page.get_by_role("tab").get_attribute("aria-selected") == "false",
              "真实导航期间阻断后不触发UI操作")
        checks += 1
        unsafe = Scenario("offline-unsafe", "离线", "/list", "关联checkbox拒绝", (click("拒绝label子元素", css("#unsafe")),))
        check(run(unsafe)["status"] == "failed", "禁止点checkbox的子span")
        checks += 1
        empty = Scenario("offline-not-empty", "离线", "/list", "同页空态不能掩盖缺按钮", (opened("缺失编辑", button("不存在的编辑", data=True)),))
        check(run(empty)["status"] == "failed", "其他区域空态不能把定位错误变成数据受限")
        checks += 1
        pop = Scenario("offline-popup", "离线", "/list", "新标签页", (popup("新页", button("查看会话"), "/detail"),inspect("新页内容")))
        result = run(pop)
        check(result["status"] == "completed", "新标签页处理")
        for extra in context.pages:
            if extra != page:
                extra.close()
        checks += 1
        redirect = Scenario("offline-auth", "离线", "/list", "认证失效停止", (opened("认证失效", button("失效跳转"), "/expected"),))
        runner = SmokeRun(context, page, BASE, active, 1600)
        result = runner.run(redirect)
        check(runner.fatal and result["status"] == "failed", "认证失效标记fatal")
        checks += 1
        active = ReadOnlyPolicy(BASE)
        runner = SmokeRun(context, page, BASE, active, 1600)
        redirect_slash = Scenario("offline-auth-slash", "离线", "/list", "尾斜杠认证失效", (
            opened("认证失效", button("尾斜杠失效跳转"), "/expected"), inspect("禁止继续"),
        ))
        result = runner.run(redirect_slash)
        check(runner.fatal and result["status"] == "failed" and
              result["steps"][1]["status"] == "not_run", "尾斜杠登录跳转停止链路")
        checks += 1
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,"case-offline-basic.json").write_text(json.dumps({"id":"offline-basic","status":"completed"}), encoding="utf-8")
            summary = json.loads(write_summary(tmp, [simple, limited]).read_text(encoding="utf-8"))
            check(summary["counts"].get("not_run") == 1, "汇总保留未执行项")
        checks += 1
        context.close()
        browser.close()
    print(json.dumps({"offline_checks": checks, "result": "ok", "network": "all requests fulfilled or blocked locally"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
