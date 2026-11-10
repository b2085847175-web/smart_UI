"""在项目根目录运行 python -m tests.smoke.cli；--list只列清单不启动浏览器。"""
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="智言无业务断言的只读功能冒烟")
    parser.add_argument("--list", action="store_true", help="只打印功能清单")
    parser.add_argument("--run", action="store_true", help="显式访问开发站运行")
    parser.add_argument("--module", default="", help="模块名，可逗号分隔")
    parser.add_argument("--id", default="", help="功能ID，可逗号分隔")
    parser.add_argument("--evidence", action="store_true", help="保存失败截图/trace，可能含业务信息")
    parser.add_argument("--check", action="store_true", help="完全离线自检，不访问业务站")
    args = parser.parse_args()
    if args.check:
        from .check_runtime import main as check
        check()
        return 0
    from .catalog import SCENARIOS
    modules = set(filter(None, args.module.split(",")))
    ids = set(filter(None, args.id.split(",")))
    selected = [case for case in SCENARIOS if (not modules or case.module in modules) and (not ids or case.id in ids)]
    if args.list or not args.run:
        print(json.dumps([{"id":case.id,"module":case.module,"path":case.path,"name":case.name,
                           "steps":[{"name":step.name,"action":step.action} for step in case.steps],
                           "limitation":case.limitation} for case in selected], ensure_ascii=False, indent=2))
        return 0
    import pytest
    arguments = ["tests/smoke/test_readonly_smoke.py", "--run-zhiyan-smoke", "-q"]
    if args.module:
        arguments += ["--smoke-module", args.module]
    if args.id:
        arguments += ["--smoke-id", args.id]
    if args.evidence:
        arguments.append("--smoke-evidence")
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
