import sqlite3
import csv
from datetime import datetime
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
from tkinter import filedialog
from tkcalendar import Calendar, DateEntry
import datetime
import math
from functools import partial
import numpy as np
import matplotlib.pyplot as plt

# SQL 語句命令
# INSERT INTO table_name(field1,field2,...,fieldn) VALUES(val1,val2,...,valn)   
# SELECT * FROM table [WHERE field='value' [AND field='value']] 
# UPDATE table SET field1='value1' [, field2='value2', ... fieldn='valuen'] [WHERE field=value] 
# DELETE FROM table [WHERE field='value']
# conn.execute(sql_query) #執行命令  conn.commit() #寫回資料庫(UPDATE, 以及其他非DELETE/INSERT/SELECT)
# cursor.fetchall() #顯示全部查詢資訊  cursor.fetchone() #顯示第一筆資訊

# tkinter 視窗元件變數
NOW_TIME = datetime.datetime.now()
SYSTEM_NAME = "實驗大鼠八臂迷宮數據管理系統(TBI 專用)"
TIMES_COUNT = 0
TK_BT_SetExpCSV = ""
TK_BT_LoadExpCSV = ""
TK_BT_SetPathData = ""
TK_BT_LoadPathData = ""
TK_BT_ShowQuantity = ""
TK_SHOW_CAL_Month = ""
TK_Console_Line = ["", "", "", ""]
TKE_Command = ""
DEL_Cal = ""
TK_BT_DEL_ExpData = ""
TK_BT_EXP_HAVE_PATH = ""

tkWin = tk.Tk()
tkWin.title(SYSTEM_NAME) #窗口名字
tkWin.geometry('%dx%d+10+10' %(1024, 780)) #窗口大小(寬X高+X偏移量+Y偏移量)
tkWin.resizable(False, False) #禁止變更視窗大小

WIN_CLOSE_LoadCSV = False
WIN_CLOSE_FilterData = False
IS_SET_ExpData_File = False
IS_SET_PathData_Path = False
ExpData_CSV_Confirm = ""
LoadCSV = ""
FilterData = ""

SQL_CONN = sqlite3.connect("./sqlite3_chimei_data.db") #建立資料庫連結
CONSOLE_FLAG = 0 #新的一則訊息要寫在哪個位置
CONSOLE_COLOR = {"GOOD": "green2", "ERROR": "orangered2", "INFO": "cyan", "NOTICE": "yellow2", "NONE": "white", "NULL": "black"}
CONSOLE_MSG = [ # 顏色, 訊息, 上一則位置, 下一則位置
	[CONSOLE_COLOR["NULL"], "", 3, 1],
	[CONSOLE_COLOR["NULL"], "", 0, 2],
	[CONSOLE_COLOR["NULL"], "", 1, 3],
	[CONSOLE_COLOR["NULL"], "", 2, 0]
]
LOAD_EXP_DATE = ""
LOAD_EXP_MODEL = ""
LOAD_EXP_MODEL_ID = -1
LOAD_EXP_TIMEPOINT = ""
LOAD_EXP_TIMEPOINT_ID = -1
LOAD_EXP_HAVE_PATH = True
# LOAD_CSV_NAME = "./rowdata/20201015(06M).csv"
LOAD_CSV_PATH = ""
LOAD_CSV_NAME = tk.StringVar()
LOAD_CSV_FULL_NAME = ""
LOAD_PATH_DIR = tk.StringVar()
TBI_QUANTITY_DATA_TYPE = "All"
TBI_QUANTITY_DATA = []
TBI_QUANTITY_Group_TOTAL = []
TBI_QUANTITY_TP_TOTAL = []
TBI_QUANTITY_TOTAL_TOTAL = []

CAL_DATE_NUM = []
CAL_CURRENT_M = [2020,7]
CAL_ExpDate_List = []
CAL_ExpDate_Color = []
CAL_ExpDate_Label = []
TK_NOW_CAL_M = tk.StringVar()
TK_NOW_CAL_M.set("%d年%02d月份" %(CAL_CURRENT_M[0], CAL_CURRENT_M[1]))

EXPTABLE_SQL_DATA_SUM = 0
EXPTABLE_SQL_DATA_PAGE = 1
EXPTABLE_SQL_DATA_RESULT = []
EXPTABLE_SQL_DATA_MAXITEM = 15
EXPTABLE_SQL_Query = "SELECT * FROM \"VIEW_TBI_ExpDetail_Data\" WHERE 1"
EXPTABLE_Data_Label = []
EXPTABLE_Filter_BT = []
EXPTABLE_Route_BT = []
EXPTABLE_SEARCH_BT = ""
EXPTABLE_PAGE_L_BT = ""
EXPTABLE_PAGE_R_BT = ""
EXPTABLE_PAGE_TOTAL = tk.StringVar()
EXPTABLE_PAGE_STATE = tk.StringVar()
EXPTABLE_SORT_BY = [-1, False]
EXPTABLE_SortData_BT = []
ExpDataTB_L_State = False
ExpDataTB_R_State = False

def BT_None():
	pass

def WriteConsoleMsg(level, msg):
	global CONSOLE_FLAG, CONSOLE_COLOR, CONSOLE_MSG, TK_Console_Line
	CONSOLE_MSG[CONSOLE_FLAG][0] = CONSOLE_COLOR[level]
	CONSOLE_MSG[CONSOLE_FLAG][1] = "[%s] %s" %(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ,msg)
	MsgID = CONSOLE_FLAG
	CONSOLE_FLAG = CONSOLE_MSG[CONSOLE_FLAG][3]
	for i in range(len(TK_Console_Line)):
		TK_Console_Line[3-i].config(text=CONSOLE_MSG[MsgID][1], fg=CONSOLE_MSG[MsgID][0])
		MsgID = CONSOLE_MSG[MsgID][2]

def SystemInit():
	global TBI_QUANTITY_DATA, TBI_QUANTITY_Group_TOTAL, TBI_QUANTITY_TP_TOTAL, TBI_QUANTITY_TOTAL_TOTAL
	global CAL_DATE_NUM#, CAL_ExpDate_Label
	global EXPTABLE_Data_Label, EXPTABLE_Filter_BT, EXPTABLE_Route_BT, EXPTABLE_SortData_BT
	
	TBI_QUANTITY_DATA = []
	TBI_QUANTITY_Group_TOTAL = []
	TBI_QUANTITY_TP_TOTAL = []
	TBI_QUANTITY_TOTAL_TOTAL = tk.IntVar()
	for i in range(4):
		data = []
		TBI_QUANTITY_Group_TOTAL.append(tk.IntVar())
		for j in range(7):
			if i == 0:
				TBI_QUANTITY_TP_TOTAL.append(tk.IntVar())
			data.append(tk.IntVar())
		TBI_QUANTITY_DATA.append(data)

	CAL_DATE_NUM = []
	CAL_ExpDate_List = []
	CAL_ExpDate_Color = []
	defaultColor = "gray85"
	for i in range(5):
		data = []
		data1 = []
		data2 = []
		for j in range(5):
			data.append(tk.StringVar())
			# data1.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])
			# data2.append([defaultColor, defaultColor, defaultColor])
			data2.append(["", "", ""])
		CAL_DATE_NUM.append(data)
		# CAL_ExpDate_List.append(data1)
		#CAL_ExpDate_Label.append(data2)
	
	EXPTABLE_Data_Label = []
	EXPTABLE_Filter_BT = []
	EXPTABLE_Route_BT = []
	EXPTABLE_SortData_BT = ["", "", "", "", "", "", "", "", ""]
	for i in range(15):
		EXPTABLE_Data_Label.append(["", "", "", "", "", "", ""])
		EXPTABLE_Filter_BT.append("")
		EXPTABLE_Route_BT.append("")


def writeData2CSV(fileName, type_, dataRow): #寫入CSV檔
	with open(fileName, type_, newline='') as csvfile:
		# 建立 CSV 檔寫入器
		writer = csv.writer(csvfile)

		# 寫入一列資料
		writer.writerow(dataRow) 

def readCSV2List(fileName): #讀取CSV檔
	AllData = []
	with open(fileName, newline='') as csvfile:
	  # 以冒號分隔欄位，讀取檔案內容
	  rows = csv.reader(csvfile, delimiter=',')

	  for row in rows:
	    AllData.append(row)

	return AllData

def string2Second(string):
	newStr1 = string.split(":")
	return int(newStr1[0])*3600 + int(newStr1[1])*60 + int(newStr1[2])

def string2RouteList(string):
	newStr1 = string.split("[")
	newStr2 = newStr1[1].split("]")
	newStr3 = newStr2[0].split(", ")
	newArr = []
	for row in newStr3:
		newArr.append((len(newArr), int(row)))
	return newArr

def SQL_SaveExpDate(exp_no, exp_date, model, timepoint, PathState): #儲存實驗日期
	global SQL_CONN
	sql_query = "SELECT \"ExpNo\" FROM \"exp_date\" WHERE \"ExpNo\" = \"%s\"" %(exp_no)
	cursor = SQL_CONN.execute(sql_query)
	result = cursor.fetchone()
	if type(result) == type(None):
		sql_query = "INSERT INTO \"exp_date\"(\"ExpNo\", \"ExpDate\", \"Model\", \"Timepoint\", \"PathState\")VALUES(\"%s\",\"%s\",\"%s\",\"%s\",%d)" %(exp_no, exp_date, model, timepoint, PathState)
		# print(sql_query)
		try:
			SQL_CONN.execute(sql_query)
			SQL_CONN.commit()
		except:
			return -1 #新增時有問題
	else:
		return 0 #資料庫內已有這筆資料
	return 1 #新增沒問題

def findSameIdDiffGroup(model, groups, Serial_data_id):
	#Group ID 轉換
	sql_query = "SELECT \"group_id\" FROM \"model_group\" WHERE \"model\" = \"%s\" AND \"groups\" = \"%s\"" %(model, groups)
	cursor = SQL_CONN.execute(sql_query)
	newGroup = cursor.fetchone()
	# print(newGroup[0])

	sql_query = "SELECT \"groups\", \"serial_data_id\" FROM \"exp_detail\" WHERE \"serial_data_id\" LIKE \"{0}%\" ORDER BY \"serial_data_id\"".format(Serial_data_id)
	cursor = SQL_CONN.execute(sql_query)
	result = cursor.fetchall()
	# print(sql_query)
	# print(result)

	count = 0
	nowDataId = ""
	for row in result:
		if newGroup[0] == row[0]:
			print("組別相同")
			sql_query = "DELETE FROM \"exp_route\" WHERE \"serial_data_id\" = \"%s\"" %(row[1])
			SQL_CONN.execute(sql_query)
			SQL_CONN.commit()
			sql_query = "DELETE FROM \"exp_detail\" WHERE \"serial_data_id\" = \"%s\"" %(row[1])
			# print(sql_query)
			try:
				SQL_CONN.execute(sql_query)
				SQL_CONN.commit()
				WriteConsoleMsg("NOTICE", "刪除同組別同大鼠編號資料(資料編號：%s)" %(row[1]))
				return [None, Serial_data_id]
			except:
				return [-1, Serial_data_id]
		else:
			count = count + 1
	
	return [None, "%s_%d" %(Serial_data_id, count)]

def SQL_SaveExpDetail(exp_date_id, groups, rat_id, shortTerm, longTerm, latency, route_list): #儲存實驗日之各大鼠資料
	global SQL_CONN
	str1 = exp_date_id.split("-")
	Serial_data_id = "%s_%s" %(exp_date_id, str(rat_id))
	# 新增大鼠詳細資料
	sql_query = "SELECT \"serial_data_id\", \"groups\" FROM \"exp_detail\" WHERE \"serial_data_id\" = \"%s\"" %(Serial_data_id)
	cursor = SQL_CONN.execute(sql_query)
	result = cursor.fetchone()
	if type(result) != type(None):
		result, Serial_data_id = findSameIdDiffGroup(str1[1], groups, Serial_data_id)
		if result == -1:
			return [-1, 0] #新增時有問題
	if type(result) == type(None):
		sql_query = "SELECT \"group_id\" FROM \"model_group\" WHERE \"model\" = \"%s\" AND \"groups\" = \"%s\"" %(str1[1],groups)
		cursor = SQL_CONN.execute(sql_query)
		newGroup = cursor.fetchone()
		# print(groups)
		sql_query = "INSERT INTO \"exp_detail\"(\"serial_data_id\",\"exp_date_id\", \"groups\", \"rat_id\", \"short_term\", \"long_term\", \"latency\")\
		 VALUES(\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d)" %(Serial_data_id, exp_date_id, newGroup[0], rat_id, shortTerm, longTerm, latency)
		# print(sql_query)
		try:
			SQL_CONN.execute(sql_query)
			SQL_CONN.commit()
		except:
			print("有問題!!")
			return [-1, 0] #新增時有問題
	else:
		return [0, 0] #資料庫內已有這筆資料
	# 新增大鼠路徑資料
	for row in route_list:
		sql_query = "SELECT * FROM \"exp_route\" WHERE \"serial_data_id\" = \"%s\" AND \"route_no\" = %d AND \"arm_no\" = %d" %(Serial_data_id, row[0], row[1])
		cursor = SQL_CONN.execute(sql_query)
		result = cursor.fetchone()
		if type(result) == type(None):
			sql_query = "INSERT INTO \"exp_route\"(\"serial_data_id\",\"route_no\", \"arm_no\") VALUES(\"%s\",%d,%d)" %(Serial_data_id, row[0], row[1])
			# print(sql_query)
			try:
				SQL_CONN.execute(sql_query)
				SQL_CONN.commit()
			except:
				return [-2, row[0]+1] #新增時有問題
		else:
			return [0, row[0]+1] #資料庫內已有這筆資料
	return [1, 0]

def InsertExpData2DB(exp_date, model, timepoint, csv_filepath, csv_filename, PathState, command=""): #儲存到DB的開頭
	csv_filefullname = csv_filepath + csv_filename
	csv_original_data = readCSV2List(csv_filefullname)

	sql_query = "SELECT \"timepoints\" FROM \"exp_timepoint\" WHERE \"tp_no\" = \"%s\"" %(timepoint)
	cursor = SQL_CONN.execute(sql_query)
	newTimepoint = cursor.fetchone()

	exp_date = exp_date.split("/")
	if command != "":
		exp_date_no = "%04d%02d%02d-%s-%s_%s" %(int(exp_date[0]), int(exp_date[1]), int(exp_date[2]), model[:5].upper(), newTimepoint[0], command)
	else:
		exp_date_no = "%04d%02d%02d-%s-%s" %(int(exp_date[0]), int(exp_date[1]), int(exp_date[2]), model[:5].upper(), newTimepoint[0])
	exp_date_date = "%04d/%02d/%02d" %(int(exp_date[0]), int(exp_date[1]), int(exp_date[2]))
	saveResult = SQL_SaveExpDate(exp_date_no, exp_date_date, model, timepoint, PathState)
	if saveResult != 1:
		if saveResult == -1:
			WriteConsoleMsg("ERROR", "%s 在新增至資料庫時有問題 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, model, exp_date_date, newTimepoint[0]))
		elif saveResult == 0:
			WriteConsoleMsg("NOTICE", "%s 已新增至資料庫 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, model, exp_date_date, newTimepoint[0]))
		WriteConsoleMsg("ERROR", "%s 新增至資料庫失敗! 成功 0 筆, 失敗 %d 筆, 共 %d 筆 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, len(csv_original_data[1:]), len(csv_original_data[1:]), model, exp_date_date, newTimepoint[0]))
		return -1
	count = 0
	for row in csv_original_data[1:]:
		ratGroup, ratId, longTerm, shortTerm, Latency = row[0], row[1], int(row[3]), int(row[4]), row[6]
		if timepoint == "pre":
			ratGroup = "Sham"
		elif timepoint != "pre" and (model == "TBI" and ratGroup == "Sham"):
			ratGroup = "Sham+NS"
		elif (model == "TBI" and ratGroup == "sham+NS"):
			ratGroup = "Sham+NS"
		elif (model == "TBI" and ratGroup == "sham+MSC"):
			ratGroup = "Sham+MSC"
		elif (model == "TBI" and ratGroup == "TBI+NS") or (model == "TBI" and ratGroup == "Control"):
			ratGroup = "rTBI+NS"
		elif (model == "TBI" and ratGroup == "TBI+MSC"):
			ratGroup = "rTBI+MSC" 
		Latency = string2Second(row[6])
		# print(ratGroup, ratId, longTerm, shortTerm, Latency)
		route = string2RouteList(row[5])
		saveResult1 = SQL_SaveExpDetail(exp_date_no, ratGroup, ratId, shortTerm, longTerm, Latency, route)
		if saveResult1[0] != 1 and saveResult1[1] != 0:
			if saveResult1[0] == -1:
				WriteConsoleMsg("ERROR", "%s 在新增編號 %s 大鼠資料至資料庫時有問題 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, str(ratId), model, exp_date_date, newTimepoint[0]))
			elif saveResult1[0] == -2:
				WriteConsoleMsg("ERROR", "%s 在新增編號 %s 大鼠資料之進臂順序編號%d有問題 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, str(ratId), saveResult1[1], model, exp_date_date, newTimepoint[0]))
			elif saveResult1[0] == 0:
				WriteConsoleMsg("NOTICE", "%s 在新增編號 %s 大鼠資料已新增至資料庫 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, str(ratId), model, exp_date_date, newTimepoint[0]))
			WriteConsoleMsg("ERROR", "%s 新增至資料庫失敗! 成功 %d 筆, 失敗 %d 筆, 共 %d 筆 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, count, len(csv_original_data[1:]) - count, len(csv_original_data[1:]), model, exp_date_date, newTimepoint[0]))
			return -1
		count = count + 1
	WriteConsoleMsg("GOOD", "%s 新增至資料庫成功! 成功 %d 筆, 失敗 0 筆, 共 %d 筆 (%s 實驗日期：%s 時間點：%s)" %(csv_filename, len(csv_original_data[1:]), len(csv_original_data[1:]), model, exp_date_date, newTimepoint[0]))
	return 1

def LoadCSV_WindowsClosing():
	global LoadCSV, WIN_CLOSE_LoadCSV
	LoadCSV.destroy()
	WIN_CLOSE_LoadCSV = False

def FilterData_WindowsClosing():
	global FilterData, WIN_CLOSE_FilterData
	FilterData.destroy()
	WIN_CLOSE_FilterData = False

def Main_WindowsClosing():
	global tkWin
	global LoadCSV, WIN_CLOSE_LoadCSV
	global FilterData, WIN_CLOSE_FilterData

	tkWin.destroy()
	if WIN_CLOSE_LoadCSV:
		LoadCSV.destroy()
	if WIN_CLOSE_FilterData:
		FilterData.destroy()

def changeHavePath():
	global LOAD_EXP_HAVE_PATH, TK_BT_EXP_HAVE_PATH

	if LOAD_EXP_HAVE_PATH:
		TK_BT_EXP_HAVE_PATH.config(text="無路徑資料", bg="salmon")
		LOAD_EXP_HAVE_PATH = False
	else:
		TK_BT_EXP_HAVE_PATH.config(text="有路徑資料", bg="PaleGreen")
		LOAD_EXP_HAVE_PATH = True

def LoadCSV_ExperimentData():
	global LoadCSV, WIN_CLOSE_LoadCSV, ExpData_CSV_Confirm
	global LOAD_EXP_DATE, LOAD_EXP_MODEL, LOAD_EXP_TIMEPOINT, LOAD_CSV_NAME, LOAD_CSV_PATH, LOAD_CSV_FULL_NAME, LOAD_EXP_TIMEPOINT_ID, LOAD_EXP_MODEL_ID
	global TKE_Command, LOAD_EXP_HAVE_PATH, TK_BT_EXP_HAVE_PATH
	global IS_SET_ExpData_File, TK_BT_SetExpCSV

	if not WIN_CLOSE_LoadCSV:

		def ExpData_Check():
			global LOAD_EXP_DATE, LOAD_PATH_DIR, LOAD_EXP_MODEL, LOAD_EXP_TIMEPOINT, LOAD_CSV_NAME, LOAD_CSV_PATH, LOAD_CSV_FULL_NAME, LOAD_EXP_TIMEPOINT_ID, LOAD_EXP_MODEL_ID
			global TKE_Command, LOAD_EXP_HAVE_PATH, TK_BT_EXP_HAVE_PATH
			global IS_SET_ExpData_File, TK_BT_SetExpCSV

			expDate = cal.get()
			sp_expdate = expDate.split("/")
			if len(sp_expdate[0]) == 4:
				newExpDate = "%04d/%02d/%02d" %(int(sp_expdate[0]), int(sp_expdate[1]), int(sp_expdate[2]))
			elif len(sp_expdate[2]) == 4:
				newExpDate = "%04d/%02d/%02d" %(int(sp_expdate[2]), int(sp_expdate[0]), int(sp_expdate[2]))
			else:
				newExpDate = "20%02d/%02d/%02d" %(int(sp_expdate[2]), int(sp_expdate[0]), int(sp_expdate[1]))
			if TimepointCombo.current() != 0:
				InfoMsg = ""
				InfoMsg = InfoMsg + "實驗日期：%s\n" %(newExpDate)
				InfoMsg = InfoMsg + "疾病模型：%s\n" %(ModelCombo.get())
				InfoMsg = InfoMsg + "時間點：%s\n" %(TimepointCombo.get())
				InfoMsg = InfoMsg + "備註文字：%s\n" %(TKE_Command.get())
				InfoMsg = InfoMsg + "是否有路徑資料：%s\n" %(LOAD_EXP_HAVE_PATH)
				InfoMsg = InfoMsg + "檔案名稱：%s" %(LOAD_CSV_NAME.get())
				
				covertTimepoint = ['pre', '00M07D', '00M14D', '00M28D', '03M00D', '06M00D', '09M00D']
				LOAD_EXP_DATE = newExpDate
				LOAD_EXP_TIMEPOINT_ID = TimepointCombo.current()
				LOAD_EXP_MODEL_ID = ModelCombo.current()
				LOAD_EXP_MODEL = ModelCombo.get()
				LOAD_EXP_TIMEPOINT = covertTimepoint[TimepointCombo.current()-1]
				LOAD_CSV_FULL_NAME = LOAD_CSV_PATH + LOAD_CSV_NAME.get()
				Command_Label = TKE_Command.get()
				LoadCSV_WindowsClosing()
				ExpData_CSV_Confirm = tk.messagebox.askokcancel(title='確認匯入資訊', message=InfoMsg)
				if ExpData_CSV_Confirm:
					InsertExpData2DB(LOAD_EXP_DATE, LOAD_EXP_MODEL, LOAD_EXP_TIMEPOINT, LOAD_CSV_PATH, LOAD_CSV_NAME.get(), int(LOAD_EXP_HAVE_PATH), Command_Label)
					LOAD_PATH_DIR.set("")
					LOAD_CSV_NAME.set("")
					LOAD_CSV_PATH = ""
					LOAD_EXP_DATE = ""
					LOAD_EXP_MODEL = ""
					LOAD_EXP_MODEL_ID = -1
					LOAD_EXP_TIMEPOINT = ""
					LOAD_EXP_TIMEPOINT_ID = -1
					TK_BT_SetExpCSV.config(text="選擇檔案", fg="black")
					LOAD_CSV_PATH = ""
					LOAD_CSV_NAME.set("")
					IS_SET_ExpData_File = False
				else:
					pass
			else:
				# print("尚未寫時間點")
				LoadCSV_WindowsClosing()
				tk.messagebox.showerror(title='錯誤!!', message="尚未寫時間點")

		WIN_CLOSE_LoadCSV = True
		LoadCSV = tk.Tk()
		LoadCSV.title("匯入CSV實驗數據") #窗口名字
		LoadCSV.geometry('%dx%d' %(300, 300)) #窗口大小(寬X高+X偏移量+Y偏移量)
		LoadCSV.resizable(False, False) #禁止變更視窗大小

		L1Y = 10
		tk.Label(LoadCSV, text="實驗日期", font=('微軟正黑體', 12)).place(x=10,y=L1Y,anchor="nw")
		if LOAD_EXP_DATE != "":
			splitCal = LOAD_EXP_DATE.split("/")
			cal = DateEntry(LoadCSV, width=10, background='gray', dateformat=4,
				year=int(splitCal[0]), month=int(splitCal[1]), day=int(splitCal[2]),
				font=('微軟正黑體', 10, "bold"), foreground='white', borderwidth=2
			)
		else:
			cal = DateEntry(LoadCSV, width=10, background='gray', dateformat=4, font=('微軟正黑體', 10, "bold"), foreground='white', borderwidth=2)
		cal.place(x=85,y=L1Y+2,anchor="nw")

		L2Y = 40
		ModelList = ['請選擇...', 'TBI', 'Radiation']
		tk.Label(LoadCSV, text="疾病模型", font=('微軟正黑體', 12)).place(x=10,y=L2Y,anchor="nw")
		ModelCombo = ttk.Combobox(LoadCSV, width=12, values=ModelList, font=('微軟正黑體', 10, "bold"), state="readonly")
		ModelCombo.place(x=85,y=L2Y+2,anchor="nw")
		if LOAD_EXP_MODEL_ID != -1:
			ModelCombo.current(LOAD_EXP_MODEL_ID)
		else:
			ModelCombo.current(0)

		L3Y = 70
		TimepointList = ['請選擇...', '手術前', '手術後7天', '手術後14天', '手術後28天', '手術後3個月', '手術後6個月', '手術後9個月']
		tk.Label(LoadCSV, text="時間點", font=('微軟正黑體', 12)).place(x=10,y=L3Y,anchor="nw")
		TimepointCombo = ttk.Combobox(LoadCSV, width=12, values=TimepointList, font=('微軟正黑體', 10, "bold"), state="readonly")
		TimepointCombo.place(x=85,y=L3Y+2,anchor="nw")
		if LOAD_EXP_TIMEPOINT_ID != -1:
			TimepointCombo.current(LOAD_EXP_TIMEPOINT_ID)
		else:
			TimepointCombo.current(0)
		
		L5Y = 100
		tk.Label(LoadCSV, text="使用者/備註", font=('微軟正黑體', 12)).place(x=10,y=L5Y,anchor="nw")
		TKE_Command = tk.Entry(LoadCSV, font=('微軟正黑體', 12), width=20)
		TKE_Command.place(x=105,y=L5Y,anchor="nw")

		L6Y = 130
		tk.Label(LoadCSV, text="是否有路徑資料", font=('微軟正黑體', 12)).place(x=10,y=L6Y,anchor="nw")
		if LOAD_EXP_HAVE_PATH:
			TK_BT_EXP_HAVE_PATH = tk.Button(LoadCSV, text="有路徑資料", font=('微軟正黑體', 10), bg="PaleGreen", command=changeHavePath)
		else:
			TK_BT_EXP_HAVE_PATH = tk.Button(LoadCSV, text="無路徑資料", font=('微軟正黑體', 10), bg="salmon", command=changeHavePath)
		TK_BT_EXP_HAVE_PATH.place(x=130,y=L6Y,anchor="nw")

		L4Y = 160
		tk.Label(LoadCSV, text="檔案名稱", font=('微軟正黑體', 12)).place(x=10,y=L4Y,anchor="nw")
		tk.Label(LoadCSV, text=LOAD_CSV_NAME.get(), font=('微軟正黑體', 11)).place(x=85,y=L4Y,anchor="nw")
		tk.Label(LoadCSV, text="檔案路徑", font=('微軟正黑體', 12)).place(x=10,y=L4Y+30,anchor="nw")
		tk.Label(LoadCSV, text=LOAD_CSV_PATH, #bg="yellow",
			font=('微軟正黑體', 10), width=34, height=3, 
			anchor='nw', justify='left', wraplength = 270
		).place(x=10,y=L4Y+52,anchor="nw")

		tk.Button(LoadCSV, text="確定匯入", font=('微軟正黑體', 10), command=ExpData_Check).place(x=150,y=265,anchor="n")
		LoadCSV.protocol("WM_DELETE_WINDOW", LoadCSV_WindowsClosing)
		LoadCSV.mainloop()

def chooseLoadPath_PathData(): #匯入實驗軌跡CSV路徑
	global TK_BT_SetPathData, IS_SET_PathData_Path, LOAD_PATH_DIR
	global LOAD_EXP_DATE, LOAD_EXP_MODEL, LOAD_EXP_TIMEPOINT, LOAD_CSV_NAME, LOAD_CSV_PATH, LOAD_EXP_TIMEPOINT_ID, LOAD_EXP_MODEL_ID
	
	if not IS_SET_PathData_Path:
		Path_FilePath = filedialog.askdirectory(initialdir = "./", title = "選擇路徑")
		LOAD_PATH_DIR.set(Path_FilePath)
		TK_BT_SetPathData.config(text="清除路徑", fg="red")
		IS_SET_PathData_Path = True
	else:
		TK_BT_SetPathData.config(text="選擇路徑", fg="black")
		IS_SET_PathData_Path = False
		LOAD_PATH_DIR.set("")
		LOAD_CSV_NAME.set("")
		LOAD_CSV_PATH = ""
		LOAD_EXP_DATE = ""
		LOAD_EXP_MODEL = ""
		LOAD_EXP_MODEL_ID = -1
		LOAD_EXP_TIMEPOINT = ""
		LOAD_EXP_TIMEPOINT_ID = -1

def chooseLoadFile_ExpData(): #匯入要寫入的實驗數據CSV路徑
	global LOAD_CSV_NAME, LOAD_CSV_PATH, IS_SET_ExpData_File, TK_BT_SetExpCSV
	if not IS_SET_ExpData_File:
		CSV_FileName = filedialog.askopenfilename(
			initialdir = "./", title = "選擇檔案",
			filetypes = (("CSV files","*.csv"),("all files","*.*"))
		)
		try:
			newFileName = CSV_FileName.split("/")
			newFilePath = CSV_FileName.split(newFileName[len(newFileName)-1])
			LOAD_CSV_PATH = newFilePath[0]
			LOAD_CSV_NAME.set(newFileName[len(newFileName)-1])
			TK_BT_SetExpCSV.config(text="清除檔案", fg="red")
			IS_SET_ExpData_File = True
			WriteConsoleMsg("INFO", "已選擇欲匯入的實驗數據檔：%s (路徑：%s)" %(newFileName[len(newFileName)-1], newFilePath[0]))
		except:
			WriteConsoleMsg("NOTICE", "已取消選擇欲匯入的實驗數據檔")
	else:
		TK_BT_SetExpCSV.config(text="選擇檔案", fg="black")
		LOAD_CSV_PATH = ""
		LOAD_CSV_NAME.set("")
		IS_SET_ExpData_File = False

def LoopMain(): #GUI介面迴圈
	global NOW_TIME, tkWin, TBI_QUANTITY_DATA_TYPE, TIMES_COUNT
	global LOAD_CSV_NAME, LOAD_CSV_PATH, TK_BT_LoadExpCSV
	global TBI_QUANTITY_DATA, TBI_QUANTITY_Group_TOTAL, TBI_QUANTITY_TP_TOTAL
	global CAL_CURRENT_M
	global ExpDataTB_L_State, ExpDataTB_R_State
	global EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM
	global WIN_CLOSE_FilterData, Filter_DateYearCombo, Filter_DateMonthCombo, Filter_DateDayCombo

	if LOAD_CSV_PATH != "" and LOAD_CSV_NAME.get() != "":
		TK_BT_LoadExpCSV.config(state="normal")
	else:
		TK_BT_LoadExpCSV.config(state="disabled")
	if TIMES_COUNT % 50 == 0:
		updateTBI_Quantity(TBI_QUANTITY_DATA_TYPE)
		updateTBI_ExpDateCal(CAL_CURRENT_M)
		updateTBI_ExpDataTable(EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM)
		TIMES_COUNT = 1
	else:
		TIMES_COUNT = TIMES_COUNT + 1
	FilterData_DateDay = ["不指定",
		"1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
		"11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
		"21", "22", "23", "24", "25", "26", "27", "28"
	]
	FilterDayCombo_Val = [3, 0, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3]
	if WIN_CLOSE_FilterData:
		if Filter_DateYearCombo.current() != 0:
			Filter_DateMonthCombo.config(state="readonly")
			if Filter_DateYearCombo.current()%4 == 0:
				FilterDayCombo_Val[1] = 1
		else:
			Filter_DateMonthCombo.config(state="disabled")
			Filter_DateMonthCombo.current(0)
			Filter_DateDayCombo.config(state="disabled")
			Filter_DateDayCombo.current(0)
		if Filter_DateMonthCombo.current() != 0:
			for i in range(29,29+FilterDayCombo_Val[Filter_DateMonthCombo.current()-1]):
				FilterData_DateDay.append(str(i))
			Filter_DateDayCombo.config(
				state="readonly",
				values=FilterData_DateDay
			)
		else:
			Filter_DateDayCombo.config(state="disabled")
			Filter_DateDayCombo.current(0)

	tkWin.after(10,LoopMain)

def ExpDataDetailSetFilter(ExpDate_detail_ID, nowFilter):
	global SQL_CONN
	global EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM
	newFilter = {0:1, 1:0}
	sql_query = "UPDATE \"exp_detail\" SET \"isFilter\" = %d WHERE \"serial_data_id\" = \"%s\"" %(newFilter[nowFilter], ExpDate_detail_ID)
	try:
		SQL_CONN.execute(sql_query)
		SQL_CONN.commit()
		updateTBI_ExpDataTable(EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM)
	except:
		WriteConsoleMsg("NOTICE", "變更 實驗編號%s 採用狀態時發生問題" %(ExpDate_detail_ID))

def updateTBI_ExpDataTable(sql_query, data_page, max_item):
	global EXPTABLE_Data_Label, EXPTABLE_Filter_BT, EXPTABLE_Route_BT, EXPTABLE_SQL_DATA_MAXITEM
	global EXPTABLE_PAGE_L_BT, EXPTABLE_PAGE_R_BT, EXPTABLE_SEARCH_BT, EXPTABLE_PAGE_TOTAL, EXPTABLE_PAGE_STATE
	global EXPTABLE_SQL_DATA_SUM, ExpDataTB_L_State, ExpDataTB_R_State, EXPTABLE_SQL_DATA_RESULT, EXPTABLE_SORT_BY

	BT_Filter_Text = {-1:"", 1:"YES", 0:"NO"}
	BT_Filter_Color = {-1:"gray80", 1:"PaleGreen", 0:"salmon"}

	for i in range(EXPTABLE_SQL_DATA_MAXITEM):
		for j in range(1,8):
			EXPTABLE_Data_Label[i][j-1].config(text="")
		EXPTABLE_Filter_BT[i].config(text=BT_Filter_Text[-1], bg=BT_Filter_Color[-1])
		EXPTABLE_Route_BT[i].config(text=BT_Filter_Text[-1], bg=BT_Filter_Color[-1])
	
	EXPTABLE_SQL_DATA_SUM, ExpDataTB_L_State, ExpDataTB_R_State, EXPTABLE_SQL_DATA_RESULT = SQLDataQuery2Table(sql_query, data_page, max_item, EXPTABLE_SORT_BY)
	
	BT_State = {True:"normal", False:"disabled"}
	EXPTABLE_PAGE_L_BT.config(state=BT_State[ExpDataTB_L_State])
	EXPTABLE_PAGE_R_BT.config(state=BT_State[ExpDataTB_R_State])
	EXPTABLE_PAGE_TOTAL.set("共%d筆" %(EXPTABLE_SQL_DATA_SUM))
	EXPTABLE_PAGE_STATE.set("第%d頁/共%d頁" %(data_page, math.ceil(EXPTABLE_SQL_DATA_SUM/EXPTABLE_SQL_DATA_MAXITEM)))

	for i in range(len(EXPTABLE_SQL_DATA_RESULT)):
		for j in range(1,len(EXPTABLE_SQL_DATA_RESULT[i])-2):
			EXPTABLE_Data_Label[i][j-1].config(text=EXPTABLE_SQL_DATA_RESULT[i][j])
		EXPTABLE_Filter_BT[i].config(
			text=BT_Filter_Text[EXPTABLE_SQL_DATA_RESULT[i][8]], 
			bg=BT_Filter_Color[EXPTABLE_SQL_DATA_RESULT[i][8]], 
			command=partial(ExpDataDetailSetFilter,EXPTABLE_SQL_DATA_RESULT[i][0], EXPTABLE_SQL_DATA_RESULT[i][8])
		)
		EXPTABLE_Route_BT[i].config(text="進臂次數%02d" %(EXPTABLE_SQL_DATA_RESULT[i][9]), bg="gray70")

def updateTBI_ExpDateCal(c_month):
	global CAL_DATE_NUM, CAL_ExpDate_Label

	# 相關參數重置
	defaultColor = "gray85"
	for i in [0, len(CAL_DATE_NUM)-1]:
		for j in range(len(CAL_DATE_NUM[i])):
			CAL_DATE_NUM[i][j].set("")
	for i in range(len(CAL_ExpDate_Label)):
		for j in range(len(CAL_ExpDate_Label[i])):
			CAL_ExpDate_Label[i][j][0].config(text="", bg=defaultColor)
			CAL_ExpDate_Label[i][j][1].config(text="", bg=defaultColor)
			CAL_ExpDate_Label[i][j][2].config(text="", bg=defaultColor)

	# 提取哪幾天有做實驗
	MonthExpList = []
	TP_Convert = {"pre": "Pre", "00M07D": "D07", "00M14D": "D14", "00M28D": "D28", "03M00D": "M03", "06M00D": "M06", "09M00D": "M09"}
	TP_Color0 = {
		"Pre": "OliveDrab", 
		"D07": "OliveDrab1", "D14": "OliveDrab2", "D28": "OliveDrab3", 
		"M03": "DarkOliveGreen1", "M06": "DarkOliveGreen2", "M09": "DarkOliveGreen3"
	}
	TP_Color1 = {
		"Pre": "SteelBlue", 
		"D07": "SkyBlue1", "D14": "SkyBlue2", "D28": "SkyBlue3", 
		"M03": "DeepSkyBlue1", "M06": "DeepSkyBlue2", "M09": "DeepSkyBlue3"
	}
	TP_Color2 = {
		"Pre": "Orchid4", 
		"D07": "MediumOrchid1", "D14": "MediumOrchid2", "D28": "MediumOrchid3", 
		"M03": "DarkOrchid1", "M06": "DarkOrchid2", "M09": "DarkOrchid3"
	}
	for i in range(31):
		MonthExpList.append([])
	sql_query = "SELECT \"ExpNo\",\"ExpDate\",\"Timepoint\",\"Total\",\"PathState\" FROM \"VIEW_Experiment_Overview_TBI\" WHERE \"ExpDate\" LIKE \"{0}/{1}/%\" ORDER BY \"ExpDate\", \"Timepoint\"".format(c_month[0],"%02d" %(c_month[1]))
	cursor = SQL_CONN.execute(sql_query)
	result = cursor.fetchall()
	# print(result)
	for row in result:
		thisDate = row[1].split("/")
		newColor = ""
		if row[4] == 0:
			newColor = TP_Color0[TP_Convert[row[2]]]
		elif row[4] == 1:
			newColor = TP_Color1[TP_Convert[row[2]]]
		elif row[4] == 2:
			newColor = TP_Color2[TP_Convert[row[2]]]
		MonthExpList[int(thisDate[2])-1].append([TP_Convert[row[2]], row[3], newColor])
	# print(MonthExpList)

	# 把日期加上去
	firstDay = datetime.datetime(c_month[0],c_month[1],1).weekday()
	maxDay = 28
	nowCountDay = 1
	nowWeekDay = firstDay
	if c_month[1] == 4 or c_month[1] == 6 or c_month[1] == 9 or c_month[1] == 11:
		maxDay = 30
	elif c_month[1] != 2:
		maxDay = 31
	elif c_month[1] == 2 and c_month[0] % 4 == 0:
		maxDay = 29
	if nowWeekDay > 4:
		nowCountDay = 1 + (7 - nowWeekDay)
		nowWeekDay = 0
	for i in range(5):
		for j in range(nowWeekDay, 5):
			if nowCountDay <= maxDay:
				CAL_DATE_NUM[i][j].set(str(nowCountDay))
				if len(MonthExpList[nowCountDay-1]) > 3:
					LabelCount = 3
				else:
					LabelCount = len(MonthExpList[nowCountDay-1])
				for k in range(LabelCount):
					CAL_ExpDate_Label[i][j][k].config(
						text = "%s(%d)" %(MonthExpList[nowCountDay-1][k][0], MonthExpList[nowCountDay-1][k][1]),
						bg = MonthExpList[nowCountDay-1][k][2]
					)
				nowCountDay = nowCountDay + 1
			else:
				break
		nowWeekDay = 0
		nowCountDay = nowCountDay + 2

def updateTBI_Quantity(Q_type): # Group: TBI+MSC, TBI+NS, Sham+MSC, Sham+NS
	global SQL_CONN
	global TBI_QUANTITY_DATA, TBI_QUANTITY_Group_TOTAL, TBI_QUANTITY_TP_TOTAL, TBI_QUANTITY_TOTAL_TOTAL

	# Quantity_item = []
	Quantity_item = [
		[0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0]
	]
	gp_Sum = 0
	tp_Sum = [0,0,0,0,0,0,0]
	total_sum = 0
	if Q_type == "All":
		sql_query = "SELECT \"Pre(Total)\",\"D7(Total)\",\"D14(Total)\",\"D28(Total)\",\"M3(Total)\",\"M6(Total)\",\"M9(Total)\" FROM \"VIEW_TBI_Model_Total_Quantity\" WHERE 1 ORDER BY \"groups\""
	elif Q_type == "Filter":
		sql_query = "SELECT \"Filter(Pre)\",\"Filter(D7)\",\"Filter(D14)\",\"Filter(D28)\",\"Filter(M3)\",\"Filter(M6)\",\"Filter(M9)\" FROM \"VIEW_TBI_Model_Total_Quantity\" WHERE 1 ORDER BY \"groups\""
	cursor = SQL_CONN.execute(sql_query)
	result = cursor.fetchall()
	if len(result) != 0:
		for i in range(0,len(result)-1):
			Quantity_item[i][0] = result[0][0]
			for j in range(1,len(result[i])):
				Quantity_item[i][j] = result[i+1][j]
		for i in range(len(TBI_QUANTITY_DATA)):
			gp_Sum = 0
			for j in range(len(TBI_QUANTITY_DATA[i])):
				TBI_QUANTITY_DATA[i][j].set(Quantity_item[3-i][j])
				if j > 0:
					total_sum = total_sum + TBI_QUANTITY_DATA[i][j].get()
					gp_Sum = gp_Sum + TBI_QUANTITY_DATA[i][j].get()
					tp_Sum[j] = tp_Sum[j] + TBI_QUANTITY_DATA[i][j].get()
					if i == len(TBI_QUANTITY_DATA)-1:
						TBI_QUANTITY_TP_TOTAL[j].set(tp_Sum[j])
			TBI_QUANTITY_TP_TOTAL[0].set(result[0][0])
			TBI_QUANTITY_DATA[0][0].set(result[0][0])
			TBI_QUANTITY_Group_TOTAL[i].set(gp_Sum)
			TBI_QUANTITY_TOTAL_TOTAL.set(total_sum + result[0][0])

def chooseQuantityType():
	global TK_BT_ShowQuantity, TBI_QUANTITY_DATA_TYPE
	if TBI_QUANTITY_DATA_TYPE == "All":
		TBI_QUANTITY_DATA_TYPE = "Filter"
		TK_BT_ShowQuantity.config(text=" TBI 各組篩選 ", bg="PaleGreen")
	elif TBI_QUANTITY_DATA_TYPE == "Filter":
		TBI_QUANTITY_DATA_TYPE = "All"
		TK_BT_ShowQuantity.config(text=" TBI 各組總數 ", bg="gray75")

def MoveUpDownDataTable(up_down):
	global ExpDataTB_L_State, ExpDataTB_R_State
	global EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_SUM, EXPTABLE_SQL_DATA_RESULT, EXPTABLE_SQL_DATA_MAXITEM

	PageBT = {"Up":-1, "Down":1}
	EXPTABLE_SQL_DATA_PAGE = EXPTABLE_SQL_DATA_PAGE + PageBT[up_down]
	updateTBI_ExpDataTable(EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM)

def MoveUpDownCal(up_down):
	global CAL_DATE_NUM, CAL_CURRENT_M, TK_NOW_CAL_M
	if up_down == "Up":
		if CAL_CURRENT_M[1] == 12:
			CAL_CURRENT_M[0] = CAL_CURRENT_M[0] + 1
			CAL_CURRENT_M[1] = 1
		else:
			CAL_CURRENT_M[1] = CAL_CURRENT_M[1] + 1
	elif up_down == "Down":
		if CAL_CURRENT_M[1] == 1:
			CAL_CURRENT_M[0] = CAL_CURRENT_M[0] - 1
			CAL_CURRENT_M[1] = 12
		else:
			CAL_CURRENT_M[1] = CAL_CURRENT_M[1] - 1
	TK_NOW_CAL_M.set("%d年%02d月份" %(CAL_CURRENT_M[0], CAL_CURRENT_M[1]))
	
	updateTBI_ExpDateCal(CAL_CURRENT_M)

def DeleteExpDate2DB(ExpDate_id):
	global SQL_CONN

	sql_query = "SELECT \"serial_data_id\" FROM \"exp_detail\" WHERE \"exp_date_id\" = \"%s\"" %(ExpDate_id)
	cursor = SQL_CONN.execute(sql_query)
	DetailID = cursor.fetchall()
	for row in DetailID:
		# sql_query = "SELECT * FROM \"exp_route\" WHERE \"serial_data_id\" = \"%s\"" %(row)
		# cursor = SQL_CONN.execute(sql_query)
		# DetailID_route = cursor.fetchall()
		sql_query = "DELETE FROM \"exp_route\" WHERE \"serial_data_id\" = \"%s\"" %(row)
		try:
			SQL_CONN.execute(sql_query)
			SQL_CONN.commit()
		except:
			WriteConsoleMsg("NOTICE", "刪除 實驗大鼠編號%s 資料時發生錯誤" %(row))
			return -1
	sql_query = "DELETE FROM \"exp_detail\" WHERE \"exp_date_id\" = \"%s\"" %(ExpDate_id)
	try:
		SQL_CONN.execute(sql_query)
		SQL_CONN.commit()
	except:
		WriteConsoleMsg("NOTICE", "刪除 實驗編號%s 時發生錯誤" %(ExpDate_id))
		return -1
	return 1	

def DeleteExpData():
	global SQL_CONN
	global DEL_TimepointCombo, DEL_Cal
	expDate = DEL_Cal.get()
	sp_expdate = expDate.split("/")
	if len(sp_expdate[0]) == 4:
		newExpDate = "%04d/%02d/%02d" %(int(sp_expdate[0]), int(sp_expdate[1]), int(sp_expdate[2]))
	elif len(sp_expdate[2]) == 4:
		newExpDate = "%04d/%02d/%02d" %(int(sp_expdate[2]), int(sp_expdate[0]), int(sp_expdate[2]))
	else:
		newExpDate = "20%02d/%02d/%02d" %(int(sp_expdate[2]), int(sp_expdate[0]), int(sp_expdate[1]))
	covertTP = {'手術前':"pre", '手術後7天':"00M07D", '手術後14天':"00M14D", '手術後28天':"00M28D", '手術後3個月':"03M00D", '手術後6個月':"06M00D", '手術後9個月':"09M00D"}
	backTP = {"pre":'手術前', "00M07D":'手術後7天', "00M14D":'手術後14天', "00M28D":'手術後28天', "03M00D":'手術後3個月', "06M00D":'手術後6個月', "09M00D":'手術後9個月'}
	nowTP = DEL_TimepointCombo.get()
	if DEL_TimepointCombo.current() != 0:
		sql_query = "SELECT \"ExpNo\", \"ExpDate\", \"Timepoint\", \"Total\" FROM \"VIEW_Experiment_Overview_TBI\" WHERE \"ExpDate\" = \"%s\" and \"Timepoint\" = \"%s\"" %(newExpDate, covertTP[nowTP])
		cursor = SQL_CONN.execute(sql_query)
		result = cursor.fetchall()
		if len(result) == 0:
			WriteConsoleMsg("NOTICE", "查無要刪除的實驗數據記錄!!(日期：%s 時間點：%s)" %(newExpDate, nowTP))
		else:
			InfoMsg = "本次搜尋到以下 %d 筆結果：\n\n" %(len(result))
			for row in result:
				InfoMsg = InfoMsg + "實驗編號：%s\n" %(row[0])
				InfoMsg = InfoMsg + "實驗日期：%s\n" %(row[1])
				InfoMsg = InfoMsg + "時間點：%s\n" %(backTP[row[2]])
				InfoMsg = InfoMsg + "實驗總數：%d\n" %(row[3])
			InfoMsg = InfoMsg + "\n確定全部刪除？"
			ExpData_DEL_Confirm = tk.messagebox.askokcancel(title='確認刪除資料', message=InfoMsg)
			if ExpData_DEL_Confirm:
				for row in result:
					delResult = DeleteExpDate2DB(row[0])
					if delResult == 1:
						sql_query = "DELETE FROM \"exp_date\" WHERE \"ExpNo\" = \"%s\"" %(row[0])
						try:
							SQL_CONN.execute(sql_query)
							SQL_CONN.commit()
						except:
							WriteConsoleMsg("NOTICE", "刪除 實驗編號%s '本身'時發生錯誤" %(row[0]))
						WriteConsoleMsg("GOOD", "刪除 實驗編號%s 資料成功!!" %(row[0]))
			else:
				pass
	else:
		WriteConsoleMsg("ERROR", "要刪除實驗數據時，請選擇\"時間點\"!!")

def SQLDataQuery2Table(query, page_num, total_item, SortBy): #SQL命令 第幾頁 一頁幾個
	global SQL_CONN

	canLeft = True #可上一頁
	canRight = True #可下一頁
	nowStart = (page_num-1)*total_item #目前資料指標
	nowItem = total_item #目前取得筆數
	resultTot = 0 #資料總數
	resultData = [] #查詢結果

	sortCol = ["ExpDate", "groups", "timepoints", "rat_id", "long_term", "short_term", "latency", "isFilter", "CountRoute"]
	sortSide = {False:"ASC", True:"DESC"}
	if SortBy[0] != -1:
		query = query + " ORDER BY \"%s\" %s" %(sortCol[SortBy[0]], sortSide[SortBy[1]])

	# SQL_Query = "SELECT * FROM \"VIEW_TBI_ExpDetail_Data\" WHERE 1"
	# 取得總共有多少筆資料
	# print(query)
	cursor = SQL_CONN.execute(query)
	result1 = cursor.fetchall()
	resultTot = len(result1)

	# 判斷是否可以上/下一頁
	if nowStart - total_item < 0:
		canLeft = False
	if nowStart + total_item > resultTot:
		canRight = False

	# 取得單頁資料
	if nowStart >= resultTot:
		return resultTot, canLeft, canRight, []
	else:
		if nowStart + total_item > resultTot:
			nowItem = resultTot - nowStart
		cursor = SQL_CONN.execute(query + " LIMIT %d,%d" %(nowStart, nowItem))
		result2 = cursor.fetchall()
		return resultTot, canLeft, canRight, result2

def setSortDataButton(sortBT_id):
	global EXPTABLE_SortData_BT, EXPTABLE_SORT_BY
	for i in range(len(EXPTABLE_SortData_BT)):
		EXPTABLE_SortData_BT[i].config(text="", bg="gray90")

	if EXPTABLE_SORT_BY[0] == -1:
		EXPTABLE_SORT_BY[0] = sortBT_id
		EXPTABLE_SORT_BY[1] = False
		EXPTABLE_SortData_BT[sortBT_id].config(text="▲升▲", bg="PaleGreen")
	elif (EXPTABLE_SORT_BY[0] == sortBT_id) and not EXPTABLE_SORT_BY[1]:
		EXPTABLE_SORT_BY[1] = True
		EXPTABLE_SortData_BT[sortBT_id].config(text="▼降▼", bg="salmon")
	elif (EXPTABLE_SORT_BY[0] == sortBT_id) and EXPTABLE_SORT_BY[1]:
		EXPTABLE_SORT_BY[0] = -1
		EXPTABLE_SORT_BY[1] = False
	elif (EXPTABLE_SORT_BY[0] != sortBT_id) and (sortBT_id != -1):
		EXPTABLE_SORT_BY[0] = sortBT_id
		EXPTABLE_SORT_BY[1] = False
		EXPTABLE_SortData_BT[sortBT_id].config(text="▲升▲", bg="PaleGreen")

def FilterData2DBData(FD_Date=None, FD_Group=None, FD_Timepoint=None, FD_LME=None, FD_SME=None, FD_Latency=None):
	global EXPTABLE_SQL_Query
	isHaveFilter = False
	EXPTABLE_SQL_Query = "SELECT * FROM \"VIEW_TBI_ExpDetail_Data\" WHERE"
	ExpDetail_Data_ColList = ['ExpDate', 'groups', 'timepoints', 'long_term', 'short_term', 'latency']
	if FD_Date != None:
		isHaveFilter = True
		if FD_Date[0] == "%" and FD_Date[1] == "%" and FD_Date[2] == "%":
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" = \"%s/%s/%s\"" %('ExpDate', FD_Date[0], FD_Date[1], FD_Date[2])
		else:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" LIKE \"%s/%s/%s\""  %('ExpDate', FD_Date[0], FD_Date[1], FD_Date[2])
	if FD_Group != None:
		if isHaveFilter:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " AND"
		else:
			isHaveFilter = True
		EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" = \"%s\""  %('groups', FD_Group)
	if FD_Timepoint != None:
		if isHaveFilter:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " AND"
		else:
			isHaveFilter = True
		EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" = \"%s\""  %('timepoints', FD_Timepoint)
	if FD_LME != None:
		if isHaveFilter:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " AND"
		else:
			isHaveFilter = True
		if FD_LME[0] != -1 and FD_LME[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" BETWEEN %d AND %d"  %('long_term', FD_LME[0], FD_LME[1])
		elif FD_LME[0] != -1 and FD_LME[1] == -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" > %d"  %('long_term', FD_LME[0])
		elif FD_LME[0] == -1 and FD_LME[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" < %d"  %('long_term', FD_LME[1])
	if FD_SME != None:
		if isHaveFilter:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " AND"
		else:
			isHaveFilter = True
		if FD_SME[0] != -1 and FD_SME[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" BETWEEN %d AND %d"  %('short_term', FD_SME[0], FD_SME[1])
		elif FD_SME[0] != -1 and FD_SME[1] == -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" > %d"  %('short_term', FD_SME[0])
		elif FD_SME[0] == -1 and FD_SME[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" < %d"  %('short_term', FD_SME[1])
	if FD_Latency != None:
		if isHaveFilter:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " AND"
		else:
			isHaveFilter = True
		if FD_Latency[0] != -1 and FD_Latency[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" BETWEEN %d AND %d"  %('latency', FD_Latency[0], FD_Latency[1])
		elif FD_Latency[0] != -1 and FD_Latency[1] == -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" > %d"  %('short_term', FD_Latency[0])
		elif FD_Latency[0] == -1 and FD_Latency[1] != -1:
			EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " \"%s\" < %d"  %('short_term', FD_Latency[1])
	if not isHaveFilter:
		EXPTABLE_SQL_Query = EXPTABLE_SQL_Query + " 1"
	WriteConsoleMsg("NOTICE", "SQL 查詢命令：%s" %(EXPTABLE_SQL_Query))

def FilterData_ExperimentForTBI():
	global FilterData, WIN_CLOSE_FilterData
	global Filter_DateYearCombo, Filter_DateMonthCombo, Filter_DateDayCombo
	global Filter_GroupCombo, Filter_TimepointCombo, Filter_LatencyLSpinbox, Filter_LatencyRSpinbox
	global Filter_LMELSpinbox, Filter_LMERSpinbox, Filter_SMELSpinbox, Filter_SMERSpinbox

	# now = datetime.datetime.now()
	if not WIN_CLOSE_FilterData:
		def TableData_Filter():
			global Filter_DateYearCombo, Filter_DateMonthCombo, Filter_DateDayCombo
			global Filter_GroupCombo, Filter_TimepointCombo, Filter_LatencyLSpinbox, Filter_LatencyRSpinbox
			global Filter_LMELSpinbox, Filter_LMERSpinbox, Filter_SMELSpinbox, Filter_SMERSpinbox

			Filter_Date = [Filter_DateYearCombo.get(), Filter_DateMonthCombo.get(), Filter_DateDayCombo.get()]
			Filter_Group = Filter_GroupCombo.get()
			Filter_Timepoint = Filter_TimepointCombo.get()
			Filter_LME = [Filter_LMELSpinbox.get(), Filter_LMERSpinbox.get()]
			Filter_SME = [Filter_SMELSpinbox.get(), Filter_SMERSpinbox.get()]
			Filter_Latency = [Filter_LatencyLSpinbox.get(), Filter_LatencyRSpinbox.get()]

			Filter_Text = "篩選結果"
			isHaveFilter = False
			if Filter_Date[0] != '不限定':
				isHaveFilter = True
				if Filter_Date[1] != '不限定' and Filter_Date[2] == '不限定':
					Filter_Text = Filter_Text + "\n●日期：%s年%s月份" %(Filter_Date[0], Filter_Date[1])
					FD_Date = [Filter_Date[0], Filter_Date[1], "%"]
				elif Filter_Date[1] != '不限定' and Filter_Date[2] != '不限定':
					Filter_Text = Filter_Text + "\n●日期：%s年%s月%s日" %(Filter_Date[0], Filter_Date[1], Filter_Date[2])
					FD_Date = [Filter_Date[0], Filter_Date[1], Filter_Date[2]]
				else:
					Filter_Text = Filter_Text + "\n●日期：%s年度" %(Filter_Date[0])
					FD_Date = [Filter_Date[0], "%", "%"]
			else:
				FD_Date = None

			if Filter_Group != '不限定':
				isHaveFilter = True
				Filter_Text = Filter_Text + "\n●組別：%s" %(Filter_Group)
				FD_Group = Filter_Group
			else:
				FD_Group = None

			if Filter_Timepoint != '不限定':
				isHaveFilter = True
				Filter_Text = Filter_Text + "\n●時間點：%s" %(Filter_Timepoint)
				FD_Timepoint = Filter_Timepoint
			else:
				FD_Timepoint = None

			if int(Filter_LME[0]) != -1 or int(Filter_LME[1]) != -1:
				isHaveFilter = True
				if int(Filter_LME[0]) != -1 and  int(Filter_LME[1]) == -1:
					Filter_Text = Filter_Text + "\n●長期記憶錯誤(LME)：大於%s次" %(int(Filter_LME[0]))
					FD_LME = [int(Filter_LME[0]), int(Filter_LME[1])]
				elif int(Filter_LME[0]) == -1 and  int(Filter_LME[1]) != -1:
					Filter_Text = Filter_Text + "\n●長期記憶錯誤(LME)：小於%s次" %(int(Filter_LME[1]))
					FD_LME = [int(Filter_LME[0]), int(Filter_LME[1])]
				elif int(Filter_LME[0]) != -1 and  int(Filter_LME[1]) != -1:
					if int(Filter_LME[0]) > int(Filter_LME[1]):
						Filter_Text = Filter_Text + "\n●長期記憶錯誤(LME)：介於%d~%d次" %(int(Filter_LME[1]), int(Filter_LME[0]))
						FD_LME = [int(Filter_LME[1]), int(Filter_LME[0])]
					else:
						Filter_Text = Filter_Text + "\n●長期記憶錯誤(LME)：介於%d~%d次" %(int(Filter_LME[0]), int(Filter_LME[1]))
						FD_LME = [int(Filter_LME[0]), int(Filter_LME[1])]
			else:
				FD_LME = None

			if int(Filter_SME[0]) != -1 or int(Filter_SME[1]) != -1:
				isHaveFilter = True
				if int(Filter_SME[0]) != -1 and  int(Filter_SME[1]) == -1:
					Filter_Text = Filter_Text + "\n●短期記憶錯誤(SME)：大於%s次" %(int(Filter_SME[0]))
					FD_SME = [int(Filter_SME[0]), int(Filter_SME[1])]
				elif int(Filter_SME[0]) == -1 and  int(Filter_SME[1]) != -1:
					Filter_Text = Filter_Text + "\n●短期記憶錯誤(SME)：小於%s次" %(int(Filter_SME[1]))
					FD_SME = [int(Filter_SME[0]), int(Filter_SME[1])]
				elif int(Filter_SME[0]) != -1 and  int(Filter_SME[1]) != -1:
					if int(Filter_SME[0]) > int(Filter_SME[1]):
						Filter_Text = Filter_Text + "\n●短期記憶錯誤(SME)：介於%d~%d次" %(int(Filter_SME[1]), int(Filter_SME[0]))
						FD_SME = [int(Filter_SME[1]), int(Filter_SME[0])]
					else:
						Filter_Text = Filter_Text + "\n●短期記憶錯誤(SME)：介於%d~%d次" %(int(Filter_SME[0]), int(Filter_SME[1]))
						FD_SME = [int(Filter_SME[0]), int(Filter_SME[1])]
			else:
				FD_SME = None

			if int(Filter_Latency[0]) != -1 or int(Filter_Latency[1]) != -1:
				isHaveFilter = True
				if int(Filter_Latency[0]) != -1 and  int(Filter_Latency[1]) == -1:
					Filter_Text = Filter_Text + "\n●實驗總時長：大於%s秒" %(int(Filter_Latency[0]))
					FD_Latency = [int(Filter_Latency[0]), int(Filter_Latency[1])]
				elif int(Filter_Latency[0]) == -1 and  int(Filter_Latency[1]) != -1:
					Filter_Text = Filter_Text + "\n●實驗總時長：小於%s秒" %(int(Filter_Latency[1]))
					FD_Latency = [int(Filter_Latency[0]), int(Filter_Latency[1])]
				elif int(Filter_Latency[0]) != -1 and  int(Filter_Latency[1]) != -1:
					if int(Filter_Latency[0]) > int(Filter_Latency[1]):
						Filter_Text = Filter_Text + "\n●實驗總時長：介於%d~%d秒" %(int(Filter_Latency[1]), int(Filter_Latency[0]))
						FD_Latency = [int(Filter_Latency[1]), int(Filter_Latency[0])]
					else:
						Filter_Text = Filter_Text + "\n●實驗總時長：介於%d~%d秒" %(int(Filter_Latency[0]), int(Filter_Latency[1]))
						FD_Latency = [int(Filter_Latency[0]), int(Filter_Latency[1])]
			else:
				FD_Latency = None
			if not isHaveFilter:
				Filter_Text = Filter_Text + "\n● 無 ●"
			FilterData_WindowsClosing()
			FilterData_CSV_Confirm = tk.messagebox.askokcancel(title='確認篩選資訊', message=Filter_Text)
			if FilterData_CSV_Confirm:
				FilterData2DBData(FD_Date, FD_Group, FD_Timepoint, FD_LME, FD_SME, FD_Latency)

		WIN_CLOSE_FilterData = True
		FilterData = tk.Tk()
		FilterData.title("篩選實驗數據資料") #窗口名字
		FilterData.geometry('%dx%d+10+10' %(350, 290)) #窗口大小(寬X高+X偏移量+Y偏移量)
		FilterData.resizable(False, False) #禁止變更視窗大小

		tk.Label(FilterData, text="請選擇以下欲查詢的條件", font=('微軟正黑體', 11, 'bold')).place(x=10,y=10,anchor="nw")
		
		L1Y = 35
		tk.Label(FilterData, text="●日期", font=('微軟正黑體', 11, 'bold')).place(x=10,y=L1Y,anchor="nw")
		FilterData_DateYear = ['不限定']
		for i in range(20,100):
			FilterData_DateYear.append("%d" %(2000 + i))
		Filter_DateYearCombo = ttk.Combobox(FilterData, width=5, values=FilterData_DateYear, font=('微軟正黑體', 10), state="readonly")
		Filter_DateYearCombo.place(x=70,y=L1Y+2,anchor="nw")
		Filter_DateYearCombo.current(0)
		tk.Label(FilterData, text="年", font=('微軟正黑體', 11)).place(x=133,y=L1Y,anchor="nw") #63
		FilterData_DateMonth = ['不限定']
		for i in range(12):
			FilterData_DateMonth.append(i+1)
		Filter_DateMonthCombo = ttk.Combobox(FilterData, width=5, values=FilterData_DateMonth, font=('微軟正黑體', 10), state="disabled")
		Filter_DateMonthCombo.place(x=155,y=L1Y+2,anchor="nw")
		Filter_DateMonthCombo.current(0)
		tk.Label(FilterData, text="月", font=('微軟正黑體', 11)).place(x=218,y=L1Y,anchor="nw") #63
		Filter_DateDayCombo = ttk.Combobox(FilterData, width=5, values=['不限定'], font=('微軟正黑體', 10), state="disabled")
		Filter_DateDayCombo.place(x=240,y=L1Y+2,anchor="nw")
		Filter_DateDayCombo.current(0)
		tk.Label(FilterData, text="日", font=('微軟正黑體', 11)).place(x=305,y=L1Y,anchor="nw") #63

		L2Y = 65
		tk.Label(FilterData, text="●組別", font=('微軟正黑體', 11, 'bold')).place(x=10,y=L2Y,anchor="nw")
		FilterData_Group = ['不限定', 'Sham', 'Sham+NS', 'Sham+MSC', 'rTBI+NS', 'rTBI+MSC']
		Filter_GroupCombo = ttk.Combobox(FilterData, width=10, values=FilterData_Group, font=('微軟正黑體', 10), state="readonly")
		Filter_GroupCombo.place(x=70,y=L2Y+2,anchor="nw")
		Filter_GroupCombo.current(0)

		L3X = 170
		L3Y = 65
		tk.Label(FilterData, text="●時間點", font=('微軟正黑體', 11, 'bold')).place(x=L3X+10,y=L3Y,anchor="nw")
		FilterData_Timepoint = ['不限定', 'Pre', 'D07', 'D14', 'D28', 'M03', 'M06', 'M09']
		Filter_TimepointCombo = ttk.Combobox(FilterData, width=5, values=FilterData_Timepoint, font=('微軟正黑體', 10), state="readonly")
		Filter_TimepointCombo.place(x=L3X+85,y=L3Y+2,anchor="nw")
		Filter_TimepointCombo.current(0)

		L4Y = 95
		tk.Label(FilterData, text="●長期記憶錯誤(LME) [-1為不限定]", font=('微軟正黑體', 11, 'bold')).place(x=10,y=L4Y,anchor="nw")
		tk.Label(FilterData, text="*左界值/大於", font=('微軟正黑體', 10)).place(x=25,y=L4Y+25,anchor="nw")
		tk.Label(FilterData, text="*右界值/小於", font=('微軟正黑體', 10)).place(x=25+150,y=L4Y+25,anchor="nw")
		Filter_LMELSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=4)
		Filter_LMELSpinbox.place(x=110,y=L4Y+26,anchor="nw")
		Filter_LMERSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=4)
		Filter_LMERSpinbox.place(x=110+150,y=L4Y+26,anchor="nw")

		L5Y = 145
		tk.Label(FilterData, text="●短期記憶錯誤(SME) [-1為不限定]", font=('微軟正黑體', 11, 'bold')).place(x=10,y=L5Y,anchor="nw")
		tk.Label(FilterData, text="*左界值/大於", font=('微軟正黑體', 10)).place(x=25,y=L5Y+25,anchor="nw")
		tk.Label(FilterData, text="*右界值/小於", font=('微軟正黑體', 10)).place(x=25+150,y=L5Y+25,anchor="nw")
		Filter_SMELSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=100)
		Filter_SMELSpinbox.place(x=110,y=L5Y+26,anchor="nw")
		Filter_SMERSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=100)
		Filter_SMERSpinbox.place(x=110+150,y=L5Y+26,anchor="nw")

		L6Y = 200
		tk.Label(FilterData, text="●實驗總時長(Latency/秒) [-1為不限定]", font=('微軟正黑體', 11, 'bold')).place(x=10,y=L6Y,anchor="nw")
		tk.Label(FilterData, text="*左界值/大於", font=('微軟正黑體', 10)).place(x=25,y=L6Y+25,anchor="nw")
		tk.Label(FilterData, text="*右界值/小於", font=('微軟正黑體', 10)).place(x=25+150,y=L6Y+25,anchor="nw")
		Filter_LatencyLSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=10000)
		Filter_LatencyLSpinbox.place(x=110,y=L6Y+26,anchor="nw")
		Filter_LatencyRSpinbox = tk.Spinbox(FilterData, font=('微軟正黑體', 10), width=5, from_=-1, to=10000)
		Filter_LatencyRSpinbox.place(x=110+150,y=L6Y+26,anchor="nw")

		tk.Button(FilterData, text="確定篩選", font=('微軟正黑體', 10), command=TableData_Filter).place(x=175,y=250,anchor="n")
		FilterData.protocol("WM_DELETE_WINDOW", FilterData_WindowsClosing)
		FilterData.mainloop()

def WindowsView():
	global tkWin, TK_BT_ShowQuantity, CONSOLE_COLOR
	global LOAD_CSV_NAME, TK_BT_SetExpCSV, TK_BT_LoadExpCSV
	global LOAD_PATH_DIR, TK_BT_SetPathData, TK_BT_LoadPathData
	global TBI_QUANTITY_DATA, TBI_QUANTITY_Group_TOTAL, TBI_QUANTITY_TP_TOTAL, TBI_QUANTITY_TOTAL_TOTAL
	global CAL_DATE_NUM, TK_NOW_CAL_M, TK_SHOW_CAL_Month, CAL_ExpDate_Label
	global DEL_Cal, DEL_TimepointCombo
	global EXPTABLE_SQL_DATA_SUM, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_RESULT, EXPTABLE_SQL_DATA_MAXITEM
	global EXPTABLE_PAGE_L_BT, EXPTABLE_PAGE_R_BT, EXPTABLE_SEARCH_BT, EXPTABLE_PAGE_TOTAL, EXPTABLE_PAGE_STATE
	global EXPTABLE_Data_Label, EXPTABLE_Filter_BT, EXPTABLE_Route_BT, ExpDataTB_L_State, ExpDataTB_R_State
	global EXPTABLE_SortData_BT, EXPTABLE_SORT_BY

	# 實驗數據匯入區
	M1Y = 10
	tk.Label(tkWin, text="匯入實驗數據(CSV)", font=('微軟正黑體', 11), bg="gray75").place(x=10,y=M1Y,anchor="nw")
	tk.Label(tkWin, text="檔案名稱", font=('微軟正黑體', 12)).place(x=10,y=M1Y+27,anchor="nw")
	TKE_ExpData_File = tk.Entry(tkWin, textvariable=LOAD_CSV_NAME, font=('微軟正黑體', 10), width=25, state="disabled")
	TKE_ExpData_File.place(x=85,y=M1Y+30,anchor="nw")
	TK_BT_SetExpCSV = tk.Button(tkWin, text='選擇檔案', font=('微軟正黑體', 10), command=chooseLoadFile_ExpData)
	TK_BT_SetExpCSV.place(x=150,y=M1Y-2,anchor="nw")
	TK_BT_LoadExpCSV = tk.Button(tkWin, text='匯入資料', font=('微軟正黑體', 10), state="disabled", command=LoadCSV_ExperimentData)
	TK_BT_LoadExpCSV.place(x=220,y=M1Y-2,anchor="nw")

	# 實驗數據匯入區
	M2Y = 70
	tk.Label(tkWin, text="匯入路徑軌跡數據(IMG/CSV)", font=('微軟正黑體', 11), bg="gray75").place(x=10,y=M2Y,anchor="nw")
	tk.Label(tkWin, text="路徑名稱", font=('微軟正黑體', 12)).place(x=10,y=M2Y+27,anchor="nw")
	TKE_PathData_Dir = tk.Entry(tkWin, textvariable=LOAD_PATH_DIR, font=('微軟正黑體', 10), width=33, state="disabled")
	TKE_PathData_Dir.place(x=85,y=M2Y+30,anchor="nw")
	TK_BT_SetPathData = tk.Button(tkWin, text='選擇路徑', font=('微軟正黑體', 10), command=chooseLoadPath_PathData)
	TK_BT_SetPathData.place(x=220,y=M2Y-2,anchor="nw")
	TK_BT_LoadPathData = tk.Button(tkWin, text='匯入資料', font=('微軟正黑體', 10), state="disabled", command=LoadCSV_ExperimentData)
	TK_BT_LoadPathData.place(x=290,y=M2Y-2,anchor="nw")

	# 實驗總數顯示區
	M3X = 370
	M3Y = 12
	TK_BT_ShowQuantity = tk.Button(tkWin, text='TBI 各組總數', font=('微軟正黑體', 10), bg="gray75", width=10, relief="flat", command=chooseQuantityType)
	TK_BT_ShowQuantity.place(x=M3X+1,y=M3Y-2,anchor="nw")
	
	M3X_1 = M3X+95
	M3Y_1 = M3Y-2
	SHOW_TP_List = ['Pre', 'D07', 'D14', 'D28', 'M03', 'M06', 'M09']
	TP_Color = {
		"Pre": "SteelBlue", 
		"D07": "SkyBlue1", "D14": "SkyBlue2", "D28": "SkyBlue3", 
		"M03": "DeepSkyBlue1", "M06": "DeepSkyBlue2", "M09": "DeepSkyBlue3"
	}
	for i in range(len(SHOW_TP_List)):
		newTBI_Title_Frame = tk.Frame(tkWin, width=54, height=30, bg=TP_Color[SHOW_TP_List[i]])
		newTBI_Title_Frame.place(x=M3X_1 + 56*i,y=M3Y_1,anchor="nw")
		tk.Label(newTBI_Title_Frame, text=SHOW_TP_List[i], font=('微軟正黑體', 11), bg=TP_Color[SHOW_TP_List[i]]).place(x=27,y=2,anchor="n")

	M3X_2 = M3X
	M3Y_2 = M3Y+30
	SHOW_TBI_Group_List = ['Sham+NS', 'Sham+MSC', 'rTBI+NS', 'rTBI+MSC']
	for i in range(len(SHOW_TBI_Group_List)):
		newTBI_Group_Frame = tk.Frame(tkWin, width=90, height=24, bg="SkyBlue1")
		newTBI_Group_Frame.place(x=M3X_2, y=M3Y_2 + 26*i, anchor="nw")
		tk.Label(newTBI_Group_Frame, text=SHOW_TBI_Group_List[i], font=('微軟正黑體', 10), bg="SkyBlue1").place(x=45,y=1,anchor="n")
		for j in range(1,len(SHOW_TP_List)):
			newTBI_Data_Frame = tk.Frame(tkWin, width=54, height=24, bg="gray85")
			newTBI_Data_Frame.place(x=M3X_2 + 95 + 56*j, y=M3Y_2 + 26*i, anchor="nw")
			tk.Label(newTBI_Data_Frame, textvariable=TBI_QUANTITY_DATA[i][j], font=('微軟正黑體', 10), bg="gray85").place(x=27,y=1,anchor="n")
	newTBI_Data_Frame = tk.Frame(tkWin, width=54, height=26*4 - 2, bg="gray85")
	newTBI_Data_Frame.place(x=M3X_2 + 95, y=M3Y_2, anchor="nw")
	tk.Label(newTBI_Data_Frame, textvariable=TBI_QUANTITY_DATA[0][0], font=('微軟正黑體', 10), bg="gray85").place(x=27,y=(26*4-2)/2-10,anchor="n")

	M3X_3 = M3X+95
	M3Y_3 = M3Y+135
	for i in range(len(TBI_QUANTITY_TP_TOTAL)):
		newTBI_Total_Frame = tk.Frame(tkWin, width=54, height=24, bg="SkyBlue2")
		newTBI_Total_Frame.place(x=M3X_3 + 56*i, y=M3Y_3, anchor="nw")
		tk.Label(newTBI_Total_Frame, textvariable=TBI_QUANTITY_TP_TOTAL[i], font=('微軟正黑體', 10, 'bold'), bg="SkyBlue2").place(x=27,y=0,anchor="n")
	
	M3X_4 = M3X+487
	M3Y_4 = M3Y+30
	for i in range(len(TBI_QUANTITY_Group_TOTAL)):
		newTBI_Group_Total_Frame = tk.Frame(tkWin, width=82, height=24, bg="DeepSkyBlue1")
		newTBI_Group_Total_Frame.place(x=M3X_4, y=M3Y_4 + 26*i, anchor="nw")
		tk.Label(newTBI_Group_Total_Frame, textvariable=TBI_QUANTITY_Group_TOTAL[i], font=('微軟正黑體', 10, 'bold'), bg="DeepSkyBlue1").place(x=41, y=1, anchor="n")

	M3X_5 = M3X+487
	M3Y_5 = M3Y-2
	newTBI_Group_Total_Label = tk.Frame(tkWin, width=82, height=30, bg="DeepSkyBlue1")
	newTBI_Group_Total_Label.place(x=M3X_5,y=M3Y_5,anchor="nw")
	tk.Label(newTBI_Group_Total_Label, text="Total(術後)", font=('微軟正黑體', 10, 'bold'), bg="DeepSkyBlue1").place(x=41, y=3, anchor="n")
	
	M3X_6 = M3X
	M3Y_6 = M3Y+135
	newTBI_TP_Total_Label = tk.Frame(tkWin, width=90, height=24, bg="SkyBlue2")
	newTBI_TP_Total_Label.place(x=M3X_6,y=M3Y_6,anchor="nw")
	tk.Label(newTBI_TP_Total_Label, text="Total(整體)", font=('微軟正黑體', 10, "bold"), bg="SkyBlue2").place(x=45,y=1,anchor="n")

	M3X_7 = M3X+487
	M3Y_7 = M3Y+135
	newTBI_TP_Total_Total = tk.Frame(tkWin, width=82, height=24, bg="SkyBlue1")
	newTBI_TP_Total_Total.place(x=M3X_7,y=M3Y_7,anchor="nw")
	tk.Label(newTBI_TP_Total_Total, textvariable=TBI_QUANTITY_TOTAL_TOTAL, font=('微軟正黑體', 11, 'bold'), bg="SkyBlue1").place(x=41,y=0,anchor="n")

	# 實驗天數資料顯示區
	M4X = 10
	M4Y = 130
	tk.Label(tkWin, text="TBI 實驗日期總覽", font=('微軟正黑體', 11), bg="gray75").place(x=M4X,y=M4Y,anchor="nw")
	TK_SHOW_CAL_Month = tk.Label(tkWin, textvariable=TK_NOW_CAL_M, font=('微軟正黑體', 11, "bold"))
	TK_SHOW_CAL_Month.place(x=M4X+125,y=M4Y,anchor="nw")
	tk.Button(tkWin, text='◀', font=('微軟正黑體', 10), width=5, command=lambda: MoveUpDownCal('Down')).place(x=M4X+235,y=M4Y-2,anchor="nw")
	tk.Button(tkWin, text='▶', font=('微軟正黑體', 10), width=5, command=lambda: MoveUpDownCal('Up')).place(x=M4X+290,y=M4Y-2,anchor="nw")

	WEEK_LIST = ['週一', '週二', '週三', '週四', '週五']
	SHOW_TBI_CAL_Title_Frame = tk.Frame(tkWin, width=350, height=25, bg="SkyBlue1")
	SHOW_TBI_CAL_Title_Frame.place(x=M4X,y=M4Y+30,anchor="nw")
	SHOW_TBI_CAL_Content_Frame = tk.Frame(tkWin, width=350, height=500)
	SHOW_TBI_CAL_Content_Frame.place(x=M4X,y=M4Y+60,anchor="nw")
	M4X_CP = M4X+2
	M4Y_CP = M4Y+60
	for i in range(len(WEEK_LIST)):
		tk.Label(SHOW_TBI_CAL_Title_Frame, text=WEEK_LIST[i], font=('微軟正黑體', 11), bg="SkyBlue1").place(x=35+70*i,y=0,anchor="n")
	for i in range(5):
		CAL_ExpDate_Label.append([])
		for j in range(len(WEEK_LIST)):
			CAL_ExpDate_Label[i].append(["", "", ""])
			tk.Frame(SHOW_TBI_CAL_Content_Frame, width=66, height=96, bg="gray85").place(x=35+70*j,y=100*i,anchor="n")
			tk.Label(tkWin, textvariable=CAL_DATE_NUM[i][j], font=('微軟正黑體', 9), bg="gray85").place(x=M4X_CP+70*j,y=M4Y_CP+100*i,anchor="nw")
			CAL_ExpDate_Label[i][j][0] = tk.Label(tkWin, text="", font=('微軟正黑體', 9), bg="gray85")
			CAL_ExpDate_Label[i][j][0].place(x=M4X_CP+5+70*j,y=M4Y_CP+21+100*i,anchor="nw")
			CAL_ExpDate_Label[i][j][1] = tk.Label(tkWin, text="", font=('微軟正黑體', 9), bg="gray85")
			CAL_ExpDate_Label[i][j][1].place(x=M4X_CP+5+70*j,y=M4Y_CP+44+100*i,anchor="nw")
			CAL_ExpDate_Label[i][j][2] = tk.Label(tkWin, text="", font=('微軟正黑體', 9), bg="gray85")
			CAL_ExpDate_Label[i][j][2].place(x=M4X_CP+5+70*j,y=M4Y_CP+67+100*i,anchor="nw")

	# Console
	M5X = 10
	M5Y = 690
	testConsoleText = "[2020-11-20 10:50:23] 20201006(07D).csv 資料匯入(TBI Model - 00M07D)，成功 13 筆， 失敗 0 筆，共 13 筆資料"
	TK_Console = tk.Frame(tkWin, width=1000, height=82, bg="black")
	TK_Console.place(x=M5X,y=M5Y,anchor="nw")
	TK_Console_Line[0] = tk.Label(TK_Console, text="", font=('微軟正黑體', 10, 'bold'), bg="black", fg=CONSOLE_COLOR["NULL"])
	TK_Console_Line[0].place(x=2,y=2,anchor="nw")
	TK_Console_Line[1] = tk.Label(TK_Console, text="", font=('微軟正黑體', 10, 'bold'), bg="black", fg=CONSOLE_COLOR["NULL"])
	TK_Console_Line[1].place(x=2,y=21,anchor="nw")
	TK_Console_Line[2] = tk.Label(TK_Console, text="", font=('微軟正黑體', 10, 'bold'), bg="black", fg=CONSOLE_COLOR["NULL"])
	TK_Console_Line[2].place(x=2,y=40,anchor="nw")
	TK_Console_Line[3] = tk.Label(TK_Console, text="", font=('微軟正黑體', 10, 'bold'), bg="black", fg=CONSOLE_COLOR["NULL"])
	TK_Console_Line[3].place(x=2,y=59,anchor="nw")

	# 刪除實驗數據區
	M6X = 370
	M6Y = 175
	tk.Label(tkWin, text="刪除實驗數據", font=('微軟正黑體', 11), bg="gray75").place(x=M6X,y=M6Y,anchor="nw")
	tk.Label(tkWin, text="實驗日期", font=('微軟正黑體', 11)).place(x=M6X+100,y=M6Y,anchor="nw")
	DEL_Cal = DateEntry(tkWin, width=10, background='gray', dateformat=4, font=('微軟正黑體', 10, "bold"), foreground='white', borderwidth=2)
	DEL_Cal.place(x=M6X+170,y=M6Y+2,anchor="nw")
	tk.Label(tkWin, text="時間點", font=('微軟正黑體', 11)).place(x=M6X+280,y=M6Y,anchor="nw")
	DEL_Timepoint = ['請選擇...', '手術前', '手術後7天', '手術後14天', '手術後28天', '手術後3個月', '手術後6個月', '手術後9個月']
	DEL_TimepointCombo = ttk.Combobox(LoadCSV, width=12, values=DEL_Timepoint, font=('微軟正黑體', 10), state="readonly")
	DEL_TimepointCombo.place(x=M6X+335,y=M6Y+2,anchor="nw")
	DEL_TimepointCombo.current(0)
	TK_BT_DEL_ExpData = tk.Button(tkWin, text='查詢刪除數據', font=('微軟正黑體', 10), command=DeleteExpData)
	TK_BT_DEL_ExpData.place(x=M6X+460,y=M6Y-2,anchor="nw")

	# 實驗數據展示區
	M7X = 370
	M7Y = 210
	tk.Label(tkWin, text="實驗數據詳細資料(TBI)", font=('微軟正黑體', 11), bg="gray75").place(x=M7X,y=M7Y,anchor="nw")
	M7TB_X = M7X
	M7TB_Y = M7Y + 48
	ExpDate_TBT = ['日期', '組別', '時間點', '編號', '*LME', '*SME', '總時間(s)', '採用', '進臂順序']
	ExpDate_TBT_Size = [90, 90, 50, 100, 40, 45, 70, 50, 80]
	ExpDate_TBT_LeftPos = [0,0,0,0,0,0,0,0,0]

	for i in range(len(ExpDate_TBT)):
		if i > 0:
			ExpDate_TBT_LeftPos[i] = ExpDate_TBT_Size[i-1] + ExpDate_TBT_LeftPos[i-1] + 2
		TB_Title = tk.Frame(tkWin, width=ExpDate_TBT_Size[i], height=25, bg="SkyBlue1")
		TB_Title.place(x=M7TB_X+ExpDate_TBT_LeftPos[i],y=M7TB_Y,anchor="nw")
		TB_Title_Label = tk.Label(TB_Title, text=ExpDate_TBT[i], font=('微軟正黑體', 10), bg="SkyBlue1")
		TB_Title_Label.place(x=int(ExpDate_TBT_Size[i]/2),y=1,anchor="n")

	# 排序資料
	for i in range(len(ExpDate_TBT)):
		SortFram = tk.Frame(tkWin, width=ExpDate_TBT_Size[i], height=16, bg="gray90")
		SortFram.place(x=M7TB_X + ExpDate_TBT_LeftPos[i], y=M7TB_Y-18, anchor="nw")
		EXPTABLE_SortData_BT[i] = tk.Button(SortFram, text="", font=('微軟正黑體', 8), width=ExpDate_TBT_Size[i], bg="gray90", relief='flat', command=partial(setSortDataButton,i))
		EXPTABLE_SortData_BT[i].place(x=int(ExpDate_TBT_Size[i]/2),y=-4,anchor="n")

	testTableData = ['2020/11/15', 'rTBI+MSC', '07D', '20201008-10', 4, 23, 2183, False, None]

	EXPTABLE_SQL_DATA_SUM, ExpDataTB_L_State, ExpDataTB_R_State, EXPTABLE_SQL_DATA_RESULT = SQLDataQuery2Table(EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM, EXPTABLE_SORT_BY)

	EXPTABLE_PAGE_STATE.set("第%d頁/共%d頁" %(0, 0))
	tk.Label(tkWin, 
		textvariable=EXPTABLE_PAGE_STATE, 
		font=('微軟正黑體', 10)
	).place(x=M7X+400,y=M7Y+2, anchor="n") # 350~450
	EXPTABLE_SEARCH_BT = tk.Button(tkWin, text='選擇篩選資料查詢條件', font=('微軟正黑體', 9), command=FilterData_ExperimentForTBI)
	EXPTABLE_SEARCH_BT.place(x=M7X+160,y=M7Y-2,anchor="nw")
	EXPTABLE_PAGE_L_BT = tk.Button(tkWin, text='◀ 上一頁', font=('微軟正黑體', 9), command=lambda: MoveUpDownDataTable('Up'), state="disabled")
	EXPTABLE_PAGE_L_BT.place(x=M7X+290,y=M7Y-2,anchor="nw") #60
	EXPTABLE_PAGE_R_BT = tk.Button(tkWin, text='下一頁 ▶', font=('微軟正黑體', 9), command=lambda: MoveUpDownDataTable('Down'), state="disabled")
	EXPTABLE_PAGE_R_BT.place(x=M7X+450,y=M7Y-2,anchor="nw") #60
	EXPTABLE_PAGE_TOTAL.set("共%d筆" %(0))
	tk.Label(tkWin, 
		textvariable=EXPTABLE_PAGE_TOTAL, 
		font=('微軟正黑體', 11, 'bold')
	).place(x=M7X+510,y=M7Y, anchor="nw") # 350~450

	for j in range(EXPTABLE_SQL_DATA_MAXITEM):
		TB_TBData_Y = M7TB_Y + 28 + 25*j
		for i in range(len(ExpDate_TBT)):
			TB_TBData = tk.Frame(tkWin, width=ExpDate_TBT_Size[i], height=23, bg="gray80")
			TB_TBData.place(x=M7TB_X+ExpDate_TBT_LeftPos[i],y=TB_TBData_Y,anchor="nw")
			if i < len(ExpDate_TBT) - 2:
				EXPTABLE_Data_Label[j][i] = tk.Label(TB_TBData, text="", font=('微軟正黑體', 9), bg="gray80")
				EXPTABLE_Data_Label[j][i].place(x=int(ExpDate_TBT_Size[i]/2),y=1,anchor="n")
			elif i == len(ExpDate_TBT)-2:
				EXPTABLE_Filter_BT[j] = tk.Button(TB_TBData, text="", font=('微軟正黑體', 9), width=ExpDate_TBT_Size[len(ExpDate_TBT)-2], bg="gray80", relief='flat', command=BT_None)
				EXPTABLE_Filter_BT[j].place(x=int(ExpDate_TBT_Size[len(ExpDate_TBT)-2]/2),y=-2,anchor="n")
			elif i == len(ExpDate_TBT)-1:
				EXPTABLE_Route_BT[j] = tk.Button(TB_TBData, text="", font=('微軟正黑體', 9), width=ExpDate_TBT_Size[len(ExpDate_TBT)-1], bg="gray80", relief='flat', command=BT_None)
				EXPTABLE_Route_BT[j].place(x=int(ExpDate_TBT_Size[len(ExpDate_TBT)-1]/2),y=-2,anchor="n")
	
	TB_command = "註：*LME = Long-Term Memory Error (長期記憶錯誤) *SME = Short-Term Memory Error (短期記憶錯誤)"
	tk.Label(tkWin, text=TB_command, font=('微軟正黑體', 8)).place(x=M7TB_X,y=M7TB_Y+402,anchor="nw")
	
	tkWin.protocol("WM_DELETE_WINDOW", Main_WindowsClosing)
	updateTBI_Quantity(TBI_QUANTITY_DATA_TYPE)
	updateTBI_ExpDateCal(CAL_CURRENT_M)
	updateTBI_ExpDataTable(EXPTABLE_SQL_Query, EXPTABLE_SQL_DATA_PAGE, EXPTABLE_SQL_DATA_MAXITEM)
	WriteConsoleMsg("NONE", "歡迎使用 %s" %(SYSTEM_NAME))
	tkWin.after(10,LoopMain)
	tkWin.mainloop()

if __name__ == "__main__":
	SystemInit()
	WindowsView()