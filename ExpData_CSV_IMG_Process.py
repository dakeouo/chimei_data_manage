import cv2
import numpy as np
import csv
from PIL import Image
import os
import math
import shutil

SourceFolder = "" #來原資料夾
DestinationFolder = './SQL_FILE' #目的資料夾

CURRENT_MODEL_NAME = "TBI"

ARM_UNIT = 8
Pixel2CM_Convert = 170/480
CurrentArm = 0 #當前進臂
IMG_PATH_WINDOWS_IS_OPEN = False

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

def makeBlackImage(color=(0,0,0)): #製造出全黑圖片(10x10)
	pixels = []
	for i in range(0,10):
		row = []
		for j in range(0,10):
			row.append(color)
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

def saveNewIMGRoute_forRatID(imgName, Rat_img, RatID, saveFolder="IMG"): #將IMG存入新的地方
	global DestinationFolder
	fileFullName = '%s/%s/%s/%s.jpg' %(DestinationFolder, saveFolder, RatID, imgName)
	if not os.path.exists('%s/%s' %(DestinationFolder, saveFolder)):
		os.mkdir('%s/%s' %(DestinationFolder, saveFolder))
	if not os.path.exists('%s/%s/%s' %(DestinationFolder, saveFolder, RatID)):
		os.mkdir('%s/%s/%s' %(DestinationFolder, saveFolder, RatID))
	cv2.imwrite(fileFullName, Rat_img)

def saveNewIMGRoute(imgName, Rat_img, saveFolder="IMG"): #將IMG存入新的地方
	global DestinationFolder
	fileFullName = '%s/%s/%s.jpg' %(DestinationFolder, saveFolder, imgName)
	if not os.path.exists('%s/%s' %(DestinationFolder, saveFolder)):
		os.mkdir('%s/%s' %(DestinationFolder, saveFolder))
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

def transfer2CoodinateList(CSV_FileName, expLatency): #將CSV內的資料轉換為一維座標點
	CSV_Info = readCSV2List(CSV_FileName)
	newCSV_Info = []
	tranStart = 0
	# print(len(CSV_Info), expLatency)
	if len(CSV_Info)*0.85 > expLatency:
	# if round(len(CSV_Info)*(1 - 0.8)) > expLatency:
		print("超過Latency範圍!!", len(CSV_Info), expLatency, "%0.4f" %(expLatency/len(CSV_Info)), CSV_FileName)
		tranStart = (len(CSV_Info) - round(expLatency/0.85))*20
		# print(tranStart, len(CSV_Info)*20)
	else:
		tranStart = 0
	PointTot = len(CSV_Info)*20
	# print(PointTot)
	for i in range(tranStart, PointTot):
		row1 = CSV_Info[int(i/20)][int(i%20)].split('[')
		row2 = row1[1].split(']')
		row3 = row2[0].split(',')
		newCSV_Info.append([int(row3[0]), int(row3[1])])
	return newCSV_Info

def RouteInfo(CSV_FileName): #匯入CSV檔路徑資料並整理成每秒20個點
	CSV_Info = readCSV2List(CSV_FileName)
	newRow = []
	for i in range(1,len(CSV_Info)):
		# row = []
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
					if len(newRow) > 0:
						newP = [newRow[len(newRow)-1][0], newRow[len(newRow)-1][0]]
						newRow.append(newP)
				else:
					newRow.append(newP)
		
		newCSV_Info = []
		coodiCount = 0
		coodiRow = []
		for row in newRow:
			if coodiCount < 20:
				# print(row)
				coodiRow.append(row)
				coodiCount = coodiCount + 1
			else:
				newCSV_Info.append(coodiRow)
				coodiCount = 0
				coodiRow = []

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

def showMultiImgPath(Img_PathID, ImgInfo_List=None, ImgFolder="IMG"):
	global DestinationFolder
	global IMG_PATH_WINDOWS_IS_OPEN

	IMG_PATH_WINDOWS_IS_OPEN = True
	IMG_List = []
	imgRowCount = 8 #一排要顯示幾張圖片
	imgColCount = 4 #總共顯示幾排
	imgTotCount = imgRowCount*(imgColCount+1)
	imgWidth = 150 #圖片寬高
	imgTxtH = 25
	imgTitleH = 40
	imgRowList = []

	#顯示目前圖像結果
	# cv2.namedWindow('Experimental Rat Path Trajectory', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
	fileFullPath = '%s/%s/%s' %(DestinationFolder, ImgFolder, Img_PathID[0])
	for i in range(imgTotCount):
		fileFullName = '%s/%s_%03d.jpg' %(fileFullPath, Img_PathID[0], i+1)
		# print(fileFullName)
		try:
			newImg = cv2.imread(fileFullName)
			bg = makeBlackImage((50,50,50))
			bg = cv2.resize(bg,(newImg.shape[1]+4, newImg.shape[0]+4),interpolation=cv2.INTER_CUBIC)
			bg[2:newImg.shape[0]+2,2:newImg.shape[1]+2] = newImg
			newImg = cv2.resize(bg,(imgWidth, imgWidth),interpolation=cv2.INTER_CUBIC)
		except:
			newImg = makeBlackImage()
			newImg = cv2.resize(newImg,(imgWidth, imgWidth),interpolation=cv2.INTER_CUBIC)
		if i % imgRowCount == 0:
			if i == 0:
				pass
			elif math.floor(i / imgRowCount) == 1:
				imgRowList = newImg1
			else:
				imgRowList = np.vstack([imgRowList, newImg1])
			newImg1 = newImg	
		else:
			newImg1 = np.hstack([newImg1, newImg])

	#圖像結果詳細資料
	newImgInfo = makeBlackImage((50,50,50))
	newImgInfo = cv2.resize(newImgInfo,(imgWidth*imgRowCount, imgTxtH),interpolation=cv2.INTER_CUBIC)
	CTY = 16
	if ImgInfo_List != None:
		cv2.putText(newImgInfo, "Rat ID:", (10,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgInfo, str(Img_PathID[0]), (60,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgInfo, "Number of image displayed:", (320,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgInfo, str(imgTotCount), (530,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgInfo, "Size of image displayed:", (620,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgInfo, "{0} x {0}".format(imgWidth), (800,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,255), 1, cv2.LINE_AA)
	
	newImgContent = np.vstack([newImgInfo, imgRowList])

	#圖像結果標題
	newImgTitle = makeBlackImage((30,30,30))
	newImgTitle = cv2.resize(newImgTitle,(imgWidth*imgRowCount, imgTitleH),interpolation=cv2.INTER_CUBIC)
	CTY = 27
	if ImgInfo_List != None:
		cv2.putText(newImgTitle, "Model:", (10,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "TBI", (85,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Timepoint:", (230,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[0]), (350,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Groups:", (470,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[1]), (560,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Quantity:", (750,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[2]), (850,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Page:", (950,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "%d / %d" %(ImgInfo_List[3],math.ceil(ImgInfo_List[2]/1)), (1020,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		
	newImgResult = np.vstack([newImgTitle, newImgContent])
	cv2.imshow("Experimental Rat Path Trajectory", newImgResult)

def ExportImg2Folder(Model, Export_Folder, Img_PathID, ImgInfo, ImgFolder="IMG"):
	global DestinationFolder
	fileFullName = '%s/%s/%s.jpg' %(DestinationFolder, ImgFolder, Img_PathID)
	newImg = cv2.imread(fileFullName)
	newExportFullName = '%s/%s_%s_%s_%s.jpg' %(Export_Folder, Model, ImgInfo[0], ImgInfo[1], Img_PathID)
	cv2.imwrite(newExportFullName, newImg)

def ExportCSV2Folder(Model, Export_Folder, CSV_PathID, CSVInfo, CSVFolder="CSV"):
	global DestinationFolder
	fileFullName = '%s/%s/%s.csv' %(DestinationFolder, CSVFolder, CSV_PathID)
	newCSV = readCSV2List(fileFullName)
	newExportFullName = '%s/%s_%s_%s_%s.csv' %(Export_Folder, Model, CSVInfo[0], CSVInfo[1], CSV_PathID)
	writeData2CSV(newExportFullName, "w", newCSV[0])
	for i in range(1,len(newCSV)):
		writeData2CSV(newExportFullName, "a", newCSV[i])

def showImgPath(Img_PathID, ImgInfo_List=None, ImgFolder="IMG"):
	global DestinationFolder
	global IMG_PATH_WINDOWS_IS_OPEN, CURRENT_MODEL_NAME

	IMG_PATH_WINDOWS_IS_OPEN = True
	IMG_List = []
	imgWidth = 320
	imgTxtH = 25
	imgTitleH = 40

	#顯示目前圖像結果
	# cv2.namedWindow('Experimental Rat Path Trajectory', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
	for i in range(8):
		if i < len(Img_PathID):
			fileFullName = '%s/%s/%s.jpg' %(DestinationFolder, ImgFolder, Img_PathID[i])
			# print(fileFullName)
			newImg1 = cv2.imread(fileFullName)
			newImg1 = cv2.resize(newImg1,(imgWidth, imgWidth),interpolation=cv2.INTER_CUBIC)
			newText = makeBlackImage((30,30,30))
			newText = cv2.resize(newText,(imgWidth,imgTxtH),interpolation=cv2.INTER_CUBIC)
			cv2.putText(newText, "ID %s" %(Img_PathID[i]), (10,16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1, cv2.LINE_AA)
			newImg = np.vstack([newImg1, newText])
		else:
			newImg = makeBlackImage()
			newImg = cv2.resize(newImg,(imgWidth, imgWidth+imgTxtH),interpolation=cv2.INTER_CUBIC)
		IMG_List.append(newImg)
	newImgLine1 = np.hstack([IMG_List[0], IMG_List[1]])
	newImgLine2 = np.hstack([IMG_List[4], IMG_List[5]])
	for i in range(2, 4):
		newImgLine1 = np.hstack([newImgLine1, IMG_List[i]])
		newImgLine2 = np.hstack([newImgLine2, IMG_List[i+4]])
	newImgLineAll = np.vstack([newImgLine1, newImgLine2])

	#圖像結果標題
	newImgTitle = makeBlackImage((30,30,30))
	newImgTitle = cv2.resize(newImgTitle,(imgWidth*4, imgTitleH),interpolation=cv2.INTER_CUBIC)
	CTY = 27
	if ImgInfo_List != None:
		cv2.putText(newImgTitle, "Model:", (10,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(CURRENT_MODEL_NAME), (85,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Timepoint:", (230,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[0]), (350,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Groups:", (470,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[1]), (560,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Quantity:", (750,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, str(ImgInfo_List[2]), (850,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "Page:", (950,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1, cv2.LINE_AA)
		cv2.putText(newImgTitle, "%d / %d" %(ImgInfo_List[3],math.ceil(ImgInfo_List[2]/8)), (1020,CTY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 1, cv2.LINE_AA)
		
	newImgResult = np.vstack([newImgTitle, newImgLineAll])
	cv2.imshow("Experimental Rat Path Trajectory", newImgResult)

def Route2_FullColor_Img(ExpDate, ExpRatDataNo, ExpLatency):
	global DestinationFolder, Pixel2CM_Convert

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)
	# print(len(RoutePath))

	# 繪製圖片
	RouteCount = len(RoutePath)
	colorLevel1 = 120*20

	# 繪製前一分鐘圖片
	newImg = makeBlackImage()
	newImg = cv2.resize(newImg,(480, 480),interpolation=cv2.INTER_CUBIC)
	# if RouteCount < colorLevel1:
	# 	Level1End = RouteCount
	# else:
	# 	Level1End = colorLevel1
	
	nowColor = [32, 32, 32]
	colorIdx = 0
	colorPlus = 16
	for i in range(0, RouteCount):
		cv2.circle(newImg, convert(RoutePath[i]), 1, (nowColor[2], nowColor[1], nowColor[0]), -1)
		if (i%(20*10)) == 0:
			if (nowColor[colorIdx] + colorPlus) < 255 and (nowColor[colorIdx] + colorPlus) > 0:
				nowColor[colorIdx] = nowColor[colorIdx] + colorPlus
			else:
				if colorIdx < 2:
					colorIdx = colorIdx + 1
				else:
					colorIdx = 0
					colorPlus = -colorPlus
			# print(nowColor)
	# saveNewIMGRoute(ExpRatDataNo, newImg, "IMG_Front(2min)")
	saveNewIMGRoute(ExpRatDataNo, newImg, "IMG_FullColor")

def Route2_Colorful_Img(ExpDate, ExpRatDataNo, ExpLatency):
	global DestinationFolder, Pixel2CM_Convert

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)

	# 繪製圖片
	newImg = makeBlackImage()
	newImg = cv2.resize(newImg,(480, 480),interpolation=cv2.INTER_CUBIC)
	BGR_Img = makeBlackImage()
	BGR_Img = cv2.resize(BGR_Img,(480, 480),interpolation=cv2.INTER_CUBIC)
	BGR_Times_Img = makeBlackImage()
	BGR_Times_Img = cv2.resize(BGR_Times_Img,(480, 480),interpolation=cv2.INTER_CUBIC)
	RouteCount = len(RoutePath)
	pathColor = [ #深灰 紅 黃 (橘) 藍 (紫) (綠) 白
		(64, 64, 64), (16, 16, 255), (16, 255, 255), (16, 128, 255), 
		(255, 64, 64), (255, 32, 192), (16, 255, 16), (255, 255, 255)
	]
	# pathColor = [ #深灰 紅 綠 (黃) 藍 (洋紅) (水藍) 白
	# 	(64, 64, 64), (0, 0, 255), (0, 255, 0), (0, 255, 255), 
	# 	(255, 0, 0), (255, 0, 255), (255, 255, 0), (255, 255, 255)
	# ]
	pathCoodi = []
	pathValue = []
	colorLevel1 = 2*60*20
	colorLevel2 = 5*60*20
	colorLevel3 = 8*60*20
	for i in range(0, RouteCount):
		nowI = i
		if nowI < colorLevel1:
			try:
				idx = pathCoodi.index(RoutePath[nowI])
			except ValueError:
				idx = -1
			if idx == -1:
				pathCoodi.append(RoutePath[nowI])
				pathValue.append([1,0,0,0])
			else:
				pathValue[idx][0] = pathValue[idx][0] + 1
		elif (nowI >= colorLevel1) and (nowI < colorLevel2):
			try:
				idx = pathCoodi.index(RoutePath[nowI])
			except ValueError:
				idx = -1
			if idx == -1:
				pathCoodi.append(RoutePath[nowI])
				pathValue.append([0,1,0,0])
			else:
				pathValue[idx][1] = pathValue[idx][1] + 1
		elif (nowI >= colorLevel2) and (nowI < colorLevel3):
			try:
				idx = pathCoodi.index(RoutePath[nowI])
			except ValueError:
				idx = -1
			if idx == -1:
				pathCoodi.append(RoutePath[nowI])
				pathValue.append([0,0,1,0])
			else:
				pathValue[idx][2] = pathValue[idx][2] + 1
		elif (nowI >= colorLevel3):
			try:
				idx = pathCoodi.index(RoutePath[nowI])
			except ValueError:
				idx = -1
			if idx == -1:
				pathCoodi.append(RoutePath[nowI])
				pathValue.append([0,0,0,1])
			else:
				pathValue[idx][3] = pathValue[idx][3] + 1
	# print(len(pathCoodi))
	for i in range(0, len(pathCoodi)):
		nowI = len(pathCoodi) - i - 1
		idx = 0
		ptimes = pathValue[nowI][3]
		for i in range(4):
			if pathValue[nowI][i] > 0 and i < 3:
				idx = idx + pow(2, i)
		ptimes = round(math.sqrt(ptimes))
		ptimes = 1
		if idx == 0:
			cv2.circle(BGR_Img, convert(pathCoodi[nowI]), ptimes, (100,100,100), -1)
			cv2.circle(newImg, convert(pathCoodi[nowI]), ptimes, pathColor[idx], -1)
	
	for i in range(0, len(pathCoodi)):
		nowI = len(pathCoodi) - i - 1
		idx = 0
		ptimes = 0
		for i in range(3):
			ptimes = ptimes + pathValue[nowI][i]
			if pathValue[nowI][i] > 0 and i < 3:
				idx = idx + pow(2, i)
		ptimes1 = ptimes
		ptimes = round(math.sqrt(ptimes))
		ptimes = 1
		if idx == 1 or idx == 2 or idx == 4:
			cv2.circle(newImg, convert(pathCoodi[nowI]), ptimes, pathColor[idx], -1)
			BGR_Color = [int((idx & 4)/4)*255, int((idx & 2)/2)*255, int((idx & 1)/1)*255]
			cv2.circle(BGR_Img, convert(pathCoodi[nowI]), ptimes, convert(BGR_Color), -1)
			BGR_Times = math.floor(ptimes1 * (128/1000)) + 127
			if BGR_Times > 255:
				BGR_Times = 255
			cv2.circle(BGR_Times_Img, convert(pathCoodi[nowI]), 1, (BGR_Times, BGR_Times, BGR_Times), -1)
	
	for i in range(0, len(pathCoodi)):
		nowI = len(pathCoodi) - i - 1
		idx = 0
		ptimes = 0
		for i in range(3):
			ptimes = ptimes + pathValue[nowI][i]
			if pathValue[nowI][i] > 0 and i < 3:
				idx = idx + pow(2, i)
		ptimes1 = ptimes
		ptimes = round((math.sqrt(ptimes)))
		ptimes = 1
		if idx == 3 or idx == 5 or idx == 6:
			cv2.circle(newImg, convert(pathCoodi[nowI]), ptimes, pathColor[idx], -1)
			BGR_Color = [int((idx & 4)/4)*255, int((idx & 2)/2)*255, int((idx & 1)/1)*255]
			cv2.circle(BGR_Img, convert(pathCoodi[nowI]), ptimes, convert(BGR_Color), -1)
			BGR_Times = math.floor(ptimes1 * (128/1000)) + 127
			if BGR_Times > 255:
				BGR_Times = 255
			cv2.circle(BGR_Times_Img, convert(pathCoodi[nowI]), 1, (BGR_Times, BGR_Times, BGR_Times), -1)
	
	for i in range(0, len(pathCoodi)):
		nowI = len(pathCoodi) - i - 1
		idx = 0
		ptimes = 0
		for i in range(3):
			ptimes = ptimes + pathValue[nowI][i]
			if pathValue[nowI][i] > 0 and i < 3:
				idx = idx + pow(2, i)
		ptimes1 = ptimes
		ptimes = round((math.sqrt(ptimes)))
		ptimes = 1
		if idx == 7:
			cv2.circle(newImg, convert(pathCoodi[nowI]), ptimes, pathColor[idx], -1)
			BGR_Color = [int((idx & 4)/4)*255, int((idx & 2)/2)*255, int((idx & 1)/1)*255]
			cv2.circle(BGR_Img, convert(pathCoodi[nowI]), ptimes, convert(BGR_Color), -1)
			BGR_Times = math.floor(ptimes1 * (128/1000)) + 127
			if BGR_Times > 255:
				BGR_Times = 255
			cv2.circle(BGR_Times_Img, convert(pathCoodi[nowI]), 1, (BGR_Times, BGR_Times, BGR_Times), -1)
	saveNewIMGRoute(ExpRatDataNo, newImg, "IMG_colorful")
	saveNewIMGRoute(ExpRatDataNo, BGR_Img, "IMG_colorful_1")
	saveNewIMGRoute(ExpRatDataNo, BGR_Times_Img, "IMG_colorful_1_times")

def Route2_Seg4Part_Img(ExpDate, ExpRatDataNo, ExpLatency, ratGroups):
	global DestinationFolder, Pixel2CM_Convert

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)
	# print(len(RoutePath))

	# 刪除資料夾
	try:
		shutil.rmtree("%s/IMG_Seg4Part/%s" %(DestinationFolder, ExpRatDataNo))
	except OSError as e:
		print(e)

	# 繪製圖片
	RouteCount = len(RoutePath)
	segBase = round(RouteCount/4)
	seg4Gate = [0, segBase*1, segBase*2, segBase*3, RouteCount]
	print(seg4Gate)
	for i in range(4):
		newImg = makeBlackImage()
		newImg = cv2.resize(newImg,(480, 480),interpolation=cv2.INTER_CUBIC)
		minR = seg4Gate[i]
		maxR = seg4Gate[i+1]
		for j in range(minR, maxR):
			cv2.circle(newImg, convert(RoutePath[j]), 2, (0,255,0), -1)
		imgName = "%s_%s_%s" %(ExpRatDataNo, ratGroups, chr(65+i))
		saveNewIMGRoute_forRatID(imgName, newImg, "Part%s" %(chr(65+i)), "IMG_Seg4Part")

def Route2_Segment_Img(ExpDate, ExpRatDataNo, ExpLatency, ratGroups):
	global DestinationFolder, Pixel2CM_Convert

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)
	# print(len(RoutePath))

	# 刪除資料夾
	try:
		shutil.rmtree("%s/IMG_Segment/%s" %(DestinationFolder, ExpRatDataNo))
	except OSError as e:
		print(e)

	# 繪製圖片
	RouteCount = len(RoutePath)
	segSec = 3*20
	segTot = 300
	for i in range(0, segTot):
		newImg = makeBlackImage()
		newImg = cv2.resize(newImg,(480, 480),interpolation=cv2.INTER_CUBIC)
		minR = segSec*i
		maxR = segSec*(i+1)
		for j in range(minR, maxR):
			if j < RouteCount:
				cv2.circle(newImg, convert(RoutePath[j]), 2, (0,255,0), -1)
			else:
				break
		imgName = "%s_%s_%03d" %(ExpRatDataNo, ratGroups, (i+1))
		saveNewIMGRoute_forRatID(imgName, newImg, "%s_%s" %(ExpRatDataNo, ratGroups), "IMG_Segment")
		
def Route2_1Min_Img(ExpDate, ExpRatDataNo, ExpLatency, ratGroups):
	global DestinationFolder, Pixel2CM_Convert

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)
	# print(len(RoutePath))

	# 繪製圖片
	RouteCount = len(RoutePath)
	colorLevel1 = 120*20

	# 繪製前一分鐘圖片
	newImg = makeBlackImage()
	newImg = cv2.resize(newImg,(480, 480),interpolation=cv2.INTER_CUBIC)
	if RouteCount < colorLevel1:
		Level1End = RouteCount
	else:
		Level1End = colorLevel1
	for i in range(0, Level1End):
		cv2.circle(newImg, convert(RoutePath[i]), 1, (0,255,0), -1)
	# saveNewIMGRoute(ExpRatDataNo, newImg, "IMG_Front(2min)")
	saveNewIMGRoute(ExpRatDataNo + "_%s" %(ratGroups), newImg, "IMG_Front(2min)")

	# 繪製最後一分鐘圖片
	newImg1 = makeBlackImage()
	newImg1 = cv2.resize(newImg1,(480, 480),interpolation=cv2.INTER_CUBIC)
	if RouteCount > colorLevel1:
		Level2Start = RouteCount - colorLevel1
	else:
		Level2Start = 0
	for i in range(Level2Start, RouteCount):
		cv2.circle(newImg1, convert(RoutePath[i]), 1, (0,255,0), -1)
	# saveNewIMGRoute(ExpRatDataNo, newImg1, "IMG_Back(2min)")
	saveNewIMGRoute(ExpRatDataNo + "_%s" %(ratGroups), newImg1, "IMG_Back(2min)")


def testingColor():
	pathColor = [ #深灰 紅 橘 黃 藍 紫 綠 白
		(64, 64, 64), (16, 16, 255), (16, 255, 255), (16, 128, 255), 
		(255, 64, 64), (255, 32, 192), (16, 255, 16), (255, 255, 255)
	]

	testImg = makeBlackImage()
	testImg = cv2.resize(testImg,(300, 50),interpolation=cv2.INTER_CUBIC)
	for i in range(len(pathColor)):
		cv2.circle(testImg, (20+30*i, 20), 10, pathColor[i], -1)
	cv2.imshow("Testing Colorful", testImg)
	cv2.waitKey(0)

def RouteProcess(ExpDate, ExpRatDataNo, ExpLatency): #實驗日期[年, 月, 日], 實驗大鼠編號, 實驗總時間
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

	# 讀取CSV內所有路徑座標點[會變成一維陣列]
	CSV_Path = "%s/CSV/%s.csv" %(DestinationFolder, ExpRatDataNo)
	RoutePath = transfer2CoodinateList(CSV_Path, ExpLatency)
	# print(RoutePath)

	# 計算距離
	totDistance = 0
	CATE_TIME_SEC["Central"] = CATE_TIME_SEC["Target"] = CATE_TIME_SEC["Normal"] = 0
	CATE_DIS_CM["Central"] = CATE_DIS_CM["Target"] = CATE_DIS_CM["Normal"] = 0
	for i in range(1, len(RoutePath)):
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
	totCSVTime = CATE_TIME_SEC["Target"] + CATE_TIME_SEC["Normal"] + CATE_TIME_SEC["Central"]
	rate = ExpLatency / totCSVTime
	CATE_TIME_SEC["Target"] = CATE_TIME_SEC["Target"] * rate
	CATE_TIME_SEC["Normal"] = CATE_TIME_SEC["Normal"] * rate
	CATE_TIME_SEC["Central"] = CATE_TIME_SEC["Central"] * rate
	# print(totDistance)
	# print(CATE_DIS_CM)
	# print(CATE_TIME_SEC)

	return totDistance, CATE_DIS_CM, CATE_TIME_SEC

if __name__ == '__main__':
	pass
	# CSV_List, Rat_Info = listRatCSVFile(SourceFolder) #取得目前所有CSV的路徑
	# print("Total of Original Data: %d" %(len(CSV_List)))