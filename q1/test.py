import json
import os

def analyze_log(filepath:str) -> dict:
    result = {"total": 0, "by_level": {}, "by_user": {}, "last_error": None}
    total = 0
    by_level = {}
    by_user = {}
    


    try:
        with open(filepath, "r", encoding="utf-8") as f:

            for line in f:
                try:
                    loaded = json.loads(line)
                except json.decoder.JSONDecodeError:
                    continue
                total = total + 1 

                status = loaded["level"]
                by_level[status] = by_level.get(status,0) + 1

                us = loaded["user"]
                by_user[us] = by_user.get(us,0) + 1

                if loaded["level"] == "ERROR":
                    result["last_error"] = loaded["message"]

                

                if total == 0:
                    return result

                


            result["total"] = total
            result["by_level"] = by_level
            result["by_user"] = by_user



        return result

    except FileNotFoundError:
        return result


          
result = analyze_log("app.jsonl")
print(result["total"])        # 5
print(result["by_level"])     # {'INFO': 3, 'ERROR': 2}
print(result["by_user"])      # {'张三': 2, '李四': 2, '王五': 1}
print(result["last_error"])   # 超时

result = analyze_log("not_exist.jsonl")
print(result)
# {'total': 0, 'by_level': {}, 'by_user': {}, 'last_error': None}

# 文件存在但内容为空
result = analyze_log("empty.jsonl")
print(result)
# {'total': 0, 'by_level': {}, 'by_user': {}, 'last_error': None}

result = analyze_log("bad.jsonl")
print(result["total"])      # 2（跳过格式错误行）
print(result["by_level"])    # {'INFO': 1, 'ERROR': 1}
print(result["last_error"])  # 失败