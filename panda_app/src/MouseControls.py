from direct.task import Task
from panda3d.core import *
from direct.showbase import DirectObject
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import BitMask32
from random import randint, random
import string
import Settings

BUTTON_DOWN = 2
BUTTON_UP = 6
DRAG_THRESH = 0.001

"""
Provides a variety of keyboard/mouse events
for the rest of the application to use
"""
class MouseControls(DirectObject.DirectObject):
    def __init__(self):

        self.keys = {}
        for char in string.ascii_lowercase:
            self.keys[char] = BUTTON_UP
            def makeKeyPair(ch):
                def keyUp():
                    self.keys[ch] = BUTTON_DOWN
                    #print "%s UP" % (ch)
                def keyDown():
                    self.keys[ch] = BUTTON_UP
                    #print "%s DOWN" % (ch)
                return [keyUp, keyDown]
            keyPair = makeKeyPair(char)
            self.accept(char,keyPair[0])
            self.accept(char+'-up',keyPair[1])
            
        self.accept('mouse1',self.leftClick)
        self.accept('mouse1-up',self.leftClickUp)
        self.accept('mouse2',self.mClick)
        self.accept('mouse2-up',self.mClickUp)
        self.accept('mouse3',self.rightClick)
        self.accept('mouse3-up',self.rightClickUp)
        
        self.mouse1Down = False
        self.mouse2Down = False
        self.mouse3Down = False
        self.trackMouseTimeOld = 0
        self.trackMouseX = 0
        self.trackMouseY = 0
        self.trackMouse_Mouse1DownOld = False
        self.trackMouse_Mouse2DownOld = False
        self.trackMouse_Mouse3DownOld = False
        taskMgr.add(self.trackMouseTask, 'trackMouseTask')

        #
        base.cTrav          = CollisionTraverser()
        self.pickerQ        = CollisionHandlerQueue()
        self.pickerCollN    = CollisionNode('mouseRay')
        self.pickerCamN     = base.camera.attachNewNode(self.pickerCollN)
        self.pickerCollN.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerCollN.addSolid(self.pickerRay)
        base.cTrav.addCollider(self.pickerCamN, self.pickerQ)
        
        self.objectUnderCursor = None
        #taskMgr.add(self.mousePickerTask, 'Mouse picker process')
        
    def leftClick(self):
        self.mouse1Down = True

        #Collision traversal
        pickerNode = CollisionNode('mouseRay')
        pickerNP = base.camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        pickerRay = CollisionRay()
        pickerNode.addSolid(pickerRay)
        myTraverser = CollisionTraverser()
        myHandler = CollisionHandlerQueue()
        myTraverser.addCollider(pickerNP, myHandler)

        if base.mouseWatcherNode.hasMouse():

            mpos = base.mouseWatcherNode.getMouse()
            pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
 
            myTraverser.traverse(render)
            # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
            if myHandler.getNumEntries() > 0:
            # This is so we get the closest object
                myHandler.sortEntries()
                pickedObj = myHandler.getEntry(0).getIntoNodePath()
                objTag = pickedObj.findNetTag('mouseCollisionTag').getTag('mouseCollisionTag')
                if objTag and len(objTag)>0:
                    messenger.send('object_click',[objTag])
        pickerNP.remove()

    def leftClickUp(self):
        self.mouse1Down = False

    def mClick(self):
        self.mouse2Down = True

    def mClickUp(self):
        self.mouse2Down = False
        
    def rightClick(self):
        self.mouse3Down = True

    def rightClickUp(self):
        self.mouse3Down = False
        
    def trackMouseTask(self, task):
        timeElapsed = task.time - self.trackMouseTimeOld
        if timeElapsed < 0.05:
            return Task.cont
        self.trackMouseTimeOld = task.time
        
        if base.mouseWatcherNode.hasMouse():
            mX = base.mouseWatcherNode.getMouseX()
            mY = base.mouseWatcherNode.getMouseY()
            diffX = mX-self.trackMouseX
            diffY = mY-self.trackMouseY
            if (abs(diffX) > DRAG_THRESH) or (abs(diffY) > DRAG_THRESH):
                messenger.send('mouseDelta',[diffX,diffY])
                self.trackMouseX = mX
                self.trackMouseY = mY
                if self.trackMouse_Mouse1DownOld and self.mouse1Down:
                    messenger.send('mouse1Delta',[diffX,diffY])
                if self.trackMouse_Mouse2DownOld and self.mouse2Down:
                    messenger.send('mouse2Delta',[diffX,diffY])
                if self.trackMouse_Mouse3DownOld and self.mouse3Down:
                    messenger.send('mouse3Delta',[diffX,diffY])

            self.trackMouse_Mouse1DownOld = self.mouse1Down
            self.trackMouse_Mouse2DownOld = self.mouse2Down
            self.trackMouse_Mouse3DownOld = self.mouse3Down
        return Task.cont

    def mousePickerTask(self, task):
        print 'lalala: ',self.objectUnderCursor
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()      
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            #self.picker.traverse(base.render)
            if self.pickerQ.getNumEntries() > 0:
                self.pickerQ.sortEntries()
                firstNode = self.pickerQ.getEntry(0).getIntoNode()
                if firstNode != self.objectUnderCursor:
                    if self.objectUnderCursor:
                        messenger.send('interactive-scene-event',[self.objectUnderCursor.getName(),'rollout'])
                        print 'Rollout', self.objectUnderCursor.getName()
                    self.objectUnderCursor = firstNode
                    messenger.send('interactive-scene-event',[self.objectUnderCursor.getName(),'rollin'])
                    print 'Rollin', self.objectUnderCursor.getName()
            else:
                if self.objectUnderCursor:
                    messenger.send('interactive-scene-event',[self.objectUnderCursor.getName(),'rollout'])
                    print 'Rollout', self.objectUnderCursor.getName()
                    self.objectUnderCursor = None
        return task.cont
