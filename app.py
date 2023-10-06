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
class Device:
    # 得到設備資訊 (API)
    def get_Device( self, url ): 
        params = {}
        response = requests.get(url, params=params)
        status_code = response.status_code
        if status_code == 200:
            data = json.loads( response.text )
            return data
        return None
    # 查詢設備
    def selectDevice(self, device):
        with db.cursor() as cursor:
            cursor.execute( 
                "SELECT * FROM `jnc_device` WHERE `DeviceName` = %s",
                (device, ) # 匯入池名稱與外來鍵ID查詢
            )
            row = cursor.fetchone()
            return row[0] if row else None # 回傳值(ID)
    # 新增設備
    def insertDevice(self, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `jnc_device` (`DeviceName`, `JNCDevice`, `GPSx`, `GPSy`, `Connect`, `USB`, `SIM`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (data['DeviceName'], data['JNCDevice'], data['GPSx'], data['GPSy'], data['Connect'], data['USB'], data['SIM'])
                )
                db.commit()
                return cursor.lastrowid # 得到該筆資料的ID
        except Exception as e:
            print(f'新增jnc_device資料至資料庫發生錯誤: {e}...')
    # 修改設備
    def updateDevice(self, id, data, device_url=None, inspect_url=None):
        try:
            with db.cursor() as cursor:
                # cursor.execute(
                #     """UPDATE `jnc_device` SET `JNCDevice`=%s, `GPSx`=%s, `GPSy`=%s, `Connect`=%s, `USB`=%s, `SIM`=%s, `device_url`=%s, `inspect_url`=%s WHERE `id` = %s""",
                #     (data["JNCDevice"], data["GPSx"], data["GPSy"], data["Connect"], data["USB"], data["SIM"], device_url, inspect_url, id)
                # )
                cursor.execute(
                    """UPDATE `jnc_device` SET `JNCDevice`=%s, `GPSx`=%s, `GPSy`=%s, `Connect`=%s, `USB`=%s, `SIM`=%s WHERE `id` = %s""",
                    (data["JNCDevice"], data["GPSx"], data["GPSy"], data["Connect"], data["USB"], data["SIM"], id)
                )
                db.commit()
                return cursor.lastrowid # 得到該筆資料的ID
        except Exception as e:
            print(f'更新jnc_device資料至資料庫發生錯誤: {e}...')

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
            for device in data['Device']:
                device["isEnable"] = True if device["isEnable"] == 'True' else False
                device["isRead"] = True if device["isRead"] == 'True' else False
            return data
        return None

    # 找尋當前檢測是否存在
    def selectInspect(self, device_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute( 
                    "SELECT * FROM `jnc_inspect` WHERE `TagName` = %s AND `device_id` = %s",
                    (data['TagName'], device_id) # 匯入池名稱與外來鍵ID查詢
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
    def insertInspect(self, device_id, data):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `jnc_inspect` (`device_id`, `ChType`, `isEnable`, `TagName`, `Unit`, `Value`, `AlarmState`, `isRead`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (device_id, data["ChType"], data["isEnable"], data["TagName"], data["Unit"], data["Value"], data["AlarmState"], data["isRead"],)
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
        

def controlDevice(url, device):
    try:
        jnc_device = Device.get_Device(url) # 得到 API
        if jnc_device: # 如API資料存在
            device_id = Device.selectDevice(device) # 搜尋資料庫當中有無該筆， key = id
            if device_id: # 已經存在 -> 更新
                # Device.updateDevice(id, jnc_device, device_url, insepct_url)
                Device.updateDevice(device_id, jnc_device)
            else: # 不存在 -> 新增
                device_id = Device.insertDevice(jnc_device)
            return device_id
        else:
            print(f"✴️【{device}】設備API抓取不到資料: {e}")
    except Exception as e:
        print(f"❌【{device}】抓取設備發生錯誤: {e}")


def controlInspect(url, device_id):
    try:
        jnc_inspect = Inspect.get_Inspect( url ) 
        if jnc_inspect:
            for inspect in jnc_inspect["Device"]:
                inspect_id = Inspect.selectInspect(device_id, inspect) # 設備ID與 TagName來查找
                print(inspect)
                # if inspect_id: # 已經存在 -> 更新
                #     Inspect.updateInspect(inspect_id, inspect)
                # else: # 不存在 -> 新增
                #     inspect_id = Inspect.insertInspect(device_id, inspect)
                
                # # 歷史資料(持續新增)
                # Inspect.insertInspectHistory(inspect_id, inspect) 
        else:
            print(f"✴️【{device}】檢測數據API抓取不到資料: {e}")
    except Exception as e:
        print(f"【{device}】抓取數據發生錯誤: {e}")


    
if __name__ == "__main__":

    db = connect(
        host="127.0.0.1",
        user="root",
        pwd="Ru,6e.4vu4wj/3",
        dbname="jnc",
        port=3306,
    )

    Device = Device()
    Inspect = Inspect()

    map_device = {
        0: "屏南育成1-水質監測",
        # 1: "向陽-義竹001養蝦廠",
        # 2: "2801餵料機",
        # 3: "屏南育成2/育成3-水質監測",
        # 4: "1901餵料機",
        # 5: "恆春",
        # 6: "東後寮",
        # 7: "1701餵料機",
        # 8: "向陽海外泵站",
        # 9: "向陽-種苗池(PCB v1.0)",
        # 10: "科技養殖系統-種苗",
        # 11: "屏南-育苗1",
        # 12: "科技養殖系統-育苗1",
        # 13: "金屬中心I6手提",
    }

    for id, device in map_device.items(): # id: Device資料表的 id
        print("----------------------------------------")
        print(f"【{device}】")
        device_url = f"http://www.jnc-demo.tw:11223/JSONDevice?Idx={id}&Key=c3VubnkBcmljaA%3D%3D&val=123545"
        insepct_url = f"http://www.jnc-demo.tw:11223/JSONDeviceCH?DeviceIdx={id}&Key=c3VubnkBcmljaA%3D%3D&val=235478"
        
        # 【處理設備】
        # device_id = controlDevice(device_url, device, device_url, insepct_url)
        # 擷取到的設備ID
        device_id = controlDevice(device_url, device)
        # print(device_id)

        # 【處理檢測數據】
        controlInspect(insepct_url, device_id)
    


    print("========================================")
    print(f"程式執行結束，三秒後自動關閉...")
    time.sleep(3)