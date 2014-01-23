from panda3d.core import *
from direct.showbase import DirectObject
import Settings
import Rerender
import Utils

def loadImageAsPlane(yresolution = 600):
    """
    Load image as 3d plane
   
    Arguments:
    filepath -- image file path
    yresolution -- pixel-perfect width resolution
    """
    tex = Texture() #loader.loadTexture(filepath)
    tex.setBorderColor(Vec4(0,0,0,0))
    tex.setWrapU(Texture.WMBorderColor)
    tex.setWrapV(Texture.WMBorderColor)
    cm = CardMaker('card')
    #cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
    k = 60
    cm.setFrame(-k,k,-k,k)
    card = NodePath(cm.generate())
    card.setTexture(tex)
    card.setScale(card.getScale()/ yresolution)
    card.flattenLight() # apply scale
    return tex, card

class MiniImage(DirectObject.DirectObject):
    def __init__(self, app):
    	self.app = app
        size = 1-Settings.MINI_IMAGE_SIZE
        self.dr = base.win.makeDisplayRegion(size,1,size,1)
        #self.dr = base.win.makeDisplayRegion(0, 1, 0, 1)
        self.dr.setSort(20)
         
        self.myCamera2d = NodePath(Camera('myCam2d'))
        self.lens = OrthographicLens()
        #lens = PerspectiveLens()
        self.lens.setFilmSize(0.21, 0.21)
        self.lens.setNearFar(-1000, 1000)
        #lens.setNearFar(0.1, 100)
        self.myCamera2d.node().setLens(self.lens)
         
        self.myRender2d = NodePath('myRender2d')
        self.myRender2d.setDepthTest(False)
        self.myRender2d.setDepthWrite(False)
        self.myCamera2d.reparentTo(self.myRender2d)
        self.dr.setCamera(self.myCamera2d)

        self.tex, self.imageNode = loadImageAsPlane() #('NP3_165.jpg')
        self.imageNode.reparentTo(self.myRender2d)
        self.visible = False
        self.imageNode.stash()

    def setImage(self, image_name):
        #self.pnmimage = PNMImage()
        #self.pnmimage.read(image_name)
        self.pnmimage = Utils.openPNM(image_name)
        self.tex.load( self.pnmimage)

    def setCamParams(self, params):
    	self.camParams = params

    def appToggleHotkeyAction(self):
    	self.setImage(Settings.RRENDER_INPUT_IMG)
    	#self.setCamParams(Rerender.parseCamH5([Settings.RRENDER_CAM_CALIB_FILE]))
    	self.toggleVisibility()

    def toggleVisibility(self):
        if (self.visible):
            self.visible = False
            self.imageNode.stash()

        else:
            self.visible = True
            self.imageNode.unstash()
            self.timeOld = 0

            imgcopy = PNMImage() 
            imgcopy.copyFrom(self.pnmimage)
            #Rerender.rerenderNoWrite( self.app.selectedObject, self.app.pointcloud.TruPos, imgcopy, self.camParams)
            Rerender.rerenderNoWriteNoH5( self.app.selectedObject, self.app.pointcloud.TruPos, imgcopy, 
                                        Settings.RRENDER_K, Settings.RRENDER_DISTORT)
            self.tex.load(imgcopy)
            
            taskMgr.add(self.renderImageTask, 'renderImageTask')
            #

    def renderImageTask(self, task):
    	timeElapsed = task.time - self.timeOld
    	if timeElapsed < Settings.RRENDER_INTERVAL:
            return task.cont
        self.timeOld = task.time

    	if (self.pnmimage is None) or (Settings.RRENDER_K is None) or (Settings.RRENDER_DISTORT is None):
    		return task.done
    	if(not self.visible):
    		return task.done

    	imgcopy = PNMImage() 
    	imgcopy.copyFrom(self.pnmimage)
    	#Rerender.rerenderNoWrite( self.app.selectedObject, self.app.pointcloud.TruPos, imgcopy, self.camParams)
        Rerender.rerenderNoWriteNoH5( self.app.selectedObject, self.app.pointcloud.TruPos, imgcopy, 
                                    Settings.RRENDER_K, Settings.RRENDER_DISTORT)
    	self.tex.load(imgcopy)
    	return task.cont