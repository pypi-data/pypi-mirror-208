import platform
import os
import base64
import ukitai.depend.filecontents as filecontents
import tarfile
import shutil
import ukitai
import subprocess

isWindows = False
isDarwin = False
isLinux = False

machineSystem = None
machineArch = None

userHome = None
binaryHome = None
helperHome = None


def prepareSystemValue():
    global isWindows, isDarwin, isLinux, machineSystem
    system = platform.system()
    isWindows = system == 'Windows'
    isDarwin = system == 'Darwin'
    isLinux = system == 'Linux'
    machineSystem = system.lower()


def prepareArchValue():
    global isWindows, isDarwin, isLinux, machineArch
    if isDarwin:
        machineArch = 'x86_64'
    elif isWindows:
        machineArch = 'x86'
    elif isLinux:
        machine = platform.machine()
        if machine == 'aarch64' or machine == 'x86_64' or machine == 'armv7l':
            machineArch = machine


def prepareUserEnvironment():
    global userHome, binaryHome, helperHome
    if os.environ.get('HOME') is not None:
        userHome = os.environ.get('HOME')
    elif os.environ.get('HOMEDRIVE') is not None and os.environ.get('HOMEPATH') is not None:
        userHome = os.environ.get('HOMEDRIVE') + os.environ.get('HOMEPATH')
    else:
        return
    helperHome = os.path.join(userHome, '.ukitai-link')
    binaryHome = os.path.join(helperHome, 'bin')
    if not os.path.exists(helperHome):
        os.mkdir(helperHome)


prepareSystemValue()
prepareArchValue()
prepareUserEnvironment()


def prepareEnvironment():
    global isWindows, isDarwin, isLinux, machineArch, machineSystem, binaryHome, helperHome

    if machineArch is None or machineSystem is None:
        raise EnvironmentError('not supported system')
    attrName = 'file_' + machineSystem + '_' + machineArch + '_contents'
    if not hasattr(filecontents, attrName):
        raise EnvironmentError('not supported system')

    tarFilePath = None
    tarFile = None
    versionFile = None
    try:
        if os.path.exists(binaryHome):
            if os.path.exists(os.path.join(binaryHome, '.version')):
                versionFile = open(os.path.join(binaryHome, '.version'), 'r')
                versionFileValue = versionFile.read()
                versionFile.close()
                versionFile = None
                if versionFileValue == ukitai.__version__ and os.path.exists(__getLinktoolPath()):
                    return
                else:
                    shutil.rmtree(binaryHome)
            else:
                shutil.rmtree(binaryHome)
        if not os.path.exists(binaryHome):
            os.mkdir(binaryHome)

        # Get base64 from code
        fileB64Content = getattr(filecontents, attrName)

        # Decode use base64
        fileContent = base64.decodebytes(bytes(fileB64Content, encoding='utf8'))

        # Write to file
        tarFilePath = os.path.join(helperHome, 'binaries.tar.xz')
        if os.path.exists(tarFilePath):
            os.remove(tarFilePath)
        tarFile = open(tarFilePath, 'wb')
        tarFile.write(fileContent)
        tarFile.close()
        tarFile = None

        # Extract to file system
        tarFile = tarfile.open(tarFilePath, "r:xz")
        fileNames = tarFile.getnames()
        for fileName in fileNames:
            tarFile.extract(fileName, binaryHome)
        tarFile.close()
        tarFile = None

        versionFile = open(os.path.join(binaryHome, '.version'), 'wb')
        try:
            versionFile.write(bytes(ukitai.__version__, encoding='utf8'))
        except:
            versionFile.write(ukitai.__version__)
        versionFile.close()
        versionFile = None
    finally:
        # Clean up
        if versionFile is not None:
            versionFile.close()
        if tarFile is not None:
            tarFile.close()
        if tarFilePath is not None and os.path.exists(tarFilePath):
            os.remove(tarFilePath)


def __getLinktoolPath():
    global isWindows, isDarwin, isLinux, binaryHome
    if isWindows:
        return os.path.join(binaryHome, 'ukitai-link.exe')
    elif isDarwin or isLinux:
        return os.path.join(binaryHome, 'ukitai-link')
    else:
        raise EnvironmentError('not supported system')


def __getLinktoolLogPath():
    global helperHome
    return (os.path.join(helperHome, 'ukitai-link.log'), os.path.join(helperHome, 'ukitai-link.err.log'))


def startLinkToolDaemon():
    global isWindows, isDarwin, isLinux, binaryHome
    linkPath = __getLinktoolPath()
    # print("link binary path: %s" % linkPath)
    if not os.path.exists(linkPath):
        return
    logLevel = 7
    logPath, errLogPath = __getLinktoolLogPath()
    if os.path.exists(logPath):
        if os.path.exists(logPath + ".last"):
            os.remove(logPath + ".last")
        os.rename(logPath, logPath + ".last")
    if os.path.exists(errLogPath):
        if os.path.exists(errLogPath + ".last"):
            os.remove(errLogPath + ".last")
        os.rename(errLogPath, errLogPath + ".last")
    if isWindows:
        subprocess.call("\"{}\" {} >>\"{}\" 2>>\"{}\"".format(linkPath, logLevel, logPath, errLogPath), shell=True)
    elif isDarwin:
        subprocess.call("\"{}\" {} \"{}\" > /dev/null".format(linkPath, logLevel, logPath), shell=True)
    elif isLinux:
        subprocess.call("\"{}\" {} 2>&1 | tee \"{}\" > /dev/null".format(linkPath, logLevel, logPath), shell=True)
