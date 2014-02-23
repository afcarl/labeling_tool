#{{ date }}
def appendURL(x):
    return os.path.join( "{{ resource_dir }}", x)

config["rgb_K"] = {{ rgb_K }}
config["distort"] = {{ rgb_distort }}
config["point_cloud"]= appendURL("{{ pcname }}")
config["objects"]=list( map( appendURL, {{ objects }} )) 
config["ref_image"]= appendURL("{{ imgname }}")

def FINALIZE_MATCH(pcname, meshname, matrix, username):
    import Settings
    import Utils
    import urllib2
    post = ''
    post += 'pc='+pcname+'&'
    post += 'mesh='+meshname+'&'
    post += 'usr='+username+'&'
    post += 'matrix='
    for i in xrange(0,4):
        for j in xrange(0,4):
            post += str(matrix[i][j])+' '

    message = urllib2.urlopen(Settings.UPLOAD_URL, post).read()

    if message.startswith("SUCCESS"):
        #success
        Utils.createOKDialog("Successful upload")
        return True
    elif message.startswith("FAILURE"):
        #fail
        Utils.createOKDialog("Failed upload: "+message[0:60])       
        return False
    else:
        #Unknown. Assume failure
        return False

config["match_fun"]=FINALIZE_MATCH

