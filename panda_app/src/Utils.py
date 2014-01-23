from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
from direct.stdpy import threading
#import ast # NOT AVAILABLE IN P3D
import urllib2
import urlparse
import Settings
import os
import traceback

def logError(errmess):
	if isinstance(errmess, Exception):
		tb = traceback.format_exc()
		print "LOGGER:", str(errmess)
		print "Traceback:",tb
	else:
		print "LOG:",str(errmess)

def errorDialog(err):
	if isinstance(err, Exception):
		tb = traceback.format_exc()
		m= str(err)+'\n'
		m+= tb
		createOKDialog(str(m))
	else:
		createOKDialog("Error: "+str(err))


"""
Evaluate a string in the python interpreter
"""
def evalString(text):
	"""
	tree = ast.parse(text)
	wrapped = ast.Interactive(body=tree.body)
	code = compile(wrapped, '', 'single')
	"""
	code = compile(text, '', 'exec')
	eval(code)

"""
Eval a config file. Returns a config dictionary
"""
def evalConfig(text):
	config = dict()
	"""
	tree = ast.parse(text)
	wrapped = ast.Interactive(body=tree.body)
	code = compile(wrapped, '', 'single')
	"""
	code = compile(text, '', 'exec')
	eval(code)
	return config

"""
def setConfig(config):
	config["calibration"]=base_url+"calibration.h5"
	config["point_cloud"]=base_url+"NP3_165.ply"
	config["objects"]=[base_url+"circlefit_mesh.ply", 
	        base_url+"circlefit_mesh2.ply"]
	config["ref_image"]=base_url+"NP3_165.jpg"

	def FINALIZE_MATCH(pcname, meshname, matrix):
	    pass

	config["match_fun"]=FINALIZE_MATCH
	
	Settings.RRENDER_CAM_CALIB_FILE = config["calibration"]
"""

def isURL(target_url):
	return urlparse.urlparse(target_url).scheme != ''

"""
Fetches and reads a file from a URL. Returns a string containing the
contents of the resource.
"""
def fetchFromURL(target_url, opt='r'):
	file = urllib2.urlopen(target_url) # it's a file like object and works just like a file
	s = file.read()
	file.close()
	return s

"""
Opens and returns an image from a URL or filename
"""
def openPNM(fname_or_url):
	pnm = PNMImage()
	if isURL(fname_or_url):
		s = fetchFromURL(fname_or_url, 'rb')
		pnm.read(StringStream(s))
		pass
	else:
		fs = FileStream(fname_or_url)
		pnm.read(fs)
	return pnm

"""
Opens a file or a url
"""
def openAll(filename, mode= 'rb'):
	if os.path.isfile(filename):
		return open(filename, mode)
	return urllib2.urlopen(filename)

def runInThread(f, _args):
	p = threading.Thread(target= f, args= _args)
	p.start()
	return p

def runInThreadFuture(f, *args):
	def ns(): pass
	def runFuture():
		retval = f(args)
		ns.retval = retval
	p = threading.Thread(target= runFuture)
	p.start()
	def getFuture():
		p.join()
		return ns.retval
	return getFuture

def createLoadBar(message = "", autodelete = True):
	def LoadBar(): pass
	LoadBar.bar = DirectWaitBar(text = "", value = 50, pos = (0,.4,.4))
	LoadBar.textObject = OnscreenText(text = message, pos = (0,0.55), 
	scale = 0.07,fg=(1,1.0,1.0,1),align=TextNode.ACenter,mayChange=1)

	def delete():
		if not LoadBar.valid:
			return
		LoadBar.bar.destroy()
		LoadBar.textObject.destroy()	
		LoadBar.valid = False
	LoadBar.delete = delete

	def _incr(i):
		val = LoadBar.bar['value']
		LoadBar.set(val+i)

	def _set(i):
		if not LoadBar.valid:
			return
		LoadBar.bar['value'] = i
		base.graphicsEngine.renderFrame()	
		if autodelete and ( LoadBar.bar['value'] >= 100):
			delete()

	LoadBar.incr = _incr
	LoadBar.set = _set
	LoadBar.valid = True
	return LoadBar

def createOKDialog(txt):
	def okCommand(arg):
		okdialog.destroy()
		#okdialog.cleanup()
	okdialog = OkDialog(text = txt,command = okCommand)
	return okdialog