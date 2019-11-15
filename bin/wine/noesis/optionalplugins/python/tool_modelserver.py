import noewin
from noewin import user32, gdi32, kernel32
from inc_noesis import *
from ctypes import *
import http.server
import socketserver
import ssl
import select
import threading
import gc
import time
import posixpath
import urllib.parse
import json
import io
import collections

MSERVER_OPTIONS = "-gltftranscene -gltfnonoeex -gltfnometalhack -gltfoneanim"

#the cache can grow quite large, so if you don't want it living under noesis\scenes, you can enter a custom absolute path here
MSERVER_CUSTOM_CACHE_LOCATION = None

MSERVER_PORT = 8080
MSERVER_SOCKET_TIMEOUT = 5.0
MSERVER_HTTPS = False #if you want to use this, you'll need to generate the .pem
#openssl req -new -x509 -keyout your_cert_file.pem -out your_cert_file.pem -days 365 -nodes

MSERVER_PLACEHOLDER_FILE_NAME = "__placeholder.txt"

MSERVER_COPY_CHUNK_SIZE = 128 * 1024

MSERVER_UPDATE_TIMER_ID = 666
MSERVER_UPDATE_TIMER_INTERVAL = 100

def registerNoesisTypes():
	handle = noesis.registerTool("Model Server", mserverToolMethod, "Launch the Model Server.")
	return 1
	
class ModelHttpServer(socketserver.TCPServer):
	#in this version of python, the server has a problem with hanging on sockets while nothing's
	#available to read. so as a hack we set a low timeout on all of our new sockets, which at least
	#lets us avoid huge hangs when stopping the server.
	def get_request(self):
		conn, addr = self.socket.accept()
		conn.settimeout(MSERVER_SOCKET_TIMEOUT)
		return conn, addr
	
class ModelHttpServerRequestHandler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		try:
			f, fLength = self.send_head()
			if f:
				readBytesToDest(self.wfile, f, fLength)
				f.close()
		except:
			pass

	def do_HEAD(self):
		try:
			f, fLength = self.send_head()
			if f:
				f.close()
		except:
			pass

	def send_head(self):
		noeWnd = self.server.noeWnd
		if self.path.startswith("/data/"):
			try:
				binPath = self.path.split("/data", 1)[1]
				if binPath not in noeWnd.webCache["cachedEntries"]:
					noesis.doException("No cache entry.")
				entry = noeWnd.webCache["cachedEntries"][binPath]

				ctype = self.guess_type(binPath)
				f = open(getCacheBinaryPath(), "rb")
				f.seek(entry["offset"], os.SEEK_SET)
				dataLength = entry["size"]
			except:
				self.send_error(404, "File not found")
				return None, 0
		elif self.path.startswith("/view/"):
			try:
				binPath = self.path.split("/view", 1)[1]
				if binPath not in noeWnd.webCache["cachedEntries"]:
					noesis.doException("No cache entry.")
				base, ext = posixpath.splitext(binPath)
				if ext.lower() != ".gltf":
					noesis.doException("Not a GLTF file.")					

				swapped = noeWnd.templateView.replace("$GLTF_PATH$", "/data" + binPath)
				data = swapped.encode("UTF-8")
				dataLength = len(data)
				f = io.BytesIO(data)
				ctype = "text/html"
			except:
				self.send_error(404, "File not found")
				return None, 0
		elif self.path.startswith("/pub/"):
			try:
				binPath = self.path.split("/pub", 1)[1].lower()
				if binPath not in noeWnd.pubList:
					noesis.doException("No pub entry.")
				ctype = self.guess_type(binPath)
				fullPath = noeWnd.pubList[binPath]
				f = open(fullPath, "rb")
				f.seek(0, os.SEEK_END)
				dataLength = f.tell()
				f.seek(0, os.SEEK_SET)
			except:
				self.send_error(404, "File not found")
				return None, 0
		else: #don't care what else they're after, shove the index back in their face
			data = noeWnd.templateIndex.encode("UTF-8")
			dataLength = len(data)
			f = io.BytesIO(data)
			ctype = "text/html"

		self.send_response(200)
		self.send_header("Content-type", ctype)
		self.send_header("Content-Length", dataLength)
		self.send_header("Last-Modified", self.date_time_string(0))
		self.end_headers()
		return f, dataLength
	
class ModelServerThread(threading.Thread):
	def setNoeWnd(self, noeWnd):
		self.noeWnd = noeWnd
	def run(self):
		noeWnd = self.noeWnd
		httpServer = noeWnd.httpServer
		httpServer.serve_forever()
	
def stopExistingServer(noeWnd):
	if noeWnd.httpServer:
		httpServer = noeWnd.httpServer
		httpServer.shutdown()
		noeWnd.httpServer = None
		gc.collect()
		
def buttonStartMethod(noeWnd, controlId, wParam, lParam):
	if midProcessingCheck(noeWnd):
		return
	
	startButton = noeWnd.getControlByIndex(noeWnd.startButtonIndex)

	if noeWnd.httpServer:
		stopExistingServer(noeWnd)
		startButton.setText("Start")
		updateStatus(noeWnd, "Server stopped.")
		return

	startButton.setText("Stop")
	httpServer = ModelHttpServer(("", MSERVER_PORT), ModelHttpServerRequestHandler)
	httpServer.noeWnd = noeWnd
	
	httpServer.socket.settimeout(MSERVER_SOCKET_TIMEOUT)
	if MSERVER_HTTPS:
		httpServer.socket = ssl.wrap_socket(httpServer.socket, certfile="your_cert_file.pem", server_side=True)	
	
	t = ModelServerThread()
	noeWnd.httpServer = httpServer
	t.setNoeWnd(noeWnd)
	t.start()
	updateStatus(noeWnd, "Server running.")
	
def getCacheIndexPath():
	if MSERVER_CUSTOM_CACHE_LOCATION:
		return os.path.join(MSERVER_CUSTOM_CACHE_LOCATION, "") + "cache_index.txt"
	return noesis.getScenesPath() + "modelserver\\cache_index.txt"

def getCacheBinaryPath():
	if MSERVER_CUSTOM_CACHE_LOCATION:
		return os.path.join(MSERVER_CUSTOM_CACHE_LOCATION, "") + "cache_data.bin"
	return noesis.getScenesPath() + "modelserver\\cache_data.bin"
	
def getWorkPath():
	return noesis.getScenesPath() + "modelserver\\work\\"

def getPubPath():
	return noesis.getScenesPath() + "modelserver\\pub\\"
	
def loadWebCache(noeWnd):
	if os.path.exists(getCacheIndexPath()):
		with open(getCacheIndexPath(), "r") as f:
			noeWnd.webCache = json.load(f)
	else:
		noeWnd.webCache = { "cachedPath" : "", "cachedEntries" : { }, "visiblePaths" : { } }
	
def saveWebCache(noeWnd):
	with open(getCacheIndexPath(), "w+") as f:
		json.dump(noeWnd.webCache, f)

def updateIndexTemplate(noeWnd):
	with open(noesis.getScenesPath() + "modelserver\\template_index.txt", "r") as f:
		noeWnd.templateIndex = f.read()
		visiblePaths = noeWnd.webCache["visiblePaths"]
		linkText = ""
		sortedPaths = collections.OrderedDict(sorted(visiblePaths.items()))
		for visiblePath, gltfPath in sortedPaths.items():
			linkText += "<a href=\"/view" + gltfPath + "\">" + visiblePath + "</a><br />"
		noeWnd.templateIndex = noeWnd.templateIndex.replace("$GLTF_FILE_LIST$", linkText)

#was originally doing some fancier mapping stuff, but scraped that out for now
def updatePubListing(noeWnd):
	noeWnd.pubList = {}
	pubPath = os.path.join(getPubPath(), "")
	for root, dirs, files in os.walk(pubPath):
		for fileName in files:
			fullPath = os.path.join(root, fileName)
			noeWnd.pubList[getLocalFilePath(pubPath, fullPath).lower()] = fullPath
		
def getLocalFilePath(basePath, path):
	return path[len(basePath) - 1:].replace("\\", "/")

def readBytesToDest(fDst, fSrc, size):
	while size > 0:
		copySize = min(size, MSERVER_COPY_CHUNK_SIZE)
		fDst.write(fSrc.read(copySize))
		size -= copySize
		
def cacheBinaryFile(noeWnd, fullPath, destMountPath):
	with open(getCacheBinaryPath(), "rb+") as fDst, open(fullPath, "rb") as fSrc:
		fDst.seek(0, os.SEEK_END)
		offset = fDst.tell()
		fSrc.seek(0, os.SEEK_END)
		size = fSrc.tell()
		fSrc.seek(0, os.SEEK_SET)
		readBytesToDest(fDst, fSrc, size)
		entryDict = { "offset" : offset, "size" : size }
		noeWnd.webCache["cachedEntries"][destMountPath] = entryDict
	
def updateStatus(noeWnd, msg):
	#if we updated the control directly on another python thread, it could hit in the middle of a message pump,
	#which can cause problems at the windows messaging level despite the fact that threads aren't running async.
	noeWnd.deferredStatus = True
	noeWnd.deferredMsg = msg
	
def statusUpdateTimer(noeWnd, controlIndex, message, wParam, lParam):
	if wParam == MSERVER_UPDATE_TIMER_ID:
		if noeWnd.deferredStatus:
			noeWnd.deferredStatus = False
			statusBox = noeWnd.getControlByIndex(noeWnd.statusIndex)
			statusBox.setText(noeWnd.deferredMsg)
	
class ProcessModelThread(threading.Thread):
	def setNoeWnd(self, noeWnd):
		self.noeWnd = noeWnd
	def run(self):
		noeWnd = self.noeWnd
		noeWnd.workFinishedEvent.clear()
		cachedPath = os.path.join(noeWnd.webCache["cachedPath"], "")
		for workIndex in range(0, len(noeWnd.workingSet)):
			if noeWnd.abortProcessing:
				break
			workPath = noeWnd.workingSet[workIndex]
			updateStatus(noeWnd, "Processing file %i / %i - "%(workIndex, len(noeWnd.workingSet)) + workPath)
			noeMod = noesis.instantiateModule()
			noesis.setModuleRAPI(noeMod)
			try:
				rapi.toolLoadGData(workPath)
				if rapi.toolGetLoadedModelCount() > 0:
					path, name = os.path.split(workPath)
					destPath = getWorkPath() + os.path.splitext(name)[0] + ".gltf"
					print("Exporting to work path:", destPath)

					sourceMountPath = getLocalFilePath(cachedPath, workPath)
					baseMountPath = sourceMountPath.rsplit("/", 1)[0] + "/"
					
					rapi.toolExportGData(destPath, MSERVER_OPTIONS)
					mainFileExists = os.path.exists(destPath)
					#now gather up everything that ended up in there, stuff it in the cache and remove it
					for root, dirs, files in os.walk(getWorkPath()):
						for fileName in files:
							if fileName.lower() != MSERVER_PLACEHOLDER_FILE_NAME:
								fullPath = os.path.join(root, fileName)
								if mainFileExists:
									destMountPath = baseMountPath + fileName
									if os.path.splitext(fileName)[1].lower() == ".gltf":
										noeWnd.webCache["visiblePaths"][sourceMountPath] = destMountPath
									cacheBinaryFile(noeWnd, fullPath, destMountPath)
								os.remove(fullPath)
				rapi.toolFreeGData()
			except:
				print("Error processing", workPath)
			noesis.freeModule(noeMod)
		#save the index whether or not we aborted, as the data bin is already modified
		saveWebCache(noeWnd)
		updateIndexTemplate(noeWnd)
		updateStatus(noeWnd, "Processing aborted." if noeWnd.abortProcessing else "Finished processing files.")
		noeWnd.workFinishedEvent.set()
		noeWnd.isProcessing = False
		noeWnd.abortProcessing = False

def abortOrWaitOnProcessing(noeWnd, canAbort = True):
	if noeWnd.isProcessing:
		if canAbort:
			noeWnd.abortProcessing = True
			noeWnd.workFinishedEvent.wait()		
			user32.MessageBoxW(noeWnd.hWnd, "Aborted processing, the cache may be incomplete.", "Model Server", noewin.MB_OK)
		else:
			print("Stalling until cache processing is finished.")
			noeWnd.workFinishedEvent.wait()

def midProcessingCheck(noeWnd):
	if noeWnd.isProcessing:
		abortIt = user32.MessageBoxW(noeWnd.hWnd, "The cache is currently being built. Do you want to abort the process? (this will leave an incomplete cache in place)", "Model Server", noewin.MB_YESNO) == noewin.IDYES
		if abortIt:
			abortOrWaitOnProcessing(noeWnd)
	return noeWnd.isProcessing
			
def rescanCachePath(noeWnd):
	if noeWnd.isProcessing:
		midProcessingCheck(noeWnd)
		return #either way, don't restart the scan if a scan was in process
		
	#destroy the existing data contents
	with open(getCacheBinaryPath(), "wb") as f:
		pass
	#reset the entries
	noeWnd.webCache["cachedEntries"] = { }
	noeWnd.webCache["visiblePaths"] = { }
	noeWnd.workingSet = []
	walkPath = noeWnd.webCache["cachedPath"]
	if len(walkPath) > 0 and os.path.exists(walkPath):
		print("Collecting resources.")
		for root, dirs, files in os.walk(walkPath):
			for fileName in files:
				#only gather stuff that looks like a model file
				if noesis.getFormatExtensionFlags(os.path.splitext(fileName)[1]) & noesis.NFORMATFLAG_MODELREAD:
					fullPath = os.path.join(root, fileName)
					noeWnd.workingSet.append(fullPath)
		noeWnd.isProcessing = True
		if len(noeWnd.workingSet) > 0:
			noeWnd.workFinishedEvent = threading.Event()
			t = ProcessModelThread()
			t.setNoeWnd(noeWnd)
			t.start()
		
def buttonBrowseMethod(noeWnd, controlId, wParam, lParam):
	dir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select a folder to serve from. (this will trigger a re-scan)", noeWnd.webCache["cachedPath"], None)
	if dir:
		noeWnd.webCache["cachedPath"] = dir
		servePathEdit = noeWnd.getControlByIndex(noeWnd.servePathIndex)
		servePathEdit.setText(dir)
		rescanCachePath(noeWnd)		

def buttonRefreshMethod(noeWnd, controlId, wParam, lParam):
	servePathEdit = noeWnd.getControlByIndex(noeWnd.servePathIndex)
	noeWnd.webCache["cachedPath"] = servePathEdit.getText()
	rescanCachePath(noeWnd)
	
def mserverToolMethod(toolIndex):
	noeWnd = noewin.NoeUserWindow("Model Server", "ModelServerWindowClass", 600, 220)
	noeWindowRect = noewin.getNoesisWindowRect()
	if noeWindowRect:
		windowMargin = 64
		noeWnd.x = noeWindowRect[0] + windowMargin
		noeWnd.y = noeWindowRect[1] + windowMargin
	if not noesis.getWindowHandle():
		#if invoked via ?runtool, we're our own entity
		noeWnd.exStyle = noewin.WS_EX_DLGMODALFRAME
		noeWnd.style |= noewin.WS_MINIMIZEBOX | noewin.WS_MAXIMIZEBOX
		noeWnd.userIcon = user32.LoadIconW(kernel32.GetModuleHandleW(0), noesis.getResourceHandle(1))

	if noeWnd.createWindow():
		noeWnd.httpServer = None
		noeWnd.isProcessing = False
		noeWnd.abortProcessing = False
		noeWnd.deferredStatus = False
		noeWnd.setFont("Arial", 14)

		with open(noesis.getScenesPath() + "modelserver\\template_view.txt", "r") as f:
			noeWnd.templateView = f.read()
		
		loadWebCache(noeWnd)
		updateIndexTemplate(noeWnd)
		updatePubListing(noeWnd)
		
		noeWnd.createStatic("Serving Path:", 16, 16, 110, 20)
		noeWnd.servePathIndex = noeWnd.createEditBox(16, 38, 460, 20, noeWnd.webCache["cachedPath"], None, False)
		noeWnd.createButton("Browse", 16 + 460 + 6, 36, 96, 24, buttonBrowseMethod)
		noeWnd.createButton("Refresh", 16, 64, 96, 24, buttonRefreshMethod)

		noeWnd.createStatic("Status:", 16, 96, 110, 20)
		noeWnd.statusIndex = noeWnd.createEditBox(16, 118, 562, 20, "", None, False, True)
		
		noeWnd.startButtonIndex = noeWnd.createButton("Start", 16 + 460 + 6, 156, 96, 24, buttonStartMethod)
	
		user32.SetTimer(noeWnd.hWnd, MSERVER_UPDATE_TIMER_ID, MSERVER_UPDATE_TIMER_INTERVAL, 0)
		noeWnd.addUserControlMessageCallback(-1, noewin.WM_TIMER, statusUpdateTimer)
	
		noeWnd.doModal()
		abortOrWaitOnProcessing(noeWnd)
		stopExistingServer(noeWnd)
	return 0
