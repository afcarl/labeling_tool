from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
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
	if text.startswith("FAILURE"):
	    createOKDialog("Could not fetch scene. Reason: ("+text+")") 
	    return None
	config = dict()
	"""
	tree = ast.parse(text)
	wrapped = ast.Interactive(body=tree.body)
	code = compile(wrapped, '', 'single')
	"""
	code = compile(text, '', 'exec')
	eval(code)
	return config

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
	try:
		pnm = PNMImage()
		if isURL(fname_or_url):
			s = fetchFromURL(fname_or_url, 'rb')
			pnm.read(StringStream(s))
			pass
		else:
			fs = FileStream(fname_or_url)
			pnm.read(fs)
		return pnm
	except urllib2.HTTPError as e:
		errorDialog(e)
		return None

"""
Opens a file or a url
"""
def openAll(filename, mode= 'rb'):
	if os.path.isfile(filename):
		return open(filename, mode)
	return urllib2.urlopen(filename)

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

"""
Checks version of app against the hardcoded url Settings.VERSIONCHECK_URL
Returns true if app is up to date or cannot be determined (ex. no internet connection)
Returns false if app is confirmed to be outdated
"""
def isAppUpToDate():
	try:
		correct_vers = fetchFromURL(Settings.VERSIONCHECK_URL) #In the format X_XX
	except:
		return True
		
	def parseVersion(v):
		x, y = v.split("_")
		if( (len(x) == 1) and (len(y)==2)):
			x = int(x)
			y = int(y)
			return 100*x+y
		return None

	app_v= parseVersion(Settings.APP_VERSION)
	if( app_v is None):
		return True
	cor_v = parseVersion(correct_vers)
	if( cor_v is None):
		return True

	print "Checking app version: ",app_v," vs ",cor_v
	if( app_v < cor_v):
		return False
	else:
		return True

def checkVersion():
	if( not isAppUpToDate()):
		createOKDialog("Application is not up to date. \nPlease visit the rll.berkeley.edu site and download the updated version.")