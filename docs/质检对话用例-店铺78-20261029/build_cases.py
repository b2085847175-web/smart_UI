"""将逐条人工设计的对话整理为 Markdown、JSON，并校验覆盖范围与轮次。"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_FILE = ROOT.parents[1] / 'artifacts' / 'quality-standards-78-20261029' / 'verification.json'
catalog = json.loads(CATALOG_FILE.read_text(encoding='utf-8'))
points = catalog['verified']
by_name = {p['name']: (i, p) for i, p in enumerate(points, 1)}
by_record_name = {p['name']: p['id'] for p in catalog['after']}
cases = []
current_point = None
current_case = None

for source in sorted(ROOT.glob('[0-9][0-9]-*.txt')):
    category = source.stem.split('-', 1)[1]
    for line_no, raw in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('@'):
            current_point = line[1:]
            if current_point not in by_name:
                raise ValueError(f'{source.name}:{line_no} 未知质检点: {current_point}')
            if by_name[current_point][1]['category'] != category:
                raise ValueError(f'{source.name}:{line_no} 分类与已添加记录不符')
            current_case = None
        elif line.startswith('#'):
            if current_point is None:
                raise ValueError('场景未指定目标质检点')
            title, trigger, reason = line[1:].split('~', 2)
            point_no, point = by_name[current_point]
            variant_no = 1 + sum(c['point_name'] == current_point for c in cases)
            current_case = {
                'case_id': f'QC78-{point_no:03d}-{variant_no}',
                'point_number': point_no,
                'point_record_id': by_record_name[current_point],
                'category': category,
                'point_name': current_point,
                'variant': variant_no,
                'scenario': title,
                'business_context': [],
                'turns': [],
                'expected': {
                    'primary_point': current_point,
                    'should_hit': True,
                    'key_trigger_turns': [int(t) for t in trigger.split(',')],
                    'reason': reason,
                    'configured_rule': point['rule'],
                    'runtime_result': '未执行实际送检',
                    'exclusive_hit_required': False,
                },
                'source_file': source.name,
            }
            cases.append(current_case)
        elif line.startswith('!'):
            if current_case is None:
                raise ValueError('业务依据未指定场景')
            current_case['business_context'].append(line[1:])
        else:
            if current_case is None or line.count('|') != 1:
                raise ValueError(f'{source.name}:{line_no} 对话行格式不正确')
            buyer, service = line.split('|')
            current_case['turns'].append({
                'turn': len(current_case['turns']) + 1,
                'buyer': buyer,
                'customer_service': service,
            })

errors = []
for case in cases:
    if len(case['turns']) != 5:
        errors.append(f"{case['case_id']}: 轮数为{len(case['turns'])}")
    if any(not t['buyer'].strip() or not t['customer_service'].strip() for t in case['turns']):
        errors.append(f"{case['case_id']}: 存在空白发言")
    if any(t not in range(1, 6) for t in case['expected']['key_trigger_turns']):
        errors.append(f"{case['case_id']}: 关键触发轮次越界")
    case['expected']['key_service_evidence'] = [
        {'turn': t, 'quote': case['turns'][t-1]['customer_service']}
        for t in case['expected']['key_trigger_turns'] if t <= len(case['turns'])
    ]
    case['messages'] = [
        {'role': role, 'turn': t['turn'], 'content': t[key]}
        for t in case['turns']
        for role, key in [('user', 'buyer'), ('assistant', 'customer_service')]
    ]
counts = Counter(c['point_name'] for c in cases)
for point in points:
    if counts[point['name']] != 3:
        errors.append(f"{point['name']}: 对话数为{counts[point['name']]}")
if len(cases) != 225:
    errors.append(f'对话总数应为225，实际为{len(cases)}')
if len({c['case_id'] for c in cases}) != len(cases):
    errors.append('用例编号重复')
fingerprints = [json.dumps(c['turns'], ensure_ascii=False, sort_keys=True) for c in cases]
if len(set(fingerprints)) != len(cases):
    errors.append('存在完全重复的对话')
if errors:
    raise ValueError('\n'.join(errors))

cases.sort(key=lambda c: (c['point_number'], c['variant']))
report = {
    'categories': len(set(c['category'] for c in cases)),
    'points': len(counts),
    'cases': len(cases),
    'turns_per_case': 5,
    'total_turns': sum(len(c['turns']) for c in cases),
    'utterances': sum(len(c['messages']) for c in cases),
    'unique_case_ids': len({c['case_id'] for c in cases}),
    'unique_conversations': len(set(fingerprints)),
    'all_points_have_three_cases': all(n == 3 for n in counts.values()),
    'cases_with_business_context': sum(bool(c['business_context']) for c in cases),
    'structural_validation': 'passed',
    'runtime_execution': '未执行；本次仅设计对话，无后台写入或实际送检',
}
payload = {
    'title': '茵倩化妆品旗舰店新增75个质检点上下文对话',
    'shop': catalog['shop'],
    'scope': '仅前次新增的75个自定义质检点，不扩展至其他官方记录',
    'turn_definition': '一轮 = 买家一句 + 客服一句；每组5轮，共10句',
    'fixture_notice': '所有业务资料及个人信息均为虚构测试夹具；违规客服话术是故意设计的触发样例。',
    'execution_notice': '预期命中属于设计判定，未经实际模型送检；不是实际测试通过记录。',
    'context_usage': 'business_context 是质检系统应加载的已知业务依据，不作为买家或客服发言；不能证明后台事实时应待核实。',
    'overlap_notice': '以主目标质检点为验证目标，部分行为可能同时命中其他规则，不要求只命中一个标签。',
    'validation': report,
    'cases': cases,
}
(ROOT / '全部225组对话.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / '结构校验结果.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

intro = [
    '# 新增75个质检点：225组五轮上下文对话',
    '',
    '适用店铺：茵倩化妆品旗舰店｜淘宝/天猫｜店铺ID 78。',
    '',
    '**范围：75个刚新增的质检点，每点3种独立场景。每组5轮，每轮买家、客服各一句，共225组、1125轮、2250句。**',
    '',
    '以下是预期触发质检点的负面样例，客服违规回复为刻意设计。所有订单、日期、商品规则、姓名、电话和地址均为虚构数据，不代表店铺真实政策或真实个人资料。',
    '',
    '每组均可独立阅读，不依赖上一组对话。标注“已知业务依据”的内容属于质检端业务上下文，不是已向买家解释过的信息。涉及真实状态、权限、政策、操作结果的判断，应将这些依据一并提供给质检系统；仅提供聊天而缺少业务事实时，不能保证确定命中。',
    '',
    '“关键触发轮”列出最明确的违规证据；部分对话更早也已出现同类行为。验证目标为主预期命中，不强制排除其他合理命中。所有案例目前仅完成设计与结构校验，尚未送检验证实际命中结果。',
    '',
    '## 分类索引',
    '',
    '| 分类 | 质检点 | 对话 | 轮次 |',
    '| --- | ---: | ---: | ---: |',
]
for cat in dict.fromkeys(c['category'] for c in cases):
    intro.append(f'| {cat} | 5 | 15 | 75 |')
intro += ['', '---', '']
full_doc = intro.copy()
for category in dict.fromkeys(c['category'] for c in cases):
    section = [f'## {category}', '']
    for name in dict.fromkeys(c['point_name'] for c in cases if c['category'] == category):
        point_no, point = by_name[name]
        section += [f'### {point_no:02d}. {name}', '', f'**已配置判断标准：**{point["rule"]}', '']
        for case in [c for c in cases if c['point_name'] == name]:
            section += [f'#### 场景{case["variant"]}：{case["scenario"]}（{case["case_id"]}）', '']
            for background in case['business_context']:
                section += [f'**已知业务依据（非对话）：**{background}', '']
            for turn in case['turns']:
                section += [f'**第{turn["turn"]}轮**', '', f'- 买家：{turn["buyer"]}', f'- 客服：{turn["customer_service"]}', '']
            turns_text = '、'.join(str(t) for t in case['expected']['key_trigger_turns'])
            section += [f'**主预期：命中「{name}」。关键触发轮：第{turns_text}轮。**', '', f'**判定依据：**{case["expected"]["reason"]}', '', '---', '']
    cat_number = 1 + list(dict.fromkeys(c['category'] for c in cases)).index(category)
    (ROOT / f'{cat_number:02d}-{category}.md').write_text('\n'.join(intro[:12] + section), encoding='utf-8')
    full_doc += section
(ROOT / '全部225组完整对话.md').write_text('\n'.join(full_doc), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
