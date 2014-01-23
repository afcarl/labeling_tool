####################
# General Settings #
####################
TRANSL_SENSITIVITY = 11 
ROT_SENSITIVITY = 50
ZOOM_SENSITIVITY = 2.5
MATCH_OBJ_HOTKEY = 'x'
TOGGLE_DEBUG_HOTKEY = 'd'
VERBOSE = True
#How frequently progress gets printed when parsing files in VERBOSE mode
PROGRESS_GRANULARITY = 3000 

################
# ICP Settings #
################
ICP_HOTKEY = 'i'
ICP_SAMPLING_SIZE = 0.5
#Threshold to stop iterating
ICP_THRESH = 0.005
ICP_MAX_ITERS = 10

########################
# Rerendering Settings #
########################
RRENDER_HOTKEY = 'r'
RRENDER_INPUT_IMG = 'NP3_165.jpg'

#For in-app rerendering
RRENDER_TOGGLE_HOTKEY = 't'
RRENDER_INTERVAL = 5 #Rerender every N sec
RRENDER_K = None
RRENDER_DISTORT = None
RRENDER_SKIP = 8
MINI_IMAGE_SIZE = 1 #range from 0 (smallest) to 1 (full screen)

###################
# Random Settings #
###################
#Parse every Nth vertex in the pointcloud (speed up for debugging) 1=Parse all vertices
PC_FILEREAD_SKIP = 1
AUTOCONFIG_URL = "http://127.0.0.1:5000/getconfig"
MATCH_FUN = None