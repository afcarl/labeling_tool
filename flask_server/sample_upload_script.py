from sql_interface import addScene, getMatch

#####################################
# Adding a scene to pending matches #
#####################################

# Use the addScene method
# Signature: addScene(Pointcloud, [List of objects], Image, Camera)
addScene("NP3_165.ply", ["circlefit_mesh.ply"], "NP3_165.jpg", "NP3_rgb")
#If using the database directly, upload to the pending table
#	int id (primary key)
#	int last_issued : Seconds since epoch of the last time this scene was fetched
#	varchar pc_name : Name of scene point cloud
#	varchar image : Name of image (for sanity check feature)
#	varchar camera : Name of camera (Ex. NP3_rgb, NP5_ir)
#	varchar objects : A list of strings, stored such that eval will return the list


##############################
# Retrieving matched results #
##############################
# Use the getMatch method
# Signature: getMatch( Pointcloud Name, Mesh Name)
m = getMatch( "NP3_165.ply", "circlefit_mesh.ply")
print( m.pcname, " ", m.meshname, " ",m.matrix)
#Where matrix[4*i+j]= m_i_j