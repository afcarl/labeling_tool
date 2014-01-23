from flask import Flask, request, render_template, send_from_directory
from flask import url_for, redirect
import traceback
from server import *
import sql_interface as sql
import cam_parameters

app = Flask(__name__)

argnames = { 'pc':['pc','pointcloud','point_cloud'],
            'mat':['mat','matrix'],
            'mesh':['mesh','object']}

keys = {'test001'}

def testKey(k):
    return k in keys

def getArg(name):
    for n in argnames[name]:
        obj = request.args.get(n)
        if obj:
            return obj
    return None

@app.route("/test")
def test():
    return "Server is running!"

@app.route("/getconfig")
def config_gen():
    d = "Date Generated: "+getDateStr()
    match = sql.getPendingMatch()
    if match:
        [pcname, objects, img, cam] = match
        return render_template('config.py', date = d,
                                            pcname = pcname,
                                            objects = objects,
                                            imgname = img,
                                            rgb_K = str(cam_parameters.getK(cam)),
                                            rgb_distort= str(cam_parameters.getDistortion(cam)))
    return "FAILURE: No pending matches"

@app.route("/app")
def runApp():
    return redirect(url_for('static', filename='app.html'))

@app.route("/retrieve")
def getResult():
    pc = getArg('pc')
    mesh = getArg('mesh')
    result = result_get(pc,mesh)
    if result:
        return result
    return "No match found"

@app.route("/upload", methods=['GET','POST'])
def handle_upload():
    if request.method == 'POST':
        return handle_post_upload()    
    return handle_url_upload()

def handle_post_upload():
    try:
        matrix = request.form['matrix']
        pc = request.form['pc']
        mesh = request.form['mesh']
        matrix = parseMatrix(matrix)
        otherinfo = {}
        otherinfo['upload_time'] = getDateStr()
        result_store( pc, mesh, matrix, otherinfo)
        return "SUCCESS: Succesful upload!"
    except Exception as e:
        traceback.print_exc()
        return "FAILURE: "+str(type(e))+' '+str(e)

def handle_url_upload():
    try:
        matrix = getArg('mat')
        matrix = (parseMatrix(matrix))
        pc = getArg('pc')
        mesh = getArg('mesh')
        otherinfo['upload_time'] = getDateStr()

        result_store( pc, mesh, matrix, otherinfo)
        return "SUCCESS: Succesful upload!"
    except Exception as e:
        traceback.print_exc()
        return "FAILURE: "+(type(e))+' '+str(e)

if __name__ == "__main__":
    app.run(debug=True)

