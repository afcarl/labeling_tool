from panda3d.core import *
import numpy as np
import random
from libs.kdtree import KDTree
import Settings
from math import floor

class PointSampler:
    def __init__(self):
        self.dict = {}
        pass

    def addPoint(self,point):
        x = floor(point[0]/Settings.ICP_SAMPLING_SIZE)
        y = floor(point[1]/Settings.ICP_SAMPLING_SIZE)
        z = floor(point[2]/Settings.ICP_SAMPLING_SIZE)
        if not (x,y,z) in self.dict:
            self.dict[(x,y,z)] = point
            return
        old_dist = (self.dict[(x,y,z)]-Vec3(x,y,z)).lengthSquared()
        new_dist = (point-Vec3(x,y,z)).lengthSquared()
        if( new_dist<old_dist):
            self.dict[(x,y,z)]=point

    def getPoints(self):
        return self.dict.values()

class ProcessedCloud:
    def __init__(self, cloud):
        ps = PointSampler()
        for pt in cloud:
            ps.addPoint( pt)
        cloud = ps.getPoints()
        self.tree = KDTree.construct_from_data(cloud)
        self.numPts = len(cloud)
        #Sample the points

    def clear(self):
        if self.tree:
            self.tree.clear()

def convertKD(pc):
    return ProcessedCloud(pc)

def processClouds(pc1, pc2):
    ps = PointSampler()
    for pt in pc1:
            ps.addPoint( pt)
    pc1 = ps.getPoints()
    return pc1, convertKD(pc2)


def ICPiter(pc1, kd2):
    #return ICPiter(pc1, convertKD(pc2))
    ps = PointSampler()
    for pt in pc1:
            ps.addPoint( pt)
    pc1 = ps.getPoints()
    R, t = _ICPiter(pc1, (kd2))
    return R, t

#1 Iteration of ICP
#Returns rot matrix R and trans vector T
def _ICPiter(pc1, proc_cloud):
    #pc1 and pc2 are lists of Vec3's
    if Settings.VERBOSE:
        print "Running an ICP iteration"
    print "PC1: %d, PC2: %d" % (len(pc1), proc_cloud.numPts)
    x = 1
    #input()
    pairs = {}
    random.shuffle(pc1)
    i=0
    for pc1pt in pc1:
        #minpt = None
        #mindist = 0
        nearest = proc_cloud.tree.query(pc1pt, t=1, markSeen=False) # find nearest point
        if( len(nearest)==1):
            minpt = nearest[0]
            newDistSq = (minpt-pc1pt).lengthSquared()
            if minpt in pairs:
                [oldpoint, oldDistSq] = pairs[minpt]
                if newDistSq < oldDistSq:
                    pairs[minpt] = [pc1pt, newDistSq]
            else:
                pairs[minpt] = [pc1pt, newDistSq]
            #pairs.append((pc1pt, minpt))
        
        if( i%1000 == 0):
            pass
            #print "Progress: %d/%d" %( i, len(pc1))
        i+=1
    #proc_cloud.clear() #Clear all seen nodes so tree can be used again

    #print "NumPairs: ", len(pairs)

    #print "Pairs: ", len(pairs)
    #calculate average
    avgDif = Vec3(0,0,0)
    avgVecA = Vec3(0,0,0)
    avgVecB = Vec3(0,0,0)
    num = 0
    for pcpt in pairs:
        [geompt, distSq] = pairs[pcpt]
        #print "Pair: ", (geompt, pcpt)
        avgVecA = avgVecA+geompt
        avgVecB = avgVecB+pcpt
        num+=1
    avgVecA = avgVecA/num
    avgVecB = avgVecB/num
    avgDiff = avgVecB-avgVecA

    #Calculate deviation. This is currently unused
    """
    total_dev = 0
    for pcpt in pairs:
        [geompt, distSq] = pairs[pcpt]
        deviation = (math.sqrt(distSq)-avgDiff)*(math.sqrt(distSq)-avgDiff)
        total_dev += deviation
        pairs[pcpt] = [geompt, deviation]
    std_dev = math.sqrt(total_dev/num)
    """

    #Calculate rotation
    N = np.zeros((3,3))
   
    for pcpt in pairs:
        [geompt, deviation] = pairs[pcpt]
        a = np.array(geompt-avgVecA)
        b = np.array(pcpt-avgVecB)
        N = N+np.outer(a,b)
        #print "N:",N

    U,S,V = np.linalg.svd(N)
    V = V.transpose() #numpy returns VT, so transpose to make it V
    
    R = U.dot(V.transpose())

    #tmp = R.dot(avgVecB)
    #t = avgVecA - Vec3(tmp[0],tmp[1],tmp[2])
    t = avgVecB-avgVecA
    
    #convert from numpy to panda matrix
    R = Mat3(R[0,0],R[0,1],R[0,2],
             R[1,0],R[1,1],R[1,2],
             R[2,0],R[2,1],R[2,2])

    
    if num > 0:
        return Mat4(R), t
    return Mat4(Mat3(1,0,0,0,1,0,0,0,1)), Vec3(0,0,0)

def converged(R,t):
    diag = R[0][0]+R[1][1]+R[2][2]
    if abs(diag-3)>= 3*Settings.ICP_THRESH:
        return False
    for i in t:
        if abs(i)>=Settings.ICP_THRESH:
            return False
    return True
    
