"""校验并生成B1增量执行报告；不启动浏览器，不将部分检查提升为场景通过。"""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path, PureWindowsPath
import re

from .catalog import ROOT, load_catalog, escape
from .guard import BASE_URL, SHOP

RUN = ROOT / "data/b1/runs/20261021.json"
RESULTS = {"passed": "通过", "failed": "失败", "inconclusive": "证据不足", "not_run": "未执行"}


def rollup(checks):
    states = {c["status"] for c in checks}
    if "failed" in states:
        return "failed"
    if states == {"passed"}:
        return "passed"
    if states == {"not_run"}:
        return "not_run"
    return "inconclusive"


def evidence_path(value, run_date):
    # 同时拒绝Windows和POSIX绝对路径；resolve也会检查目录联接后的真实位置。
    base = (ROOT / "outputs" / ("exploration-" + run_date.replace("-", ""))).resolve()
    if not isinstance(value, str) or not value or Path(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise ValueError("证据文件缺失或越界")
    target = (base / value).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError("证据文件缺失或越界")
    return target


def validate_run(data, catalog=None):
    if data.get("schema_version") != 1 or data.get("site") != BASE_URL or data.get("shop") != SHOP or data.get("platform") != "tmall":
        raise ValueError("执行环境或版本错误")
    run_date = data.get("executed_on", "")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", run_date):
        raise ValueError("执行日期错误")
    date.fromisoformat(run_date)
    if data.get("verification") != "manual_browser_observation":
        raise ValueError("执行来源错误")
    dataset = data.get("dataset")
    if not isinstance(dataset, list) or not dataset or any(not isinstance(item, str) or not item.strip() for item in dataset):
        raise ValueError("保留数据说明缺失")
    known = {c["id"] for c in (catalog or load_catalog())["scenarios"]}
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("执行记录为空")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not re.fullmatch(r"B1-R[0-9]{3}", record["id"]):
            raise ValueError("执行ID格式错误")
        key = record["id"]
        if key in seen:
            raise ValueError("执行ID重复")
        seen.add(key)
        covers = record.get("covers")
        if (not isinstance(covers, list) or not covers or any(not isinstance(item, str) for item in covers)
                or not set(covers).issubset(known) or len(covers) != len(set(covers))):
            raise ValueError("关联场景不存在")
        for field in ("title", "preconditions", "steps", "cleanup", "limitation"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError("执行字段缺失: " + field)
        checks = record.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError("检查为空")
        check_ids = set()
        for check in checks:
            if not isinstance(check, dict) or not isinstance(check.get("id"), str) or not check["id"] or check["id"] in check_ids:
                raise ValueError("检查ID缺失或重复")
            check_ids.add(check["id"])
            if check.get("status") not in RESULTS:
                raise ValueError("检查状态错误")
            if any(not isinstance(check.get(field), str) or not check[field].strip() for field in ("expected", "actual")):
                raise ValueError("检查预期或实际结果缺失")
            evidence = check.get("evidence")
            if not isinstance(evidence, list):
                raise ValueError("证据列表缺失")
            if check["status"] == "not_run":
                if check["actual"] != "本次未执行" or evidence:
                    raise ValueError("未执行检查不能带结论或证据")
            elif not evidence:
                raise ValueError("执行检查缺少证据")
            for item in evidence:
                evidence_path(item, run_date)
        if record.get("status") != rollup(checks):
            raise ValueError("记录结论与检查不一致")
    return data


def load_run(path=RUN):
    return validate_run(json.loads(Path(path).read_text(encoding="utf-8")))


def summary(data):
    checks = [c for r in data["records"] for c in r["checks"]]
    return {"executed_on": data["executed_on"], "shop": data["shop"], "records": len(data["records"]), "record_results": dict(Counter(r["status"] for r in data["records"])),
            "checks": len(checks), "check_results": dict(Counter(c["status"] for c in checks)),
            "verification": data["verification"], "terminal_browser_automation_run": False}


def record_lines(record, run_date):
    lines = [f"### {record['id']} {record['title']}", "", f"- 关联场景：{', '.join(record['covers'])}",
             f"- 本次结论：{RESULTS[record['status']]}", f"- 前置：{record['preconditions']}",
             f"- 步骤：{record['steps']}", f"- 收尾：{record['cleanup']}", f"- 验证边界：{record['limitation']}", "",
             "| 检查 | 预期 | 实际观察 | 状态 |", "| --- | --- | --- | --- |"]
    for check in record["checks"]:
        lines.append(f"| {escape(check['id'])} | {escape(check['expected'])} | {escape(check['actual'])} | {RESULTS[check['status']]} |")
    lines.append("")
    for name in dict.fromkeys(e for c in record["checks"] for e in c["evidence"]):
        rel = "../outputs/exploration-" + run_date.replace("-", "") + "/" + name
        lines.append(f"- 证据：[{name}]({rel})")
    return lines + [""]


def write_reports(data):
    validate_run(data)
    catalog = load_catalog()
    counts = summary(data)
    lines = [f"# B1增量回归（{data['executed_on']}）", "", f"环境：{BASE_URL}；天猫；{SHOP}。", "",
             "由内置浏览器执行。逐项检查与完整场景分开统计；下述部分检查通过不表示B1-G002/G003/G004全部通过。历史84条清单保留原始状态。", "",
             f"执行记录{counts['records']}条；检查{counts['checks']}项：" + "、".join(f"{RESULTS[k]}{v}" for k, v in counts['check_results'].items()) + "。", "",
             "统计按时间累加检查记录，含早期当时未执行的条目；不等同于当前仍待测的唯一验收点数。R006/C01共享更新已由R007补测；R004/C02推荐排除已由R008补测，早期记录保留原貌。", "",
             "本轮发现的推荐内容错配、上架状态矛盾及待查现象见 [问题记录](B1问题记录.md)。", "",
             "## 本次保留数据", ""]
    for item in data["dataset"]:
        lines.append("- " + item)
    lines += ["", "## 实际执行与验收", ""]
    for record in data["records"]:
        lines += record_lines(record, data["executed_on"])
    output = ROOT / "docs"
    output.mkdir(exist_ok=True)
    (output / ("B1增量回归-" + data["executed_on"].replace("-", "") + ".md")).write_text("\n".join(lines), encoding="utf-8")
    manual = ["# B1已验证功能用例", "", "来源：2026-10-20的23条已验证操作，以及2026-10-21增量记录。只检查过入口的20条与未执行的41条不作为通过用例。", "",
              "本文件由 python -m tests.b1.executions --write-report 生成。每条可单独选取执行；复测必须重新记录实际结果，历史观察不作为本次通过。", "",
              "## 通用前置与执行约束", "",
              f"- 登录{BASE_URL}，选中天猫/{SHOP}，操作前复核店铺。",
              "- 新建用例使用新的UIAUTO日期前缀、唯一商品ID/编码；将旧识别码替换为本轮识别码，避免重名与历史消息干扰。",
              "- 查询类用例可复用保留样本；用例所需货品、商品、知识、订单、会话在各条前置中列明，不要求按文档顺序连续运行。",
              "- 消息断言限定本次新增回复；核对该回复的知识来源，不能搜索整段历史聊天判通过。",
              "- 修改前记录状态，结束后恢复推荐/启停状态；保留隔离测试记录，不删除、不同步其他店铺、不向真实买家发送消息。", "",
              "## 历史已验证功能", ""]
    for case in catalog["scenarios"]:
        if case["status"] != "verified":
            continue
        manual += [f"### {case['id']} {case['title']}", "", f"- 模块：{case['module']}（{case['path']}）", f"- 目的：{case['purpose']}",
                   "- 前置：" + "；".join(case["preconditions"]), "", "操作步骤：", ""]
        manual += [f"{i}. {step}" for i, step in enumerate(case["steps"], 1)]
        manual += ["", "验收预期：" + case["expected"], "", "历史实际（2026-10-20）：" + case["actual"], "",
                   "自动化范围：" + case["automation"], "", f"原始来源：checkpoint.json第{case['ledger_record']}条。", ""]
        if case.get("limitation"):
            manual += ["验证边界：" + case["limitation"], ""]
        for image in case["evidence"]:
            manual += [f"证据：[{image}](../outputs/exploration-20261020/{image})", ""]
    manual += ["## 本次新增业务用例", "", "以下记录保留每项检查的实际状态，包含通过、失败和证据不足，标题不代表全部通过。按执行先后累加：R006/C01已由R007补测，R004/C02已由R008补测；其他证据不足及未执行项仍需补测。问题复现见 [问题记录](B1问题记录.md)。", ""]
    for record in data["records"]:
        manual += record_lines(record, data["executed_on"])
    (output / "B1已验证功能用例.md").write_text("\n".join(manual), encoding="utf-8")
    target = ROOT / "outputs" / ("exploration-" + data["executed_on"].replace("-", "")) / "execution-summary.json"
    target.write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    data = load_run()
    print(json.dumps(write_reports(data) if args.write_report else summary(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
