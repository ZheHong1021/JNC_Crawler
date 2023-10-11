# JNC_Crawler
## 檔案說明

### app.py (*常用到)
主要用來爬取資料 + 匯入資料庫的程式碼

### delete_duplicate_inspect.py (*有需要才會用到)
因為最一開始測試抓取時，不小心抓取到重複的inspect內容，要將其刪除
只要其inspect_id對應的history(歷史資料)數量小於 100筆，則都刪除

### jnc.sql
整個系統的資料庫架構 +　資料(jnc_history_inspect會很大，不能一次匯入，額外處理)

### jnc_inspect_history.sql
由於包含著眾多數據，因此需要額外處理，建議先建立架構後再決定要匯入多少資料


### build / dist / app.spec
以下為 pyinstaller所產生的結果，可以不用理會

### requirements.txt
虛擬環境下安裝的套件列表