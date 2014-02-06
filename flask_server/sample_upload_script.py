from sql_interface import addScene

#####
#Adding a scene to pending matches
#####

# Pointcloud, [List of objects], Image, Camera
addScene("NP3_165.ply", ["circlefit_mesh.ply"], "NP3_165.jpg", "NP3_rgb")

#If using the database directly, upload to the pending table
#	int id (primary key)
#	int last_issued : Seconds since epoch of the last time this scene was fetched
#	varchar pc_name : Name of scene point cloud
#	varchar image : Name of image (for sanity check feature)
#	varchar camera : Name of camera (Ex. NP3_rgb, NP5_ir)
#	varchar objects : A list of strings, stored such that eval will return the list


#####
#Getting matched results
#####
#getMatch( Pointcloud, Mesh)
getMatch( "NP3_165.ply", "circlefit_mesh.ply")
#Returns a string in the form:
"""

pcname = "NP3_165.ply"
mesh= "circlefit_mesh.ply"
matrix= [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

"""
#Where matrix[4*i+j]= m_i_j