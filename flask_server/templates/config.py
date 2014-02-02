#{{ date }}
#base_url = "http://127.0.0.1:5000/static/res/"
def appendURL(x):
    return "http://127.0.0.1:5000/static/res/"+x

"""
config["rgb_K"] = [[1.07452881e3,0,6.37934076e2],
                    [0,1.07579061e3,5.09474174e2],
                    [0,0,1]]
config["distort"] = [0,0,0,0,0]
config["point_cloud"]=base_url+"NP3_165.ply"
config["objects"]=[base_url+"circlefit_mesh.ply"]
config["ref_image"]=base_url+"NP3_165.jpg"
"""

config["rgb_K"] = {{ rgb_K }}
config["distort"] = {{ rgb_distort }}
config["point_cloud"]= appendURL("{{ pcname }}")
config["objects"]=list( map( appendURL, {{ objects }} )) 
config["ref_image"]= appendURL("{{ imgname }}")

def FINALIZE_MATCH(pcname, meshname, matrix):
    weburl = 'http://127.0.0.1:5000/upload'
    post = ''
    post += 'pc='+pcname+'&'
    post += 'mesh='+meshname+'&'
    post += 'matrix='
    for i in xrange(0,4):
        for j in xrange(0,4):
            post += str(matrix[i][j])+' '
    #http://127.0.0.1:5000/upload/test001?pointcloud=NP3_165&mesh=circlefit&matrix=2.3e4%201.7%201%201%201%201%201%201%201%201%201%201%201%201%201%201 
    import urllib2
    message = urllib2.urlopen(weburl, post).read()
    import Utils
    if message.startswith("SUCCESS"):
        #success
        Utils.createOKDialog("Successful upload")
        return True
    elif message.startswith("FAILURE"):
        #fail
        Utils.createOKDialog("Failed upload: "+message)       
        return False
    else:
        #Unknown. Assume failure
        return False

config["match_fun"]=FINALIZE_MATCH

