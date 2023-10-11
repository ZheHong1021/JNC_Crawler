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

# 設備資料庫處理
class Position:
    # 得到設備資訊 (API)
    def get_Position( self, url ): 
        params = {}
        response = requests.get(url, params=params)
        status_code = response.status_code
        if status_code == 200:
            data = json.loads( response.text )
            return data
        return None
    

    # 查詢設備
    def selectPosition(self, position):
        with db.cursor() as cursor:
            cursor.execute( 
                "SELECT * FROM `jnc_position` WHERE `DeviceName` = %s",
                (position, ) # 匯入池名稱與外來鍵ID查詢
            )
            row = cursor.fetchone()
            return row[0] if row else None # 回傳值(ID)
    # 新增設備
    def insertPosition(self, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `jnc_position` (`DeviceName`, `JNCDevice`, `GPSx`, `GPSy`, `Connect`, `USB`, `SIM`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (data['DeviceName'], data['JNCDevice'], data['GPSx'], data['GPSy'], data['Connect'], data['USB'], data['SIM'])
                )
                db.commit()
                return cursor.lastrowid # 得到該筆資料的ID
        except Exception as e:
            print(f'新增jnc_position資料至資料庫發生錯誤: {e}...')
    # 修改設備
    def updatePosition(self, id, data, position_url=None, inspect_url=None):
        try:
            with db.cursor() as cursor:
                # cursor.execute(
                #     """UPDATE `jnc_position` SET `JNCDevice`=%s, `GPSx`=%s, `GPSy`=%s, `Connect`=%s, `USB`=%s, `SIM`=%s, `position_url`=%s, `inspect_url`=%s WHERE `id` = %s""",
                #     (data["JNCDevice"], data["GPSx"], data["GPSy"], data["Connect"], data["USB"], data["SIM"], position_url, inspect_url, id)
                # )
                cursor.execute(
                    """UPDATE `jnc_position` SET `JNCDevice`=%s, `GPSx`=%s, `GPSy`=%s, `Connect`=%s, `USB`=%s, `SIM`=%s WHERE `id` = %s""",
                    (data["JNCDevice"], data["GPSx"], data["GPSy"], data["Connect"], data["USB"], data["SIM"], id)
                )
                db.commit()
                return cursor.lastrowid # 得到該筆資料的ID
        except Exception as e:
            print(f'更新jnc_position資料至資料庫發生錯誤: {e}...')

# 檢測項目資料庫處理
class Inspect:
    # 得到設備測量數據 (API)
    def get_Inspect( self, url ): 
        params = {}
        response = requests.get(url, params=params)
        status_code = response.status_code
        if status_code == 200:
            data = json.loads( response.text )
            # 調整 String -> Boolean
            for position in data['Device']:
                position["isEnable"] = True if position["isEnable"] == 'True' else False
                position["isRead"] = True if position["isRead"] == 'True' else False
            return data
        return None

    # 找尋當前檢測是否存在
    def selectInspect(self, position_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute( 
                    "SELECT * FROM `jnc_inspect` WHERE `TagName` = %s AND `position_id` = %s",
                    (data['TagName'], position_id) # 匯入池名稱與外來鍵ID查詢
                )
                row = cursor.fetchone()
                return row[0] if row else None # 有值則回傳 ID
        except Exception as e:
            print(f'查詢jnc_inspect資料庫發生錯誤: {e}...')
    
    # 更新當前檢測項目
    def updateInspect(self, updated_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """UPDATE `jnc_inspect` SET `ChType`=%s, `isEnable`=%s, `TagName`=%s, `Unit`=%s, `Value`=%s, `AlarmState`=%s, `isRead`=%s WHERE `id` = %s;""",
                    (data["ChType"], data["isEnable"], data["TagName"], data["Unit"], data["Value"], data["AlarmState"], data["isRead"], updated_id, )
                )
                db.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f'修改jnc_inspect資料庫發生錯誤: {e}...')
    
    # 新增當前檢測項目 
    def insertInspect(self, position_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `jnc_inspect` (`position_id`, `ChType`, `isEnable`, `TagName`, `Unit`, `Value`, `AlarmState`, `isRead`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (position_id, data["ChType"], data["isEnable"], data["TagName"], data["Unit"], data["Value"], data["AlarmState"], data["isRead"],)
                )
                db.commit()
                return cursor.lastrowid 
        except Exception as e:
            print(f'新增jnc_inspect資料庫發生錯誤: {e}...')
        
    # 新增當前檢測項目 (*history)
    def insertInspectHistory(self, inspect_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `jnc_inspect_history` (`isEnable`, `Value`, `AlarmState`, `isRead`, `inspect_id`) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (data["isEnable"], data["Value"], data["AlarmState"], data["isRead"], inspect_id,)
                )
                db.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f'新增jnc_inspect_history資料庫發生錯誤: {e}...')
        

def controlPosition(url, position):
    try:
        jnc_position = Position.get_Position(url) # 得到 API
        if jnc_position: # 如API資料存在
            position_id = Position.selectPosition(position) # 搜尋資料庫當中有無該筆， key = id
            if position_id: # 已經存在 -> 更新
                # Position.updatePosition(id, jnc_position, position_url, insepct_url)
                Position.updatePosition(position_id, jnc_position)
            else: # 不存在 -> 新增
                position_id = Position.insertPosition(jnc_position)
            return position_id
        else:
            print(f"✴️【{position}】設備API抓取不到資料: {e}")
    except Exception as e:
        print(f"❌【{position}】抓取設備發生錯誤: {e}")


def controlInspect(url, position_id):
    try:
        jnc_inspect = Inspect.get_Inspect( url ) 
        if jnc_inspect:
            for inspect in jnc_inspect["Device"]:
                inspect_id = Inspect.selectInspect(position_id, inspect) # 設備ID與 TagName來查找
                if inspect_id: # 已經存在 -> 更新
                    Inspect.updateInspect(inspect_id, inspect)
                else: # 不存在 -> 新增
                    inspect_id = Inspect.insertInspect(position_id, inspect)
                
                # 歷史資料(持續新增)
                Inspect.insertInspectHistory(inspect_id, inspect) 
        else:
            print(f"✴️【{position}】檢測數據API抓取不到資料: {e}")
    except Exception as e:
        print(f"😥【{position}】抓取數據發生錯誤: {e}")


    
if __name__ == "__main__":

    db = connect(
        host="127.0.0.1",
        user="root",
        pwd="Ru,6e.4vu4wj/3",
        dbname="jnc",
        port=3306,
    )

    Position = Position()
    Inspect = Inspect()

    map_position = {
        0: "屏南育成1-水質監測",
        1: "向陽-義竹001養蝦廠",
        2: "2801餵料機",
        3: "屏南育成2/育成3-水質監測",
        4: "1901餵料機",
        5: "恆春",
        6: "東後寮",
        7: "1701餵料機",
        8: "向陽海外泵站",
        9: "向陽-種苗池(PCB v1.0)",
        10: "科技養殖系統-種苗",
        11: "屏南-育苗1",
        12: "科技養殖系統-育苗1",
        13: "金屬中心I6手提",
    }

    for id, position in map_position.items(): # id: Position資料表的 id
        print("----------------------------------------")
        print(f"【{position}】")
        position_url = f"http://www.jnc-demo.tw:11223/JSONDevice?Idx={id}&Key=c3VubnkBcmljaA%3D%3D&val=123545"
        insepct_url = f"http://www.jnc-demo.tw:11223/JSONDeviceCH?DeviceIdx={id}&Key=c3VubnkBcmljaA%3D%3D&val=235478"
        
        # 【處理設備】
        # position_id = controlPosition(position_url, position, position_url, insepct_url)
        # 擷取到的設備ID
        position_id = controlPosition(position_url, position)

        # 【處理檢測數據】
        controlInspect(insepct_url, position_id)
    


    print("========================================")
    print(f"程式執行結束，三秒後自動關閉...")
    time.sleep(3)