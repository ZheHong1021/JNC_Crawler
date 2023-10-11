import requests
import json
import time
from random import randint
import pymysql

def connect(host, user, pwd, dbname, port):
    try:
        connect = pymysql.connect(
            host = host,
            user = user,
            passwd = pwd,
            database = dbname,
            port = int(port)
        )
        return connect
    except Exception as e:
        print('連線資料庫失敗: {}'.format(str(e)))
    return None

    

# 檢測項目資料庫處理
class Inspect:
    # 找尋當前檢測是否存在
    def selectInspect(self):
        try:
            with db.cursor() as cursor:
                cursor.execute( 
                    "SELECT `id`, `TagName` FROM `jnc_inspect`",
                )
                row = cursor.fetchall()
                return row if row else None # 有值則回傳 ID
        except Exception as e:
            print(f'查詢jnc_inspect資料庫發生錯誤: {e}...')
    # 找尋當前檢測是否存在
    def selectHistoryInspect(self, inspect_id):
        try:
            with db.cursor() as cursor:
                cursor.execute( 
                    "SELECT COUNT(`inspect_id`) FROM `jnc_inspect_history` WHERE `inspect_id` = %s",
                    (inspect_id, )
                )
                row = cursor.fetchone()
                return row[0] if row else None # 有值則回傳 ID
        except Exception as e:
            print(f'查詢jnc_inspect_history資料庫發生錯誤: {e}...')

    def deleteInspect(self, inspect_id):
        try:
            with db.cursor() as cursor:
                cursor.execute( 
                    "DELETE FROM `jnc_inspect` WHERE `id` = %s",
                    (inspect_id, )
                )
                db.commit()
        except Exception as e:
            print(f'刪除jnc_inspect資料庫發生錯誤: {e}...')
if __name__ == "__main__":

    db = connect(
        host="127.0.0.1",
        user="root",
        pwd="Ru,6e.4vu4wj/3",
        dbname="jnc",
        port=3306,
    )

    Inspect = Inspect()
    inspects = Inspect.selectInspect()
    exceed_count = 0
    invalid_count = 0
    for inspect in inspects:
        inspect_id = inspect[0]
        tagName = inspect[1]
        COUNT = Inspect.selectHistoryInspect(inspect_id)
        print(f"{inspect_id} - {tagName} => COUNT = {COUNT}")
        if COUNT > 10:
            exceed_count += 1
        else:
            # 重複紀錄 => 殺掉
            Inspect.deleteInspect(inspect_id)
            invalid_count += 1

    
    print("==================")
    print(exceed_count)
    print(invalid_count)