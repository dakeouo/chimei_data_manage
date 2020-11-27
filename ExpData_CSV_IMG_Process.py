import cv2
import numpy as np
import csv
from PIL import Image
import os
import math

SourceFolder = "" #來原資料夾
DestinationFolder = './SQL_FILE' #目的資料夾

ARM_UNIT = 8
Pixel2CM_Convert = 170/480
CurrentArm = 0 #當前進臂

ExpData_ArmPos = []  #8臂座標點
ExpData_ArmLine = [] #計算進臂線用=>若臂口朝上[右上(內1), 右下(外1), 左上(內2), 左下(外2)]
ExpData_MaskPos = [] #遮罩要用的座標陣列
ExpData_InLinePoint = [] #進臂線
ExpData_ArmLine_DISTANCE = 65/15 #進臂線距離中間區域距離(臂總長度/進臂線距臂口長度)

CATE_TIME_SEC = {"Central":0, "Target":0, "Normal":0} #各區域所待的時間[中間, 目標臂, 非目標臂]
CATE_DIS_CM = {"Central":0, "Target":0, "Normal":0} #各區域所行走的距離[中間, 目標臂, 非目標臂]

def convert(list):
    return tuple(list)

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

def TwoPointDistance(P1, P2):
	return math.sqrt(pow(P1[0] - P2[0],2) + pow(P1[1] - P2[1],2))

def makeBlackImage(): #製造出全黑圖片(10x10)
	pixels = []
	for i in range(0,10):
		row = []
		for j in range(0,10):
			row.append((0,0,0))
		pixels.append(row)
	array = np.array(pixels, dtype=np.uint8)
	newBlack = Image.fromarray(array)
	newBlack = cv2.cvtColor(np.asarray(newBlack),cv2.COLOR_RGB2BGR)  
	return newBlack

def saveNewCSVRoute(csvName, Rat_route): #將CSV存入新的地方
	global DestinationFolder
	fileFullName = '%s/CSV/%s.csv' %(DestinationFolder, csvName)
	if not os.path.exists('%s/CSV' %(DestinationFolder)):
		os.mkdir('%s/CSV' %(DestinationFolder))
	writeData2CSV(fileFullName, "w", Rat_route[0])
	for i in range(1,len(Rat_route)):
		writeData2CSV(fileFullName, "a", Rat_route[i])

def saveNewIMGRoute(imgName, Rat_img): #將IMG存入新的地方
	global DestinationFolder
	fileFullName = '%s/IMG/%s.jpg' %(DestinationFolder, imgName)
	if not os.path.exists('%s/IMG' %(DestinationFolder)):
		os.mkdir('%s/IMG' %(DestinationFolder))
	cv2.imwrite(fileFullName, Rat_img)

def listRatDataFile(fileType, source): #取得資料夾內所有的CSV檔(8ArmRat)
	DataList = []
	RatInfo = []
	idx = 0
	fTypeCovert = {"CSV":".csv", "IMG":".jpg"}
	for root, dirs, files in os.walk(source): # 當前目錄路徑/當前路徑下所有子目錄/當前路徑下所有子檔案
		for file in files: 
			if os.path.splitext(file)[1] == fTypeCovert[fileType]:
				DataList.append(os.path.join(root, file))
				newRatInfo = PathSplitInfo(idx, os.path.join(root, file), fTypeCovert[fileType])
				RatInfo.append(newRatInfo)
				idx = idx + 1
	return DataList, RatInfo

def PathSplitInfo(idx, path, fileType): #取得路徑整理(儲存資料詳細用)-8ArmRat
	newSplit = path.split('\\')
	newSplit1 = newSplit[1].split(fileType) 	#Model(病因)
	rat_file = newSplit1[0]						#CSV 檔案名稱
	expdate, rat_model, rat_group, rat_id = rat_file.split('_')

	return {"serial":idx, "ExpDate":expdate, "Model":rat_model, "Groups":rat_group, "RatID":rat_id, "FileName":rat_file}

def transfer2CoodinateList(CSV_FileName): #將CSV內的資料轉換為一維座標點
	CSV_Info = readCSV2List(CSV_FileName)
	newCSV_Info = []
	PointTot = len(CSV_Info)*20
	# print(PointTot)
	for i in range(0,PointTot):
		row1 = CSV_Info[int(i/20)][int(i%20)].split('[')
		row2 = row1[1].split(']')
		row3 = row2[0].split(',')
		newCSV_Info.append([int(row3[0]), int(row3[1])])
	return newCSV_Info

def RouteInfo(CSV_FileName): #匯入CSV檔路徑資料並整理成每秒20個點
	CSV_Info = readCSV2List(CSV_FileName)
	newCSV_Info = []
	for i in range(1,len(CSV_Info)):
		row = []
		for j in range(0,len(CSV_Info[i])):
			if CSV_Info[i][j] != "":
				try:
					row1 = CSV_Info[i][j].split('[')
					row2 = row1[1].split(']')
					row3 = row2[0].split(',')
					newP = [int(row3[0]), int(row3[1])]
				except:
					print(CSV_FileName)
					print("[%d,%d]" %(i,j))
				if newP[0] == -20 and newP[1] == -20 and i > 0:
					if j == 0:
						try:
							idx = len(newCSV_Info)-1
							newP = [newCSV_Info[idx][len(newCSV_Info[idx])-1][0], newCSV_Info[idx][len(newCSV_Info[idx])-1][1]]
						except:
							print(CSV_FileName)
							print("[%d,%d]" %(i,j))
							print(len(newCSV_Info)-1)
					else:
						newP = [row[len(row)-1][0], row[len(row)-1][1]]
				row.append(newP)
		newRow = []
		if len(row) != 20:
			for j in range(0,20):
				idx = int((len(row)/20)*j)
				newRow.append([row[idx][0], row[idx][1]])
			newCSV_Info.append(newRow)
		else:
			newCSV_Info.append(row)
	return newCSV_Info

def Line2PointTotalDistance(line_point1, line_point2, target_point):
	return TwoPointDistance(target_point, line_point1) + TwoPointDistance(target_point, line_point2)

def ArmProcess(originArmsData): #8臂座標點處理
	global ExpData_ArmPos, ExpData_ArmLine, ARM_UNIT
	global ExpData_InLinePoint, ExpData_ArmLine_DISTANCE, ExpData_MaskPos
	ExpData_ArmPos = []
	ExpData_ArmLine = []
	
	# 弄成八臂座標點
	for row in originArmsData:
		for x in range(int(len(row)/2)):
			ExpData_ArmPos.append([int(row[x*2]), int(row[x*2 + 1])])
	ExpData_MaskPos = np.array(ExpData_ArmPos)
	
	# 計算進出臂線要用
	for i in range(ARM_UNIT):
		ExpData_ArmLine.append([ExpData_ArmPos[0 + 4*i], ExpData_ArmPos[1 + 4*i], ExpData_ArmPos[3 + 4*i], ExpData_ArmPos[2 + 4*i]])
	
	# 計算進臂線
	mask1 = [0, 0]
	mask2 = [0, 0]
	ExpData_InLinePoint = []
	for i in range(ARM_UNIT):
		Pos1 = [ExpData_ArmLine[i][0][0], ExpData_ArmLine[i][0][1]]
		Pos2 = [ExpData_ArmLine[i][1][0], ExpData_ArmLine[i][1][1]]
		Pos3 = [ExpData_ArmLine[i][2][0], ExpData_ArmLine[i][2][1]]
		Pos4 = [ExpData_ArmLine[i][3][0], ExpData_ArmLine[i][3][1]]
		mask1 = [int(Pos1[0] - (Pos1[0] - Pos2[0])/ExpData_ArmLine_DISTANCE), int(Pos1[1] - (Pos1[1] - Pos2[1])/ExpData_ArmLine_DISTANCE)]
		mask2 = [int(Pos3[0] - (Pos3[0] - Pos4[0])/ExpData_ArmLine_DISTANCE), int(Pos3[1] - (Pos3[1] - Pos4[1])/ExpData_ArmLine_DISTANCE)]
		ExpData_InLinePoint.append([mask1, mask2])
	# print(ExpData_InLinePoint)

def drawArmsImage(nowPoint=None): #繪製目前八臂與進臂線狀況
	global ExpData_ArmPos, ExpData_ArmLine, ARM_UNIT, ExpData_InLinePoint, ExpData_MaskPos

	ArmImage = makeBlackImage()	#產生畫老鼠路徑用圖
	ArmImage = cv2.resize(ArmImage,(480,480),interpolation=cv2.INTER_CUBIC)
	cv2.polylines(ArmImage, [ExpData_MaskPos], True, (0, 255, 255), 1)  #繪製八臂外框
	for row in ExpData_InLinePoint:
		cv2.line(ArmImage, convert(row[0]), convert(row[1]), (0, 128, 255), 1)
	if nowPoint != None:
		cv2.circle(ArmImage, convert(nowPoint), 5, (0,0,255), -1)

	return ArmImage

def DetermineEntryArms(ArmState, coodinate): #判斷是否進臂出臂
	global ExpData_ArmLine, ExpData_InLinePoint

	if ArmState == 0:
		Arm = 1
		for row in ExpData_InLinePoint:
			currentDis = Line2PointTotalDistance(row[0], row[1], coodinate) #目前該座標點與進臂線的距離
			armLevel = TwoPointDistance(row[0], row[1]) #進臂門檻值
			if currentDis < armLevel + 10:
				ArmState = Arm
				break
			Arm = Arm + 1
	else:
		# print(len(ExpData_ArmLine))
		# print(ArmState)
		currentDis = Line2PointTotalDistance(ExpData_ArmLine[ArmState-1][0], ExpData_ArmLine[ArmState-1][2], coodinate) #目前該座標點與進臂線的距離
		armLevel = TwoPointDistance(ExpData_ArmLine[ArmState-1][0], ExpData_ArmLine[ArmState-1][2]) #進臂門檻值
		if currentDis < armLevel + 10:
			ArmState = 0
		else:
			Arm = 1
			for row in ExpData_InLinePoint:
				currentDis = Line2PointTotalDistance(row[0], row[1], coodinate) #目前該座標點與進臂線的距離
				armLevel = TwoPointDistance(row[0], row[1]) #進臂門檻值
				if currentDis < armLevel + 10:
					ArmState = Arm
					break
				Arm = Arm + 1
	return ArmState

def drawDashboard(nowTime=0):
	global CurrentArm, CATE_TIME_SEC, CATE_DIS_CM
	DashImage = makeBlackImage()	#產生畫老鼠路徑用圖
	DashImage = cv2.resize(DashImage,(480,100),interpolation=cv2.INTER_CUBIC)
	
	cv2.putText(DashImage, "NowTime(sec): %d" %(nowTime), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))
	cv2.putText(DashImage, "NowArm: %d" %(CurrentArm), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))
	cv2.putText(DashImage, "Time(sec): [Central] %0.0f [Target] %0.0f [Normal] %0.0f" %(
		CATE_TIME_SEC['Central'], CATE_TIME_SEC['Target'], CATE_TIME_SEC['Normal']
	), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))
	cv2.putText(DashImage, "Distance: [Central] %0.0f [Target] %0.0f [Normal] %0.0f" %(
		CATE_DIS_CM['Central'], CATE_DIS_CM['Target'], CATE_DIS_CM['Normal']
	), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))

	return DashImage

def RouteProcess(ExpDate, ExpRatDataNo): #實驗日期[年, 月, 日], 實驗大鼠編號
	global DestinationFolder, Pixel2CM_Convert
	global CurrentArm, CATE_TIME_SEC, CATE_DIS_CM

	# 處理八臂座標點
	MaskCSV_Path = "%s/MASK/ARMS_LINE(%04d%02d%02d).csv" %(DestinationFolder, ExpDate[0], ExpDate[1], ExpDate[2])
	MaskCSV = readCSV2List(MaskCSV_Path)
	ArmProcess(MaskCSV)

	# # 繪製目前八臂狀況
	# ArmImage = drawArmsImage()
	# ArmImage = np.vstack([drawArmsImage(), drawDashboard()])
	# cv2.imshow("ArmImage", ArmImage)
	# cv2.waitKey(0)

	# 計算像素點轉實際長度(cm)
	Pixel2CM_Convert = 170/TwoPointDistance(ExpData_ArmLine[2][1], ExpData_ArmLine[6][3])
	# print(Pixel2CM_Convert)

	# 讀取CSV內所有路徑座標點
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path)
	# print(RoutePath)

	# 計算距離
	totDistance = 0
	CATE_TIME_SEC["Central"] = CATE_TIME_SEC["Target"] = CATE_TIME_SEC["Normal"] = 0
	CATE_DIS_CM["Central"] = CATE_DIS_CM["Target"] = CATE_DIS_CM["Normal"] = 0
	for i in range(1,len(RoutePath)):
		pixelDis = TwoPointDistance(RoutePath[i-1], RoutePath[i]) * Pixel2CM_Convert
		totDistance = totDistance + pixelDis
		CurrentArm = DetermineEntryArms(CurrentArm, RoutePath[i-1])
		if CurrentArm != 0:
			if CurrentArm%2 == 0:
				CATE_DIS_CM["Target"] = CATE_DIS_CM["Target"] + pixelDis
				CATE_TIME_SEC["Target"] = CATE_TIME_SEC["Target"] + 0.05
			else:
				CATE_DIS_CM["Normal"] = CATE_DIS_CM["Normal"] + pixelDis
				CATE_TIME_SEC["Normal"] = CATE_TIME_SEC["Normal"] + 0.05
		else:
			CATE_DIS_CM["Central"] = CATE_DIS_CM["Central"] + pixelDis
			CATE_TIME_SEC["Central"] = CATE_TIME_SEC["Central"] + 0.05
		# ArmImage = np.vstack([drawArmsImage(RoutePath[i-1]), drawDashboard(int(i/20))])
		# cv2.imshow("ArmImage", ArmImage)
		# cv2.waitKey(1)
	# print(totDistance)
	# print(CATE_DIS_CM)
	# print(CATE_TIME_SEC)
	return totDistance, CATE_DIS_CM, CATE_TIME_SEC

if __name__ == '__main__':
	pass
	# CSV_List, Rat_Info = listRatCSVFile(SourceFolder) #取得目前所有CSV的路徑
	# print("Total of Original Data: %d" %(len(CSV_List)))