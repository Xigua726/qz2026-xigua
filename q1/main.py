import json
import os

def analyze_log(filepath:str) -> dict:
    result = {"total": 0, "by_level": {}, "by_user": {}, "last_error": None}
    total = 0
    by_level = {}
    by_user = {}                                                       #初始化字典
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:

            for line in f:
                try:
                    loaded = json.loads(line)
                except json.decoder.JSONDecodeError:
                    continue                                           #判断jsonl是否含有错误的行，如果含有跳过该行并不在total计数

                total = total + 1                                      #统计total

                status = loaded["level"]
                by_level[status] = by_level.get(status,0) + 1          #统计by_level

                us = loaded["user"]
                by_user[us] = by_user.get(us,0) + 1                    #统计by_user

                if loaded["level"] == "ERROR":
                    result["last_error"] = loaded["message"]           #返回最后一次error信息

                if total == 0:
                    return result                                      #空文件时返回空字典
           
            result["total"] = total
            result["by_level"] = by_level
            result["by_user"] = by_user

        return result

    except FileNotFoundError:                                           #文件不存在时返回空字典
        return result

if __name__ == "__main__":                                              #测试，在被import时候不会额外输出内容
    result = analyze_log("bad.jsonl")
    print(result)