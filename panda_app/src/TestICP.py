from ICP import *
from panda3d.core import *
import random

def applyTransf(transf, points):
    newv = []
    for v in points:
        p = transf.xformPoint(v);
        newv.append(p);
    return newv

def translate(t, points):
    newv = []
    for v in points:
        p = v+t;
        newv.append(p);
    return newv

def converged(a, b):
    for i in xrange(len(a)):
        aa = a[i]
        bb = b[i]
        for j in xrange(len(aa)):
            if( abs(aa[j]-bb[j]) >0.01):
                return False
    return True

testPC = []
k = 10
#for i in range(0,4):
#    testPC.append( Vec3(random.uniform(0,k), random.uniform(0,k), random.uniform(0,k)))
testPC = [Vec3(3,0,0), Vec3(0,3,0), Vec3(0,0,3), Vec3(3.05,0,0), Vec3(3.07,0,0)]

transf = Mat4.rotateMat( 0, Vec3(0,1,1))

testGM = applyTransf(transf, testPC);
#testGM[3][2] += 10
testGM = translate(Vec3(-1,0,0), testGM)
print "Target: ",testPC
print "Original: ",testGM
print "\n\n"

#proc_cloud =  convertKD(testPC)

prevGM = testGM
for i in range(0,10):
    R, t = ICPiter(testGM, testPC)
    testGM = translate(t, testGM)
    testGM = applyTransf(R, testGM)

    print "R: ",R
    print "T: ",t
    print "Iter ",i+1,": ",testGM
    
    if( converged(prevGM, testGM)):
        print "Converged on iter ",i+1
        break
    else:
        prevGM = testGM

#print "Corrected: ",testGM
