"""显式只读功能清单的数据结构；不从页面自动生成点击计划。"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    kind: str
    value: str
    scope: str = "main"
    row: str = ""
    sample: bool = False
    data: bool = False


@dataclass(frozen=True)
class Step:
    name: str
    action: str
    target: Target | None = None
    wait: Target | None = None
    value: str = ""
    destination: str = ""
    candidates: str = ""


@dataclass(frozen=True)
class Scenario:
    id: str
    module: str
    path: str
    name: str
    steps: tuple[Step, ...]
    limitation: str = ""


def button(value, scope="main", **kwargs):
    return Target("button", value, scope, **kwargs)


def text(value, scope="main", **kwargs):
    return Target("text", value, scope, **kwargs)


def tab(value, scope="main", **kwargs):
    return Target("tab", value, scope, **kwargs)


def css(value, scope="main", **kwargs):
    return Target("css", value, scope, **kwargs)


def field(value, scope="main", **kwargs):
    return Target("placeholder", value, scope, **kwargs)


def click(name, target, wait=None):
    return Step(name, "click", target, wait)


def opened(name, target, destination="overlay", wait=None):
    return Step(name, "open", target, wait, destination=destination)


def inspect(name, target=None):
    return Step(name, "inspect", target)


def menu(name, target, candidates=""):
    return Step(name, "menu", target, candidates=candidates)


def search(name, placeholder, value):
    return Step(name, "search", field(placeholder), value=value)


def popup(name, target, path):
    return Step(name, "popup", target, destination=path)


def gap(name, reason):
    return Step(name, "limited", value=reason)
