from panda3d.core import *
#import h5py
import numpy as np
import math
import Settings

def __calcPixel( point2d, ox,oy, img_dim_x, img_dim_y):
    x_frac = point2d[0]/ox
    y_frac = point2d[1]/oy
    x_pix = x_frac*(img_dim_x/2)
    y_pix = y_frac*(img_dim_y/2)
    x_pix += img_dim_x/2
    y_pix += img_dim_y/2
    return int(x_pix), int(y_pix)

def findPixel(point, K, mv_transf, distort, img_dim_x, img_dim_y):
    #print "point: ",point
    v4 = np.array([point[0],point[1],point[2],1])
    #print "v4: ",v4
    cam4 = mv_transf.dot(v4)
    #print "cam4: ",cam4
    cam4h = np.array([ cam4[0]/cam4[3], cam4[1]/cam4[3], cam4[2]/cam4[3]])
    #print "cam4h: ",cam4h
    imgK = K.dot(cam4h)
    #print "imgK: ",imgK
    imgKh = np.array([ imgK[0]/imgK[2], imgK[1]/imgK[2]])
    ox = K[0][2]
    oy = K[1][2]
    #print "imgKh: ",imgKh," ox:",ox, " oy:",oy
    imgKh = np.array( [imgKh[0]-ox, imgKh[1]-oy])
    x,y= __calcPixel(imgKh, ox, oy, img_dim_x, img_dim_y)
    
    #Distortion
    r = x*x+y*y
    r2 = r*r
    r4 = r2*r2
    r6 = r2*r4
    radial_distort = (1+distort[0]*r2+distort[1]*r4+distort[4]*r6)
    tan_distort_x = 2*distort[2]*x*y + distort[3]*(r2+2*x*x)
    tan_distort_y = 2*distort[3]*x*y + distort[2]*(r2+2*y*y)
    x= (x*radial_distort)+tan_distort_x
    y= (y*radial_distort)+tan_distort_y
    return [int(x),int(y)]

"""
def rerender(match_obj, origin_node, img_filename, h5_files):
    img_filename = Filename(img_filename)
    if Settings.VERBOSE:
        print "Running rerender on :",img_filename    
        print "\tCalibration:",h5_files    

    #h5files = map( lambda x: h5py.File(x,  "r"), h5_files)
    cam_specs = parseCamH5(h5files)
    #map( lambda x: x.close(), h5files)
    img = PNMImage()

    #istrm = FileStream(img_filename)
    b = img.read(img_filename)
    if b:
        _rerender(match_obj, origin_node, img, cam_specs)
    else:
        if Settings.VERBOSE:
            print "Failed to open image file:",img_filename

def parseCamH5(h5files):
    #Read data from disk into memory.
    h5files = map( lambda x: h5py.File(x,  "r"), h5files)
    i = 0
    dictionary = {}
    for h5file in h5files:
        for name in h5file:
            data = h5file.get(name)
            name = str(name)
            dictionary[name] = np.array(data)
            if name.startswith('NP3'):
                print name,":",dictionary[name]
    map( lambda x: x.close(), h5files)
    return dictionary

def _rerender(match_obj, origin_node, imgfile, cam_specs):
    xdim = imgfile.getReadXSize()
    ydim = imgfile.getReadYSize()

    mv_transf = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    K = cam_specs[Settings.RRENDER_CAMERA+'_rgb_K']
    distort = cam_specs[Settings.RRENDER_CAMERA+'_rgb_distortion']
    #print "K",K
    i = 0
    for pnt in match_obj.getPoints(origin_node):
        #tmp = pnt[1]
        #pnt[1] = -pnt[2]
        #pnt[2] = tmp
        
        i+=1
        if i>10:
            pass
            #break
        #print "Point: ", pnt
        pix = findPixel(pnt, K, mv_transf,distort, xdim, ydim)
        #print "Pix: ", pix
        if( pix[0]< 0) or pix[0]>=xdim:
            continue
        if( pix[1]< 0) or pix[1]>=ydim:
            continue
        imgfile.setRed(pix[0],pix[1],1)
        imgfile.setGreen(pix[0],pix[1],0)
        imgfile.setBlue(pix[0],pix[1],0)
        
    b = imgfile.write(Settings.RRENDER_OUTFILE)
    if Settings.VERBOSE:
        if b:
            print "Done rerendering image to ", Settings.RRENDER_OUTFILE
        else:
            print "Failed rerendering image to ", Settings.RRENDER_OUTFILE

def rerenderNoWrite(match_obj, origin_node, imgfile, cam_specs):
    xdim = imgfile.getReadXSize()
    ydim = imgfile.getReadYSize()
    mv_transf = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    K = cam_specs[Settings.RRENDER_CAMERA+'_rgb_K']
    distort = cam_specs[Settings.RRENDER_CAMERA+'_rgb_distortion']
    for pnt in match_obj.getPoints(origin_node):        
        pix = findPixel(pnt, K, mv_transf, distort, xdim, ydim)
        if( pix[0]< 0) or pix[0]>=xdim:
            continue
        if( pix[1]< 0) or pix[1]>=ydim:
            continue
        imgfile.setRed(pix[0],pix[1],1)
        imgfile.setGreen(pix[0],pix[1],0)
        imgfile.setBlue(pix[0],pix[1],0)
"""

def rerenderNoWriteNoH5(match_obj, origin_node, imgfile, K, distort ):
    xdim = imgfile.getReadXSize()
    ydim = imgfile.getReadYSize()
    mv_transf = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    #K = cam_specs[Settings.RRENDER_CAMERA+'_rgb_K']
    #distort = cam_specs[Settings.RRENDER_CAMERA+'_rgb_distortion']
    i=0
    points = match_obj.getPoints(origin_node)
    for pnt in points:
        if (i%Settings.RRENDER_SKIP) != 0:
            continue
        pix = findPixel(pnt, K, mv_transf, distort, xdim, ydim)
        if( pix[0]< 0) or pix[0]>=xdim:
            continue
        if( pix[1]< 0) or pix[1]>=ydim:
            continue
        imgfile.setRed(pix[0],pix[1],1)
        imgfile.setGreen(pix[0],pix[1],0)
        imgfile.setBlue(pix[0],pix[1],0)

if __name__ == "__main__":
    """
    img_dim_x = 1000
    img_dim_y = 2000
    ox = 5.0
    oy = 10.0
    point2d = [-5.0,-5.0]
    mv_transf_test = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    K_test = np.array([ [1,0,5.0],
                        [0,1,5.0],
                        [0,0,1]])
    point = [5,0,2]
    print findPixel(point, K_test, mv_transf_test, img_dim_x, img_dim_y)
    """
    parseCamH5(['calibration.h5'])

    #rerender(None, "NP3_165.jpg", "calibration.h5")
    
