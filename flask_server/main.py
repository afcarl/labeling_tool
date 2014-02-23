from flask import Flask, request, render_template, send_from_directory
from flask import url_for, redirect
import traceback
from server import *
import sql_interface as sql
import cam_parameters
from Settings import ROOT_URL, DEBUG, DOMAIN
import os

argnames = { 'pc':['pc','pointcloud','point_cloud'],
            'mat':['mat','matrix'],
            'usr':['usr','user','username'],
            'mesh':['mesh','object']}

app = Flask(__name__)

def getArg(name):
    for n in argnames[name]:
        obj = request.args.get(n)
        if obj:
            return obj
    return None

@app.route("/")
def test():
    return "Server is running!"

@app.route(ROOT_URL+"/appversion")
def appvers():
    return "1_00"

@app.route(ROOT_URL+"/getconfig")
def config_gen():
    d = "Date Generated: "+getDateStr()
    match = sql.getPendingMatch()
    if match:
        [pcname, objects, img, cam] = match
        print("DOMAIN: ",os.path.join(DOMAIN, ROOT_URL))
        return render_template('config.py', date = d,
            resource_dir = "http://"+DOMAIN+ROOT_URL+"/static/res",
            pcname = pcname,
            objects = objects,
            imgname = img,
            rgb_K = str(cam_parameters.getK(cam)),
            rgb_distort= str(cam_parameters.getDistortion(cam)))
    return "FAILURE: No pending matches"

@app.route(ROOT_URL+"/app")
def runApp():
    return redirect(url_for('static', filename='app.html'))

@app.route(ROOT_URL+"/static/<path:filen>")
def getStatic(filen):
    return redirect(url_for('static', filename=filen))


@app.route(ROOT_URL+"/retrieve")
def getResult():
    pc = getArg('pc')
    mesh = getArg('mesh')
    result = result_get(pc,mesh)
    if result:
        return result
    return "No match found"

@app.route(ROOT_URL+"/upload", methods=['GET','POST'])
def handle_upload():
    if request.method == 'POST':
        return handle_post_upload()    
    return handle_url_upload()

def handle_post_upload():
    try:
        matrix = request.form['matrix']
        pc = request.form['pc']
        mesh = request.form['mesh']
        usr = request.form['usr']
        matrix = parseMatrix(matrix)
        otherinfo = {}
        otherinfo['upload_time'] = getDateStr()
        result_store( pc, mesh, matrix, usr, otherinfo)
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
        usr = getArg('usr')
        otherinfo['upload_time'] = getDateStr()

        result_store( pc, mesh, matrix, usr, otherinfo)
        return "SUCCESS: Succesful upload!"
    except Exception as e:
        traceback.print_exc()
        return "FAILURE: "+(type(e))+' '+str(e)

if __name__ == "__main__":
    if DEBUG:
        app.config['DEBUG'] = True
        #app.config['APPLICATION_ROOT'] = '/poo'

        app.run()
    else:
        pass
        #app.run(host='0.0.0.0')

