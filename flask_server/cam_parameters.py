calibration_dict = eval( open('calibration.txt').read().lower())

def getK(camname):
	return calibration_dict[camname.lower()+'_k']

def getDistortion(camname):
	return calibration_dict[camname.lower()+'_distortion'][0]
