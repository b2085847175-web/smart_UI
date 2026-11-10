"""智言冒烟专用配置；必须显式启用，凭据只从环境变量取。"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid

import pytest

from .runner import SmokeRun, write_summary
from .safety import ReadOnlyPolicy


ROOT = Path(__file__).resolve().parents[2]


def pytest_generate_tests(metafunc):
    if "scenario" not in metafunc.fixturenames:
        return
    from .catalog import SCENARIOS
    modules = set(filter(None, metafunc.config.getoption("--smoke-module").split(",")))
    ids = set(filter(None, metafunc.config.getoption("--smoke-id").split(",")))
    selected = [case for case in SCENARIOS if (not modules or case.module in modules) and (not ids or case.id in ids)]
    if not selected:
        raise pytest.UsageError("冒烟筛选未匹配任何功能，请检查模块或功能ID")
    known_modules = {case.module for case in SCENARIOS}
    known_ids = {case.id for case in SCENARIOS}
    if modules - known_modules or ids - known_ids:
        raise pytest.UsageError("冒烟筛选包含未知模块或功能ID")
    metafunc.parametrize("scenario", selected, ids=[case.id for case in selected])


def pytest_collection_modifyitems(config, items):
    smoke_items = [item for item in items if "scenario" in getattr(item, "fixturenames", ())]
    if not smoke_items:
        return
    if config.getoption("--run-zhiyan-smoke"):
        if config.getoption("numprocesses", default=None) not in (None, 0, "0"):
            raise pytest.UsageError("只读冒烟暂不支持xdist并行，请去掉-n参数")
        if config.getoption("reruns", default=0):
            raise pytest.UsageError("只读冒烟不自动重试，请去掉--reruns参数")
    else:
        for item in smoke_items:
            item.add_marker(pytest.mark.skip(reason="未启用--run-zhiyan-smoke，不访问业务站点"))


@pytest.fixture(scope="session")
def smoke_results_dir(request):
    if not request.config.getoption("--run-zhiyan-smoke"):
        pytest.skip("需要--run-zhiyan-smoke")
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    directory = ROOT / "reports" / "zhiyan-smoke" / name
    directory.mkdir(parents=True)
    yield directory
    planned = [item.callspec.params["scenario"] for item in request.session.items
               if hasattr(item, "callspec") and "scenario" in item.callspec.params]
    path = write_summary(directory, planned)
    terminal = request.config.pluginmanager.getplugin("terminalreporter")
    if terminal:
        terminal.write_line("智言冒烟记录: " + str(path))


@pytest.fixture(scope="session")
def smoke_auth(browser, browser_context_args, config, smoke_results_dir):
    username = os.environ.get("UI_TEST_USERNAME", "")
    password = os.environ.get("UI_TEST_PASSWORD", "")
    if not username or not password:
        pytest.exit("缺少UI_TEST_USERNAME/UI_TEST_PASSWORD环境变量；未访问业务站点", returncode=4)
    base = config["base_url"].rstrip("/")
    if base != "https://dev.zhiyan.chat":
        pytest.exit("只允许dev.zhiyan.chat，请使用TEST_ENV=dev", returncode=4)
    timeout = int(config.get("timeout", {}).get("default", 30000))
    policy = ReadOnlyPolicy(base)
    options = {**browser_context_args, "service_workers": "block", "accept_downloads": False}
    context = browser.new_context(**options)
    context.set_default_timeout(timeout)
    context.set_default_navigation_timeout(int(config.get("timeout", {}).get("navigation", 30000)))
    policy.install(context)
    page = context.new_page()
    try:
        page.goto(base + "/login", wait_until="domcontentloaded")
        page.locator("#login_username").fill(username)
        page.locator("#login_password").fill(password)
        policy.begin_login(username, password)
        page.locator("button[type=submit]").click()
        if policy.blocked:
            raise RuntimeError("认证请求被只读策略阻断")
        page.wait_for_url(base + "/", wait_until="domcontentloaded")
        policy.end_login()
        search = page.get_by_placeholder("输入店铺名称搜索", exact=True)
        search.fill("儒意官方")
        shop = page.locator('div:has(> img[src*="tmall"])').filter(has_text="儒意官方旗舰店")
        shop.wait_for(state="visible")
        shop.click()
        page.wait_for_url(base + "/dashboard")
        if policy.blocked:
            raise RuntimeError("登录/选店前置触发未放行请求，请核实后再运行")
        state = context.storage_state()
        session_items = page.evaluate("Object.entries(sessionStorage)")
        (smoke_results_dir / "preflight.json").write_text(json.dumps({
            "stage": "authentication_and_shop_selection", "status": "completed",
            "platform": "tmall", "shop": "儒意官方旗舰店",
            "credentials_or_storage_state_persisted": False,
            "blocked_requests": [],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as error:
        safe = SmokeRun.clean(type("Redactor", (), {"redact": (username, password)})(), str(error))
        diagnostic = {"stage": "authentication_or_shop_selection", "error": safe,
                      "path": policy.safe_path(page.url), "blocked_requests": policy.blocked}
        (smoke_results_dir / "preflight.json").write_text(
            json.dumps(diagnostic, ensure_ascii=False, indent=2), encoding="utf-8")
        pytest.exit("登录或选店失败，停止整套冒烟: " + safe
                    + "；只读拦截路径: " + ",".join(item["path"] for item in policy.blocked), returncode=4)
    finally:
        policy.end_login()
        context.close()
    return {"base": base, "state": state, "session": session_items,
            "timeout": timeout, "options": options, "fatal": False,
            "redact": (username, password)}


@pytest.fixture
def smoke_run(browser, smoke_auth, request, smoke_results_dir, scenario):
    auth = smoke_auth
    if auth["fatal"]:
        pytest.skip("之前的流程发现认证失效，停止后续业务遍历")
    context = browser.new_context(**{**auth["options"], "storage_state": auth["state"]})
    context.set_default_timeout(auth["timeout"])
    context.set_default_navigation_timeout(auth["timeout"])
    policy = ReadOnlyPolicy(auth["base"])
    policy.install(context)
    context.add_init_script("""(() => {
        const data = """ + json.dumps({"base": auth["base"], "items": auth["session"]}, ensure_ascii=True) + """;
        if (location.origin === data.base) for (const [key,value] of data.items) {
            if (sessionStorage.getItem(key) === null) sessionStorage.setItem(key,value);
        }
    })();""")
    evidence = request.config.getoption("--smoke-evidence")
    if evidence:
        context.tracing.start(screenshots=True, snapshots=True, sources=False)
    page = context.new_page()
    run = SmokeRun(context, page, auth["base"], policy, auth["timeout"], auth["redact"])
    try:
        yield run
    finally:
        auth["fatal"] = auth["fatal"] or run.fatal
        try:
            if run.report:
                record_path = smoke_results_dir / ("case-" + scenario.id + ".json")
                try:
                    if evidence and (run.report["status"] == "failed" or run.report["infrastructure_failed"]):
                        run.ui.page.screenshot(path=str(smoke_results_dir / (scenario.id + ".png")), full_page=True)
                        context.tracing.stop(path=str(smoke_results_dir / (scenario.id + "-trace.zip")))
                    elif evidence:
                        context.tracing.stop()
                except Exception as error:
                    run.report["evidence_error"] = run.clean(error)
                record_path.write_text(json.dumps(run.report, ensure_ascii=False, indent=2), encoding="utf-8")
        finally:
            context.close()
