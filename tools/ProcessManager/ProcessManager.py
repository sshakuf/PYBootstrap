#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
from flask import Flask, render_template, Response
from flask import jsonify
import os
from dronekit import connect, VehicleMode
import thread
import time

app = Flask(__name__)


@app.route('/')
def index():
    pid, procs= findPythonProcess('.py')
    print (procs)
    pid, pft= findProcess('node' ,'frontail')
    return render_template('procman.html', proc=procs + pft)

@app.route('/kill/<int:inPID>')
def kill(inPID):
    p = psutil.Process(inPID)
    p.kill()
    pid, procs= findPythonProcess('run.py')
    return render_template('procman.html', proc=procs)
    # return redirect(url_for('index'))


@app.route('/run')
def run():
    print ("run DronePi")
    pid, procs= findPythonProcess('run.py')
    print (pid)
    if (len(pid) == 0):
        print ("Starting Run.py")
        cwd = os.getcwd()
        p = psutil.Popen(["/usr/bin/python2", "./run.py", "settings.json"], cwd = cwd )
        
        #popen(cmd, mode='r', buffering=-1)
    pid, procs= findPythonProcess('run.py')
    return render_template('procman.html', proc=procs)

@app.route('/runfrontail')
def runfrontail():
    print ("run frontail")
    pid, pft= findProcess('node' ,'frontail')
    print (pid)
    if (len(pid) == 0):
        print ("Starting frontail")
        cwd = os.getcwd()
        p = psutil.Popen(["frontail", "raw/log.log"], cwd = cwd )
        #p = psutil.Popen(["frontail", "/private/var/log/system.log"], cwd = cwd )
        
        #popen(cmd, mode='r', buffering=-1)
    pid, procs= findPythonProcess('run.py')
    return render_template('procman.html', proc=procs)

@app.route('/udpplayer')
def udpplayer():
    print ("run udpplayer")
    pid, pft= findProcess('python' ,'udpplayer')
    print (pid)
    if (len(pid) == 0):
        print ("Starting udpplayer")
        cwd = os.getcwd()
        p = psutil.Popen(["/usr/bin/python2", "./UDPPlayer.py"], cwd = cwd )
        
        #popen(cmd, mode='r', buffering=-1)
    pid, procs= findPythonProcess('run.py')
    return render_template('procman.html', proc=procs)



# @app.route('/summary')
# def summary():
#     data = make_summary()
#     response = app.response_class(
#         response=json.dumps(data),
#         status=200,
#         mimetype='application/json'
#     )
#     return response


def runFlask():
    try:
        DataStore.flaskApp = app
        # app.run(host='0.0.0.0', debug=True, use_reloader=False, port=8091)
    except Exception as err:
        DataStore.PrintError(err)


#psutil.pids()
def findPythonProcess(inScriptName):
    return findProcess("python", inScriptName)

def findProcess(inProgName, inScriptName):
    pids=[]
    procs = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cmdline'])
            cmd = pinfo['cmdline']
            if inProgName in pinfo['name'].lower():
                #print(cmd)
                if (cmd != None and inScriptName in " ".join(cmd)):
                    #print (cmd)
                    pid = pinfo['pid']
                    print ("found " + inScriptName +" in PID=" + str(pid))
                    pids.append(pid)
                    procs.append(pinfo)
        except psutil.NoSuchProcess:
            pass
        else:
            pass
            #print(pinfo)
    return pids, procs



def mode_callback(self, attr_name, value):
    print (attr_name)
    print (value)

def connectDrone():
    global vehicle
    
    connection_string = "udp:127.0.0.1:14554"

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    vehicle = connect(connection_string, wait_ready=True)

    #vehicle.add_attribute_listener('mode', mode_callback)

    while(True):
        c8 = vehicle.channels['8']
        if c8 > 1700:
                pid, procs= findPythonProcess('run.py')
                print (pid)
                if (len(pid) > 0):
                    kill(pid[0])
                    print ("Channel 8 on Killing Current Run.py")

        time.sleep(5)

    

if __name__ == '__main__':
    #thread.start_new_thread(connectDrone, ())

    app.run(host='0.0.0.0', port=8080, use_reloader=False, debug=True)

    