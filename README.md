# Todo MVP (Python CLI)

這是一個從零建立的最小可用專案（MVP），提供可執行的待辦事項命令列工具。

## MVP 功能

- 新增待辦事項：`add`
- 列出待辦事項：`list`
- 標記完成：`done`
- 刪除項目：`remove`
- 本地 JSON 持久化（預設路徑：`~/.todo_mvp/todos.json`）

## 專案結構

```text
.
├── pyproject.toml
├── README.md
├── src/
│   └── todo_mvp/
│       ├── __init__.py
│       ├── cli.py
│       └── todo.py
└── tests/
    └── test_todo.py
```

## 安裝

### 方式 A：開發模式安裝（建議）

```bash
python -m pip install -e .
```

安裝後可直接使用命令：

```bash
todo-mvp list
```

### 方式 B：不安裝，直接執行

```bash
PYTHONPATH=src python -m todo_mvp.cli list
```

## 執行方式

```bash
# 新增
todo-mvp add "買牛奶"

# 列出
todo-mvp list

# 完成 id=1
todo-mvp done 1

# 刪除 id=1
todo-mvp remove 1
```

## 測試

本專案使用 Python 內建 `unittest`，不需額外測試依賴。

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 設計說明（簡化依賴）

- 使用 `argparse` 實作 CLI，避免引入額外 CLI framework。
- 使用 `json` + `pathlib` 作為儲存層，先滿足 MVP 的可用性與易懂性。
- 測試使用 `unittest`，避免額外安裝 `pytest`，降低專案啟動成本。

## 可擴充方向

- 增加 `update`、`clear-done` 指令
- 支援優先級、截止日期
- 改用 SQLite 並加入資料遷移
