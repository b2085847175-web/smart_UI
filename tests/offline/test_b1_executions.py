"""验证增量执行不会虚增通过，且证据只引用本轮目录中的真实文件。"""
from copy import deepcopy
import json

import pytest

from tests.b1.catalog import ROOT, load_catalog
from tests.b1.executions import load_run, validate_run, summary


def test_run_has_independent_check_results():
    data = load_run()
    counts = summary(data)
    assert counts["checks"] == sum(counts["check_results"].values())
    assert counts["record_results"]["inconclusive"] > 0
    assert counts["check_results"]["not_run"] > 0
    assert counts["terminal_browser_automation_run"] is False
    catalog = {case["id"]: case for case in load_catalog()["scenarios"]}
    for case_id in ("B1-G002", "B1-G003", "B1-G004"):
        assert catalog[case_id]["status"] == "planned"  # 历史快照不可被部分检查改写。


def test_partial_evidence_cannot_promote_record_to_passed():
    data = deepcopy(load_run())
    record = next(item for item in data["records"] if item["status"] == "inconclusive")
    record["status"] = "passed"
    with pytest.raises(ValueError, match="结论与检查不一致"):
        validate_run(data)


@pytest.mark.parametrize("evidence", ["../../pytest.ini", "F:/UI自动化/pytest.ini", "/etc/passwd", "absent.png"])
def test_run_rejects_escaped_or_missing_evidence(evidence):
    data = deepcopy(load_run())
    data["records"][0]["checks"][0]["evidence"] = [evidence]
    with pytest.raises(ValueError, match="证据文件缺失或越界"):
        validate_run(data)


def test_executed_check_requires_evidence():
    data = deepcopy(load_run())
    data["records"][0]["checks"][0]["evidence"] = []
    with pytest.raises(ValueError, match="执行检查缺少证据"):
        validate_run(data)


@pytest.mark.parametrize("field,value", [("actual", "已通过"), ("evidence", ["10-restored-products.png"])])
def test_unexecuted_check_cannot_claim_observation(field, value):
    data = deepcopy(load_run())
    check = next(check for record in data["records"] for check in record["checks"] if check["status"] == "not_run")
    check[field] = value
    with pytest.raises(ValueError, match="未执行检查不能带结论或证据"):
        validate_run(data)


def test_run_rejects_unknown_scenario():
    data = deepcopy(load_run())
    data["records"][0]["covers"] = ["B1-G999"]
    with pytest.raises(ValueError, match="关联场景不存在"):
        validate_run(data)


def test_run_rejects_duplicate_record():
    data = deepcopy(load_run())
    data["records"].append(deepcopy(data["records"][0]))
    with pytest.raises(ValueError, match="执行ID重复"):
        validate_run(data)


def test_run_rejects_duplicate_check():
    data = deepcopy(load_run())
    data["records"][0]["checks"].append(deepcopy(data["records"][0]["checks"][0]))
    with pytest.raises(ValueError, match="检查ID缺失或重复"):
        validate_run(data)


def test_shared_fixture_markers_are_distinct_and_traceable():
    samples = json.loads((ROOT / "data/b1/shared-fixtures.json").read_text(encoding="utf-8"))
    products = samples["products"]
    assert len(products) == 2
    assert len({sample["id"] for sample in products}) == 2
    assert len({sample["marker"] for sample in products}) == 2
    for sample in products:
        assert sample["marker"] != sample["other_marker"]
        assert sample["other_marker"] in {item["marker"] for item in products}
        evidence = ROOT / "outputs/exploration-20261021" / ("11-a-knowledge-persisted.txt" if sample["id"] == "9102026102101" else "12-b-knowledge-persisted.txt")
        text = evidence.read_text(encoding="utf-8")
        assert sample["id"] in text and sample["marker"] in text and sample["operation"] in text
    text = (ROOT / "outputs/exploration-20261021/10-restored-products.txt").read_text(encoding="utf-8")
    assert samples["stock"]["code"] in text


def test_failed_check_cannot_be_hidden_by_record_rollup():
    data = deepcopy(load_run())
    record = next(item for item in data["records"] if item["status"] == "failed")
    record["status"] = "inconclusive"
    with pytest.raises(ValueError, match="结论与检查不一致"):
        validate_run(data)
