"""q1 作业的测试脚本（规范版）。

用法
----
    cd q1
    python test_analyze_log.py

    也可以直接 pytest test_analyze_log.py（装了 pytest 的话）

它做什么
--------
1. 检查 q1/ 下的示例数据文件是否与题目（README）描述一致；
2. 用**临时目录里自造的数据**验证 analyze_log 的四种行为：
   正常解析 / 文件不存在 / 空文件 / 含非法行；
3. 额外覆盖几个题目没给示例、但要求里提到的边界情况。

设计原则
--------
* 全部用 assert 判定，不靠人眼看 print —— 错了就报出来；
* 测试数据在临时目录里生成，**不依赖、也不修改仓库里的文件**；
* 不依赖当前工作目录：路径从 __file__ 推导，在任何目录下都能跑；
* 只用标准库。

作者：DeepSeek-Chan（应 Xigua726 要求编写）
"""

import json
import os
import sys
import tempfile
import shutil

# --------------------------------------------------------------------------
# 让本脚本无论从哪个目录运行，都能 import 到同目录下的 main.py
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from main import analyze_log  # noqa: E402  （必须在 sys.path 调整之后导入）

EMPTY = {"total": 0, "by_level": {}, "by_user": {}, "last_error": None}

# 题目 README 里 app.jsonl 的原文（用于比对仓库里的数据文件）
README_APP = [
    {"timestamp": "2026-10-01 10:23:45", "level": "INFO", "message": "用户登录成功", "user": "张三"},
    {"timestamp": "2026-10-01 10:24:01", "level": "ERROR", "message": "数据库连接失败", "user": "李四"},
    {"timestamp": "2026-10-01 10:25:12", "level": "INFO", "message": "用户登出", "user": "张三"},
    {"timestamp": "2026-10-01 10:26:30", "level": "ERROR", "message": "超时", "user": "李四"},
    {"timestamp": "2026-10-01 10:27:00", "level": "INFO", "message": "任务完成", "user": "王五"},
]
APP_EXPECT = {
    "total": 5,
    "by_level": {"INFO": 3, "ERROR": 2},
    "by_user": {"张三": 2, "李四": 2, "王五": 1},
    "last_error": "超时",
}


# --------------------------------------------------------------------------
# 测试数据：在临时目录里现造（不碰仓库文件）
# --------------------------------------------------------------------------
class Fixture:
    """造一套测试数据，退出时自动清理。"""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="q1-test-")
        self.files = {}

        # 正常数据（内容与 README 的 app.jsonl 一致）
        self.write("app.jsonl", README_APP)

        # 含一行非法 JSON（README 示例 4）
        self.write_raw("bad.jsonl", [
            '{"timestamp": "2026-10-01 10:23:45", "level": "INFO", "message": "ok", "user": "张三"}',
            "这不是合法的 JSON",
            '{"timestamp": "2026-10-01 10:24:01", "level": "ERROR", "message": "失败", "user": "李四"}',
        ])

        # 空文件（0 字节）
        self.write_raw("empty.jsonl", [])

        # 末尾没有换行符
        self.write_raw("no_newline.jsonl",
                       ['{"timestamp": "t", "level": "ERROR", "message": "x", "user": "甲"}'],
                       trailing_newline=False)

        # 全是非法行
        self.write_raw("all_bad.jsonl", ["垃圾", "还是垃圾"])

        # 全是 INFO，一条 ERROR 都没有
        self.write("all_info.jsonl", [
            {"timestamp": "t", "level": "INFO", "message": "a", "user": "甲"},
            {"timestamp": "t", "level": "INFO", "message": "b", "user": "乙"},
        ])

        # 多条 ERROR（验证取的是最后一条，不是第一条）
        self.write("multi_error.jsonl", [
            {"timestamp": "t", "level": "ERROR", "message": "第一条错误", "user": "甲"},
            {"timestamp": "t", "level": "INFO", "message": "中间", "user": "乙"},
            {"timestamp": "t", "level": "ERROR", "message": "最后一条错误", "user": "甲"},
        ])

        # 出现题目没提过的 level
        self.write("warn.jsonl", [
            {"timestamp": "t", "level": "WARNING", "message": "警告", "user": "甲"},
            {"timestamp": "t", "level": "DEBUG", "message": "调试", "user": "乙"},
        ])

        # 非法行夹在中间、且行首行尾有空白
        self.write_raw("spaces.jsonl", [
            "   ",
            '{"timestamp": "t", "level": "INFO", "message": "m", "user": "甲"}',
            "",
            "  {坏行}  ",
            '{"timestamp": "t", "level": "ERROR", "message": "e", "user": "乙"}',
        ])

    def path(self, name):
        return os.path.join(self.dir, name)

    def write(self, name, records):
        with open(self.path(name), "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def write_raw(self, name, lines, trailing_newline=True):
        text = "\n".join(lines)
        if lines and trailing_newline:
            text += "\n"
        with open(self.path(name), "w", encoding="utf-8") as f:
            f.write(text)

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


FIX = Fixture()


# --------------------------------------------------------------------------
# 测试用例
# --------------------------------------------------------------------------
def test_app_normal():
    """示例 1：正常数据 —— 五个字段/键全部要对上。"""
    got = analyze_log(FIX.path("app.jsonl"))
    assert got == APP_EXPECT, "期望 %r，实际 %r" % (APP_EXPECT, got)


def test_returns_four_keys():
    """返回值必须稳定包含四个键（题目规定的返回格式）。"""
    got = analyze_log(FIX.path("app.jsonl"))
    assert set(got.keys()) == {"total", "by_level", "by_user", "last_error"}, \
        "键不对：%r" % sorted(got.keys())


def test_missing_file():
    """示例 2：文件不存在 —— 返回空结果，且不得抛异常。"""
    got = analyze_log(FIX.path("这个文件不存在.jsonl"))
    assert got == EMPTY, "期望 %r，实际 %r" % (EMPTY, got)


def test_empty_file():
    """示例 3：空文件 —— 返回空结果。"""
    got = analyze_log(FIX.path("empty.jsonl"))
    assert got == EMPTY, "期望 %r，实际 %r" % (EMPTY, got)
    # 空文件时 by_level 必须是空字典（不能凭空多出 INFO/ERROR 键）
    assert got["by_level"] == {}, "空文件的 by_level 应为 {}，实际 %r" % (got["by_level"],)


def test_bad_lines_skipped():
    """示例 4：含非法行 —— 跳过该行，total 只数成功的。"""
    got = analyze_log(FIX.path("bad.jsonl"))
    assert got["total"] == 2, "total 期望 2，实际 %r" % (got["total"],)
    assert got["by_level"] == {"INFO": 1, "ERROR": 1}, "by_level 实际 %r" % (got["by_level"],)
    assert got["last_error"] == "失败", "last_error 期望 '失败'，实际 %r" % (got["last_error"],)


def test_no_error_line():
    """一条 ERROR 都没有时，last_error 必须是 None。"""
    got = analyze_log(FIX.path("all_info.jsonl"))
    assert got["last_error"] is None, "期望 None，实际 %r" % (got["last_error"],)
    assert got["total"] == 2
    assert got["by_level"] == {"INFO": 2}


def test_last_error_is_the_last_one():
    """多条 ERROR 时，last_error 取【最后一条】，不是第一条。"""
    got = analyze_log(FIX.path("multi_error.jsonl"))
    assert got["last_error"] == "最后一条错误", \
        "期望 '最后一条错误'（最后一条），实际 %r（说明取错成第一条了？）" % (got["last_error"],)


def test_unknown_level_does_not_crash():
    """出现题目没列举过的 level 时，不应崩溃，且要如实统计。"""
    got = analyze_log(FIX.path("warn.jsonl"))
    assert got["total"] == 2, "total 实际 %r" % (got["total"],)
    assert got["by_level"] == {"WARNING": 1, "DEBUG": 1}, "by_level 实际 %r" % (got["by_level"],)


def test_all_lines_bad():
    """整个文件全是非法行 —— 等同于"没有有效数据"，不崩。"""
    got = analyze_log(FIX.path("all_bad.jsonl"))
    assert got == EMPTY, "期望 %r，实际 %r" % (EMPTY, got)


def test_no_trailing_newline():
    """最后一行没有换行符，也要被算进去。"""
    got = analyze_log(FIX.path("no_newline.jsonl"))
    assert got["total"] == 1, "total 期望 1，实际 %r" % (got["total"],)
    assert got["last_error"] == "x"


def test_blank_lines_and_spaces():
    """空行、纯空白行、带前后空格的坏行：都不能让解析中断。"""
    got = analyze_log(FIX.path("spaces.jsonl"))
    assert got["total"] == 2, "total 期望 2（空行不算、坏行跳过），实际 %r" % (got["total"],)
    assert got["by_level"] == {"INFO": 1, "ERROR": 1}
    assert got["last_error"] == "e"


def test_input_not_mutated_across_calls():
    """同一个文件连续调用两次，结果必须一致（不能有残留状态）。"""
    first = analyze_log(FIX.path("app.jsonl"))
    second = analyze_log(FIX.path("app.jsonl"))
    assert first == second, "两次调用结果不一致：%r vs %r" % (first, second)


def test_returns_dict_not_none():
    """返回值必须是 dict（题目签名 -> dict；返回 None 会让调用方崩）。"""
    for name in ("app.jsonl", "empty.jsonl"):
        got = analyze_log(FIX.path(name))
        assert isinstance(got, dict), "%s 的返回值不是 dict，而是 %s" % (name, type(got).__name__)


def test_repo_sample_data_matches_readme():
    """仓库里的 q1/*.jsonl 内容是否与题目 README 一致（数据自检）。"""
    app = os.path.join(HERE, "app.jsonl")
    if not os.path.exists(app):
        raise AssertionError("缺少示例数据 app.jsonl（题目示例 1 依赖它）")

    with open(app, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    assert records == README_APP, \
        "q1/app.jsonl 的内容与 README 不一致：%r" % (records,)

    # 顺便验证仓库数据喂给 analyze_log 也能得到正确结果
    got = analyze_log(app)
    assert got == APP_EXPECT, "用仓库里的 app.jsonl 跑，结果不对：%r" % (got,)

    for name in ("bad.jsonl", "empty.jsonl"):
        target = os.path.join(HERE, name)
        assert os.path.exists(target), "缺少示例数据 %s" % name


# --------------------------------------------------------------------------
# 运行器：不依赖 pytest，直接 python test_analyze_log.py 也能跑
# --------------------------------------------------------------------------
def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed, failed = [], []
    width = max(len(n) for n, _ in tests)

    print("运行 %d 个测试（数据目录：%s）" % (len(tests), FIX.dir))
    print("-" * (width + 28))

    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed.append((name, str(exc)))
            print("FAIL  %-*s  %s" % (width, name, exc))
        except Exception as exc:  # 非断言类异常也算失败，并打印类型
            failed.append((name, "%s: %s" % (type(exc).__name__, exc)))
            print("ERROR %-*s  %s: %s" % (width, name, type(exc).__name__, exc))
        else:
            passed.append(name)
            print("ok    %-*s" % (width, name))

    print("-" * (width + 28))
    print("通过 %d 项，失败 %d 项" % (len(passed), len(failed)))

    doc = (main.__doc__ or "").strip().split("\n")[0]
    print("（%s）" % doc if doc else "")
    FIX.cleanup()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
