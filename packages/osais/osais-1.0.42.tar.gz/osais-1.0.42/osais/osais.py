
__version__="1.0.42"

## ========================================================================
## 
##                      Utilities starts here 
## 
## ========================================================================

## ------------------------------------------------------------------------
#       OSAIS python Tools (used by libOSAISVirtualAI.py)
## ------------------------------------------------------------------------

import uuid 
import subprocess as sp
import pkg_resources
import os
import platform
import ctypes
import threading
import boto3

cuda=0                          ## from cuda import cuda, nvrtc
gObserver=None

## ------------------------------------------------------------------------
#       Observer (check updates in directory)
## ------------------------------------------------------------------------

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, fnOnFileCreated, _args):
        self.fnOnFileCreated = fnOnFileCreated
        self._args = _args

    def on_created(self, event):
        global gS3Bucket
        global gS3

        if event.is_directory:
            return
        if event.event_type == 'created':
            ## only notify if uid in the filename (otherwise we are getting notified of another AI's job !)
            if self._args["-uid"] in event.src_path:
                self.fnOnFileCreated(os.path.dirname(event.src_path), os.path.basename(event.src_path), self._args)

                ## also send to S3
                osais_uploadeFileToS3(event.src_path, "output/")

def start_observer_thread(path, fnOnFileCreated, _args):

    ## watch directory and call back if file was created
    def watch_directory(path, fnOnFileCreated, _args):    
        global gObserver
        if gObserver!=None:
            gObserver.stop()
        event_handler = NewFileHandler(fnOnFileCreated, _args)
        gObserver = Observer()
        gObserver.schedule(event_handler, path, recursive=False)
        gObserver.start()
        gObserver.join(1)

    thread = threading.Thread(target=watch_directory, args=(path, fnOnFileCreated, _args))
    thread.start()
    return watch_directory

def start_notification_thread(fnOnNotify):
    def _run(_fn):
        _fn()
    thread = threading.Thread(target=_run, args=(fnOnNotify))
    thread.start()
    return _run

## ------------------------------------------------------------------------
#       Directory utils
## ------------------------------------------------------------------------

## list content of a directory
def listDirContent(_dir):
    from os.path import isfile, join
    onlyfiles = [f for f in os.listdir(_dir)]
    ret="Found "+str (len(onlyfiles)) + " files in path "+_dir+"<br><br>";
    for x in onlyfiles:
        if isfile(join(_dir, x)):
            ret = ret+x+"<br>"
        else:
            ret = ret+"./"+x+"<br>"

    from datetime import datetime
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string+"<br>"+ret

def clearOldFiles(_dir):  
    from datetime import timedelta
    from datetime import datetime
    _now=datetime.now()
    cutoff_time = _now - timedelta(minutes=10)
    for filename in os.listdir(_dir):
        file_path = os.path.join(_dir, filename)
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if modification_time < cutoff_time:
            os.remove(file_path)
            
## ------------------------------------------------------------------------
#       System utils
## ------------------------------------------------------------------------

def consoleLog(err): 
    msg=""
    if hasattr(err, 'msg'):
        msg=err.msg
    else:
        if err.args and err.args[0]:
            msg=err.args[0]                      
    print("CRITICAL: "+msg)

## get a meaningful name for our machine
def get_machine_name() :
    _machine=str (hex(uuid.getnode()))
    _isDocker=is_running_in_docker()
    if _isDocker:
        _machine = os.environ.get('HOSTNAME') or os.popen('hostname').read().strip()
    return _machine

## which OS are we running on?
def get_os_name():
    os_name = platform.system()
    return os_name

## Are we running inside a docker session?
def is_running_in_docker():
    if os.path.exists('/proc/self/cgroup'):
        with open('/proc/self/cgroup', 'rt') as f:
            return 'docker' in f.read()
    return False

## get ip address of the host
def get_container_ip():
    import socket

    # Get the hostname of the machine running the script
    hostname = socket.gethostname()

    # Get the IP address of the container by resolving the hostname
    ip_address = socket.gethostbyname(hostname)
    return ip_address

## get our external ip address
def get_external_ip():
    import requests
    url = "https://api.ipify.org"
    response = requests.get(url)
    return response.text.strip()

## get our external port
def get_port(): 
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    return port

## just to get the list of all installed Python modules in the running session
def get_list_of_modules():
    installed_packages = pkg_resources.working_set
    installed_packages_list=[]
    for i in installed_packages:
        installed_packages_list.append({i.key: i.version})
    return installed_packages_list

## ------------------------------------------------------------------------
#       GPU utils
## ------------------------------------------------------------------------

## which GPU is this? (will require access to nvidia-smi)
def get_gpu_attr(_attr):
   output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
   COMMAND = "nvidia-smi --query-gpu="+_attr+" --format=csv"
   try:
        memory_use_info = output_to_list(sp.check_output(COMMAND.split(),stderr=sp.STDOUT))[1:]
   except sp.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
   memory_use_values = [x.replace('\r', '') for i, x in enumerate(memory_use_info)]
   return memory_use_values


## get GPU Cuda info
# see here: https://gist.github.com/tispratik/42a71cae34389fd7c8e89496ae8813ae
def getCudaInfo():
    
    display_name = "no GPU"
    display_cores = "0"
    display_major = "0"
    display_minor = "0"

    if cuda:
        CUDA_SUCCESS = 0
        CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT = 16
        CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR = 39
        CU_DEVICE_ATTRIBUTE_CLOCK_RATE = 13
        CU_DEVICE_ATTRIBUTE_MEMORY_CLOCK_RATE = 36

        nGpus = ctypes.c_int()
        name = b' ' * 100
        cc_major = ctypes.c_int()
        cc_minor = ctypes.c_int()
        cores = ctypes.c_int()
        threads_per_core = ctypes.c_int()
        clockrate = ctypes.c_int()
        freeMem = ctypes.c_size_t()
        totalMem = ctypes.c_size_t()

        result = ctypes.c_int()
        device = ctypes.c_int()
        context = ctypes.c_void_p()
        error_str = ctypes.c_char_p()

        result=cuda.cuInit(0)
        if(result != CUDA_SUCCESS):
            print("error %d " % (result))
            return 0
        
        if(cuda.cuDeviceGetCount(ctypes.byref(nGpus)) != CUDA_SUCCESS):
            return 0

        for i in range(nGpus.value):

            # get device
            if(cuda.cuDeviceGet(ctypes.byref(device), i) != CUDA_SUCCESS):
                return 0
            if (cuda.cuDeviceComputeCapability(ctypes.byref(cc_major), ctypes.byref(cc_minor), device) != CUDA_SUCCESS):  
                return 0
            if (cuda.cuDeviceGetName(ctypes.c_char_p(name), len(name), device) != CUDA_SUCCESS): 
                return 0
            if(cuda.cuDeviceGetAttribute(ctypes.byref(cores), CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT, device) != CUDA_SUCCESS):
                return 0

        display_name=name.split(b'\0', 1)[0].decode()
        display_major=cc_major.value
        display_minor=cc_minor.value
        display_cores=cores.value * _ConvertSMVer2Cores(cc_major.value, cc_minor.value)

    return {
        "name": display_name,
        "compute_major": display_major,
        "compute_minor": display_minor,
        "cuda cores": display_cores 
    }

def _ConvertSMVer2Cores(major, minor):
    # Returns the number of CUDA cores per multiprocessor for a given
    # Compute Capability version. There is no way to retrieve that via
    # the API, so it needs to be hard-coded.
    return {
    # Tesla
      (1, 0):   8,      # SM 1.0
      (1, 1):   8,      # SM 1.1
      (1, 2):   8,      # SM 1.2
      (1, 3):   8,      # SM 1.3
    # Fermi
      (2, 0):  32,      # SM 2.0: GF100 class
      (2, 1):  48,      # SM 2.1: GF10x class
    # Kepler
      (3, 0): 192,      # SM 3.0: GK10x class
      (3, 2): 192,      # SM 3.2: GK10x class
      (3, 5): 192,      # SM 3.5: GK11x class
      (3, 7): 192,      # SM 3.7: GK21x class
    # Maxwell
      (5, 0): 128,      # SM 5.0: GM10x class
      (5, 2): 128,      # SM 5.2: GM20x class
      (5, 3): 128,      # SM 5.3: GM20x class
    # Pascal
      (6, 0):  64,      # SM 6.0: GP100 class
      (6, 1): 128,      # SM 6.1: GP10x class
      (6, 2): 128,      # SM 6.2: GP10x class
    # Volta
      (7, 0):  64,      # SM 7.0: GV100 class
      (7, 2):  64,      # SM 7.2: GV11b class
    # Turing
      (7, 5):  64,      # SM 7.5: TU10x class
    }.get((major, minor), 64)   # unknown architecture, return a default value

## ------------------------------------------------------------------------
#       getInfo endoint
## ------------------------------------------------------------------------

## get various info about this host
def getHostInfo(_engine):
    from datetime import datetime
    now = datetime.now()
    objGPU={}
    objGPU["memory_free"]=get_gpu_attr("memory.free")[0]
    objGPU["memory_used"]=get_gpu_attr("memory.used")[0]
    objGPU["name"]=get_gpu_attr("gpu_name")[0]
    objGPU["driver_version"]=get_gpu_attr("driver_version")[0]
    objGPU["temperature"]=get_gpu_attr("temperature.gpu")[0]
    objGPU["utilization"]=get_gpu_attr("utilization.gpu")[0]

    objCuda=getCudaInfo()        
    return {
        "datetime": now.strftime("%d/%m/%Y %H:%M:%S"), 
        "isDocker": is_running_in_docker(),
        "internal IP": get_container_ip(),
        "port": get_port(),
        "engine": _engine,
        "machine": get_machine_name(),
        "GPU": objGPU,
        "Cuda": objCuda,
        "modules": get_list_of_modules()
    }

## ------------------------------------------------------------------------
#       File / Image utils
## ------------------------------------------------------------------------

## downloads an image as file from external URL
def downloadImage(url) :
    import urllib.request

    # Determine the file name and extension of the image based on the URL.
    file_name, file_extension = os.path.splitext(url)
    
    # Define the local file path where the image will be saved.
    spliter='/'
    local_filename=file_name.split(spliter)[-1]
    local_file_path = f"./_input/{local_filename}{file_extension}"
    
    # Download the image from the URL and save it locally.
    urllib.request.urlretrieve(url, local_file_path)
    return f"{local_filename}{file_extension}"

def osais_uploadeFileToS3(_filename, _dirS3): 
    global gS3

    if gS3!=None:
        try:
            # Filename - File to upload
            # Bucket - Bucket to upload to (the top level directory under AWS S3)
            # Key - S3 object name (can contain subdirectories). If not specified then file_name is used
            gS3.meta.client.upload_file(Filename=_filename, Bucket=gS3Bucket, Key=_dirS3+os.path.basename(_filename))
            return True
        except Exception as err:
            consoleLog({"msg":"Could not upload file to S3"})
            raise err
        
    return False

## ========================================================================
## 
##                      OSAIS starts here 
## 
## ========================================================================

## ------------------------------------------------------------------------
#       OSAIS python Lib (interface between AIs and OSAIS)
## ------------------------------------------------------------------------

import requests
import schedule
import json
import sys
import base64
from datetime import datetime
import argparse

## from osais_utils import getHostInfo, listDirContent, is_running_in_docker, get_external_ip, get_container_ip, get_machine_name, get_os_name, getCudaInfo, downloadImage, start_observer_thread, clearOldFiles, start_notification_thread

## ------------------------------------------------------------------------
#       all global vars
## ------------------------------------------------------------------------

gVersionLibOSAIS=__version__    ## version of this library (to keep it latest everywhere)
gUsername=None                  ## user owning this AI (necessary to claim VirtAI regs)

gName=None                      ## name of this AI (name of engine)
gVersion="0.0.0"                ## name of this AI's version (version of engine)
gDescription=None               ## AI's quick description
gOrigin=None                    ## where this AI came from (on internet)
gMachineName=get_machine_name() ## the name of the machine (will change all the time if inside docker, ot keep same if running on local server)
gLastChecked_at=datetime.utcnow()  ## when was this AI last used for processing anything
gLastProcessStart_at=None       ## when was this AI last start event for processing anything

## authenticate into OSAIS
gAuthToken=None                 ## auth token into OSAIS for when working as virtual Ai
gToken=None                     ## token used for authentication into OSAIS
gSecret=None                    ## secret used for authentication into OSAIS
gOriginOSAIS=None               ## location of OSAIS

## authenticate into a local OSAIS (debug)
gAuthTokenLocal=None            ## auth token into a local OSAIS (debug) for when working as virtual Ai
gTokenLocal=None                ## token used for authentication into a local OSAIS (debug)
gSecretLocal=None               ## secret used for authentication into a local OSAIS (debug)
gOriginLocalOSAIS=None          ## location of a local OSAIS (debug)
gClientID=None                  ## ID to authenticate as client into OSAIS (using the ai page to request AI processing)
gClientSecret=None              ## Pwd to authenticate as client into OSAIS (using the ai page to request AI processing)
gClientAuthToken=None           ## the resulting Auth token as Client, after login
gClientAuthTokenLocal=None      ## the resulting Auth token as Client, after login (for debug)

gOriginGateway=None             ## location of the local gateway for this (local) AI

## AWS related
gS3=None
gS3Bucket=None
gAWSSession=None

## IP and Ports
gExtIP=get_external_ip()        ## where this AI can be accessed from outside (IP)
gIPLocal=get_container_ip()     ## where this AI can be accessed locally
gPortAI=None                    ## port where this AI is accessed (will be set by AI config)
gPortGateway=3023               ## port where the gateway can be accessed
gPortLocalOSAIS=3022            ## port where a local OSAIS can be accessed

## virtual AI / local /docker ?
gIsDocker=is_running_in_docker()   ## are we running in a Docker?
gIsVirtualAI=False              ## are we working as a Virtual AI config?
gIsLocal=False                  ## are we working locally (localhost server)?

## temp cache
gAProcessed=[]                  ## all token being sent to processing (never call twice for same)
gIsScheduled=False              ## do we have a scheduled event running?

## run times
gIsWarmup=False                 ## True if the request was a warmup one (not a true one from client)
gIsBusy=False                   ## True if AI busy processing
gDefaultCost=1000               ## default cost value in ms (will get overriden fast, this value is no big deal)
gaProcessTime=[]                ## Array of last x (10/20?) time spent for processed requests 

## processing specifics
gArgsOSAIS=None                 ## the args passed to the AI which are specific to OSAIS for sending notifications

## when running as vAI
gInputDir="./_input/"
gOutputDir="./_output/"

AI_PROGRESS_ERROR=-1
AI_PROGRESS_REQSENT=0                  # unused (that s for OSAIS to know it sent the req)
AI_PROGRESS_REQRECEIVED=1
AI_PROGRESS_AI_STARTED=2
AI_PROGRESS_INIT_IMAGE=3
AI_PROGRESS_DONE_IMAGE=4
AI_PROGRESS_AI_STOPPED=5

## ------------------------------------------------------------------------
#       Load config
## ------------------------------------------------------------------------

# load the config file into a JSON
def _loadConfig(_name): 
    global gVersion
    global gDescription
    global gOrigin
    global gDefaultCost

    _json = None
    _dirFile=None
    try:
        from pathlib import Path
        current_working_directory = Path.cwd()
        _dirFile=f'{current_working_directory}/{_name}.json'
        fJSON = open(_dirFile)
        _json = json.load(fJSON)
    except Exception as err:
        print(f'CRITICAL: No config file {_dirFile}')
        sys.exit()

    gVersion=_json["version"]
    gDescription=_json["description"]
    gOrigin=_json["origin"]
    _cost=_json["default_cost"]
    if _cost!=None:
        gDefaultCost=_cost

    return _json

# get the full AI config, including JSON params and hardware info
def _getFullConfig(_name) :
    global gUsername
    global gPortAI
    global gName
    global gToken
    global gSecret
    global gOriginOSAIS
    global gTokenLocal
    global gSecretLocal
    global gOriginLocalOSAIS
    global gIsVirtualAI
    global gIPLocal
    global gExtIP
    global gIsLocal
 
    _ip=gExtIP
    if gIsVirtualAI==False:
        _ip=gIPLocal                ## we register with local ip if we are in local gateway mode

    _jsonAI=_loadConfig(_name)
    _jsonBase=_loadConfig("osais")

    objCudaInfo=getCudaInfo()
    gpuName="no GPU"
    if objCudaInfo != 0 and "name" in objCudaInfo and objCudaInfo["name"]:
        gpuName=objCudaInfo["name"]
    _osais="https://opensourceais.com/"
    if gIsLocal: 
        _osais="http://"+_ip+":3022/"

    return {
        "username": gUsername,
        "os": get_os_name(),
        "gpu": gpuName,
        "machine": get_machine_name(),
        "ip": _ip,
        "port": gPortAI,
        "osais": _osais,
        "gateway": "http://"+_ip+":3023/",
        "config_ai": _jsonAI,
        "config_base": _jsonBase
    }

## PUBLIC - are we running locally?
def osais_isLocal():
    global gIsLocal
    return gIsLocal

## PUBLIC - load the config of this AI
def osais_loadConfig(_name): 
    return _loadConfig(_name)

## PUBLIC - Get env from file (local or docker)
def osais_getEnv(_filename):
    global gUsername
    global gDemoID
    global gDemoSecret
    global gIsVirtualAI
    global gIsLocal
    global gName
    global gAWSSession
    global gS3
    global gS3Bucket

    AWSID=None
    AWSSecret=None

    ## read env from config file
    try:
        with open(_filename, "r") as f:
            content = f.read()
        print(f'Reading env vars from {_filename}')
        variables = content.split("\n")
        for var in variables:
            if var!="":
                key, value = var.split("=")
                if key == "USERNAME":
                    gUsername = value
                elif key == "IS_LOCAL":
                    gIsLocal = (value=="True")
                elif key == "IS_VIRTUALAI":
                    gIsVirtualAI = (value=="True")
                elif key == "ENGINE":
                    gName = value
                elif key == "S3_BUCKET":
                    gS3Bucket = value
                elif key == "AWS_ACCESS_KEY_ID":
                    AWSID = value
                elif key == "AWS_ACCESS_KEY_SECRET":
                    AWSSecret = value
    except Exception as err: 
        print(f'No env file {_filename}')

    # overload with env settings if any
    if os.environ.get('IS_LOCAL'):
        _isLocal=(os.environ.get('IS_LOCAL')=="True")
        if _isLocal!=gIsLocal:
            print(f'is Local updated to {_isLocal} from ENV var')
            gIsLocal=_isLocal
    if os.environ.get('IS_VIRTUALAI'):
        _isVirtualAI=(os.environ.get('IS_VIRTUALAI')=="True")
        if _isVirtualAI!=gIsVirtualAI:
            print(f'is Virtual updated to {_isVirtualAI} from ENV var')
            gIsVirtualAI=_isVirtualAI
    if os.environ.get('ENGINE'):
        _name=os.environ.get('ENGINE')
        if _name!=gName:
            print(f'Engine name updated to {_name} from ENV var')
            gName=_name
    if os.environ.get('S3_BUCKET'):
        _s3=os.environ.get('S3_BUCKET')
        if _s3!=gS3Bucket:
            print(f'Set S3 bucket to {_s3} from ENV var')
            gS3Bucket=_s3
    if os.environ.get('USERNAME') and gUsername==None:
        gUsername=os.environ.get('USERNAME')
    if os.environ.get('AWS_ACCESS_KEY_ID') and AWSID==None:
        AWSID=os.environ.get('AWS_ACCESS_KEY_ID')
    if os.environ.get('AWS_ACCESS_KEY_SECRET') and AWSSecret==None:
        AWSSecret=os.environ.get('AWS_ACCESS_KEY_SECRET')

    if AWSID!=None and AWSSecret!=None:
        gAWSSession = boto3.Session(
            aws_access_key_id=AWSID,
            aws_secret_access_key=AWSSecret
        )
        gS3 = gAWSSession.resource('s3')
        print(f'Logged into AWS S3')
        
    return {
        "username": gUsername,
        "isLocal": gIsLocal,
        "isVirtualAI": gIsVirtualAI,
        "name": gName
    }

## ------------------------------------------------------------------------
#       cost calculation
## ------------------------------------------------------------------------

# init the dafault cost array
def _initializeCost() :
    global gDefaultCost
    global gaProcessTime
    from array import array
    gaProcessTime=array('f', [gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost,gDefaultCost])

# init the dafault cost array
def _addCost(_cost) :
    global gIsWarmup
    global gaProcessTime
    if gIsWarmup==False:
        gaProcessTime.insert(0, _cost)
        gaProcessTime.pop()

# init the dafault cost array
def _getAverageCost() :
    global gaProcessTime
    average = sum(gaProcessTime) / len(gaProcessTime)
    return average

## ------------------------------------------------------------------------
#       args processing
## ------------------------------------------------------------------------

# where is the output dir?
def _getOutputDir():
    global gArgsOSAIS
    global gOutputDir

    if gArgsOSAIS!=None:
        return gArgsOSAIS.outdir
    return gOutputDir

# receives args from request and put them in a array for processing
def _getArgs(_args):
    aResult = []
    for key, value in _args.items():
        if key.startswith("-"):
            aResult.append(key)
            aResult.append(value)
    return aResult

# give new args 
def _argsFromFilter(_originalArgs, _aFilter, _bKeep):
    from werkzeug.datastructures import MultiDict
    _dict = MultiDict([])
    for i, arg in enumerate(_originalArgs):
        if _bKeep:
            if arg in _aFilter and i < len(_originalArgs) - 1:
                _dict.add(arg, _originalArgs[i+1])
        else:
            if arg not in _aFilter and i < len(_originalArgs) - 1:
                _dict.add(arg, _originalArgs[i+1])
    
    _args=_getArgs(_dict)
    return _args

## ------------------------------------------------------------------------
#       System info
## ------------------------------------------------------------------------

def _clearDir():
    clearOldFiles(gInputDir)
    clearOldFiles(gOutputDir)

## PUBLIC - info about harware this AI is running on
def osais_getHarwareInfo() :
    global gName
    return getHostInfo(gName)

## PUBLIC - get list of files in a dir (check what was generated)
def osais_getDirectoryListing(_dir) :
    return listDirContent(_dir)

## PUBLIC - info about this AI
def osais_getInfo() :
    global gExtIP
    global gPortAI
    global gName
    global gVersion
    global gIsDocker
    global gMachineName
    global gUsername
    global gIsBusy
    global gLastProcessStart_at
    global gLastChecked_at

    objConf=_getFullConfig(gName)

    return {
        "name": gName,
        "version": gVersion,
        "location": f'http://{objConf["ip"]}:{objConf["port"]}/',
        "osais": objConf["osais"],
        "gateway": objConf["gateway"],
        "isRunning": True,    
        "isDocker": gIsDocker,    
        "lastActive_at": gLastChecked_at,
        "lastProcessStart_at": gLastProcessStart_at,
        "machine": gMachineName,
        "owner": gUsername, 
        "isAvailable": (gIsBusy==False),
        "averageResponseTime": _getAverageCost(), 
        "config_ai": objConf["config_ai"],
        "config_base": objConf["config_base"]
    }

## ------------------------------------------------------------------------
#       connect to Gateway
## ------------------------------------------------------------------------

# notify the gateway of our AI config file
def _notifyGateway() : 
    global gName
    global gOriginGateway

    headers = {
        "Content-Type": 'application/json', 
        'Accept': 'text/plain',
    }
    objParam=_getFullConfig(gName)

    ## notify gateway
    try:
        response = requests.post(f"{gOriginGateway}api/v1/public/ai/config", headers=headers, data=json.dumps(objParam))
        objRes=response.json()["data"]
        if objRes is None:
            raise ValueError("CRITICAL: could not notify Gateway")

    except Exception as err:
        consoleLog({"msg":"CRITICAL: could not notify Gateway"})
        raise err
    return True

## PUBLIC - Reset connection to local gateway
def osais_resetGateway(_localGateway):
    global gOriginGateway
    gOriginGateway=_localGateway
    try:
        _notifyGateway()
    except Exception as err:
        consoleLog({"msg":"Could not reset connection to Gateway"})
        raise err
    
    print("=> This AI is reset to talk to Gateway "+_localGateway)
    return True

## ------------------------------------------------------------------------
#       authenticate into OSAIS as virtual AI
## ------------------------------------------------------------------------

# Register our VAI into OSAIS
def _registerVAI(_originOSAIS):
    global gName
    global gToken
    global gSecret
    global gOriginOSAIS
    global gTokenLocal
    global gSecretLocal
    global gOriginLocalOSAIS
    global gIsLocal

    headers = {
        "Content-Type": 'application/json', 
        'Accept': 'text/plain',
    }
    objParam=_getFullConfig(gName)

    ## our AI is on AWS
    if gIsLocal==False:
        # make it call the OSAIS that was requested to call (prod or local)
        isProdToProd=(_originOSAIS==None)
        if _originOSAIS==None:
            _originOSAIS=gOriginOSAIS
        try:
            response = requests.post(f"{_originOSAIS}api/v1/public/virtualai/register", headers=headers, data=json.dumps(objParam))
            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT REGISTER, stopping it here")
                sys.exit()

            if isProdToProd:
                gToken=objRes["token"]
                gSecret=objRes["secret"]
            else :
                gTokenLocal=objRes["token"]
                gSecretLocal=objRes["secret"]

            print("We are REGISTERED with OSAIS Prod")
        except Exception as err:
            consoleLog({"msg":"Exception raised while trying to register to PROD"})
            raise err

    ## our AI is local, reg with Local OSAIS (debug)
    else:
        try:
            response = requests.post(f"{gOriginLocalOSAIS}api/v1/public/virtualai/register", headers=headers, data=json.dumps(objParam))
            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT REGISTER with debug")

            gTokenLocal=objRes["token"]
            gSecretLocal=objRes["secret"]
            print("We are REGISTERED with OSAIS Local (debug)")
        except Exception as err:
            consoleLog({"msg":"Exception raised while trying to register to DEBUG"})
            raise err

    return True

# Authenticate into OSAIS
def _loginVAI(_originOSAIS):
    global gToken
    global gSecret
    global gAuthToken
    global gTokenLocal
    global gSecretLocal
    global gAuthTokenLocal

    headers = {
        "Content-Type": "application/json"
    }

    if gToken!= None:
        try:
            response = requests.post(f"{gOriginOSAIS}api/v1/public/virtualai/login", headers=headers, data=json.dumps({
                "token": gToken,
                "secret": gSecret
            }))

            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT LOGIN, stopping it here")
                sys.exit()
            print("We got an authentication token into OSAIS")
            gAuthToken=objRes["authToken"]    
        except Exception as err:
            consoleLog({"msg":"Exception raised while trying to login to PROD"})
            raise err

    if gTokenLocal!= None:
        if _originOSAIS==None:
            _originOSAIS=gOriginLocalOSAIS
        try:
            response = requests.post(f"{_originOSAIS}api/v1/public/virtualai/login", headers=headers, data=json.dumps({
                "token": gTokenLocal,
                "secret": gSecretLocal
            }))

            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT LOGIN into OSAIS Local")
            print("We got an authentication token into OSAIS Local (debug)")
            gAuthTokenLocal=objRes["authToken"]    
        except Exception as err:
            return True

    return True

## PUBLIC - Authenticate the Virtual AI into OSAIS
def osais_authenticateAI(_originOSAIS):
    global gIsVirtualAI
    global gOriginOSAIS
    global gIsScheduled
    global gDemoID
    global gDemoSecret
    
    resp={"data": None}
    if gIsVirtualAI:
        try:
            resp= _registerVAI(_originOSAIS)
            resp=_loginVAI(_originOSAIS)
        except Exception as err:
            consoleLog({"msg":"Exception raised while trying to authenticate to OSAIS"})
            raise err
        
        # Run the scheduler
        if gIsScheduled==False:
            gIsScheduled=True
            schedule.every().day.at("10:30").do(_loginVAI)

    return resp

## ------------------------------------------------------------------------
#       authenticate into OSAIS as Client (user)
## ------------------------------------------------------------------------

def getClientInfo(_authToken):
    global gOriginOSAIS
    global gOriginLocalOSAIS

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_authToken}"
    }

    objRes=None
    if gIsLocal:        # if local 
        try:
            response = requests.get(f"{gOriginLocalOSAIS}api/v1/private/client", headers=headers)
            objRes=response.json()["data"]            
        except Exception as err:
            return {"data": objRes}
    else:    
        try:
            response = requests.get(f"{gOriginOSAIS}api/v1/private/client", headers=headers)
            objRes=response.json()["data"]            
        except Exception as err:
            return {"data": objRes}

    return {"data": objRes}
            

# Authenticate into OSAIS (as client)
def osais_authenticateClient(_id, _secret):
    global gOriginOSAIS
    global gOriginLocalOSAIS
    global gClientAuthToken
    global gClientAuthTokenLocal
    global gIsLocal

    authToken=None

    headers = {
        "Content-Type": "application/json"
    }
    resp={"data": None}
    if gIsLocal:        # if local ... log as client into debug
        try:
            url=f"{gOriginLocalOSAIS}api/v1/public/client/demo"      ## get a demo auth token
            if _id!= None:
                url=f"{gOriginLocalOSAIS}api/v1/public/client/login"
            response = requests.post(url, headers=headers, data=json.dumps({
                "token": _id,
                "secret": _secret
            }))

            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT LOGIN AS CLIENT into OSAIS Local")
            print("We got a CLIENT authentication token into OSAIS Local (debug)")
            gClientAuthTokenLocal=objRes["authToken"]
            authToken=gClientAuthTokenLocal
            resp={"data": {
                "token": objRes["token"],
                "authToken": gClientAuthTokenLocal,
            }}

        except Exception as err:
            ## no big deal
            gClientAuthTokenLocal=None

    else:       # else ... log as client into prod        
        try:
            url=f"{gOriginOSAIS}api/v1/public/client/demo"      ## get a demo auth token
            if _id!= None:
                url=f"{gOriginOSAIS}api/v1/public/client/login"
            response = requests.post(url, headers=headers, data=json.dumps({
                "token": _id,
                "secret": _secret
            }))

            objRes=response.json()["data"]
            if objRes is None:
                print("COULD NOT LOGIN AS CLIENT, stopping it here")
                sys.exit()
            print("We got a CLIENT authentication token into OSAIS")
            gClientAuthToken=objRes["authToken"]    
            authToken=gClientAuthToken
            resp={"data": {
                "token": objRes["token"],
                "authToken": gClientAuthToken,
            }}

        except Exception as err:
            consoleLog({"msg":"Exception raised while trying to login as CLIENT to PROD"})
            gClientAuthToken=None

    dataClient=getClientInfo(authToken)
    resp["data"]["user"]=dataClient["data"]["user"]
    return resp 

## ------------------------------------------------------------------------
#       ask OSAIS to process a request
## ------------------------------------------------------------------------

def osais_postRequest(objReq):
    global gClientAuthToken
    global gClientAuthTokenLocal
    global gIsLocal
    global gName

    resp={"data": None}
    _url=None
    _authToken=None
    if gIsLocal:
        _authToken=gClientAuthTokenLocal
        _url=f"{gOriginLocalOSAIS}api/v1/private/client/ai/"+objReq.gName
    else:
        _authToken=gClientAuthToken
        _url=f"{gOriginOSAIS}api/v1/private/client/ai/"+objReq.gName

    try:
        response = requests.post(_url, headers={
            "Content-Type": "application/json",
            'Accept': 'text/plain',
            "Authorization": f"Bearer {_authToken}"
        }, data=json.dumps(objReq))
        objRes=response.json()["data"]
        if objRes is None:
            print("COULD NOT post request")
        resp={"data": objRes}

    except Exception as err:
        raise err

    return resp 

## ------------------------------------------------------------------------
#       Run the AI
## ------------------------------------------------------------------------

## PUBLIC - parse args for OSAIS (not those for AI)
def osais_initParser(aArg):
    global gArgsOSAIS
    global gInputDir
    global gOutputDir
    global gIsWarmup

    # Create the parser
    vq_parser = argparse.ArgumentParser(description='Arg parser init by OSAIS')

    # Add the AI Gateway / OpenSourceAIs arguments
    vq_parser.add_argument("-orig",  "--origin", type=str, help="AI Gateway server origin", default=f"http://{gIPLocal}:{gPortGateway}/" , dest='OSAIS_origin')     ##  this is for comms with AI Gateway
    vq_parser.add_argument("-t",  "--token", type=str, help="OpenSourceAIs token", default="0", dest='tokenAI')               ##  this is for comms with OpenSourceAIs
    vq_parser.add_argument("-u",  "--username", type=str, help="OpenSourceAIs username", default="", dest='username')       ##  this is for comms with OpenSourceAIs
    vq_parser.add_argument("-uid",  "--unique_id", type=int, help="Unique ID of this AI session", default=0, dest='uid')    ##  this is for comms with OpenSourceAIs
    vq_parser.add_argument("-odir", "--outdir", type=str, help="Output directory", default=gOutputDir, dest='outdir')
    vq_parser.add_argument("-idir", "--indir", type=str, help="input directory", default=gInputDir, dest='indir')
    vq_parser.add_argument("-local", "--islocal", type=bool, help="is local or prod?", default=False, dest='isLocal')
    vq_parser.add_argument("-cycle", "--cycle", type=int, help="cycle", default=0, dest='cycle')
    vq_parser.add_argument("-filename", "--filename", type=str, help="filename", default="default", dest='filename')
    vq_parser.add_argument("-warmup", "--warmup", type=bool, help="warmup", default=False, dest='warmup')

    gArgsOSAIS = vq_parser.parse_args(aArg)
    gIsWarmup=gArgsOSAIS.warmup
    return True

## PUBLIC - run the AI (at least try)
def osais_runAI(*args):
    global gIsBusy
    global gAProcessed
    global gName 
    global gLastProcessStart_at
    global gOriginOSAIS
    global gOriginLocalOSAIS
    global gIsLocal

    ## get args
    fn_run=args[0]
    _args=args[1]

    ## do not process twice same uid
    _uid=_args.get('-uid')
    if _uid in gAProcessed:
        return  "not processing, already tried..."

    ## where is the caller?
    _orig=None
    try: 
        if _args["-orig"]:
            _orig=_args["-orig"]
    except:
        _orig=None

    ## start time
    gIsBusy=True
    beg_date = datetime.utcnow()

    ## reprocess AI args
    aArgForparserAI=_getArgs(_args)
    args_ExclusiveOSAIS=['-orig', '-t', '-u', '-uid', '-local', '-cycle', '-warmup']
    aArgForparserAI=_argsFromFilter(aArgForparserAI, args_ExclusiveOSAIS, False)

    ## process the filename passed in dir (case localhost / AI Gateway), or download file from URL (case AI running as Virtual AI)
    _input=None
    _filename=_args.get('-filename')
    _urlUpload=_args.get('url_upload')
    if not _filename and _urlUpload:
        try:
            _input=downloadImage(_urlUpload)
            if _input:
                aArgForparserAI.append("-filename")
                aArgForparserAI.append(_input)
            else:
                ## min requirements
                print("no image to process")
                return "input required"
        except Exception as err:
            gIsBusy=False
            consoleLog({"msg":"Could not download image"})
            raise err
    
    ## Init OSAIS Params (from all args, keep only those for OSAIS)
    aArgForParserOSAIS=_getArgs(_args)
    args_ExclusiveOSAIS.append('-odir')
    args_ExclusiveOSAIS.append('-idir')
    aArgForParserOSAIS=_argsFromFilter(aArgForParserOSAIS, args_ExclusiveOSAIS, True)
    osais_initParser(aArgForParserOSAIS)

    ## notify OSAIS (Req received)
    CredsParam=getCredsParams()
    MorphingParam=getMorphingParams()
    StageParam=getStageParams(AI_PROGRESS_REQRECEIVED, 0)
    osais_notify(_orig, CredsParam, MorphingParam , StageParam)

    if gIsWarmup:
        print("\r\n=> Warming up... \r\n")
    else:
        print("\r\n=> before run: processed args from url: "+str(aArgForparserAI)+"\r\n")

    ## processing accepted
    gLastProcessStart_at=datetime.utcnow()
    gAProcessed.append(_uid)

    ## notify OSAIS (start)
    StageParam=getStageParams(AI_PROGRESS_AI_STARTED, 0)
    osais_notify(_orig, CredsParam, MorphingParam , StageParam)

    ## start watch file creation
    _output=_getOutputDir()
    watch_directory(_output, osais_onNotifyFileCreated, _args)

    ## Notif OSAIS
    StageParam=getStageParams(AI_PROGRESS_INIT_IMAGE, 0)
    osais_notify(_orig, CredsParam, MorphingParam , StageParam)

    ## run AI
    response=None
    try:
        if len(args)==2:
            response=fn_run(aArgForparserAI)
        else:
            if len(args)==3:
                response=fn_run(aArgForparserAI, args[2])
            else:
                response=fn_run(aArgForparserAI, args[2], args[3])
    except Exception as err:
        gIsBusy=False
        consoleLog({"msg": "Error processing args in RUN command"})
        raise err

    ## calculate cost
    gIsBusy=False
    end_date = datetime.utcnow()
    delta=end_date - beg_date
    cost = int(delta.total_seconds()* 1000 + delta.microseconds / 1000)
    _addCost(cost)

    ## notify end
    StageParam=getStageParams(AI_PROGRESS_AI_STOPPED, cost)
    osais_notify(_orig, CredsParam, MorphingParam , StageParam)

    if gIsWarmup:
        _strDelta=str(delta)
        print("\r\n=> AI ready!")
        print("=> Able to process requests in "+_strDelta+" secs\r\n")

    ## default OK response if the AI does not send any
    if response==None:
        response=True
    return response

## ------------------------------------------------------------------------
#       get formatted params from AI current state
## ------------------------------------------------------------------------

def getCredsParams() :
    global gName
    global gArgsOSAIS
    return {
        "engine": gName, 
        "version": gVersion, 
        "tokenAI": gArgsOSAIS.tokenAI,
        "username": gArgsOSAIS.username,
        "isLocal": gArgsOSAIS.isLocal
    } 

def getMorphingParams() :
    global gArgsOSAIS
    return {
        "uid": gArgsOSAIS.uid,
        "cycle": gArgsOSAIS.cycle,
        "filename": gArgsOSAIS.filename, 
        "odir": _getOutputDir()
    }

def getStageParams(_stage, _cost) :
    global gArgsOSAIS
    if _stage==AI_PROGRESS_REQRECEIVED:
        return {"stage": AI_PROGRESS_REQRECEIVED, "descr":"Acknowledged request"}
    if _stage==AI_PROGRESS_ERROR:
        return {"stage": AI_PROGRESS_AI_STOPPED, "descr":"AI stopped with error"}
    if _stage==AI_PROGRESS_AI_STARTED:
        return {"stage": AI_PROGRESS_AI_STARTED, "descr":"AI started"}
    if _stage==AI_PROGRESS_AI_STOPPED:
        return {"stage": AI_PROGRESS_AI_STOPPED, "descr":"AI stopped", "cost": _cost}
    if _stage==AI_PROGRESS_INIT_IMAGE:
        return {"stage": AI_PROGRESS_INIT_IMAGE, "descr":"destination image = "+gArgsOSAIS.filename}
    if _stage==AI_PROGRESS_DONE_IMAGE:
        return {"stage": AI_PROGRESS_DONE_IMAGE, "descr":"copied input image to destination image"}
    return {"stage": AI_PROGRESS_ERROR, "descr":"error"}

## ------------------------------------------------------------------------
#       Notifications to Gateway / OSAIS
## ------------------------------------------------------------------------

# Upload image to OSAIS 
def _uploadImageToOSAIS(_origin, objParam, isLocal):
    if gIsVirtualAI==False:
        return None
    
    global gAuthToken
    global gAuthTokenLocal
    
    _auth=gAuthToken
    if isLocal:
        _auth=gAuthTokenLocal

    # lets go call OSAIS AI Gateway / or OSAIS itself
    headers = {
        "Content-Type": 'application/json', 
        'Accept': 'text/plain',
        "Authorization": f"Bearer {_auth}"
    }

    api_url=f"{_origin}api/v1/private/virtualai/upload"        
    payload = json.dumps(objParam)
    response = requests.post(api_url, headers=headers, data=payload )
    objRes=response.json()
    return objRes    

def osais_onNotifyFileCreated(_dir, _filename, _args):
    ## where is the caller?
    _orig=None
    try: 
        if _args["-orig"]:
            _orig=_args["-orig"]
    except:
        _orig=None

    # notify
    gArgsOSAIS.filename=_filename
    _stageParam=getStageParams(AI_PROGRESS_DONE_IMAGE, 0)
    _morphingParam=getMorphingParams()
    _credsParam=getCredsParams()
    osais_notify(_orig, _credsParam, _morphingParam, _stageParam)            # OSAIS Notification
    return True

# Direct Notify OSAIS 
def osais_notify(_origin, CredParam, MorphingParam, StageParam):
    global gIPLocal
    global gPortGateway
    global gIsVirtualAI
    global gAuthToken
    global gAuthTokenLocal
    global gLastChecked_at
    global gIsWarmup

    ## no notification of warmup or unknown caller
    if gIsWarmup or _origin==None:
        return None
    
    gLastChecked_at = datetime.utcnow()

    # notification console log
    merged = dict()
    merged.update(CredParam)
    merged.update(MorphingParam)
    print("NotifyOSAIS ("+str(StageParam["stage"])+"/ "+StageParam["descr"]+"): "+str(merged))
    print("\r\n")

    _filename=""
    if MorphingParam["filename"]!="":
        _filename=MorphingParam["filename"]

    # lets go call OSAIS AI Gateway / or OSAIS itself
    headers = {
        "Content-Type": "application/json"
    }

    ## config for calling gateway
    api_url = f"{_origin}api/v1/public/notify"

    ## config for calling OSAIS (no gateway)
    if gIsVirtualAI:
        _auth=gAuthToken

        if CredParam["isLocal"]:
            _auth=gAuthTokenLocal

        if gIsVirtualAI==True:
            headers["Authorization"]= f"Bearer {_auth}"
            api_url=f"{_origin}api/v1/private/virtualai/notify"

    objParam={
        "response": {
            "token": CredParam["tokenAI"],
            "uid": str(MorphingParam["uid"]),
            "stage": str(StageParam["stage"]),
            "cycle": str(MorphingParam["cycle"]),
            "engine": CredParam["engine"],
            "username": CredParam["username"],
            "descr": StageParam["descr"],
            "filename": _filename
        }
    }

    if "cost" in StageParam:
        objParam["response"]["cost"]= str(StageParam["cost"])
    
    response = requests.post(api_url, headers=headers, data=json.dumps(objParam) )
    objRes=response.json()

    if StageParam["stage"]==AI_PROGRESS_DONE_IMAGE:
        if gIsVirtualAI==True:
            _dir=MorphingParam["odir"]
            if _dir==None:
                _dir=gOutputDir
            _dirImage=_dir+_filename

            with open(_dirImage, "rb") as image_file:
                image_data = image_file.read()

            im_b64 = base64.b64encode(image_data).decode("utf8")
            param={
                "image": im_b64,
                "uid": str(MorphingParam["uid"]),
                "cycle": str(MorphingParam["cycle"]),
                "engine": CredParam["engine"],
            }            
            _uploadImageToOSAIS(_origin, param, CredParam["isLocal"])
    return objRes

## ------------------------------------------------------------------------
#       Init processing
## ------------------------------------------------------------------------

## PUBLIC - resetting who this AI is talking to (OSAIS prod and dbg)
def osais_resetOSAIS(_locationProd, _localtionDebug):
    global gOriginOSAIS
    global gOriginLocalOSAIS
    gOriginOSAIS=_locationProd
    gOriginLocalOSAIS=_localtionDebug
    if _locationProd!=None:
        print("=> This AI is reset to talk to PROD "+gOriginOSAIS)
    if _localtionDebug!=None:
        print("=> This AI is reset to talk to DEBUG "+gOriginLocalOSAIS+"\r\n")
    return True

## PUBLIC - Init the Virtual AI
def osais_initializeAI():
    global gIsDocker
    global gIsLocal
    global gIsVirtualAI
    global gUsername
    global gName
    global gPortAI
    global gVersion
    global gPortGateway
    global gPortLocalOSAIS
    global gIPLocal
    global gExtIP
    global gOriginGateway
    global gAuthToken
    global gAuthTokenLocal
    global gOriginOSAIS
    global gOriginLocalOSAIS

    ## load env 
    _envFile="env_local"
    if gIsDocker:
        _envFile="env_docker"
        print("\r\n=> in Docker\r\n")
    else:
        print("\r\n=> NOT in Docker\r\n")        
    obj=osais_getEnv(_envFile)
    gIsLocal=obj["isLocal"]
    gIsVirtualAI=obj["isVirtualAI"]
    gUsername=obj["username"]
    gName=obj["name"]

    ## from env, load AI config
    gConfig=osais_loadConfig(gName)
    gPortAI = gConfig["port"]
    gVersion = gConfig["version"]

    print("\r\n===== Config =====")
    print("engine: "+str(gName) + " v"+str(gVersion))
    print("is Local: "+str(gIsLocal))
    print("is Virtual: "+str(gIsVirtualAI))
    print("username: "+str(gUsername))
    if gIsLocal:
        print("location (local): "+str(gIPLocal)+":"+str(gPortAI))
    else: 
        print("location (external): "+str(gExtIP)+":"+str(gPortAI))
    print("===== /Config =====\r\n")

    ## make sure we have a config file
    _loadConfig(gName)

    ## where is OSAIS for us then?
    gOriginGateway=f"http://{gIPLocal}:{gPortGateway}/"         ## config for local gateway (local and not virtual)

    ## we set OSAIS location in all cases (even if in gateway) because this AI can generate it s own page for sending reqs (needs a client logged into OSAIS)
    if gIsLocal:
        osais_resetOSAIS(None, f"http://{gIPLocal}:{gPortLocalOSAIS}/")
    else:
        osais_resetOSAIS("https://opensourceais.com/", None)
    if gIsVirtualAI:
        try:
            osais_authenticateAI(None)
        except Exception as err:
            print("=> CRITICAL: Could not connect virtual AI "+gName+ " to OSAIS")
            return None

        if gAuthToken!=None:
            print("=> Running "+gName+" AI as a virtual AI connected to: "+gOriginOSAIS)
        if gAuthTokenLocal!=None:
            print("=> Running "+gName+" AI as a virtual AI connected to: "+gOriginLocalOSAIS)
    else:
        try:
            osais_resetGateway(gOriginGateway)
            print("=> Running "+gName+" AI as a server connected to local Gateway "+gOriginGateway)
        
        except Exception as err:
            print("CRITICAL: could not notify Gateway at "+gOriginGateway)
            return None

    ## init default cost
    _initializeCost()

    print("\r\n")
    return gName

## ------------------------------------------------------------------------
#       Starting point of Lib
## ------------------------------------------------------------------------

# Multithreading for observers
watch_directory=start_observer_thread(_getOutputDir(), osais_onNotifyFileCreated, None)     

#cleaning dir every 10min
schedule.every(10).minutes.do(_clearDir)

print("\r\nPython OSAIS Lib is loaded...")
