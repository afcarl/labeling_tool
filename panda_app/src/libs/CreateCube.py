from panda3d.core import *

#
#Note: This code is taken from the Panda3D forums. I did not write this.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Function name : CreateCube
#
# Description:
#
#   Create a Panda3D GeomNode representing a simple unit cube and include
#   texture coordinates, colors, and normals at each vertex.
#
# Input(s):
#
#   nodeName - Name for the GeomNode (string)
#   color - Color for the cube (list/tuple of 4 values)
#
# Output(s):
#
#   A GeomNode representing a unit icosahedron.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def CreateCube(nodeName,size, color):

   # Define the vetex data format (GVF). 
   format = GeomVertexFormat.getV3n3c4t2()

   # Create the vetex data container (GVD) using the GVF from above to
   # describe its contents.
   vdata = GeomVertexData(nodeName+'GVD',format,Geom.UHStatic)

   # Create writers for the GVD, one for each type of data (column) that
   # we are going to store in it.
   gvwV = GeomVertexWriter(vdata, 'vertex')
   gvwT = GeomVertexWriter(vdata, 'texcoord')
   gvwC = GeomVertexWriter(vdata, 'color')
   gvwN = GeomVertexWriter(vdata, 'normal')

   # Upload the model info to the GVD using the writers
   gvwV.addData3f(-size,-size, size)
   gvwT.addData2f( 0.26500, 0.67500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size, size)
   gvwT.addData2f( 0.49000, 0.97500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size, size)
   gvwT.addData2f( 0.26500, 0.97500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size, size)
   gvwT.addData2f( 0.26500, 0.67500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size, size)
   gvwT.addData2f( 0.49000, 0.67500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size, size)
   gvwT.addData2f( 0.49000, 0.97500)
   gvwN.addData3f( 0.00000,-0.00000, 1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size,-size)
   gvwT.addData2f( 0.26500, 0.35000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size, size)
   gvwT.addData2f( 0.49000, 0.65000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size, size)
   gvwT.addData2f( 0.26500, 0.65000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size,-size)
   gvwT.addData2f( 0.26500, 0.35000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size,-size)
   gvwT.addData2f( 0.49000, 0.35000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size, size)
   gvwT.addData2f( 0.49000, 0.65000)
   gvwN.addData3f( 0.00000,-1.00000,-0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size,-size)
   gvwT.addData2f( 0.73500, 0.35000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size, size)
   gvwT.addData2f( 0.51000, 0.65000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size,-size)
   gvwT.addData2f( 0.51000, 0.35000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size,-size)
   gvwT.addData2f( 0.73500, 0.35000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size, size)
   gvwT.addData2f( 0.73500, 0.65000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size, size)
   gvwT.addData2f( 0.51000, 0.65000)
   gvwN.addData3f( 1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size,-size)
   gvwT.addData2f( 0.75500, 0.35000)
   gvwN.addData3f( 0.00000, 1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size, size)
   gvwT.addData2f( 0.98000, 0.65000)
   gvwN.addData3f( 0.00000, 1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size, size)
   gvwT.addData2f( 0.75500, 0.65000)
   gvwN.addData3f( 0.00000, 0.00000,-1.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size,-size)
   gvwT.addData2f( 0.75500, 0.35000)
   gvwN.addData3f( 0.00000, 1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size,-size)
   gvwT.addData2f( 0.98000, 0.35000)
   gvwN.addData3f( 0.00000, 1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size, size)
   gvwT.addData2f( 0.98000, 0.65000)
   gvwN.addData3f( 0.00000, 1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size, size)
   gvwT.addData2f( 0.02000, 0.65000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size,-size)
   gvwT.addData2f( 0.24500, 0.35000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size, size)
   gvwT.addData2f( 0.24500, 0.65000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size, size)
   gvwT.addData2f( 0.02000, 0.65000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size,-size)
   gvwT.addData2f( 0.02000, 0.35000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size,-size)
   gvwT.addData2f( 0.24500, 0.35000)
   gvwN.addData3f(-1.00000, 0.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size,-size)
   gvwT.addData2f( 0.49000, 0.32500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size,-size)
   gvwT.addData2f( 0.26500, 0.02500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size, size,-size)
   gvwT.addData2f( 0.49000, 0.02500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f( size,-size,-size)
   gvwT.addData2f( 0.49000, 0.32500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size,-size,-size)
   gvwT.addData2f( 0.26500, 0.32500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   gvwV.addData3f(-size, size,-size)
   gvwT.addData2f( 0.26500, 0.02500)
   gvwN.addData3f( 0.00000,-1.00000, 0.00000)
   gvwC.addData4f(color[0],color[1],color[2],color[3])

   geom = Geom(vdata)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(0)
   tris.addVertex(1)
   tris.addVertex(2)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(3)
   tris.addVertex(4)
   tris.addVertex(5)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(6)
   tris.addVertex(7)
   tris.addVertex(8)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(9)
   tris.addVertex(10)
   tris.addVertex(11)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(12)
   tris.addVertex(13)
   tris.addVertex(14)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(15)
   tris.addVertex(16)
   tris.addVertex(17)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(18)
   tris.addVertex(19)
   tris.addVertex(20)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(21)
   tris.addVertex(22)
   tris.addVertex(23)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(24)
   tris.addVertex(25)
   tris.addVertex(26)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(27)
   tris.addVertex(28)
   tris.addVertex(29)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(30)
   tris.addVertex(31)
   tris.addVertex(32)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   tris = GeomTriangles(Geom.UHStatic)
   tris.addVertex(33)
   tris.addVertex(34)
   tris.addVertex(35)
   tris.closePrimitive()
   geom.addPrimitive(tris)
   node = GeomNode('Cube')
   node.addGeom(geom)
   return node

