import json
import os

class UserManager:
    def __init__(self):
        self.users = []
        self._next_id = 1 


    def add_user(self, name:str, age:int) -> dict:
        user_id = self._next_id
        self._next_id += 1 
        user_dict = {f"id":user_id, "name":name, "age":age}
        self.users.append(user_dict)
        return user_dict

    def get_user(self, get_id:int):
        for i in self.users:
            if i["id"] == get_id:
                return i
            


if __name__ == "__main__":
    um = UserManager()
    print(um.add_user("张三", 18))     # 期望 {'id': 1, 'name': '张三', 'age': 18}
    print(um.add_user("李四", 20))     # 期望 {'id': 2, 'name': '李四', 'age': 20}
    print(um.users)   
    print(um.get_user(1) )
    print(um.get_user(99))

                

        
