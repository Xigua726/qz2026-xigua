"""q2 作业的测试脚本（用户管理器）。

用法
----
    cd q2
    python test.py

    装了 pytest 的话也可以：pytest test.py -v

它做什么
--------
用 assert 逐项验证 UserManager 的七个功能：

    添加用户 / 按 id 查询 / 修改年龄 / 删除用户 /
    列出用户 / 保存 JSON / 加载 JSON

以及题目 README 里给出的行为示例和几条边界情况。

设计原则
--------
* 全部用 assert 判定，不靠人眼看 print —— 错了就报出来，退出码为 1；
* 测试文件写在临时目录里，**不依赖、也不修改仓库里的文件**；
* 不依赖当前工作目录：路径从 __file__ 推导，在任何目录下都能跑；
* 只用标准库；
* 只调用公开方法，不读 _next_id 这类内部属性
  —— 题目说"方法命名、参数设计由你决定"，测试不该绑死实现细节。

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

from main import UserManager  # noqa: E402  （必须在 sys.path 调整之后导入）


class Fixture:
    """临时目录：存放测试用的 JSON 文件，退出时清理。"""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="q2-test-")

    def path(self, name):
        return os.path.join(self.dir, name)

    def write_json(self, name, data):
        """直接写一个 JSON 文件（用于准备"已有数据"的场景）。"""
        with open(self.path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return self.path(name)

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


FIX = Fixture()


# --------------------------------------------------------------------------
# 一、构造与基本状态
# --------------------------------------------------------------------------
def test_new_manager_is_empty():
    """刚创建的管理器里没有任何用户。"""
    um = UserManager()
    assert um.list_users() == [], "新建的管理器应该是空的，实际 %r" % (um.list_users(),)
    assert um.get_user(1) is None, "空管理器里查任何 id 都该是 None"


# --------------------------------------------------------------------------
# 二、添加用户（题目 README 的示例）
# --------------------------------------------------------------------------
def test_add_user_returns_dict():
    """add_user 返回该用户字典，且 id 从 1 开始。"""
    um = UserManager()
    got = um.add_user("张三", 18)
    assert got == {"id": 1, "name": "张三", "age": 18}, "实际 %r" % (got,)


def test_add_user_ids_increment():
    """连续添加，id 依次递增：1, 2, 3..."""
    um = UserManager()
    first = um.add_user("张三", 18)
    second = um.add_user("李四", 20)
    assert first["id"] == 1 and second["id"] == 2, \
        "id 应为 1、2，实际 %r、%r" % (first["id"], second["id"])

    ids = [um.add_user("用户%d" % k, k)["id"] for k in range(3, 6)]
    assert ids == [3, 4, 5], "id 应继续为 3、4、5，实际 %r" % (ids,)


def test_add_user_returns_dict_type():
    """返回值必须是 dict（题目：返回该用户字典）。"""
    um = UserManager()
    got = um.add_user("张三", 18)
    assert isinstance(got, dict), "返回值类型是 %s，应为 dict" % type(got).__name__


def test_added_user_appears_in_list():
    """添加后能在列表中查到，且内容一致。"""
    um = UserManager()
    created = um.add_user("张三", 18)
    assert created in um.list_users(), "添加的用户没出现在 list_users() 里"


# --------------------------------------------------------------------------
# 三、按 id 查询
# --------------------------------------------------------------------------
def test_get_user_found():
    """查到存在的用户，返回该字典。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    assert um.get_user(2) == {"id": 2, "name": "李四", "age": 20}


def test_get_user_not_found_returns_none():
    """查不存在的 id，返回 None（题目明确要求）。"""
    um = UserManager()
    um.add_user("张三", 18)
    assert um.get_user(99) is None, "期望 None，实际 %r" % (um.get_user(99),)


def test_get_user_not_found_when_deleted():
    """用户被删掉后再查，应该返回 None。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.remove_user(2)
    assert um.get_user(2) is None, "已删除的用户不该还能查到"


# --------------------------------------------------------------------------
# 四、修改年龄
# --------------------------------------------------------------------------
def test_update_age_success():
    """修改成功返回 True，且新年龄生效。"""
    um = UserManager()
    um.add_user("张三", 18)
    assert um.update_age(1, 19) is True, "期望 True"
    assert um.get_user(1)["age"] == 19, "年龄没改成功"


def test_update_age_not_found():
    """用户不存在时返回 False（而不是抛异常或返回 None）。"""
    um = UserManager()
    um.add_user("张三", 18)
    got = um.update_age(99, 30)
    assert got is False, "期望 False，实际 %r" % (got,)


def test_update_age_only_touches_target():
    """改一个人的年龄，不影响别人。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.update_age(1, 19)
    assert um.get_user(2)["age"] == 20, "改张三的年龄不该影响李四"


def test_update_age_works_on_second_user():
    """目标用户不是列表第一个时，也要能找到（防止只检查第一个就跳出）。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.add_user("王五", 22)
    assert um.update_age(3, 23) is True, "改第三个用户应返回 True"
    assert um.get_user(3)["age"] == 23


# --------------------------------------------------------------------------
# 五、删除用户
# --------------------------------------------------------------------------
def test_remove_user_success_then_fail():
    """删除成功返回 True；再删同一个返回 False（题目示例）。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    assert um.remove_user(2) is True, "第一次删除应返回 True"
    assert um.remove_user(2) is False, "重复删除应返回 False"


def test_remove_user_not_found():
    """删不存在的 id 返回 False。"""
    um = UserManager()
    um.add_user("张三", 18)
    assert um.remove_user(99) is False


def test_remove_user_from_empty_manager():
    """空管理器里删除，返回 False，不崩。"""
    um = UserManager()
    assert um.remove_user(1) is False


def test_remove_user_works_on_second_user():
    """要删的用户不是列表第一个时，也要能删掉（这道题最容易错的地方）。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    assert um.remove_user(2) is True, "删第二个用户应返回 True"
    names = [u["name"] for u in um.list_users()]
    assert names == ["张三"], "删完后应只剩张三，实际 %r" % (names,)


def test_remove_only_removes_target():
    """删除一个用户，其他用户不受影响。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.add_user("王五", 22)
    um.remove_user(2)
    remaining = [u["id"] for u in um.list_users()]
    assert remaining == [1, 3], "应剩 id 1 和 3，实际 %r" % (remaining,)


def test_remove_does_not_break_add_id():
    """删除用户后，新用户的 id 继续递增，不与已删除的重复。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.remove_user(2)
    new = um.add_user("王五", 22)
    assert new["id"] == 3, "删过用户后新 id 应为 3，实际 %r" % (new["id"],)


# --------------------------------------------------------------------------
# 六、列出用户
# --------------------------------------------------------------------------
def test_list_users_keeps_order():
    """list_users 按添加顺序返回。"""
    um = UserManager()
    for name in ("张三", "李四", "王五"):
        um.add_user(name, 20)
    names = [u["name"] for u in um.list_users()]
    assert names == ["张三", "李四", "王五"], "顺序不对：%r" % (names,)


def test_list_users_returns_list_of_dicts():
    """返回值是可遍历的列表，元素是含 id/name/age 的字典。"""
    um = UserManager()
    um.add_user("张三", 18)
    users = um.list_users()
    assert isinstance(users, list), "应为 list，实际 %s" % type(users).__name__
    assert len(users) == 1
    assert set(users[0].keys()) == {"id", "name", "age"}, \
        "用户字典的键应为 id/name/age，实际 %r" % sorted(users[0].keys())


def test_list_users_reflects_updates():
    """修改后，list_users 里能看到新值。"""
    um = UserManager()
    um.add_user("张三", 18)
    um.update_age(1, 19)
    assert um.list_users()[0]["age"] == 19


# --------------------------------------------------------------------------
# 七、保存 / 加载 JSON
# --------------------------------------------------------------------------
def test_save_then_load_roundtrip():
    """存进去再读出来，数据一致。"""
    path = FIX.path("roundtrip.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.save_to_json(path)

    um2 = UserManager()
    um2.load_from_json(path)
    assert um2.list_users() == [{"id": 1, "name": "张三", "age": 18},
                                {"id": 2, "name": "李四", "age": 20}], \
        "加载后数据不一致：%r" % (um2.list_users(),)


def test_saved_file_is_valid_json():
    """保存出来的文件是合法 JSON 数组，且字段完整。"""
    path = FIX.path("valid.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.save_to_json(path)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "应为 JSON 数组"
    assert data == [{"id": 1, "name": "张三", "age": 18}], "内容不对：%r" % (data,)


def test_saved_file_keeps_chinese_readable():
    """中文要按原字符写入，不能变成 \\uXXXX 转义（题目要求 ensure_ascii=False）。"""
    path = FIX.path("chinese.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.save_to_json(path)

    raw = open(path, encoding="utf-8").read()
    assert "张三" in raw, "文件里没找到中文原字符，可能被转义了：%r" % (raw,)
    assert "\\u" not in raw, "中文被转成了 \\uXXXX 转义：%r" % (raw,)


def test_load_overwrites_current_data():
    """加载会【覆盖】当前数据，而不是追加（题目要求）。"""
    path = FIX.path("overwrite.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.save_to_json(path)

    um2 = UserManager()
    um2.add_user("旧数据", 99)          # 先放一条无关数据
    um2.load_from_json(path)
    assert um2.list_users() == [{"id": 1, "name": "张三", "age": 18}], \
        "加载应覆盖原有数据，实际 %r" % (um2.list_users(),)


def test_load_then_add_continues_id():
    """【题目明确要求】加载后添加用户，id 接续已加载的最大 id。"""
    path = FIX.path("continue.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.add_user("王五", 22)
    um.save_to_json(path)

    um2 = UserManager()
    um2.load_from_json(path)
    new = um2.add_user("赵六", 24)
    assert new["id"] == 4, \
        "加载了 id 1~3 之后，新用户 id 应为 4，实际 %r（id 接续没做对？）" % (new["id"],)

    ids = [u["id"] for u in um2.list_users()]
    assert len(ids) == len(set(ids)), "出现了重复 id：%r" % (ids,)


def test_load_then_add_continues_id_after_deletion():
    """保存时最大的 id 是 3（中间删过），加载后新用户 id 仍应接续 3。"""
    path = FIX.path("gap.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.add_user("李四", 20)
    um.add_user("王五", 22)
    um.remove_user(2)                    # 删掉中间那个，剩下 id 1、3
    um.save_to_json(path)

    um2 = UserManager()
    um2.load_from_json(path)
    new = um2.add_user("赵六", 24)
    assert new["id"] == 4, "应接续最大 id 3，新 id 为 4，实际 %r" % (new["id"],)


def test_load_empty_list():
    """加载一个空数组 []，不崩溃，且之后从 id=1 开始分配。"""
    path = FIX.write_json("empty.json", [])
    um = UserManager()
    um.load_from_json(path)
    assert um.list_users() == [], "加载空数组后列表应为空"
    assert um.add_user("张三", 18)["id"] == 1, "空数据加载后，id 应重新从 1 开始"


def test_load_replaces_with_existing_data():
    """加载一个"已经有多条数据"的文件，字段保持原样。"""
    path = FIX.write_json("existing.json", [
        {"id": 10, "name": "甲", "age": 30},
        {"id": 11, "name": "乙", "age": 31},
    ])
    um = UserManager()
    um.load_from_json(path)
    assert um.get_user(10) == {"id": 10, "name": "甲", "age": 30}
    assert um.get_user(11)["name"] == "乙"


def test_save_after_load_keeps_data():
    """加载再保存，内容不丢。"""
    src = FIX.path("src.json")
    dst = FIX.path("dst.json")
    um = UserManager()
    um.add_user("张三", 18)
    um.save_to_json(src)

    um2 = UserManager()
    um2.load_from_json(src)
    um2.save_to_json(dst)

    with open(dst, encoding="utf-8") as f:
        assert json.load(f) == [{"id": 1, "name": "张三", "age": 18}]


# --------------------------------------------------------------------------
# 八、两个管理器互不干扰
# --------------------------------------------------------------------------
def test_two_managers_are_independent():
    """两个 UserManager 实例的数据互不影响（验证数据挂在 self 上）。"""
    a = UserManager()
    b = UserManager()
    a.add_user("张三", 18)
    assert b.list_users() == [], "另一个管理器的数据被污染了"
    assert b.add_user("李四", 20)["id"] == 1, "另一个管理器应各自从 id=1 开始"


# --------------------------------------------------------------------------
# 九、题目 README 的完整示例，按顺序走一遍
# --------------------------------------------------------------------------
def test_readme_full_example():
    """题目 README「行为示例」逐行核对。"""
    path = FIX.path("readme.json")
    um = UserManager()
    assert um.add_user("张三", 18) == {"id": 1, "name": "张三", "age": 18}
    assert um.add_user("李四", 20) == {"id": 2, "name": "李四", "age": 20}
    assert um.get_user(1) == {"id": 1, "name": "张三", "age": 18}
    assert um.get_user(99) is None
    assert um.update_age(1, 19) is True
    assert um.remove_user(2) is True
    assert um.remove_user(2) is False
    assert um.list_users() == [{"id": 1, "name": "张三", "age": 19}]

    um.save_to_json(path)
    um2 = UserManager()
    um2.load_from_json(path)
    assert um2.list_users() == [{"id": 1, "name": "张三", "age": 19}]


# --------------------------------------------------------------------------
# 运行器：不依赖 pytest，直接 python test.py 也能跑
# --------------------------------------------------------------------------
def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed, failed = [], []
    width = max(len(n) for n, _ in tests)

    print("运行 %d 个测试（临时目录：%s）" % (len(tests), FIX.dir))
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
    FIX.cleanup()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
