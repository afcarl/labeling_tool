import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBase import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from panda3d.core import *
from pandac.PandaModules import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from agilemenu import HorizontalMenu
from math import *
from MatcherObject import MatcherObject
import ICP
import GeometryParser
from libs import CreateCube
import Settings
import MouseControls as MCont
import Rerender
import Utils
from MiniImage import MiniImage

 
"""
Create a small cube at a node.
"""
def addDebugPoint(node, r, g, b):
    n = CreateCube.CreateCube("dbg", 0.1,[r,g,b,1.0])
    return node.attachNewNode(n)

class MyApp(ShowBase):
    def __init__(self):
        #ShowBase.__init__(self)
        Utils.checkVersion()
 
        # Disable the camera trackball controls.
        base.disableMouse()
        self.render = base.render

        #create a list of debug points. These can be toggled ON/OFF
        self.debugPoints = []

        #Disable moving stuff until all assets are loaded
        self.assetsLoaded = False
        
        
        #create my own "camera"
        self.rroot = self.render.attachNewNode('rroot') #Translational Root
        self.rroot.setPos(0.0,0.0,0.0)
        self.root = self.rroot.attachNewNode('root') #Rotational Root

        self.camPosTrackerUp = self.render.attachNewNode('camPosTrackerUp')
        self.camPosTrackerUp.setPos(0,0,1)
        
        self.z = self.root.attachNewNode('z')
        self.z.setPos(0,0,1)
        self.y = self.root.attachNewNode('y')
        self.y.setPos(0,1,0)
        self.x = self.root.attachNewNode('x')
        self.x.setPos(1,0,0)
        self.debugPoints.append(addDebugPoint(self.root, 1.0, 1.0, 1.0))
        self.debugPoints.append(addDebugPoint(self.z, 0.0, 0.0, 1.0))
        self.debugPoints.append(addDebugPoint(self.y, 0.0, 0.5, 0.5))
        self.debugPoints.append(addDebugPoint(self.x, 0.5, 0.0, 0.5))

        #Load matcher object
        #self.object = MatcherObject(self.root, GeometryParser.loadGeomObject)
        self.objects = {}
        self.selectedObject = None

        #Load point cloud
        self.pointcloud = MatcherObject(self.root, GeometryParser.loadPointCloud)
        self.pointcloud.setPointCloudThickness(4)
        
        self.accept('mouse1Delta',self.ldelta)
        self.accept('mouse2Delta',self.mdelta)
        self.accept('mouse3Delta',self.rdelta)
        self.accept('wheel_up',self.mscrollUp)
        self.accept('wheel_down',self.mscrollDown)
        self.accept(Settings.TOGGLE_DEBUG_HOTKEY, self.toggleDebug)
        self.accept(Settings.ICP_HOTKEY, self.runICP)

        #self.accept('q', self.testFunc)
        self.accept('object_click', self.selectObject)
        self.accept(base.win.getWindowEvent(), self.onWindowEvent)
        self.hideDebugPoints() #Hide debug points
        self.debugPointsShown = False
        self.mouseCont = MCont.MouseControls()

        #MENU
        self.accept(base.win.getWindowEvent(), self.onWindowEvent)
 
        self.bridgeMenu=HorizontalMenu(self, file('res/bridgeMenu.txt').read(),
                style = 'transparent.ccss', scale=.05)
        self.mini_img = MiniImage(self)
        self.accept(Settings.RRENDER_TOGGLE_HOTKEY, self.mini_img.appToggleHotkeyAction)

    #
    # UTILITY METHODS
    #

    """
    Get the up vector of the camera 
    """
    def getUpVec(self):
        up = self.camPosTrackerUp.getPos(self.root)-self.render.getPos(self.root)
        up.normalize()
        return up
        
    """
    Get vector pointing from the camera to the center of the scene
    """
    def getViewVec(self):
        v = -(self.render.getPos(self.root))
        v.normalize()
        return v

    """
    Helper function for translating objects
    """
    def translObject(self, objR, objT, distx, disty, distz):
        xVec = Vec3(1,0,0)
        yVec = Vec3(0,0,1) #Y and Z got switched, because Panda treats Z as up
        zVec = Vec3(0,1,0) #and Y as in, whereas on the screen Y is up/down
        oldPos = objT.getPos(self.render);
        newPos = oldPos + (xVec*distx)+(yVec*disty)+(zVec*distz)
        objT.setPos(self.render, newPos[0],newPos[1],newPos[2]);

    """
    Helper function for rotating objects
    """
    def rotateObject(self, objR, objT, distx, disty):
        up = self.getUpVec()
        view = self.getViewVec()
        right = view.cross(up)
        rotVec = right*(-disty)+up*(distx)
        dist = sqrt((disty*disty)+(distx*distx))
        rotmat = Mat4.rotateMat(dist, rotVec)
        transf = objR.getMat(objT);
        objR.setMat(objT, transf*rotmat)
        
    
    def zoomCamera(self, dist):
        #print "Up: %s, View: %s" % (str(self.getUpVec()), str(self.getViewVec()))
        pos = self.rroot.getPos();
        self.rroot.setPos(pos[0],pos[1]-dist, pos[2])

    #
    # KEYBOARD/MOUSE LISTENERS
    #

    """
    Action to take when left click is dragged: Translate
    """
    def ldelta(self, distx, disty):
        if not self.assetsLoaded:
            return
        distx *=Settings.TRANSL_SENSITIVITY;
        disty *=Settings.TRANSL_SENSITIVITY;

        #Translate matcher object
        if self.mouseCont.keys[Settings.MATCH_OBJ_HOTKEY] == MCont.BUTTON_DOWN:
            if self.selectedObject:
                self.translObject(self.selectedObject.R, self.selectedObject.T, distx,disty,0)
        else: #Translate scene
            self.translObject(self.root, self.rroot, distx,disty,0)

    """
    Action to take when right click is dragged: Rotate
    """
    def rdelta(self, distx, disty):

        if not self.assetsLoaded:
            return
        distx *=Settings.ROT_SENSITIVITY;
        disty *=Settings.ROT_SENSITIVITY;

        #Rotate matcher object
        if self.mouseCont.keys[Settings.MATCH_OBJ_HOTKEY] == MCont.BUTTON_DOWN:
            if self.selectedObject:
                self.rotateObject(self.selectedObject.R, self.selectedObject.T, distx, disty)
        #Rotate scene
        else:
            transf = self.root.getMat(self.rroot);
            dist = sqrt((disty*disty)+(distx*distx))
            rotmat = Mat4.rotateMat(dist, Vec3(-disty, 0, distx))
            self.root.setMat(self.rroot, transf*rotmat)
    """
    Action to take when mouse wheel click is dragged: Nothing yet
    """
    def mdelta(self, distx, disty):
        pass

    """
    Zoom camera in when mouse wheel is scrolled up
    """
    def mscrollUp(self):

        if not self.assetsLoaded:
            return
        if self.mouseCont.keys[Settings.MATCH_OBJ_HOTKEY] == MCont.BUTTON_DOWN:
            if self.selectedObject:
                self.translObject(self.selectedObject.R, self.selectedObject.T, 0,0,0.5*Settings.ZOOM_SENSITIVITY)
        else:
            self.zoomCamera(Settings.ZOOM_SENSITIVITY)

    """
    Zoom camera out when mouse wheel is scrolled down
    """
    def mscrollDown(self):        

        if not self.assetsLoaded:
            return
        if self.mouseCont.keys[Settings.MATCH_OBJ_HOTKEY] == MCont.BUTTON_DOWN:
            if self.selectedObject:
                self.translObject(self.selectedObject.R, self.selectedObject.T, 0,0,-0.5*Settings.ZOOM_SENSITIVITY)
        else:
            self.zoomCamera(-Settings.ZOOM_SENSITIVITY)

    """
    Action to take when an object is clicked: Select it.
    """
    def selectObject(self, objname):

        if not self.assetsLoaded:
            return
        if Settings.VERBOSE:
            print "Clicked object: ",objname
        if objname in self.objects:
            self.selectMatchObject(objname)
    
    def runICP(self):
        print "RUNNING ICP"

        """
        if not self.assetsLoaded:
            print "Assets unloaded"
            return
        """
        if self.pointcloud == None or self.pointcloud.isEmpty():
            if Settings.VERBOSE:
                print "Cannot run ICP: No pointcloud loaded"
            return
        if self.selectedObject == None:
            if Settings.VERBOSE:
                print "Cannot run ICP: No selected object"
            return

        print "0"
        bnds = self.selectedObject.getBounds()
        print "1"
        pc_pts = ICP.convertKD(self.pointcloud.getPointsBounded(bnds))
        print "2"

        for i in xrange(0,Settings.ICP_MAX_ITERS):
            objPoints = self.selectedObject.getPoints()
            R, t = ICP.ICPiter( objPoints, pc_pts)
            self.selectedObject.translV3(t)
            self.selectedObject.rotateM4(R)
            if (i%5==0): #refresh bounds
                bnds = self.selectedObject.getBounds()
                pc_pts = ICP.convertKD(self.pointcloud.getPointsBounded(bnds))
            if( ICP.converged(R,t)):
                if Settings.VERBOSE:
                    print "ICP Converged!"
                break
            if( i == Settings.ICP_MAX_ITERS-1):
                if Settings.VERBOSE:
                    print "Max iterations reached (Did not converge)"

    def toggleRerender(self):

        if not self.assetsLoaded:
            return
        if self.pointcloud == None or self.pointcloud.isEmpty():
            if Settings.VERBOSE:
                print "Cannot run rerender: No pointcloud loaded"
            return
        if self.selectedObject == None:
            if Settings.VERBOSE:
                print "Cannot run rerender: No selected object"
            return
        success = self.mini_img.setImage(Settings.RRENDER_INPUT_IMG)
        if( success):
	        self.mini_img.toggleVisibility()

    """
    Toggle the showing of debug points
    """
    def toggleDebug(self):

        if not self.assetsLoaded:
            return
        if self.debugPointsShown:
            self.selectedObject.hideBounds()
            self.hideDebugPoints()
        else:
            self.selectedObject.showBounds()
            #self.selectedObject.R.showTightBounds()
            self.showDebugPoints()
        
    def showDebugPoints(self):
        for d in self.debugPoints:
            d.unstash()
        self.debugPointsShown = True

    def hideDebugPoints(self):
        for d in self.debugPoints:
            d.stash()
        self.debugPointsShown = False

    """
    Keep menu on upper-left corner when window is resized
    """
    def onWindowEvent(self, window):
    	self.bridgeMenu.setPos((-base.getAspectRatio()+.02, 0, .925))

    def selectMatchObject(self, objname):
        if self.selectedObject:
            self.selectedObject.onUnselect()
        self.selectedObject= self.objects[objname]
        self.selectedObject.onSelect()
        if self.debugPointsShown:
            self.selectedObject.showBounds()

    def loadMatchObject(self, filename):
        print "a0"   	
        if filename and filename != '':
            matchObj = MatcherObject(self.root, GeometryParser.loadGeomObject, filename,
                        "Loading mesh")
        print "aa"
        while matchObj.name in self.objects:
            matchObj.rename(matchObj.name+'~')
        print "ab"
        #self.bridgeMenu.addchildren(matchObj.getMenuStr(),'manage')
        print "ac"       
        self.objects[matchObj.name] = matchObj
        print "ad"              
        self.selectMatchObject(matchObj.name)

    def loadPointCloud(self, filename):
        if filename and filename != '':
            self.pointcloud.changeObject(filename, "Loading point cloud")
            #Utils.runInThread(self.pointcloud.changeObject, (filename,))
            self.pointcloud.setPointCloudThickness(4)
            self.pointcloud.repositionCamera(self.render, self.rroot)

    def loadFromConfigURL(self, confurl):
        self.assetsLoaded = False
        try:
            import numpy as np
            conf = Utils.evalConfig( Utils.fetchFromURL(confurl, 'r'))
            if( conf is None):
            	return
            #print conf
            self.resetScene()
            self.loadPointCloud(conf['point_cloud'])
            Settings.RRENDER_INPUT_IMG = conf['ref_image']
            Settings.MATCH_FUN = conf['match_fun']
            objects = conf['objects']
            print "OBJECTS:",objects
            for o in objects:
                self.loadMatchObject(o)
            print "1"
            Settings.RRENDER_DISTORT = np.array(conf['distort'])
            print "2"
            Settings.RRENDER_K = np.array(conf['rgb_K'])
            print "3"
            self.assetsLoaded = True
        except Exception as e:
            Utils.logError(e)
            Utils.errorDialog(e)                                  

    def removeMatchObject(self, matchObjName):
    	if( matchObjName in self.objects):
	        obj = self.objects[matchObjName]
	        del self.objects[matchObjName]
	        if not (obj is None):
		        obj.remove()
		        self.bridgeMenu.delete(obj.getMenuName())
		        if obj == self.selectedObject:
		            self.selectedObject = None
    
    def resetScene(self):
        while len(self.objects)>0:
            self.removeMatchObject(self.objects.keys()[0])

    #
    # Menu Button Listeners
    #
    def menu_loadPC(self, it):
        #print 'ldPC'
        try:
            Tk().withdraw() 
            filename = askopenfilename()
            self.loadPointCloud(filename)
        except Exception as e:
            Utils.logError(e)           
            Utils.errorDialog(e)                                  

    def menu_loadObject(self,it):
        #print 'ldObject'
        try:
            Tk().withdraw() 
            filename = askopenfilename()
            self.loadMatchObject(filename)
        except Exception as e:
            Utils.logError(e)           
            Utils.errorDialog(e)                                  

    def menu_test(self,it):
        pass

    def menu_finalizeMatch(self, it):
        #Print matcher object's position relative to point cloud
        try:
            if self.assetsLoaded != True:
                return
            if Settings.VERBOSE:
                print "Finalizing match"
            for objname in self.objects:
                obj = self.objects[objname]
                #netTransf = self.selectedObject.TruPos.getMat(self.pointcloud.TruPos)
                netTransf = obj.TruPos.getMat(self.pointcloud.TruPos)
                netTransf.transposeInPlace()
                if Settings.VERBOSE:
                    print "\tPointCloud->ROOT:",str(self.pointcloud.TruPos.getPos(self.root))
                    print "\t"+objname+"->ROOT:",str(self.selectedObject.TruPos.getPos(self.root))
                if Settings.MATCH_FUN:
                    success = Settings.MATCH_FUN(self.pointcloud.name, obj.name, netTransf)
                    if Settings.VERBOSE:
                        print "Succesful upload?", success

        except Exception as e:
            Utils.logError(e)           
            Utils.errorDialog(e)                       
        
    def menu_clickObj(self, it, obj):
        try:
            print '---MENU CLICK OBJ: ', obj
            self.removeMatchObject(obj)
        except Exception as e:
            Utils.logError(e)
            Utils.errorDialog(e)           
        
    def menu_setOpt(self, it, opt):
        #TODO: make a popup where you can enter values.
        print "Options are not implemented yet! Edit Settings.py directly for now"

    def menu_resetView(self, it):
        self.pointcloud.repositionCamera(self.render, self.rroot)
        
    def menu_autoConfig(self, it):
        self.loadFromConfigURL(Settings.AUTOCONFIG_URL)

    def menu_manualConfig(self, it):
        try:
            #callback function to set  text 
            def setText(textEntered):
                self.loadFromConfigURL(textEntered)
                b.destroy()

            #clear the text
            def clearText():
                b.enterText('')
             
            #add button
            b = DirectEntry(text = "" ,scale=.06,command=setText,
                initialText="Enter Scene URL", numLines = 5,focus=1,focusInCommand=clearText) 
        except Exception as e:
            Utils.logError(e)
            Utils.errorDialog(e)
