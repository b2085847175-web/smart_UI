"""新套件的在线开关；与 config/settings.py 的配置一起注入。"""
import pytest

from tests.support.data import SITE, SHOPS

pytest_plugins = ["tests.support.session"]


def pytest_addoption(parser):
    group = parser.getgroup("zhiyan")
    group.addoption("--run-online", action="store_true", help="显式启用三店在线用例")
    group.addoption("--online-shop", default="B1", choices=sorted(SHOPS),
                    help="在线用例使用的店铺代号，默认 B1")
    group.addoption("--batch-size", type=int, default=20, help="批量增删改的数据条数，默认 20")


def pytest_configure(config):
    config.addinivalue_line("markers", "online: 三店在线 UI 用例（需 --run-online）")
    config.addinivalue_line("markers", "offline: 不访问站点的本地校验")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-online"):
        if config.getoption("numprocesses", default=None) not in (None, 0, "0"):
            raise pytest.UsageError("在线 UI 用例不并行，请去掉 -n 参数")
        if config.getoption("reruns", default=0):
            raise pytest.UsageError("在线 UI 用例不自动重试，请去掉 --reruns")
        return
    skip = pytest.mark.skip(reason="在线用例需 --run-online 显式启用")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip)


def pytest_report_header(config):
    if config.getoption("--run-online"):
        return f"在线目标: {SITE} / 店铺 {config.getoption('--online-shop')}"
    return "在线用例未启用（--run-online）"
