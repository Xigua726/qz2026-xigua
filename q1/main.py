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

if __name__ == "__main__":
    result = analyze_log("bad.jsonl")
    print(result)