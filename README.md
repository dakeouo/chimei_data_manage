# 八臂迷宮實驗數據管理系統

國立勤益科大陳啟鈞教授團隊與台南市奇美醫院產學合作，進行【以路徑預測失智症之八臂迷宮系統】計畫，目的是探討使用紀錄被測者行走路徑來判斷出被測者是否有失智症傾向，以協助醫師診斷被測者是否罹患失智症。

此系統僅能接受【圖像化自動追蹤紀錄動物軌跡8臂迷宮系統平台】的實驗數據使用。

## Steps for System
### Python Libarary
Python需安裝下列套件才可成功執行：
```bash
sudo apt install python3-tk #tkinter, 要裝在系統層(此為ubuntu命令)(import tkinter)
pip install tkcalendar #tkcalendar(import tkcalendar)
pip install opencv-python #OpenCV(import cv2)
pip install matplotlib #matplotlib(import matplotlib.pyplot as plt)
```

### Prepare
1. 將**sqlite3_chimei_data.sql**匯入SQLite DB內
2. 建立**SQL_FILE**資料夾，底下再新增**CSV**、**IMG**和**MASK**三個資料夾
3. 將目前所有的遮罩CSV檔匯入至**MASK**資料夾中
4. 將所需的**群組**與**時間點**資訊，分別輸入至"model_group"與"exp_timepoint"資料表中
   - **群組**資料表(model_group)欄位：
     - group_id：組別標籤。全為英文小寫，以底線區隔單字詞
     - model：疾病模型名稱。全為英文大寫，若疾病名字數>5則只取前五字母作為疾病名
     - groups：組別名稱。統一為**疾病名+治療方式**的格式作為組別名稱
   - **時間點**資料表(exp_timepoint)欄位：
     - tp_no：時間點標籤。以**ooMxxD**格式代表"幾個月又幾天"的時間點
     - tp_show：時間點顯示名稱。通常以Mxx(幾月)、Wxx(幾周)、Dxx(幾天)的格式來做為顯示名稱
     - note：備註標記

### Run
![image](https://i.imgur.com/ZW9TAuA.png)
#### 五大區域
- 實驗數據匯入
- 實驗日期總覽
- 路徑結果顯示和匯出與實驗數據刪除
- 實驗數據詳細資料顯示與查詢
- 系統狀態顯示

#### 三大功能
- 實驗數據結果匯入與實驗日期總覽
  - 使用者依序匯入實驗數據結果資料與實驗大鼠的軌跡結果圖和座標檔後，並填入相關的實驗數據匯入資訊，即可成功的將實驗數據匯入

- 路徑結果檢視與軌跡檔案輸出
  - 依序選擇疾病模型的時間點以及組別，並按下「開啟圖片」按鈕，即可觀看選擇的時間點和組別之實驗大鼠的路徑軌跡結果圖

- 實驗數據查詢與資料篩選
  - 使用者可以點選「選擇篩選資料查詢條件」按鈕，來查詢欲查詢的條件
  - 使用者可以依據實驗日期、組別、時間點等六個條件，來篩選想要查詢的資料

## Database - SQLite3
![image](https://i.imgur.com/06THgpr.png)
使用5個資料表，有3個主要的資料表：
- 實驗資訊(exp_date)：紀錄每次實驗的資訊，包含實驗日期、此次實驗鼠為何種疾病、患病時間點(多久前患病)等
  - 其中**患病時間點**的詳細資訊，以exp_timepoint資料表儲存
- 實驗鼠量化數據(exp_detail)：紀錄每筆實驗鼠的量化數據，包含實驗資訊ID、組別、老鼠編號等
  - 其中**組別**的詳細資訊，以model_group資料表儲存
- 實驗鼠進臂序列(exp_route)：紀錄每筆實驗鼠的進臂順序，欄位有：實驗鼠量化數據ID、序列編號(進的第幾個臂)、進去那個臂的編號

## Designer
National Chin-Yi University of Techology Department of Electronic Engineering 
- Master [Hong, Liang-Jyun](https://github.com/dakeouo)