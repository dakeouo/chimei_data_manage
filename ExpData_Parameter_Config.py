CURRENT_MODEL_ID = 0
CURRENT_MODEL_LIST = ["TBI", "RADIA", "HI"]

ModelList = ['請選擇...', "TBI", "RADIA", "HI"]
FilterData_Group = {
	"TBI": ['不限定', 'Sham', 'Sham+NS', 'Sham+MSC', 'rTBI+NS', 'rTBI+MSC'],
	"RADIA": ['不限定', 'Sham', '0gy', '2gy', '4gy', '10gy'],
	"HI": ['不限定', 'Sham', 'LPS', 'LPS+MSC', 'HIP', 'HIP+MSC', 'HIS', 'HIS+MSC']
}
IMG_TBI_G = {
	"TBI": ['請選擇組別', 'Sham', 'Sham+NS', 'Sham+MSC', 'rTBI+NS', 'rTBI+MSC'],
	"RADIA": ['請選擇組別', 'Sham', '0gy', '2gy', '4gy', '10gy'],
	"HI": ['請選擇組別', 'Sham', 'Sham+MSC', 'LPS+NS', 'LPS+MSC', 'HIP+NS', 'HIP+MSC', 'HIS+NS', 'HIS+MSC']
}
CURRENT_CONVERT_TP_ID = 0
CURRENT_TimepointList = {
	0:['請選擇時間點...', '手術前', '手術後7天', '手術後14天', '手術後28天', '手術後3個月', '手術後6個月', '手術後9個月'],
	1:['請選擇時間點...', '手術後', '手術後4週', '手術後5週', '手術後6週', '手術後8週']
}
CURRENT_CONVERT_TP_STR2ID_LIST = {
	0:{
		'手術前':'pre', 
		'手術後7天':'00M07D', '手術後14天':'00M14D', 
		'手術後28天':'00M28D', '手術後3個月':'03M00D', 
		'手術後6個月':'06M00D', '手術後9個月':'09M00D'
	},
	1:{ # 目前為HI專用
		'手術後':'past', 
		'手術後4週':'01M00D', '手術後5週':'01M07D', 
		'手術後6週':'01M14D', '手術後8週':'02M00D' 
	}
}
CURRENT_CONVERT_TP_ID2STR_LIST = {
	0:{
		"pre":'手術前', 
		"00M07D":'手術後7天', "00M14D":'手術後14天', 
		"00M28D":'手術後28天', "03M00D":'手術後3個月', 
		"06M00D":'手術後6個月', "09M00D":'手術後9個月'
	
	},
	1:{ # 目前為HI專用
		'past':'手術後', 
		'01M00D':'手術後4週', '01M07D':'手術後5週', 
		'01M14D':'手術後6週', '02M00D':'手術後8週'
	}
}
CURRENT_CONVERT_TP_ID2SHOW_LIST = {
	0:{
		"pre": "Pre", 
		"00M07D": "D07", "00M14D": "D14", 
		"00M28D": "D28", "03M00D": "M03", 
		"06M00D": "M06", "09M00D": "M09"
	
	},
	1:{ # 目前為HI專用
		"past": "Past", 
		"01M00D": "W04", "01M07D": "W05", 
		"01M14D": "W06", "02M00D": "W08"
	}
}
CURRENT_TP_OnlyID_LIST = {
	0:['pre', '00M07D', '00M14D', '00M28D', '03M00D', '06M00D', '09M00D'],
	1:['past', '01M00D', '01M07D', '01M14D', '02M00D']
}
CURRENT_TP_OnlyShow_LIST = {
	0:['不限定', 'Pre', 'D07', 'D14', 'D28', 'M03', 'M06', 'M09'],
	1:['不限定', 'Past', 'W04', 'W05', 'W06', 'W08']
}

TP_Color0 = { #綠色(無手寫資料)
	"Pre": "OliveDrab", 
	"D07": "OliveDrab1", "D14": "OliveDrab2", "D28": "OliveDrab3", 
	"M03": "DarkOliveGreen1", "M06": "DarkOliveGreen2", "M09": "DarkOliveGreen3",
	"Past": "OliveDrab", 
	"W04": "OliveDrab1", "W05": "OliveDrab2", "W06": "OliveDrab3",
	"W08": "DarkOliveGreen1"
}
TP_Color1 = { #藍色(有手寫資料，但CSV/IMG還沒上傳)
	"Pre": "SteelBlue", 
	"D07": "SkyBlue1", "D14": "SkyBlue2", "D28": "SkyBlue3", 
	"M03": "DeepSkyBlue1", "M06": "DeepSkyBlue2", "M09": "DeepSkyBlue3",
	"Past": "SteelBlue", 
	"W04": "SkyBlue1", "W05": "SkyBlue2", "W06": "SkyBlue3", 
	"W08": "DeepSkyBlue1"
}
TP_Color2 = { #黃色(有手寫資料，但只有CSV上傳)
	"Pre": "DarkGoldenrod", 
	"D07": "gold", "D14": "gold2", "D28": "gold3", 
	"M03": "goldenrod", "M06": "goldenrod2", "M09": "goldenrod3",
	"Past": "DarkGoldenrod", 
	"W04": "gold", "W05": "gold2", "W06": "gold3", 
	"W08": "goldenrod"
}
TP_Color3 = { #橘色(有手寫資料，但只有IMG上傳)
	"Pre": "DarkOrange", 
	"D07": "orange", "D14": "orange2", "D28": "orange3", 
	"M03": "DarkOrange2", "M06": "DarkOrange3", "M09": "DarkOrange4",
	"Past": "DarkOrange", 
	"W04": "orange", "W05": "orange2", "W06": "orange3", 
	"W08": "DarkOrange2"
}
TP_Color4 = { #紫色(有手寫資料，IMG/CSV都上傳)
	"Pre": "MediumOrchid", 
	"D07": "MediumOrchid1", "D14": "MediumOrchid2", "D28": "MediumOrchid3", 
	"M03": "DarkOrchid1", "M06": "DarkOrchid2", "M09": "DarkOrchid3",
	"Past": "MediumOrchid", 
	"W04": "MediumOrchid1", "W05": "MediumOrchid2", "W06": "MediumOrchid3", 
	"W08": "DarkOrchid1"
}

def ModelGroupCheck(models, ratGroup, timepoint):
	if models == "TBI":
		if timepoint == "pre":
			ratGroup = "Sham"
		elif timepoint != "pre" and ratGroup == "Sham":
			ratGroup = "Sham+NS"
		elif ratGroup == "sham+NS":
			ratGroup = "Sham+NS"
		elif ratGroup == "sham+MSC":
			ratGroup = "Sham+MSC"
		elif ratGroup == "TBI+NS" or ratGroup == "Control":
			ratGroup = "rTBI+NS"
		elif ratGroup == "TBI+MSC":
			ratGroup = "rTBI+MSC" 
	elif models == "HI":
		if ratGroup == "sham":
			ratGroup = "Sham"
		elif ratGroup == "sham+MSC":
			ratGroup = "Sham+MSC"
		elif ratGroup == "LPS":
			ratGroup = "LPS+NS"
		elif ratGroup == "HIS":
			ratGroup = "HIS+NS"
		elif ratGroup == "HIP":
			ratGroup = "HIP+NS"
	return models, ratGroup, timepoint