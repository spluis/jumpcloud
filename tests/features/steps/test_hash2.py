from behave import given, when, then
import os
import requests
import time
import subprocess
from threading import Thread
import json 
import random
import string
import datetime

hashID = None


######################
@given('the PORT is set to "{port}"')
def setPort(context, port):
    PortNumber = port
    context.portnum = port
    os.environ["PORT"]=port   

@given('the hashing server is running')
def startServer(context):
    subprocess.Popen(['open','./../../broken-hashserve_darwin'])
    time.sleep(3)
    
@when('I call POST to /hash with password {password} on port "{port}"')
def createHash(context, password, port):
    url = 'http://127.0.0.1:' + str(port) + '/hash'
    payload = {'password': password}
    headers = {"Content-Type": "application/json", "Accept-Charset": "UTF-8"}
    context.start = time.time()
    try:
        context.response = requests.post(url, json=payload, headers=headers)
        
    except requests.exceptions.ConnectionError:
        context.connError = True
    else: 
        context.sum+=context.response.elapsed.total_seconds()
        context.id = context.response.text
        return context.id
    

@then('I should receive an ID right away')
def receive_immediateResponse(context):
    roundtrip = time.time() - context.start
    assert roundtrip < 2, 'Expected a more immediate response with identifier'
    
@then('5 seconds later a 200 response')
def receive_200(context):
    assert context.response.status_code == '200', 'Expected a 200 Response'
    #TODO: Check response time in response body for >5sec
    ##assert createHash.res.status_code == 200
    #assert createHash.res.elapsed.total_seconds() >4.9
    
@then('I should receive a ConnectionRefused Error')
def verifyConnRefused(context):
    assert context.connError == True, 'Expected a ConnectionRefused Error'
 
#############    
@given('a hash is already created')
def assertHashIDCreated(context):
    hashID = createHash(context, generatePassword(), os.environ["PORT"])
    context.id = hashID
    assert hashID != None
    

@when('I call GET to /hash/ID')
def getHash(context):
    url = 'http://127.0.0.1:{portnum}/hash/{id}'.format(portnum=os.environ["PORT"],id=context.id)
    context.hash = requests.get(url).text
    
@then('I should receive a base64 password hash')
def assertHash(context):
    assert context.hash != None
    
@given('an INVALID HASH ID')
def setInvalidHashId(context):
    context.id = 1000

@then('I should receive an error')
def assertInvalidId(context):
    assert context.hash.strip() == "Hash not found", 'Expected to see "Hash not found" error'

################
@given('a reset of server')
def resetServer(context):
    shutdownServer(context)
    time.sleep(3)
    startServer(context)
    
@when('I call GET /STATS')
def getStats(context):
    context.response = requests.get('http://127.0.0.1:{portnum}/stats'.format(portnum=os.environ["PORT"]))
    context.newDict = json.loads(context.response.text) 
    
@then('I should receive JSON with "{totReqs}" TotalRequests')
def assertTotalRequests(context, totReqs):
    assert context.newDict['TotalRequests']==int(totReqs), 'Expected {totReqs} TotalRequests'.format(totReqs=totReqs)

@then('"{avgTime}" AverageTime')
def assertAvgTime(context, avgTime):
    if(avgTime=="0"):
        assert context.newDict['AverageTime']==int(avgTime), 'Expected AverageTime from /STATS to be 0 seconds'
    else:
        running_avg = context.sum/context.newDict['TotalRequests']*1000 
        assert context.newDict['AverageTime'] < running_avg +1000 and context.newDict['AverageTime'] > running_avg - 1000, 'Expected AverageTime from /STATS to be {avg}+-1sec - WAS {dictTime}'.format(avg=running_avg/1000,dictTime=context.newDict['AverageTime'])

##################

@given('I generate "{totReqs}" total requests since server boot')
def generate_x_hashes(context, totReqs):
    getStats(context)
    while(context.newDict['TotalRequests'] < int(totReqs)):
        createHash(context, generatePassword(), os.environ["PORT"])
        getStats(context)

##################
#
@given('I queue up "{nthreads}" threads for "{numPass}" passwords and a shutdown')
def queueThreads(context, nthreads, numPass):    
    context.threads = []  
    url = 'http://127.0.0.1:{portnum}/hash'.format(portnum=os.environ["PORT"])
    allPasswords = []
    for x in range(int(numPass)):
        allPasswords.append(generatePassword())
        
    headers = {"Content-Type": "application/json", "Accept-Charset": "UTF-8"}
    for i in range(int(nthreads)):
        passwords = allPasswords[i::int(nthreads)]
        context.t = Thread(target=createHash_range, args=(context, passwords,i))
        context.threads.append(context.t)
    
@when('I trigger them to POST /HASH')
def triggerThreads(context):
    [context.t.start() for context.t in context.threads ]
    shutdownServer(context)

@then('I should receive "{expResponses}" OK responses')
def expectResponses(context,expResponses):
    time.sleep(10)
    responses = len(context.store)
    assert responses == int(expResponses), 'We should have {expResponses} responses and had {responses} responses instead.'.format(expResponses=expResponses, responses=responses)
    context.store.clear()
    context.t = None
        
######

@then('Shutdown should occur with 200 Response')
def assertShutdown_success(context):
    assert int(context.shutdown.status_code) == 200, "Shutdown Should have received 200 Response - received {resp}".format(resp=context.response.content)
#####

def createHash_range(context, pass_range,i):
    if context.store is None:
        context.store = {}

    for password in range(len(pass_range)):
        context.store[i*len(pass_range)+password]  = createHash(context, pass_range[password], os.environ["PORT"])


def setup_server():
    portnum = "8088"
    os.environ["PORT"]="8088"
    subprocess.Popen(['open','./../../broken-hashserve_darwin'])
    time.sleep(3)

def shutdownServer(context):
    url = 'http://127.0.0.1:{portnum}/hash'.format(portnum=os.environ["PORT"])
    payload = 'shutdown'
    context.shutdown = requests.post(url,data=payload)
    context.sum = 0

def generatePassword():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

    