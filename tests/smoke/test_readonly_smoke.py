"""每条功能链独立context；不添加业务断言。"""
import json

import allure
import pytest


@pytest.mark.smoke
@pytest.mark.zhiyan_smoke
def test_readonly_function(smoke_run, scenario):
    allure.dynamic.feature(scenario.module)
    allure.dynamic.story(scenario.name)
    result = smoke_run.run(scenario)
    allure.attach(json.dumps(result, ensure_ascii=False, indent=2), name="只读遍历步骤",
                  attachment_type=allure.attachment_type.JSON)
    if result["status"] in {"failed", "completed_with_events"} or result["infrastructure_failed"] or result.get("events"):
        failed = [step["name"] for step in result["steps"] if step["status"] == "failed"]
        events = sorted({event["kind"] for event in result.get("events", [])})
        details = failed + (["运行事件: " + ", ".join(events)] if events else [])
        pytest.fail("只读冒烟基础设施或操作异常: " + "; ".join(
            details or [result.get("error", "现场清理失败")]
        ), pytrace=False)
    if result["status"] in {"partial", "blocked"}:
        pytest.skip("流程未完整覆盖: " + result["status"] + "，请查看独立步骤记录")
