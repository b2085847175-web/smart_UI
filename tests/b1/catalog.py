"""B1业务清单及报告生成；只读本地JSON，不启动浏览器。"""
from collections import Counter
import argparse
import json
from pathlib import Path
import re

from tests.smoke.catalog import PAGES
from .guard import BASE_URL, SHOP

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "b1" / "scenarios.json"
EVIDENCE = ROOT / "outputs" / "exploration-20261020"
LABELS = {"verified": "具体操作已验证", "inspected": "仅检查入口或配置", "planned": "未执行补测"}


def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_catalog(data)
    return data


def validate_catalog(data):
    if data.get("schema_version") != 1 or data.get("site") != BASE_URL or data.get("shop") != SHOP or data.get("platform") != "tmall":
        raise ValueError("清单环境、店铺、平台或版本错误")
    known_paths = {"/" + path for path, _ in PAGES}
    seen, observed = set(), set()
    for case in data["scenarios"]:
        case_id = case["id"]
        if case_id in seen or not re.fullmatch(r"B1-(?:G)?[0-9]{3}", case_id):
            raise ValueError("场景ID重复或格式错误: " + case_id)
        seen.add(case_id)
        if case["path"] not in known_paths or case["status"] not in LABELS:
            raise ValueError("场景路由或状态错误: " + case_id)
        for field in ("module", "title", "purpose", "expected", "actual", "verification", "automation"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError("缺少有效字段 " + field + ": " + case_id)
        for field in ("preconditions", "steps"):
            values = case.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError("前置或步骤为空: " + case_id)
        if case["status"] == "planned":
            if case["actual"] != "本次未执行" or case["verification"] != "not_run" or case["evidence"]:
                raise ValueError("未执行场景不能带已执行结论: " + case_id)
        else:
            observed.add(case["path"])
            if case["verification"] != "manual_browser_observation" or not case.get("ledger_record"):
                raise ValueError("缺少观察来源: " + case_id)
        for evidence in case["evidence"]:
            target = (EVIDENCE / evidence).resolve()
            if not target.is_relative_to(EVIDENCE.resolve()) or not target.is_file():
                raise ValueError("证据文件缺失或越界: " + case_id)
    if observed != known_paths:
        raise ValueError("观察记录未覆盖全部登记路由")


def summary(data):
    counts = Counter(case["status"] for case in data["scenarios"])
    return {"registered_routes": len(PAGES), "observed_routes": len({c["path"] for c in data["scenarios"] if c["status"] != "planned"}),
            "scenarios": len(data["scenarios"]), **{key: counts[key] for key in LABELS},
            "browser_automation_run": False, "new_readonly_assertion_tests": 7}


def escape(value):
    return str(value).replace("|", r"\|").replace("\n", " ")


def write_reports(data):
    output = ROOT / "docs"
    output.mkdir(exist_ok=True)
    counts = summary(data)
    report = ["# B1 店铺探索报告（2026-10-20）", "",
        "目标站点：开发站 dev.zhiyan.chat；平台：天猫；店铺：" + SHOP + "。", "",
        f"检查了{counts['observed_routes']}/{counts['registered_routes']}个登记页面；形成{counts['scenarios']}条场景：{counts['verified']}条具体操作已验证、{counts['inspected']}条仅检查入口/配置、{counts['planned']}条未执行补测。", "",
        "这些是观察记录和后续场景清单，不代表所有业务分支达到100%覆盖。相同模块的早期空态和稍后的新增结果按探索顺序保留。新增的7条自动化断言仅完成离线检查和收集，未运行终端浏览器。", "",
        "这是2026-10-20的历史快照；2026-10-21的局部补测单列于 [增量报告](B1增量回归-20261021.md)，不回写历史状态。当前共有12条只读断言，历史快照记录的是当时新增的7条。", "",
        "## 已完成的业务链路", "",
        "1. 新建货品 → 配置使用方法 → 新建商品并关联货品 → 配置规格和商品知识。",
        "2. 新建指定商品的礼盒知识 → 测试窗发商品和问题 → 核对回复及知识来源。",
        "3. 自定义关键词原文回复 → 输出替换词实际生效 → 停用替换规则保留基线。",
        "4. 模拟待发货订单 → 触发人工兜底 → 转接统计查看会话 → 质检详情核对订单 → 标记已检。", "",
        "## 需要处理的发现", "",
        "- 测试窗明确提示没有配置【人工客服】的策略；售前策略为空。现有四个转接场景指向售后客服，并不等于原因策略完整。",
        "- B1客服账号管理暂无AI员工数据；测试专用1不能证明真实员工已经接入。",
        "- 余额显示0、套餐到期但测试窗仍应答；页面存在授信信息，计费原因与本次扣减尚未核实。",
        "- 有知识来源命中，但知识统计仍为空；需确认统计口径、数据处理周期，暂不判为缺陷。",
        "- 快速发送商品和问题曾出现两条相近回复；单独追问只收到一条新回复，现有证据不足以认定重复回复缺陷。",
        "- 历史观察记录保留页面当时显示的线性检索顺序；业务预期以2026-10-21用户确认的规则为准，商品与店铺知识库同级。", "",
        "## 后续确认的业务规则", "",
        "规则来源与浏览器观察分别记录；确认规则不会增加已验证数量。详见 [B1业务规则](B1业务规则.md)。", ""]
    rules = data.get("business_rules", {})
    for rule in rules.get("rules", []):
        report.append(f"- {rule['id']}（{rules['confirmed_on']}，用户确认）：{rule['description']}")
    for uncertainty in rules.get("remaining_uncertainties", []):
        report.append("- 待明确：" + uncertainty)
    report += ["",
        "## 保留数据与最终状态", "",
        "| 类型 | 标识或内容 | 最终状态 |", "| --- | --- | --- |"]
    for item in data["dataset"]:
        identifier = item.get("name") or item.get("keyword") or item.get("code", "")
        extra = item.get("id") or item.get("code") or item.get("value") or item.get("replacement") or item.get("scope", "")
        state = "未启用/停用" if item.get("enabled") is False else "保留供复测"
        report.append(f"| {escape(item['type'])} | {escape(identifier)} {escape(extra)} | {state} |")
    report += ["", "保留两个测试会话：tmall_c075516ce6f64769、tmall_c95a35f6b5aa4f21。模拟订单1234567890、金额99元、待发货，不代表真实电商订单。测试质检记录已标记已检。没有删除记录、修改其他店铺或全局既有变量、提交同步、充值、对真实买家发送跟单。", "",
        "结束时仪表盘：接待2、消息17、转接1、转接率50%；初次对账为消息10。数字随测试增加，禁止将快照写成长期固定总量断言。", "",
        "## 可复测的测试窗步骤", "", "详见 [B1测试窗回归](B1测试窗回归.md)。断言必须限定到本次新消息和本条知识来源，不能因为历史聊天中存在识别码就判通过。", "",
        "## 逐项记录与后续场景", ""]
    for case in data["scenarios"]:
        report += [f"### {case['id']} {case['title']}", "", f"- 模块 / 路由：{case['module']} / {case['path']}", f"- 状态：{LABELS[case['status']]}", f"- 目的：{case['purpose']}", "- 前置：" + "；".join(case["preconditions"]), "- 操作：" + " → ".join(case["steps"]), f"- 验收点：{case['expected']}", f"- 实际结果：{case['actual']}", f"- 自动化：{case['automation']}"]
        for image in case["evidence"]:
            report.append(f"- 截图：[查看 {image}](../outputs/exploration-20261020/{image})")
        if case.get("ledger_record"):
            report.append(f"- 原始观察：checkpoint.json 第{case['ledger_record']}条（1开始）。")
        if case.get("limitation"):
            report.append("- 限制：" + case["limitation"])
        report.append("")
    (output / "B1探索报告-20261020.md").write_text("\n".join(report), encoding="utf-8")
    matrix = ["# B1 场景覆盖矩阵", "", "以下为2026-10-20的84条历史快照；部分业务分支的后续结果见 [2026-10-21增量报告](B1增量回归-20261021.md)，不将局部通过计作整场景覆盖。", "", "页面访问、具体业务结果和自动化执行分别记录。未执行场景没有计入通过数。", "",
              "| 页面 | 路由 | 已验证操作 | 仅检查 | 待补测 |", "| --- | --- | ---: | ---: | ---: |"]
    for path, title in PAGES:
        counted = Counter(c["status"] for c in data["scenarios"] if c["path"] == "/" + path)
        matrix.append(f"| {title} | /{path} | {counted['verified']} | {counted['inspected']} | {counted['planned']} |")
    matrix += ["", "## 场景索引", "", "| ID | 目的 | 状态 | 路由 |", "| --- | --- | --- | --- |"]
    for case in data["scenarios"]:
        matrix.append(f"| {case['id']} | {escape(case['purpose'])} | {LABELS[case['status']]} | {case['path']} |")
    (output / "B1场景覆盖矩阵.md").write_text("\n".join(matrix) + "\n", encoding="utf-8")
    (EVIDENCE / "coverage-summary.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true", help="从JSON更新探索报告和覆盖矩阵")
    args = parser.parse_args()
    data = load_catalog()
    counts = write_reports(data) if args.write_report else summary(data)
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
