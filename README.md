# qz2026-xigua

ITStudio 程序部 2026 国庆考核答卷。

## 题目与完成情况

| 题目 | 内容 | 状态 |
| --- | --- | --- |
| 选择题 / 简答题 | 见 [`written.md`](written.md) | 已完成 |
| 编程题 1 | JSON 日志管道 | 已完成 |
| 编程题 2 | 用户管理器 | 已完成 |
| 工程题 A / B | 文章管理系统 / 内容管理系统（选做） | 未做 |

## 目录结构

```
.
├── written.md              选择题 + 简答题答案
├── q1/                     编程题 1：JSON 日志管道
│   ├── main.py               实现
│   ├── test_analyze_log.py   测试脚本（14 项）
│   ├── SOLUTION.md           实现说明（思路、边界处理、约束自查）
│   ├── app.jsonl             示例数据：正常日志
│   ├── bad.jsonl             示例数据：含格式错误的行
│   ├── empty.jsonl           示例数据：空文件
│   └── README.md             题目原文
└── q2/                     编程题 2：用户管理器
    ├── main.py               实现
    └── test.py               测试脚本（32 项）
```

## 运行方式

全部使用 Python 3，**只依赖标准库**，无需安装任何第三方包。

### 编程题 1：JSON 日志管道

```bash
cd q1
python main.py                   # 跑一遍示例
python test_analyze_log.py       # 运行测试（14 项）
```

核心接口：

```python
from main import analyze_log

analyze_log("app.jsonl")
# {'total': 5,
#  'by_level': {'INFO': 3, 'ERROR': 2},
#  'by_user': {'张三': 2, '李四': 2, '王五': 1},
#  'last_error': '超时'}
```

实现思路与边界情况处理详见 [`q1/SOLUTION.md`](q1/SOLUTION.md)。

### 编程题 2：用户管理器

```bash
cd q2
python main.py                   # 跑一遍示例
python test.py                   # 运行测试（32 项）
```

核心接口：

```python
from main import UserManager

um = UserManager()
um.add_user("张三", 18)          # {'id': 1, 'name': '张三', 'age': 18}
um.get_user(1)                   # {'id': 1, 'name': '张三', 'age': 18}
um.update_age(1, 19)             # True
um.remove_user(1)                # True
um.list_users()                  # [{'id': 1, 'name': '张三', 'age': 19}]

um.save_to_json("users.json")    # 保存到 JSON 文件
um.load_from_json("users.json")  # 从 JSON 文件加载（覆盖当前数据）
```

## 开发约定

- **过程性提交**：一题或一小步一个 commit，提交信息说明本次改动内容；
- **不提交无关产物**：`.gitignore` 已排除 `__pycache__/`、`*.pyc`、程序运行生成的
  `users.json`，以及 `.vscode/`、`.idea/` 等本地配置；
- **不 force push**：不改写已推送的历史。

## 学习记录

- 简答题第 1 题（浅拷贝与深拷贝）不在每日一题课程范围内，
  是课后查阅 `copy` 模块文档后自己总结的；
- 编程题 1 的实现经过几轮调试：先是文件打开模式用错，
  后是把 `.jsonl` 当成整份 JSON 解析，最后确认要逐行 `json.loads`；
- 编程题 2 的 `load_from_json` 一开始漏了"加载后 id 接续已加载的最大 id"，
  写测试时才暴露出来并修正。
