import App
import getopt
import sys
import Settings

"""
if __name__ == "__main__":
    def usage():
        print "Labeling tool"
        print "-p PLYFILE | --pointcloud=PLYFILE Specify the PLY geom file of the point cloud"
        print "-m PLYFILE | --matcher=PLYFILE Specify the PLY geom file of the matching object"
        print "-v | --verbose Print verbose (mostly debugging) information"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "p:m:v", ["pointcloud=", "matcher=","verbose"])
    except Exception as e:
        usage()
        exit()

    pfile = None
    mfile = None
    for o,a in opts:
        if o in ("-p", "--pointcloud="):
            pfile = a
        elif o in ("-m", "--matcher="):
            mfile = a
        elif o in ("-v", "--verbose"):
            Settings.VERBOSE = True
            
    app = App.MyApp()
    if pfile:
        app.pointcloud.changeObject(pfile)
        app.pointcloud.setPointCloudThickness(4)
    if mfile:
        app.loadMatchObject(mfile)
    run()
"""
print "RUNNING"
app = App.MyApp()
run()    

