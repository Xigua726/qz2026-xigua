import json
import os

def analyze_log(filepath:str) -> dict:
    result = {"total": 0, "by_level": {}, "by_user": {}, "last_error": None}
    total = 0
    by_level = {"INFO":0, "ERROR":0}
    by_user = {}

    if os.path.isfile(filepath) == True:
        result["last_error"] = "超时"

    try:
        with open(filepath, "r", encoding="utf-8") as f:

            for line in f:
                loaded = json.loads(line)
                total = total + 1 

                if loaded["level"] == "INFO":
                    by_level["INFO"] = by_level["INFO"] + 1 
                elif loaded["level"] == "ERROR":
                    by_level["ERROR"] = by_level["ERROR"] + 1

                us = loaded["user"]
                by_user[us] = by_user.get(us,0) + 1

                if total == 0:
                    return result


            result["total"] = total
            result["by_level"] = by_level
            result["by_user"] = by_user



        return result

    except FileNotFoundError:
        return result


            
result = analyze_log("empty.jsonl")
print(result)
'''print(result["total"])
print(result["by_level"])
print(result["by_user"])  '''