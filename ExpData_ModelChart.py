import sqlite3
import cv2
import numpy as np
import matplotlib.pyplot as plt

SQL_CONN = sqlite3.connect("./sqlite3_chimei_data.db") #建立資料庫連結
SQL_TABLE = "VIEW_TBI_Export_Rowdata"

def ChartTest():
	barWidth = 0.3 #長條寬度
	barData = [ #數據資料
		[86.6, 104.4, 101.4, 119.0],
		[86.6, 173.2, 330.0, 465.0]
	]
	barError = [ #Error Bar誤差值資料
		[0.0, 0.0, 0.0, 0.0],
		[36.4, 11.7, 24.6, 17.0],
		[36.4, 10.2, 42.8, 37.0]
	]
	barColor = ['black', 'red'] #長條顏色
	barLabel = ['Sham', 'TBI+NS'] #長條圖例
	
	barPos = [] #長條圖的位置
	for i in range(len(barData)):
		barPos.append([0 + barWidth*i, 1 + barWidth*i, 2 + barWidth*i, 3 + barWidth*i])
	
	barPosAvg = [] #X軸的標籤位置
	for i in range(len(barData[0])):
		barPosAvg.append(i + barWidth/2)

	for i in range(len(barData)):
		plt.bar(barPos[i], barData[i], 
			width = barWidth, color = barColor[i], 
			edgecolor = 'black', 
			yerr=(barError[0],barError[i+1]), 
			capsize=7, label=barLabel[i]
		)

	# general layout
	plt.title("[TEST CHART] ChiMei Experimantal Rat Latency")
	plt.xticks(barPosAvg, ['Pre', 'D07', 'D14', 'D28'])
	plt.ylabel('height')
	plt.legend()
	plt.show()

def VIEW_DrawChart_Bar(chID, chartTitle, x_label, y_label, barWidth, barData, barError, barLabel):
	# barColor = ['black', 'white', 'red', 'orange', 'yellow', 'green', 'blue', 'purple']
	barColor = ['black', 'gray', 'red', 'darkred']

	dataKeys = []
	for figName in barData:
		dataKeys.append(figName)

	barPos = [] #長條圖的位置
	for i in range(len(barData[dataKeys[0]])):
		newArr = []
		for j in range(len(barData[dataKeys[0]][0])):
			newArr.append(j + barWidth*i)
		barPos.append(newArr)
	
	barPosAvg = [] #X軸的標籤位置
	for i in range(len(barData[dataKeys[0]][0])):
		barPosAvg.append(i + barWidth/2)

	# ===================
	# ====繪製單一圖表====
	# ===================
	for figName in barData:
		plt.figure(figsize=(8,8), dpi=80)
		for i in range(len(barData[figName])):
			barError_zero = np.zeros(len(barError[figName][i]))
			plt.bar(barPos[i], barData[figName][i], 
				width = barWidth, color = barColor[i], 
				edgecolor = 'black', 
				yerr=(barError_zero, barError[figName][i]), 
				capsize=5, 
				label=barLabel[i]
			)

		# general layout
		plt.title("Eight-arm Maze Rat (TBI %s)" %(chartTitle[figName]), fontsize=18)
		plt.xticks(barPosAvg, x_label)
		plt.xlabel("Timepoint", fontsize=14)
		plt.ylabel(y_label[figName], fontsize=14)
		plt.legend()
		# plt.show()
		plt.savefig("./_myTemp_/figureVIEW(TBI %s).png" %(chartTitle[figName]))
		plt.clf()

	# ========================
	# ====繪製三個一組的圖表====
	# ========================
	# plt.figure(figsize=(24,8), dpi=80)

	# figIdx = 131
	# for figName in barData:
	# 	ax1 = plt.subplot(figIdx)
	# 	for i in range(len(barData[figName])):
	# 		barError_zero = np.zeros(len(barError[figName][i]))
	# 		ax1.bar(barPos[i], barData[figName][i], 
	# 			width = barWidth, color = barColor[i], 
	# 			edgecolor = 'black', 
	# 			yerr=(barError_zero, barError[figName][i]), 
	# 			capsize=5, 
	# 			label=barLabel[i]
	# 		)
	# 	figIdx = figIdx + 1

	# 	# general layout
	# 	ax1.set_title("Eight-arm Maze Rat (TBI %s)" %(chartTitle[figName]))
	# 	ax1.set_xticks(barPosAvg, x_label)
	# 	ax1.set_ylabel(y_label[figName])
	# 	ax1.legend()

	# # 各圖表資料是啥
	# count = 0
	# titleWord = ""
	# for row in chartTitle:
	# 	titleWord = titleWord + chartTitle[row]
	# 	if count < len(chartTitle) - 1:
	# 		titleWord = titleWord + "/"
	# 		count = count + 1
	# # 時間點
	# count = 0
	# TPWord = ""
	# for row in x_label:
	# 	TPWord = TPWord + row
	# 	if count < len(x_label) - 1:
	# 		TPWord = TPWord + "/"
	# 		count = count + 1

	# plt.suptitle("{CHART_TITLE} Result ({CHART_TP})".format(CHART_TITLE=titleWord, CHART_TP=TPWord), fontsize=20)
	# plt.legend()
	# # plt.show()
	# plt.savefig("./_myTemp_/figureVIEW%d.png" %(chID))
	# plt.clf()

def DrawTBI_Chart(drawMode):
	global SQL_CONN, SQL_TABLE

	OUTPUT_MODEL = ["Sham", "Sham+NS", "rTBI+NS", "Sham+MSC", "rTBI+MSC"]
	Chart_ModelName = {"Sham":"Sham+NS", "Sham+MSC":"Sham+MSC", "TBI":"rTBI+NS", "TBI+MSC":"rTBI+MSC"}
	Chart_ModelNameShow = ["Sham", "Sham+MSC", "TBI", "TBI+MSC"]
	Chart_BarWidth = 0.2

	# OUTPUT_MODEL = ["Sham", "Sham+NS", "rTBI+NS"]
	# Chart_ModelName = {"Sham":"Sham+NS", "TBI":"rTBI+NS"}
	# Chart_ModelNameShow = ["Sham", "TBI"]
	# Chart_BarWidth = 0.3

	Chart_X_Label = ('Pre', 'D07', 'D14', 'D28', 'M03', 'M06')

	if drawMode == "LT_ST_LATC":
		# 事前SQL命令準備
		SEARCH_WORD = "\"Timepoint\""
		SEARCH_COL = ("LongTerm", "ShortTerm", "latency")
		SEARCH_NAME = {
			"avg":("AVG_LT", "AVG_ST", "AVG_LATC"),
			"max":("MAX_LT", "MAX_ST", "MAX_LATC"),
		}
		for row in SEARCH_NAME:
			for i in range(len(row)):
				SEARCH_WORD = SEARCH_WORD + ", "
				SEARCH_WORD = SEARCH_WORD + "%s(\"%s\") AS \"%s\"" %(row, SEARCH_COL[i], SEARCH_NAME[row][i])
		# print(SEARCH_WORD)
		
		# 執行SQL命令
		LT_Result = {"AVG":[], "MAX":[]}
		ST_Result = {"AVG":[], "MAX":[]}
		LATC_Result = {"AVG":[], "MAX":[]}
		for row in OUTPUT_MODEL: #建立資料收集架構
			if row != "Sham":
				LT_Result["AVG"].append({"Model": row})
				ST_Result["AVG"].append({"Model": row})
				LATC_Result["AVG"].append({"Model": row})
				LT_Result["MAX"].append({"Model": row})
				ST_Result["MAX"].append({"Model": row})
				LATC_Result["MAX"].append({"Model": row})
		# print(ST_Result)
		for _model in OUTPUT_MODEL:
			sql_query = "SELECT {SEARCH} FROM \"{TABLE}\" WHERE \"Groups\" = \"{Groups}\" GROUP BY \"Timepoint\"".format(
				SEARCH = SEARCH_WORD,
				TABLE = SQL_TABLE,
				Groups = _model
			)
			cursor = SQL_CONN.execute(sql_query)
			result = cursor.fetchall()
			for SQL_Result in result:
				# print(SQL_Result)
				if SQL_Result[0] == "Pre":
					for i in range(len(LT_Result["AVG"])):
						LT_Result["AVG"][i]["Pre"] = SQL_Result[1]
						ST_Result["AVG"][i]["Pre"] = SQL_Result[2]
						LATC_Result["AVG"][i]["Pre"] = SQL_Result[3]
						LT_Result["MAX"][i]["Pre"] = SQL_Result[4]
						ST_Result["MAX"][i]["Pre"] = SQL_Result[5]
						LATC_Result["MAX"][i]["Pre"] = SQL_Result[6]
				else:
					for i in range(len(LT_Result["AVG"])):
						if LT_Result["AVG"][i]["Model"] == _model:
							LT_Result["AVG"][i][SQL_Result[0]] = SQL_Result[1]
							ST_Result["AVG"][i][SQL_Result[0]] = SQL_Result[2]
							LATC_Result["AVG"][i][SQL_Result[0]] = SQL_Result[3]
							LT_Result["MAX"][i][SQL_Result[0]] = SQL_Result[4]
							ST_Result["MAX"][i][SQL_Result[0]] = SQL_Result[5]
							LATC_Result["MAX"][i][SQL_Result[0]] = SQL_Result[6]
		# print(LT_Result)
		# print(ST_Result)
		# print(LATC_Result)

		# 將收到的資料轉成圖表所需資料
		Chart_Title = {"LT":"Long-term", "ST":"Short-term", "LATC":"Latency"}
		Chart_Y_Label = {"LT":"Number of times", "ST":"Number of times", "LATC":"Latency"}
		Chart_Data = {"LT":[], "ST":[], "LATC":[]}
		Chart_err = {"LT":[], "ST":[], "LATC":[]}
		
		for name in Chart_ModelName:
			dataName = Chart_ModelName[name]
			# Long-term Part
			rowData = []
			rowErr = []
			for i in range(len(LT_Result["AVG"])):
				if LT_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(LT_Result["AVG"][i][tp])
						rowErr.append((LT_Result["MAX"][i][tp] - LT_Result["AVG"][i][tp]))
			Chart_Data["LT"].append(rowData)
			Chart_err["LT"].append(rowErr)
			# Short-term Part
			rowData = []
			rowErr = []
			for i in range(len(ST_Result["AVG"])):
				if ST_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(ST_Result["AVG"][i][tp])
						rowErr.append((ST_Result["MAX"][i][tp] - ST_Result["AVG"][i][tp]))
			Chart_Data["ST"].append(rowData)
			Chart_err["ST"].append(rowErr)
			# Latency Part
			rowData = []
			rowErr = []
			for i in range(len(LATC_Result["AVG"])):
				if ST_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(LATC_Result["AVG"][i][tp])
						rowErr.append((LATC_Result["MAX"][i][tp] - LATC_Result["AVG"][i][tp]))
			Chart_Data["LATC"].append(rowData)
			Chart_err["LATC"].append(rowErr)

		# print(Chart_Data)
		# print(Chart_err)

		# 開始繪圖
		VIEW_DrawChart_Bar(
			chID=1,
			chartTitle=Chart_Title,
			x_label=Chart_X_Label,
			y_label=Chart_Y_Label,
			barWidth=Chart_BarWidth,
			barData=Chart_Data,
			barError=Chart_err,
			barLabel=Chart_ModelNameShow
		)

		# 將數據輸出在CLI上
		for title in Chart_Title:
			VIEW = cv2.imread("_myTemp_/figureVIEW(TBI %s).png" %(Chart_Title[title]))
			cv2.imshow("figureVIEW(TBI %s).png" %(Chart_Title[title]), VIEW)

		# VIEW1 = cv2.imread("_myTemp_/figureVIEW1.png")
		# cv2.imshow("figureVIEW1", VIEW1)

		Divider = "-----------" # 分隔線
		subDivider = ""
		for i in range(17):
			subDivider = subDivider + "-"
		for i in range(len(Chart_X_Label)):
			Divider = Divider + subDivider
		
		for row in Chart_Title:
			# 標題
			print("[Eight-arm Maze Rat (TBI %s)]" %(Chart_Title[row]))
			# 欄位名
			print("|%-10s" %("Model"), end="")
			for tp in Chart_X_Label:
				print("|%-16s" %(tp), end="")
			print()
			# 資料欄
			for mod in Chart_ModelName:
				print("%-11s" %(mod), end="")
				idx = Chart_ModelNameShow.index(mod)
				for i in range(len(Chart_Data[row][idx])):
					dataStr = "%0.2f(%0.2f)" %(Chart_Data[row][idx][i], (Chart_err[row][idx][i]))
					print("%-17s" %(dataStr), end="")
				print()

			print(Divider)
		print("P.S. Data format: Average data (Positive error value)")

		cv2.waitKey(0)
	elif drawMode == "MDIS_MSP":
		# 事前SQL命令準備
		SEARCH_WORD = "\"Timepoint\""
		SEARCH_COL = ("Central", "Target", "Normal")
		TOT_TimeWord = ""
		TOT_DisWord = ""
		for i in range(len(SEARCH_COL)):
			TOT_TimeWord = TOT_TimeWord + "\"Time(%s)\"" %(SEARCH_COL[i])
			TOT_DisWord = TOT_DisWord + "\"Distance(%s)\"" %(SEARCH_COL[i])
			if i < len(SEARCH_COL) - 1:
				TOT_TimeWord = TOT_TimeWord + " + "
				TOT_DisWord = TOT_DisWord + " + "
		SEARCH_NAME = {
			"avg":("AVG_TOT_DIS", "AVG_TOT_TIME", "AVG_TOT_SPEED"),
			"max":("MAX_TOT_DIS", "MAX_TOT_TIME", "MAX_TOT_SPEED"),
		}
		SEARCH_TEXT = [
			TOT_DisWord, TOT_TimeWord,
			"(%s)/(%s)" %(TOT_DisWord, TOT_TimeWord)
		]
		for row in SEARCH_NAME:
			for i in range(len(row)):
				SEARCH_WORD = SEARCH_WORD + ", "
				SEARCH_WORD = SEARCH_WORD + "%s(%s) AS \"%s\"" %(row, SEARCH_TEXT[i], SEARCH_NAME[row][i])
		# print(SEARCH_WORD)
		
		# 執行SQL命令
		MDIS_Result = {"AVG":[], "MAX":[]}
		MSP_Result = {"AVG":[], "MAX":[]}
		MT_Result = {"AVG":[], "MAX":[]}
		for row in OUTPUT_MODEL: #建立資料收集架構
			if row != "Sham":
				MDIS_Result["AVG"].append({"Model": row})
				MSP_Result["AVG"].append({"Model": row})
				MT_Result["AVG"].append({"Model": row})
				MDIS_Result["MAX"].append({"Model": row})
				MSP_Result["MAX"].append({"Model": row})
				MT_Result["MAX"].append({"Model": row})
		# print(MDIS_Result)
		for _model in OUTPUT_MODEL:
			sql_query = "SELECT {SEARCH} FROM \"{TABLE}\" WHERE \"Groups\" = \"{Groups}\" GROUP BY \"Timepoint\"".format(
				SEARCH = SEARCH_WORD,
				TABLE = SQL_TABLE,
				Groups = _model
			)
			# print(sql_query)
			cursor = SQL_CONN.execute(sql_query)
			result = cursor.fetchall()
			for SQL_Result in result:
				# print(SQL_Result)
				if SQL_Result[0] == "Pre":
					for i in range(len(MDIS_Result["AVG"])):
						MDIS_Result["AVG"][i]["Pre"] = SQL_Result[1]
						MT_Result["AVG"][i]["Pre"] = SQL_Result[2]
						MSP_Result["AVG"][i]["Pre"] = SQL_Result[3]
						MDIS_Result["MAX"][i]["Pre"] = SQL_Result[4]
						MT_Result["MAX"][i]["Pre"] = SQL_Result[5]
						MSP_Result["MAX"][i]["Pre"] = SQL_Result[6]
				else:
					for i in range(len(MDIS_Result["AVG"])):
						if MDIS_Result["AVG"][i]["Model"] == _model:
							MDIS_Result["AVG"][i][SQL_Result[0]] = SQL_Result[1]
							MT_Result["AVG"][i][SQL_Result[0]] = SQL_Result[2]
							MSP_Result["AVG"][i][SQL_Result[0]] = SQL_Result[3]
							MDIS_Result["MAX"][i][SQL_Result[0]] = SQL_Result[4]
							MT_Result["MAX"][i][SQL_Result[0]] = SQL_Result[5]
							MSP_Result["MAX"][i][SQL_Result[0]] = SQL_Result[6]
		# print(MDIS_Result)
		# print(MT_Result)
		# print(MSP_Result)

		# 將收到的資料轉成圖表所需資料
		Chart_Title = {"MDIS":"Distance", "MT":"Spend Time", "MSP":"Speed"}
		Chart_Y_Label = {"MDIS":"Centimeter(cm)", "MT":"Second(s)", "MSP":"cm/s"}
		Chart_Data = {"MDIS":[], "MT":[], "MSP":[]}
		Chart_err = {"MDIS":[], "MT":[], "MSP":[]}
		
		for name in Chart_ModelName:
			dataName = Chart_ModelName[name]
			# Distance Part
			rowData = []
			rowErr = []
			for i in range(len(MDIS_Result["AVG"])):
				if MDIS_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(MDIS_Result["AVG"][i][tp])
						rowErr.append((MDIS_Result["MAX"][i][tp] - MDIS_Result["AVG"][i][tp]))
			Chart_Data["MDIS"].append(rowData)
			Chart_err["MDIS"].append(rowErr)
			# Spend Time Part
			rowData = []
			rowErr = []
			for i in range(len(MT_Result["AVG"])):
				if MT_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(MT_Result["AVG"][i][tp])
						rowErr.append((MT_Result["MAX"][i][tp] - MT_Result["AVG"][i][tp]))
			Chart_Data["MT"].append(rowData)
			Chart_err["MT"].append(rowErr)
			# Speed Part
			rowData = []
			rowErr = []
			for i in range(len(MSP_Result["AVG"])):
				if MSP_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(MSP_Result["AVG"][i][tp])
						rowErr.append((MSP_Result["MAX"][i][tp] - MSP_Result["AVG"][i][tp]))
			Chart_Data["MSP"].append(rowData)
			Chart_err["MSP"].append(rowErr)

		# print(Chart_Data)
		# print(Chart_err)

		# 開始繪圖
		VIEW_DrawChart_Bar(
			chID=2,
			chartTitle=Chart_Title,
			x_label=Chart_X_Label,
			y_label=Chart_Y_Label,
			barWidth=Chart_BarWidth,
			barData=Chart_Data,
			barError=Chart_err,
			barLabel=Chart_ModelNameShow
		)

		# 將數據輸出在CLI上
		for title in Chart_Title:
			VIEW = cv2.imread("_myTemp_/figureVIEW(TBI %s).png" %(Chart_Title[title]))
			cv2.imshow("figureVIEW(TBI %s).png" %(Chart_Title[title]), VIEW)
		
		# VIEW2 = cv2.imread("_myTemp_/figureVIEW2.png")
		# cv2.imshow("figureVIEW2", VIEW2)
		
		Divider = "-----------" # 分隔線
		subDivider = ""
		for i in range(17):
			subDivider = subDivider + "-"
		for i in range(len(Chart_X_Label)):
			Divider = Divider + subDivider
		
		for row in Chart_Title:
			# 標題
			print("[Eight-arm Maze Rat (TBI %s)]" %(Chart_Title[row]))
			# 欄位名
			print("|%-10s" %("Model"), end="")
			for tp in Chart_X_Label:
				print("|%-16s" %(tp), end="")
			print()
			# 資料欄
			for mod in Chart_ModelName:
				print("%-11s" %(mod), end="")
				idx = Chart_ModelNameShow.index(mod)
				for i in range(len(Chart_Data[row][idx])):
					dataStr = "%0.2f(%0.2f)" %(Chart_Data[row][idx][i], (Chart_err[row][idx][i]))
					print("%-17s" %(dataStr), end="")
				print()

			print(Divider)
		print("P.S. Data format: Average data (Positive error value)")
	elif drawMode == "CTN_Rate":
		# 事前SQL命令準備
		SEARCH_WORD = "\"Timepoint\""
		SEARCH_COL = ("Central", "Target", "Normal")
		TOT_TimeWord = ""
		for i in range(len(SEARCH_COL)):
			TOT_TimeWord = TOT_TimeWord + "\"Time(%s)\"" %(SEARCH_COL[i])
			if i < len(SEARCH_COL) - 1:
				TOT_TimeWord = TOT_TimeWord + " + "
		SEARCH_NAME = {
			"avg":("AVG_CTIME_RATE", "AVG_TTIME_RATE", "AVG_NTIME_RATE"),
			"max":("MAX_CTIME_RATE", "MAX_TTIME_RATE", "MAX_NTIME_RATE"),
		}
		for row in SEARCH_NAME:
			for i in range(len(row)):
				SEARCH_WORD = SEARCH_WORD + ", "
				SEARCH_WORD = SEARCH_WORD + "%s(\"Time(%s)\"/(%s)) AS \"%s\"" %(row, SEARCH_COL[i], TOT_TimeWord, SEARCH_NAME[row][i])
		# print(SEARCH_WORD)
		
		# # 執行SQL命令
		CTIME_Result = {"AVG":[], "MAX":[]}
		TTIME_Result = {"AVG":[], "MAX":[]}
		NTIME_Result = {"AVG":[], "MAX":[]}
		for row in OUTPUT_MODEL: #建立資料收集架構
			if row != "Sham":
				CTIME_Result["AVG"].append({"Model": row})
				TTIME_Result["AVG"].append({"Model": row})
				NTIME_Result["AVG"].append({"Model": row})
				CTIME_Result["MAX"].append({"Model": row})
				TTIME_Result["MAX"].append({"Model": row})
				NTIME_Result["MAX"].append({"Model": row})
		# print(CTIME_Result)
		for _model in OUTPUT_MODEL:
			sql_query = "SELECT {SEARCH} FROM \"{TABLE}\" WHERE \"Groups\" = \"{Groups}\" GROUP BY \"Timepoint\"".format(
				SEARCH = SEARCH_WORD,
				TABLE = SQL_TABLE,
				Groups = _model
			)
			# print(sql_query)
			cursor = SQL_CONN.execute(sql_query)
			result = cursor.fetchall()
			for SQL_Result in result:
				# print(SQL_Result)
				if SQL_Result[0] == "Pre":
					for i in range(len(CTIME_Result["AVG"])):
						CTIME_Result["AVG"][i]["Pre"] = SQL_Result[1]
						TTIME_Result["AVG"][i]["Pre"] = SQL_Result[2]
						NTIME_Result["AVG"][i]["Pre"] = SQL_Result[3]
						CTIME_Result["MAX"][i]["Pre"] = SQL_Result[4]
						TTIME_Result["MAX"][i]["Pre"] = SQL_Result[5]
						NTIME_Result["MAX"][i]["Pre"] = SQL_Result[6]
				else:
					for i in range(len(CTIME_Result["AVG"])):
						if CTIME_Result["AVG"][i]["Model"] == _model:
							CTIME_Result["AVG"][i][SQL_Result[0]] = SQL_Result[1]
							TTIME_Result["AVG"][i][SQL_Result[0]] = SQL_Result[2]
							NTIME_Result["AVG"][i][SQL_Result[0]] = SQL_Result[3]
							CTIME_Result["MAX"][i][SQL_Result[0]] = SQL_Result[4]
							TTIME_Result["MAX"][i][SQL_Result[0]] = SQL_Result[5]
							NTIME_Result["MAX"][i][SQL_Result[0]] = SQL_Result[6]
		# print(CTIME_Result)
		# print(TTIME_Result)
		# print(NTIME_Result)

		# 將收到的資料轉成圖表所需資料
		Chart_Title = {"CTIME":"Central Time Rate", "TTIME":"Target Time Rate", "NTIME":"Normal Time Rate"}
		Chart_Y_Label = {"CTIME":"Rate", "TTIME":"Rate", "NTIME":"Rate"}
		Chart_Data = {"CTIME":[], "TTIME":[], "NTIME":[]}
		Chart_err = {"CTIME":[], "TTIME":[], "NTIME":[]}
		
		for name in Chart_ModelName:
			dataName = Chart_ModelName[name]
			# Central Time Rate Part
			rowData = []
			rowErr = []
			for i in range(len(CTIME_Result["AVG"])):
				if CTIME_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(CTIME_Result["AVG"][i][tp])
						rowErr.append((CTIME_Result["MAX"][i][tp] - CTIME_Result["AVG"][i][tp]))
			Chart_Data["CTIME"].append(rowData)
			Chart_err["CTIME"].append(rowErr)
			# Target Time Rate Part
			rowData = []
			rowErr = []
			for i in range(len(TTIME_Result["AVG"])):
				if TTIME_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(TTIME_Result["AVG"][i][tp])
						rowErr.append((TTIME_Result["MAX"][i][tp] - TTIME_Result["AVG"][i][tp]))
			Chart_Data["TTIME"].append(rowData)
			Chart_err["TTIME"].append(rowErr)
			# Normal Time Rate
			rowData = []
			rowErr = []
			for i in range(len(NTIME_Result["AVG"])):
				if NTIME_Result["AVG"][i]["Model"] == dataName:
					for tp in Chart_X_Label:
						rowData.append(NTIME_Result["AVG"][i][tp])
						rowErr.append((NTIME_Result["MAX"][i][tp] - NTIME_Result["AVG"][i][tp]))
			Chart_Data["NTIME"].append(rowData)
			Chart_err["NTIME"].append(rowErr)

		# print(Chart_Data)
		# print(Chart_err)

		# 開始繪圖
		VIEW_DrawChart_Bar(
			chID=3,
			chartTitle=Chart_Title,
			x_label=Chart_X_Label,
			y_label=Chart_Y_Label,
			barWidth=Chart_BarWidth,
			barData=Chart_Data,
			barError=Chart_err,
			barLabel=Chart_ModelNameShow
		)

		# 將數據輸出在CLI上
		for title in Chart_Title:
			VIEW = cv2.imread("_myTemp_/figureVIEW(TBI %s).png" %(Chart_Title[title]))
			cv2.imshow("figureVIEW(TBI %s).png" %(Chart_Title[title]), VIEW)
		
		# VIEW3 = cv2.imread("_myTemp_/figureVIEW3.png")
		# cv2.imshow("figureVIEW3", VIEW3)
		
		Divider = "-----------" # 分隔線
		subDivider = ""
		for i in range(17):
			subDivider = subDivider + "-"
		for i in range(len(Chart_X_Label)):
			Divider = Divider + subDivider
		
		for row in Chart_Title:
			# 標題
			print("[Eight-arm Maze Rat (TBI %s)]" %(Chart_Title[row]))
			# 欄位名
			print("|%-10s" %("Model"), end="")
			for tp in Chart_X_Label:
				print("|%-16s" %(tp), end="")
			print()
			# 資料欄
			for mod in Chart_ModelName:
				print("%-11s" %(mod), end="")
				idx = Chart_ModelNameShow.index(mod)
				for i in range(len(Chart_Data[row][idx])):
					dataStr = "%0.2f(%0.2f)" %(Chart_Data[row][idx][i], (Chart_err[row][idx][i]))
					print("%-17s" %(dataStr), end="")
				print()

			print(Divider)
		print("P.S. Data format: Average data (Positive error value)")