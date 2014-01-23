from panda3d.core import *
from ParsePLY import *
from Settings import PROGRESS_GRANULARITY, PC_FILEREAD_SKIP, VERBOSE
import Utils

"""
Generates a function that prints progress percentages
"""
def printProgressFunc(message):
    if not VERBOSE:
        return lambda x: x
    def printfun(perc):
        print message % (perc,)
    return printfun

"""
Parse a pointcloud from an input stream
A callback with args (x,y,z,r,g,b,a) will be called
for each point found.
"""
def _parsePointCloud( filename, callback, progress):
    numVerts = 0
    header = getHeaderInfoStream(Utils.openAll(filename))
    for elem_name in header.elements:
        if( elem_name == "vertex"):
            numVerts = header.elements[elem_name].count

    def plyparse_cb(typ, args, i):
        if (i%PC_FILEREAD_SKIP != 0): return
        
        if typ=="vertex":
            x = args['x']
            y = args['y']
            z = args['z']
            r = args['red']
            g = args['green']
            b = args['blue']
            a = 255
            if (i%(PROGRESS_GRANULARITY)==0):
                progress(100*float(i)/numVerts)
                #print "\tParsing vertex %d: %.2f%% done" % (i,100*float(i)/numVerts)
            callback(x,y,z,r,g,b,a)
        else:
            #print type, args
            pass
    #parsePLY(filename, plyparse_cb)
    parsePLYstream( Utils.openAll(filename) , plyparse_cb)
    progress(100)
    
"""
Returns a NodePath representing the point cloud stored in <filename>
"""
def loadPointCloud(render, filename, 
        progressFunc= printProgressFunc("\tParsing pointcloud: %.2f%% done"), extras = False):
    if VERBOSE:
        print "Loading point cloud from ",filename
    
    format = GeomVertexFormat.getV3c4()       
    vdata = GeomVertexData('PointCloud',format,Geom.UHStatic)
    gvwV = GeomVertexWriter(vdata, 'vertex')
    gvwC = GeomVertexWriter(vdata, 'color')

    def ns(): pass #make a namespace because python2.7 does not have nonlocal
    ns.count = 0
    ns.xsum = 0
    ns.ysum = 0
    ns.zsum = 0
    ns.maxv = [-float('inf'),-float('inf'),-float('inf')]
    ns.minv = [float('inf'),float('inf'),float('inf')]
    ns.points = []
    
    def pc_callback(x,y,z,r,g,b,a):
        gvwV.addData3f(x,y,z) #add position data
        gvwC.addData4f(r/255.0,g/255.0,b/255.0,a/255.0) #add color data
        ns.count += 1
        ns.xsum += x
        ns.ysum += y
        ns.zsum += z
        ns.maxv = map(max, ns.maxv, [x,y,z])
        ns.minv = map(min, ns.minv, [x,y,z])
        if extras:
            ns.points.append(Vec3(x,y,z))
        
    _parsePointCloud( filename,pc_callback, progressFunc)
    
    if VERBOSE:
        print "\tBuilding geometry..."
    avgX = ns.xsum/ns.count
    avgY = ns.ysum/ns.count
    avgZ = ns.zsum/ns.count
    avgv = [avgX, avgY, avgZ]
    
    geom = Geom(vdata)
    pts = GeomPoints(Geom.UHStatic)
    pts.addConsecutiveVertices(0, ns.count )
    pts.closePrimitive()
    geom.addPrimitive(pts)
    ptnode = GeomNode('PointCloud')
    ptnode.addGeom(geom)
    dummy = render.attachNewNode('dummy')
    nodepath = dummy.attachNewNode(ptnode)

    #Reposition point cloud so that it is centered at the mean
    nodepath.setPos(dummy, -avgX, -avgY, -avgZ)
    if VERBOSE:
        print "\tDone! Offsetting pointcloud by (%f,%f,%f)" % (-avgX,-avgY,-avgZ)

    if extras:
        def extravals(): pass
        extravals.baseNode = dummy
        extravals.TruPos = nodepath
        extravals.maxv = ns.maxv
        extravals.minv = ns.minv
        extravals.avgv = [avgX,avgY,avgZ]
        extravals.points = ns.points
        return extravals
    return dummy, nodepath
     
def loadGeomObject(render, filename, 
        progressFunc= printProgressFunc("\tParsing mesh: %.2f%% done"), extras=False):
    if VERBOSE:
        print "Loading matcher object from ",filename
    numVerts = 0
    numFaces = 0
    header = getHeaderInfoStream(Utils.openAll(filename))
    for elem_name in header.elements:
        if( elem_name == "vertex"):
            numVerts = header.elements[elem_name].count
        if( elem_name == "face"):
            numFaces = header.elements[elem_name].count
    
    format = GeomVertexFormat.getV3n3c4()       
    vdata = GeomVertexData('PointCloud',format,Geom.UHStatic)
    vdata.setNumRows( numVerts)
    gvwV = GeomVertexWriter(vdata, 'vertex')
    gvwC = GeomVertexWriter(vdata, 'color')
    #gvwN = GeomVertexWriter(vdata, 'normal')
    #vertNorms = (None,)*numVerts

    
    def ns(): pass #make a namespace because python2.7 does not have nonlocal
    ns.count = 0
    ns.xsum = 0
    ns.ysum = 0
    ns.zsum = 0
    ns.geom = Geom(vdata)
    ns.pts = GeomTriangles(Geom.UHStatic)
    ns.maxv = [-float('inf'),-float('inf'),-float('inf')]
    ns.minv = [float('inf'),float('inf'),float('inf')]
    ns.points = []

    def plyparse_cb(typ, args, i):
        if typ=="vertex":
            x = args['x']
            y = args['y']
            z = args['z']
            ns.count += 1
            ns.xsum += x
            ns.ysum += y
            ns.zsum += z
            gvwV.addData3f(x,y,z) #add position data
            gvwC.addData4f(0.8,0.8,0.8,0.8) #add color data
            ns.maxv = map(max, ns.maxv, [x,y,z])
            ns.minv = map(min, ns.minv, [x,y,z])
            if extras:
                ns.points.append(Vec3(x,y,z))
            if (i%(PROGRESS_GRANULARITY)==0):
                progressFunc(50*float(i)/numVerts)
                #print "\tParsing vertex %d: %.2f%% done" % (i,100*float(i)/numVerts)
        elif typ == "face":
            vertlist = args['vertex_indices']
            for vert in vertlist:
                ns.pts.addVertex(vert)
            if (i%(PROGRESS_GRANULARITY)==0):
                 progressFunc(50+50*float(i)/numFaces)               
                #print "\tParsing face %d: %.2f%% done" % (i,100*float(i)/numFaces)
            #calculate vertex normals?
            
    #parsePLY(filename, plyparse_cb)
    parsePLYstream( Utils.openAll(filename) , plyparse_cb)
    progressFunc(100)

    """ Add support for normals later?
    for i in range(0, numVerts):
        vnorm = vertNorms[i]
        vnorm.normalize()
        gvwN.addData3f(vnorm[0],vnorm[1],vnorm[2])
    """
    
    if VERBOSE:
        print "\tBuilding geometry..."

    avgX = ns.xsum/ns.count
    avgY = ns.ysum/ns.count
    avgZ = ns.zsum/ns.count

    ns.pts.closePrimitive()
    ns.geom.addPrimitive(ns.pts)
    
    ptnode = GeomNode('GeomObj')
    ptnode.addGeom(ns.geom)
    dummy = render.attachNewNode('dummy')
    nodepath = dummy.attachNewNode(ptnode)
    #Reposition object so that it is centered at the mean
    nodepath.setPos(dummy, -avgX, -avgY, -avgZ)
    if VERBOSE:
        print "\tDone! Offsetting matcher object by (%f,%f,%f)" % (-avgX,-avgY,-avgZ)

    if extras:
        def extravals(): pass
        extravals.baseNode = dummy
        extravals.TruPos = nodepath
        extravals.maxv = ns.maxv
        extravals.minv = ns.minv
        extravals.avgv = [avgX,avgY,avgZ]
        extravals.points = ns.points
        return extravals
    return dummy, nodepath
