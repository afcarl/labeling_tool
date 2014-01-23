from panda3d.core import *
import Settings
import math
import Utils

class MatcherObject():
    def __init__(self, root, loadfunc, filename = None, _message = ""):
        self.loadfunc = loadfunc
        self.root = root
        self.T = root.attachNewNode("objectT")
        self.center = self.T.attachNewNode('objCenter')
        self.TruPos = self.center
        self.empty = True

        if filename:
            lb = Utils.createLoadBar(message = _message, autodelete = True)
            retval = loadfunc(self.T, filename, progressFunc=lb.set, extras = True)
            self.R = retval.baseNode
            self.TruPos = retval.TruPos
            self.maxv = retval.maxv #Untransformed maximum bound
            self.minv = retval.minv #Untransformed min bound
            self.avgv = retval.avgv #Untransformed avg pos
            self.points = retval.points
            self.name = Filename(filename).getBasename()
            self.T.setTag('mouseCollisionTag', self.name)
            #self.R, self.TruPos = PointCloudParser.loadGeomObject(self.T, filename)
            self.empty=False
        else:
            self.R = self.center.attachNewNode('nothing')
        self.z = self.R.attachNewNode('z')
        self.z.setPos(0,0,1)
        self.y = self.R.attachNewNode('y')
        self.y.setPos(0,1,0)
        self.x = self.R.attachNewNode('x')
        self.x.setPos(1,0,0)

    def isEmpty(self):
        return self.empty

    def rename(self, newname):
        self.name = newname
        self.T.setTag('mouseCollisionTag', newname)
        
    def getMenuStr(self):
        return 'delimiter={{\nRemove %s {{ kind=button,menu_clickObj(%s),id=obj_%s' % (self.name, self.name, self.name)

    def getMenuName(self):
        return 'obj_'+self.name

    def clear(self):
        if( self.R):
            self.R.remove_node()

    def changeObject(self, filename, _message = ""):
        self.rename(Filename(filename).getBasename())
        if( self.R):
            self.R.remove_node()
        lb = Utils.createLoadBar(message = _message, autodelete = True)
        retval = self.loadfunc(self.T, filename, progressFunc=lb.set, extras = True)
        #retval = self.loadfunc(self.T, filename, extras = True)
        self.R = retval.baseNode
        self.TruPos = retval.TruPos
        self.maxv = retval.maxv #Untransformed maximum bound
        self.minv = retval.minv #Untransformed min bound
        self.avgv = retval.avgv #Untransformed avg pos
        self.points = retval.points
        
        self.x.reparentTo(self.R)
        self.y.reparentTo(self.R)
        self.z.reparentTo(self.R)
        self.empty=False

    def remove(self):
        self.T.remove()

    def setPointCloudThickness(self,i):
        self.R.setRenderModeThickness(i)

    def onSelect(self):
        self.R.setColor(1,0,0,0)

    def onUnselect(self):
        self.R.setColor(0.8,0.8,0.8,0)
        self.R.hideBounds()

    def showBounds(self):
        self.R.showBounds()
        
    def hideBounds(self):
        self.R.hideBounds()
        
    def _toRootMatrix(self):
        return self.TruPos.getMat(self.root)

    def translV3(self, v):
        oldPos = self.T.getPos();
        newPos = oldPos + v
        self.T.setPos(newPos);
        
    def rotateM4(self, rotmat):
        transf = self.R.getMat(self.T);
        self.R.setMat(self.T, transf*rotmat)

    """
    Returns pivot point relative to root
    """
    def getRotatePivot(self):
        return self.T.getPos(self.root)
    """
    Returns a two lists of the form [maxX,maxY,maxZ],[minX,minY,minZ]
    where each coordinate (in the root's coordinate system) represents
    the bounding box of this geom's points
    """
    def getBounds(self, expand = 1):
        """
        bsph = self.T.getBounds()
        c = bsph.getCenter()
        r = bsph.getRadius()
        return [c[0]+expand*r,c[1]+expand*r,c[2]+expand*r],[c[0]-expand*r,c[1]-expand*r,c[2]-expand*r]
        """
        return self.T.getBounds()
        
    def getPoints(self, relative = None):
        if relative is None:
            relative = self.root
        transf = self.TruPos.getMat(relative)
        #transf = self._toRootMatrix()
        transformedPoints = map( transf.xformPoint, self.points)
        return transformedPoints
        
    def getPointsBounded(self, bounds):#bounds_max, bounds_min):
        transformedPoints = self.getPoints()

        def ns(): pass
        ns.count = 0

        delta = Vec3(.01,.01,.01);
        def filterFunc(point):
            b = BoundingBox(Point3(point-delta), Point3(point+delta))
            i = bounds.contains(b)
            if i != 0:
                return True
            return False
            """
            ns.count += 1
            if( ns.count< 10):
                pass
                #print point
                
            if ( point[0]<=bounds_max[0] and point[0]>=bounds_min[0]):
                if ( point[1]<=bounds_max[1] and point[1]>=bounds_min[1]):
                    if ( point[2]<=bounds_max[2] and point[2]>=bounds_min[2]):
                        #print "Point passed: %.2f<%.2f<%.2f" %(bounds_min[0],point[0],bounds_max[0])
                        return True
            return False
            """

        return filter(filterFunc, transformedPoints)

    def repositionCamera(self,render, rroot):
        p = self.T.getPos(self.TruPos)
        d = math.sqrt( p.lengthSquared())
        #hpr = self.T.getHpr(self.TruPos)
        nPos= Vec3(0, d, 0)
        rroot.setPos(nPos)
        #self.rroot.setHpr(root, hpr)