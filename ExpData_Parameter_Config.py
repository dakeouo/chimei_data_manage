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
	"HI": ['不限定', 'Sham', 'LPS', 'LPS+MSC', 'HIP', 'HIP+MSC', 'HIS', 'HIS+MSC']
}
def ModelGroupCheck(models):
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