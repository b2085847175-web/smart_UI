"""全局 fixtures：浏览器、配置注入、失败截图附加到 allure。"""
import allure
import pytest
from playwright.sync_api import Browser

from config.settings import load_config


@pytest.fixture(scope="session")
def config() -> dict:
    return load_config()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, config):
    """覆盖 pytest-playwright 默认上下文参数。"""
    return {
        **browser_context_args,
        "viewport": config["browser"]["viewport"],
        "locale": config["browser"]["locale"],
        "timezone_id": config["browser"]["timezone"],
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, config):
    return {
        **browser_type_launch_args,
        "headless": config["browser"]["headless"],
        "slow_mo": config["browser"]["slow_mo"],
    }


@pytest.fixture(scope="session")
def browser(browser_type_launch_args, playwright, config):
    browser_name = config["browser"]["name"]
    browser_type = getattr(playwright, browser_name)
    browser: Browser = browser_type.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def base_url(config) -> str:
    return config["base_url"]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时把截图附加到 allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            try:
                allure.attach(
                    page.screenshot(full_page=True),
                    name=f"失败截图-{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
