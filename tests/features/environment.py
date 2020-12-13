import time
import os
import subprocess
import requests


#def setup_server():
#    portnum = "8088"
#    os.environ["PORT"]="8088"
#    subprocess.Popen(['open','./../../broken-hashserve_darwin'])
#    time.sleep(3)

#def shutdownServer():
#    url = 'http://127.0.0.1:8088/hash'
#    payload = 'shutdown'
#    res = requests.post(url,data=payload)


def before_all(context):
    #setup_server()
    context.start = None
    context.stop = None
    context.response = None
    context.id = None
    context.hash = None
    context.portnum = None
    context.connError = False
    context.sum = 0
    context.storeSize = 0
    context.store = {}
    context.shutdown = None