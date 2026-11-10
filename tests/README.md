# 测试套件

只保留一套新用例。旧的儒意店冒烟、B1 只读回归、SauceDemo 示例已删除（可用 `git checkout -- tests` 从初始提交恢复）。

## 目录

| 路径 | 内容 |
| --- | --- |
| `tests/offline/` | 离线校验：三店白名单、夹具完整性、批量自毁规则、授权范围、对话清单。不联网、不要账号。 |
| `tests/online/` | 在线 UI：CRUD、授权、测试窗对话。需 `--run-online` 和账号。 |
| `tests/support/` | 数据加载、店铺护栏、会话封装。 |
| `data/shops.json` | 三家 UI 店白名单。 |
| `data/fixtures/` | 永久夹具、20 条临时批、授权、对话清单。 |

## 跑法

离线（随时可跑）：

```bash
.venv/Scripts/python.exe -m pytest tests/offline -q
```

在线 CRUD 与对话（需要 B1 账号）：

```bash
export UI_TEST_USERNAME=... UI_TEST_PASSWORD=...
.venv/Scripts/python.exe -m pytest tests/online -q --run-online
```

授权用例另需要普通员工/质检员账号（超管没有授权抽屉）：

```bash
export UI_TEST_EMPLOYEE_USERNAME=... UI_TEST_EMPLOYEE_PASSWORD=...
export UI_TEST_EMPLOYEE_ACCOUNT=<账号名>
```

只跑某一块：

```bash
.venv/Scripts/python.exe -m pytest tests/online/test_crud_stock_product.py -q --run-online
.venv/Scripts/python.exe -m pytest tests/online/test_talk.py -q --run-online
```

## 约束

- 只进 B1 / A1 / A2 三家 UI 店；`tests/support/guard.py` 会拦下其他店名。
- 永久夹具（`permanent.json` 的 `do_not_delete`）只查、只改测试字段，不删。
- CRUD 20 条用 `UIAUTO_CRUD_` 前缀，删完按前缀搜索必须为 0。
- 对话只看新会话本轮回复和知识来源。
