#Most protocol bits are informed by dorita980, which is a more complete and actively maintained Roomba 800+ implementation:
# https://github.com/koalazak/dorita980
#This implementation has only been tested with a 980 on currently-latest firmware. If you find you're having issues with
#this implementation, I'd encourage you to:
# A) Fix it and let me know what you had to do!
#or
# B) Write a script for dorita980 to spit out raw point data in the .noeroomba format.

import socket, ssl
import time
import random
import json
import noewin
import math
import paho.mqtt.client as mqtt
from noewin import user32, gdi32, kernel32
from inc_noesis import *
from ctypes import *

ROOMBA_TRACKER_SAVE_SETTINGS = False #be warned, if you make this true it will save your Roomba's user/pass in plaintext.

ROOMBA_UPDATE_ON_RECV = True #if false, use a separate timer to collect on a fixed interval, allowing samples to be dropped.

ROOMBA_BROADCAST_PORT = 5678
ROOMBA_BROADCAST_MSG = "irobotmcs"
ROOMBA_BROADCAST_MAX_SIZE = 1024
ROOMBA_BROADCAST_TIMEOUT = 5.0

ROOMBA_PASS_PORT = 8883
ROOMBA_PASS_KEY = bytes((0xf0, 0x05, 0xef, 0xcc, 0x3b, 0x29, 0x00))
ROOMBA_PASS_MAX_SIZE = 1024

ROOMBA_TRACK_PORT = 8883
ROOMBA_TRACK_KEEPALIVE = 5

ROOMBA_TRACK_CANVAS_W = 512
ROOMBA_TRACK_CANVAS_H = 512
ROOMBA_TRACK_CANVAS_OFFSET_X = 0
ROOMBA_TRACK_CANVAS_OFFSET_Y = 0
ROOMBA_TRACK_CANVAS_Y_MARGIN = 32
ROOMBA_TRACK_CANVAS_TRAIL_WIDTH = 1
ROOMBA_TRACK_CANVAS_BORDER_WIDTH = 1
ROOMBA_TRACK_CANVAS_TEXT_COLOR = noewin.RGB(0, 100, 0)
ROOMBA_TRACK_CANVAS_BG_COLOR = noewin.RGB(255, 255, 255)
ROOMBA_TRACK_CANVAS_ROOMBA_COLOR = noewin.RGB(0, 255, 0)
ROOMBA_TRACK_CANVAS_ROOMBA_OUTLINE_COLOR = noewin.RGB(0, 0, 0)
ROOMBA_TRACK_CANVAS_ROOMBA_DIR_COLOR = noewin.RGB(0, 100, 0)
ROOMBA_TRACK_CANVAS_BORDER_COLOR = noewin.RGB(0, 0, 0)
ROOMBA_TRACK_CANVAS_COORDSHIFT = 2 #higher values will allow the visible canvas map to cover greater area
ROOMBA_TRACK_CANVAS_BOTSIZE = 8
ROOMBA_TRACK_CANVAS_DIRLEN = 12
ROOMBA_TRACK_CANVAS_DIRLINESIZE = 2

ROOMBA_SAMPLE_UPDATE_INTERVAL = 1000
ROOMBA_SAMPLE_TIMER_ID = 666

MQTT_UPDATE_INTERVAL = 50
MQTT_UPDATE_TIMER_ID = 667
MQTT_TIMEOUT = 0.0333
MQTT_MAXPACKETS = 16

NOE_ROOMBA_HEADER = "NOESISROOMBAFILE"
NOE_ROOMBA_HEADER_SIZE = 24
NOE_ROOMBA_SAMPLE_SIZE = 12
NOE_ROOMBA_VERSION = 1
NOE_ROOMBA_EXTENSION = ".noeroomba"
NOE_ROOMBA_FLAG_NOCONNECTION = (1 << 0) #indicates that this sample doesn't connect to the next one - useful for merging runs.

ENABLE_TEST_FUNCTIONS = False

def registerNoesisTypes():
	handle = noesis.registerTool("Roomba Tracker", roombaToolMethod, "Launch the Roomba Tracker.")

	handle = noesis.registerTool("NoeRoomba Merger", noeRoombaMergeToolMethod, "Merge multiple NoeRoomba files.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, noeRoombaContextVisible)
	
	handle = noesis.registerTool("DOOMBA", doombaToolMethod, "Convert a NoeRoomba file into a Doom map.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, noeRoombaContextVisible)	
	
	if ENABLE_TEST_FUNCTIONS:
		handle = noesis.registerTool("Image to NoeRoomba", imageToRoombaToolMethod, "Convert an image to a NoeRoomba file.")
		noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
		noesis.setToolVisibleCallback(handle, imageToRoombaContextVisible)	
	
	return 1

def broadcastFindRoomba(noeWnd):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(ROOMBA_BROADCAST_TIMEOUT)
		s.bind(("", ROOMBA_BROADCAST_PORT))
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		s.sendto(ROOMBA_BROADCAST_MSG.encode("UTF-8"), ("255.255.255.255", ROOMBA_BROADCAST_PORT))
		
		foundParse = None
		foundAddr = None
		startTime = time.time()
		while (time.time() - startTime) < ROOMBA_BROADCAST_TIMEOUT:
			#noesis.pumpModalStatus("Searching for a Roomba...", 3.0)
			data, addr = s.recvfrom(ROOMBA_BROADCAST_MAX_SIZE)
			if data and len(data) > 10:
				#being lazy about the validation here.
				try:
					tryParse = json.loads(noeStrFromBytes(data, "UTF-8"))
					print("Received reply from Roomba:", tryParse, addr)
					useThisOne = (user32.MessageBoxW(noeWnd.hWnd, "Found a robot named " + tryParse["robotname"] + ". Use this one?", "Roomba Tracker", noewin.MB_YESNO) == noewin.IDYES)			
					if useThisOne:
						foundParse = tryParse
						foundAddr = addr
						break
				except:
					pass
			time.sleep(0.1)
		#noesis.clearModalStatus()
		s.close()
		return foundParse, foundAddr
	except:
		return None, None

def getRoombaPassword(addr):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssl_sock = ssl.wrap_socket(s, ca_certs=None, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1)
	ssl_sock.connect((addr, ROOMBA_PASS_PORT))
	ssl_sock.send(ROOMBA_PASS_KEY)
	sliceFrom = 11
	data = bytearray()
	while True:
		data += ssl_sock.recv(ROOMBA_PASS_MAX_SIZE)
		if len(data) == 2:
			sliceFrom = 7
		elif len(data) >= 8:
			return noeStrFromBytes(data[sliceFrom:], "UTF-8")
		else:
			print("Unexpected response length:", len(data))
			break
	ssl_sock.close()
	return None
	
def buttonAutoFindMethod(noeWnd, controlId, wParam, lParam):
	parsed, addr = broadcastFindRoomba(noeWnd)
	if addr:
		ipBox = noeWnd.getControlByIndex(noeWnd.roombaHostIndex)
		userBox = noeWnd.getControlByIndex(noeWnd.roombaUserIndex)
		passBox = noeWnd.getControlByIndex(noeWnd.roombaPassIndex)
		ipBox.setText(addr[0])
		userName = parsed["hostname"].split("-")[1]
		userBox.setText(userName)
		getPass = (user32.MessageBoxW(noeWnd.hWnd, "Username was retrieved. In order to retrieve the password, you must turn the Roomba on, then press and hold the Home button until you hear a noise. Upon releasing the Home button, the Wi-fi light should be flashing. You may then continue. Are you ready to continue?", "Roomba Tracker", noewin.MB_YESNO) == noewin.IDYES)
		while getPass:
			password = getRoombaPassword(addr[0])
			if password:
				passBox.setText(password)
				break
			getPass = (user32.MessageBoxW(noeWnd.hWnd, "The password could not be retrieved. Ensure that the unit is in the correct state, and that you held the Home button long enough to hear a noise, followed by the Wi-fi light flashing. Retry now?", "Roomba Tracker", noewin.MB_YESNO) == noewin.IDYES)
		saveWindowPrefs(noeWnd)
	else:
		noesis.messagePrompt("Failed to find any Roombas.")

def onRoombaConnect(mqttc, userdata, flags, rc):
	pass

def onRoombaDisconnect(mqttc, userdata, rc):
	pass

def onRoombaMessage(mqttc, userdata, msg):
	if msg.topic == "wifistat":
		try:
			payload = json.loads(noeStrFromBytes(msg.payload, "UTF-8"))
			if "state" in payload:
				state = payload["state"]
				if "reported" in state:
					reported = state["reported"]
					if "pose" in reported:
						pose = reported["pose"]
						oldPose = userdata.lastPose
						userdata.lastPose = pose
						userdata.lastPoseTime = time.time()
						userdata.poseCount += 1
						updateTrackCanvas(userdata, oldPose)
						userdata.freshPose = True
						if ROOMBA_UPDATE_ON_RECV:
							processFreshPose(userdata)
		except:
			print("Exception on message.")

def onRoombaPublish(mqttc, userdata, mid):
	pass

def processFreshPose(noeWnd):
	if noeWnd.freshPose:
		#print("Fresh pose:", noeWnd.lastPose, "Count:", noeWnd.poseCount, "Time:", noeWnd.lastPoseTime - noeWnd.trackStartTime)
		noeWnd.freshPose = False
		if noeWnd.dumpFile:
			df = noeWnd.dumpFile
			#not sure if x/y could actually get out of int16 range, but just using int32 as spec either way
			x, y, theta = getPoseTuple(noeWnd.lastPose)
			flags = 0 #reserved for future possibilities
			df.write(noePack("iihH", x, y, theta, flags))

def mqttUpdateTimer(noeWnd, controlIndex, message, wParam, lParam):
	if wParam == MQTT_UPDATE_TIMER_ID:
		if noeWnd.mqttc:
			r = noeWnd.mqttc.loop(MQTT_TIMEOUT, MQTT_MAXPACKETS)
			if r != 0:
				toggleTrack(noeWnd)
				noesis.messagePrompt("Lost connection to the Roomba.")			
	elif wParam == ROOMBA_SAMPLE_TIMER_ID:
		processFreshPose(noeWnd)

def closeDumpFile(noeWnd):
	if noeWnd.dumpFile:
		noeWnd.dumpFile.close()
		noeWnd.dumpFile = None
		return True
	return False
	
def closeExistingMqtt(noeWnd):
	if noeWnd.mqttc:
		noeWnd.mqttc.disconnect()
		noeWnd.mqttc = None
		return True
	return False
		
def toggleTrack(noeWnd):
	closeDumpFile(noeWnd)
	
	trackButton = noeWnd.getControlByIndex(noeWnd.trackButtonIndex)
	
	if closeExistingMqtt(noeWnd):
		trackButton.setText("Track")
		return
	
	dumpPath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save Pathing Data", "Select a destination to write pathing data, or cancel to track without writing.", "", None)

	ipBox = noeWnd.getControlByIndex(noeWnd.roombaHostIndex)
	userBox = noeWnd.getControlByIndex(noeWnd.roombaUserIndex)
	passBox = noeWnd.getControlByIndex(noeWnd.roombaPassIndex)
	
	noeWnd.poseCount = 0
	noeWnd.freshPose = False
	noeWnd.lastPose = None
	
	try:
		mqttc = mqtt.Client(userBox.getText())
		mqttc._userdata = noeWnd
		mqttc.tls_set(ca_certs=noeDefaultCertPath(), certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1)
		mqttc.username_pw_set(userBox.getText(), passBox.getText())
		mqttc.on_message = onRoombaMessage
		mqttc.on_publish = onRoombaPublish
		mqttc.on_connect = onRoombaConnect
		mqttc.on_disconnected = onRoombaDisconnect
		mqttc.connect(ipBox.getText(), ROOMBA_TRACK_PORT, ROOMBA_TRACK_KEEPALIVE)
		
		noeWnd.mqttc = mqttc
		trackButton.setText("Stop")
		noeWnd.trackStartTime = time.time()

		#open the dump stream if applicable
		if dumpPath and len(dumpPath) > 0:
			if os.path.splitext(dumpPath)[1].lower() != NOE_ROOMBA_EXTENSION:
				dumpPath += NOE_ROOMBA_EXTENSION
			noeWnd.dumpFile = open(dumpPath, "wb")
			df = noeWnd.dumpFile
			#start by writing a standard header
			df.write(NOE_ROOMBA_HEADER.encode("ASCII"))
			df.write(noePack("II", NOE_ROOMBA_VERSION, ROOMBA_SAMPLE_UPDATE_INTERVAL))
	except:
		noesis.messagePrompt("Exception during MQTT connection. The device may not be accepting connections, or the socket may already be in use.")
		
def buttonTrackMethod(noeWnd, controlId, wParam, lParam):
	saveWindowPrefs(noeWnd)
	toggleTrack(noeWnd)
	
def getPrefsFilePath():
	return noesis.getScenesPath() + "roomba_tracker_tool.cfg"

def saveWindowPrefs(noeWnd):
	if ROOMBA_TRACKER_SAVE_SETTINGS:
		ipBox = noeWnd.getControlByIndex(noeWnd.roombaHostIndex)
		userBox = noeWnd.getControlByIndex(noeWnd.roombaUserIndex)
		passBox = noeWnd.getControlByIndex(noeWnd.roombaPassIndex)
		with open(getPrefsFilePath(), "w") as f:
			f.write("ROOMBA_IP=" + ipBox.getText() + "\n")
			f.write("ROOMBA_USER=" + userBox.getText() + "\n")
			f.write("ROOMBA_PASS=" + passBox.getText() + "\n")
			
def loadWindowPrefs(noeWnd):
	if ROOMBA_TRACKER_SAVE_SETTINGS and os.path.exists(getPrefsFilePath()):
		with open(getPrefsFilePath(), "r") as f:
			ipBox = noeWnd.getControlByIndex(noeWnd.roombaHostIndex)
			userBox = noeWnd.getControlByIndex(noeWnd.roombaUserIndex)
			passBox = noeWnd.getControlByIndex(noeWnd.roombaPassIndex)
			for line in f:
				if line.startswith("ROOMBA_IP="):
					ipBox.setText(line.split("=", 1)[1].replace("\n", ""))
				elif line.startswith("ROOMBA_USER="):
					userBox.setText(line.split("=", 1)[1].replace("\n", ""))
				elif line.startswith("ROOMBA_PASS="):
					passBox.setText(line.split("=", 1)[1].replace("\n", ""))
				
def createInterfaceWindow(noeWnd):
	noeWnd.setFont("Arial", 14)

	noeWnd.poseCount = 0
	noeWnd.freshPose = False
	noeWnd.lastPose = None
	noeWnd.trackStartTime = 0.0
	
	standardTextFieldSize = 22
	currentY = 16
	
	noeWnd.createButton("Auto-Find", 16, currentY, 96, 24, buttonAutoFindMethod)		
	currentY += 32
	
	noeWnd.createStatic("Roomba IP:", 16, currentY + 2, 120, 20)
	noeWnd.roombaHostIndex = noeWnd.createEditBox(140, currentY, 460, 20, "", None, False)
	currentY += standardTextFieldSize

	noeWnd.createStatic("Roomba User:", 16, currentY + 2, 120, 20)
	noeWnd.roombaUserIndex = noeWnd.createEditBox(140, currentY, 460, 20, "", None, False)
	currentY += standardTextFieldSize

	noeWnd.createStatic("Roomba Pass:", 16, currentY + 2, 120, 20)
	noeWnd.roombaPassIndex = noeWnd.createEditBox(140, currentY, 460, 20, "", None, False)
	currentY += standardTextFieldSize
	
	currentY += 16
	noeWnd.trackButtonIndex = noeWnd.createButton("Track", 16, currentY, 96, 24, buttonTrackMethod)
	if ENABLE_TEST_FUNCTIONS:
		noeWnd.createButton("Load", 128, currentY, 96, 24, buttonLoadNoeRoombaMethod)
		noeWnd.createButton("Clear", 240, currentY, 96, 24, buttonClearCanvasMethod)
	currentY += 32
	
	noeWnd.mqttc = None
	noeWnd.timerProc = mqttUpdateTimer
	user32.SetTimer(noeWnd.hWnd, MQTT_UPDATE_TIMER_ID, MQTT_UPDATE_INTERVAL, 0)
	if not ROOMBA_UPDATE_ON_RECV:
		user32.SetTimer(noeWnd.hWnd, ROOMBA_SAMPLE_TIMER_ID, ROOMBA_SAMPLE_UPDATE_INTERVAL, 0)
	noeWnd.addUserControlMessageCallback(-1, noewin.WM_TIMER, mqttUpdateTimer)
	
def calculateCanvasRect(noeWnd):
	hWnd = noeWnd.hWnd
	rect = noewin.RECT()
	user32.GetClientRect(hWnd, byref(rect))
	
	rectWidth = rect.right - rect.left
	rectHeight = rect.bottom - rect.top
	xDiff = rectWidth - ROOMBA_TRACK_CANVAS_W
	canvasRect = noewin.RECT()
	canvasRect.left = rect.left + xDiff // 2
	canvasRect.right = canvasRect.left + ROOMBA_TRACK_CANVAS_W
	canvasRect.top = rect.bottom - ROOMBA_TRACK_CANVAS_H - ROOMBA_TRACK_CANVAS_Y_MARGIN
	canvasRect.bottom = canvasRect.top + ROOMBA_TRACK_CANVAS_H
	return canvasRect
	
def getPoseTuple(pose):
	theta = int(pose["theta"])
	point = pose["point"]
	return (int(point["x"]), int(point["y"]), theta)

def mapCoordToCanvas(x, y):
	midX = ROOMBA_TRACK_CANVAS_W >> 1
	midY = ROOMBA_TRACK_CANVAS_H >> 1
	#base so that 0, 0 is the middle of the canvas, and shift as needed
	canvasX = midX + ROOMBA_TRACK_CANVAS_OFFSET_X + (x >> ROOMBA_TRACK_CANVAS_COORDSHIFT)
	canvasY = midY + ROOMBA_TRACK_CANVAS_OFFSET_Y + ((-y) >> ROOMBA_TRACK_CANVAS_COORDSHIFT)
	#clamp to the canvas
	canvasX = max(min(canvasX, ROOMBA_TRACK_CANVAS_W - 1), 0)
	canvasY = max(min(canvasY, ROOMBA_TRACK_CANVAS_H - 1), 0)
	return canvasX, canvasY
	
def buttonClearCanvasMethod(noeWnd, controlId, wParam, lParam):
	if noeWnd.hCanvasBmp:
		gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hBorderPen)
		gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hBgBrush)
		gdi32.Rectangle(noeWnd.hCanvasMapOnlyDc, 0, 0, ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H)
		if noeWnd.lastPose:
			updateTrackCanvas(noeWnd, None)

def buttonLoadNoeRoombaMethod(noeWnd, controlId, wParam, lParam):
	filePath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Select File", "Select file to draw to canvas.", noesis.getSelectedFile(), noeRoombaValidate)
	if filePath:
		with open(filePath, "rb") as f:
			drawNoeRoombaToCanvas(noeWnd, f.read())

def drawNoeRoombaToCanvas(noeWnd, data):
	if noeWnd.hCanvasBmp:
		gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hTrailPen)
		bs = NoeBitStream(data)
		bs.seek(NOE_ROOMBA_HEADER_SIZE, NOESEEK_ABS)
		if bs.checkEOF():
			return #empty file
		rawX = bs.readInt()
		rawY = bs.readInt()
		x, y = mapCoordToCanvas(rawX, rawY)
		angle = bs.readShort()
		flags = bs.readUShort()
		noeWnd.lastPose = { "theta" : angle, "point" : { "x" : rawX, "y" : rawY } }
		sampleCount = 1
		sanityDistanceSq = 100 >> ROOMBA_TRACK_CANVAS_COORDSHIFT
		sanityDistanceSq *= sanityDistanceSq
		while not bs.checkEOF():
			nextX, nextY = mapCoordToCanvas(bs.readInt(), bs.readInt())
			angle = bs.readShort()
			nextFlags = bs.readUShort()
			sampleCount += 1
			if x != nextX or y != nextY:
				if not flags & NOE_ROOMBA_FLAG_NOCONNECTION:
					dx = x - nextX
					dy = y - nextY
					lSq = dx * dx + dy * dy
					if lSq <= sanityDistanceSq:
						gdi32.MoveToEx(noeWnd.hCanvasMapOnlyDc, x, y, None)
						gdi32.LineTo(noeWnd.hCanvasMapOnlyDc, nextX, nextY)
			
			x = nextX
			y = nextY
			flags = nextFlags
		noeWnd.poseCount = sampleCount
		noeWnd.lastPoseTime = sampleCount
		noeWnd.trackStartTime = 0.0
		updateTrackCanvas(noeWnd, None)

def updateTrackCanvas(noeWnd, oldPose):
	if noeWnd.hCanvasBmp:
		x, y, theta = getPoseTuple(noeWnd.lastPose)
		canvX, canvY = mapCoordToCanvas(x, y)
		if oldPose: #draw a line into the map-only canvas
			oldX, oldY, oldTheta = getPoseTuple(oldPose)
			oldCanvX, oldCanvY = mapCoordToCanvas(oldX, oldY)
			if oldCanvX != canvX or oldCanvY != canvY:
				gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hTrailPen)
				gdi32.MoveToEx(noeWnd.hCanvasMapOnlyDc, oldCanvX, oldCanvY, None)
				gdi32.LineTo(noeWnd.hCanvasMapOnlyDc, canvX, canvY)
				
		#copy the map over before drawing dynamic elements
		gdi32.BitBlt(noeWnd.hCanvasDc, 0, 0, ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H, noeWnd.hCanvasMapOnlyDc, 0, 0, 0x00CC0020)
	
		#draw roomba
		roombaLeft = canvX - ROOMBA_TRACK_CANVAS_BOTSIZE
		roombaRight = canvX + ROOMBA_TRACK_CANVAS_BOTSIZE
		roombaTop = canvY - ROOMBA_TRACK_CANVAS_BOTSIZE
		roombaBottom = canvY + ROOMBA_TRACK_CANVAS_BOTSIZE
		gdi32.SelectObject(noeWnd.hCanvasDc, noeWnd.hRoombaPen)
		gdi32.SelectObject(noeWnd.hCanvasDc, noeWnd.hRoombaBrush)
		gdi32.Ellipse(noeWnd.hCanvasDc, roombaLeft, roombaTop, roombaRight, roombaBottom)
		#draw a line indicating direction
		gdi32.SelectObject(noeWnd.hCanvasDc, noeWnd.hRoombaDirPen)
		rad = theta * noesis.g_flDegToRad
		lineEndX = int(canvX + math.cos(rad) * ROOMBA_TRACK_CANVAS_DIRLEN + 0.5)
		lineEndY = int(canvY - math.sin(rad) * ROOMBA_TRACK_CANVAS_DIRLEN + 0.5)
		gdi32.MoveToEx(noeWnd.hCanvasDc, canvX, canvY, None)
		gdi32.LineTo(noeWnd.hCanvasDc, lineEndX, lineEndY)
	
		#status text
		gdi32.SetTextColor(noeWnd.hCanvasDc, ROOMBA_TRACK_CANVAS_TEXT_COLOR)
		gdi32.SetBkMode(noeWnd.hCanvasDc, noewin.TRANSPARENT)
		trect = noewin.RECT()
		trect.left = 4
		trect.top = 4
		trect.right = ROOMBA_TRACK_CANVAS_W - trect.left
		trect.bottom = ROOMBA_TRACK_CANVAS_H - trect.top
		statusText = "Position: (%i, %i)\r\nAngle: %i\r\nSample count: %i\r\nTime: %.02f\r\n"%(x, y, theta, noeWnd.poseCount, noeWnd.lastPoseTime - noeWnd.trackStartTime)
		noewin.user32.DrawTextW(noeWnd.hCanvasDc, statusText, -1, byref(trect), 0)
	
		#make sure we repaint after updating the canvas
		user32.InvalidateRect(noeWnd.hWnd, 0, False)

def destroyCanvasObjects(noeWnd):
	if noeWnd.hCanvasBmp:
		gdi32.DeleteObject(noeWnd.hCanvasDc)
		gdi32.DeleteObject(noeWnd.hCanvasBmp)
		gdi32.DeleteObject(noeWnd.hCanvasMapOnlyDc)
		gdi32.DeleteObject(noeWnd.hCanvasMapOnlyBmp)
		gdi32.DeleteObject(noeWnd.hBgBrush)
		gdi32.DeleteObject(noeWnd.hBorderPen)
		gdi32.DeleteObject(noeWnd.hTrailPen)
		gdi32.DeleteObject(noeWnd.hRoombaPen)
		gdi32.DeleteObject(noeWnd.hRoombaDirPen)
		gdi32.DeleteObject(noeWnd.hRoombaBrush)
		
def roombaWindowProc(hWnd, message, wParam, lParam):
	if message == noewin.WM_PAINT:
		noeWnd = noewin.getNoeWndForHWnd(hWnd)
		ps = noewin.PAINTSTRUCT()
		hDC = user32.BeginPaint(hWnd, byref(ps))
		
		if not noeWnd.hCanvasBmp:
			bpp = gdi32.GetDeviceCaps(hDC, 12)
			noeWnd.hCanvasDc = gdi32.CreateCompatibleDC(hDC)
			noeWnd.hCanvasBmp = gdi32.CreateBitmap(ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H, 1, bpp, 0)
			noeWnd.hCanvasMapOnlyDc = gdi32.CreateCompatibleDC(hDC)
			noeWnd.hCanvasMapOnlyBmp = gdi32.CreateBitmap(ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H, 1, bpp, 0)

			noeWnd.hBgBrush = gdi32.CreateSolidBrush(ROOMBA_TRACK_CANVAS_BG_COLOR)
			noeWnd.hBorderPen = gdi32.CreatePen(0, ROOMBA_TRACK_CANVAS_BORDER_WIDTH, ROOMBA_TRACK_CANVAS_BORDER_COLOR)
			noeWnd.hTrailPen = gdi32.CreatePen(0, ROOMBA_TRACK_CANVAS_TRAIL_WIDTH, ROOMBA_TRACK_CANVAS_BORDER_COLOR)
			noeWnd.hRoombaPen = gdi32.CreatePen(0, ROOMBA_TRACK_CANVAS_BORDER_WIDTH, ROOMBA_TRACK_CANVAS_ROOMBA_OUTLINE_COLOR)
			noeWnd.hRoombaDirPen = gdi32.CreatePen(0, ROOMBA_TRACK_CANVAS_DIRLINESIZE, ROOMBA_TRACK_CANVAS_ROOMBA_DIR_COLOR)
			noeWnd.hRoombaBrush = gdi32.CreateSolidBrush(ROOMBA_TRACK_CANVAS_ROOMBA_COLOR)
	
			gdi32.SelectObject(noeWnd.hCanvasDc, noeWnd.hCanvasBmp)
			gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hCanvasMapOnlyBmp)

			#default fill the map-only canvas
			gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hBorderPen)
			gdi32.SelectObject(noeWnd.hCanvasMapOnlyDc, noeWnd.hBgBrush)
			gdi32.Rectangle(noeWnd.hCanvasMapOnlyDc, 0, 0, ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H)
			#copy over to the final canvas
			gdi32.BitBlt(noeWnd.hCanvasDc, 0, 0, ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H, noeWnd.hCanvasMapOnlyDc, 0, 0, 0x00CC0020)			
		
		canvasRect = calculateCanvasRect(noeWnd)
			
		gdi32.BitBlt(hDC, canvasRect.left, canvasRect.top, ROOMBA_TRACK_CANVAS_W, ROOMBA_TRACK_CANVAS_H, noeWnd.hCanvasDc, 0, 0, 0x00CC0020)

		user32.EndPaint(hWnd, byref(ps))
	
	return noewin.defaultWindowProc(hWnd, message, wParam, lParam)

def setDefaultWindowPos(noeWnd):
	#offset a bit into the noesis window
	noeWindowRect = noewin.getNoesisWindowRect()
	if noeWindowRect:
		windowMargin = 64
		noeWnd.x = noeWindowRect[0] + windowMargin
		noeWnd.y = noeWindowRect[1] + windowMargin

def roombaToolMethod(toolIndex):
	noeWnd = noewin.NoeUserWindow("Roomba Tracker", "RoombaWindowClass", 644, 750, roombaWindowProc)
	setDefaultWindowPos(noeWnd)
	if not noesis.getWindowHandle():
		#if invoked via ?runtool, we're our own entity
		noeWnd.exStyle = noewin.WS_EX_DLGMODALFRAME
		noeWnd.style |= noewin.WS_MINIMIZEBOX | noewin.WS_MAXIMIZEBOX
		noeWnd.userIcon = user32.LoadIconW(kernel32.GetModuleHandleW(0), noesis.getResourceHandle(0))
	if noeWnd.createWindow():
		noeWnd.hCanvasBmp = None
		noeWnd.dumpFile = None
		createInterfaceWindow(noeWnd)
		loadWindowPrefs(noeWnd)
		noeWnd.doModal()
		closeDumpFile(noeWnd)
		closeExistingMqtt(noeWnd)
		destroyCanvasObjects(noeWnd)
	
	return 0

def noeRoombaValidate(inVal):
	if not os.path.exists(inVal):
		return "File does not exist or cannot be read."
	elif os.path.splitext(inVal)[1].lower() != NOE_ROOMBA_EXTENSION:
		return "Expected NoeRoomba file extension."
	return None

def noeRoombaContextVisible(toolIndex, selectedFile):
	if selectedFile is None or noeRoombaValidate(selectedFile) is not None:
		return 0
	return 1

def noeRoombaMergeToolMethod(toolIndex):
	filePath0 = noesis.getSelectedFile()
	filePath1 = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Second File", "Select the second NoeRoomba file to be merged.", filePath0, noeRoombaValidate)
	if filePath1:			
		destPath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save File", "Choose the merged NoeRoomba filename.", os.path.splitext(filePath0)[0] + " merged" + NOE_ROOMBA_EXTENSION, None)
		if destPath:
			with open(filePath0, "rb") as f0, open(filePath1, "rb") as f1, open(destPath, "wb") as fd:
				noesis.logPopup()
				#could warn about mismatched rates and stuff, but for now just don't care
				f0Stream = NoeBitStream(f0.read())
				f0Len = len(f0Stream.getBuffer())
				#shunt a no-connection flag in there
				if f0Len >= (NOE_ROOMBA_HEADER_SIZE + NOE_ROOMBA_SAMPLE_SIZE):
					f0Stream.seek(f0Len - 2) #assume the last 2 bytes are always flags
					print("Writing no-connection flag in at offset", f0Stream.tell())
					f0Stream.writeUShort(NOE_ROOMBA_FLAG_NOCONNECTION)
				fd.write(f0Stream.getBuffer())
				f1Data = f1.read()
				if len(f1Data) > NOE_ROOMBA_HEADER_SIZE:
					print("Appending second file at offset", fd.tell())
					f1.seek(NOE_ROOMBA_HEADER_SIZE, os.SEEK_SET)
					fd.write(f1.read())
					print("Final merged size is", fd.tell())
	return 0
	
def imageToRoombaContextVisible(toolIndex, selectedFile):
	if selectedFile is None or (noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_IMGREAD) == 0:
		return 0
	return 1

def imageToRoombaToolMethod(toolIndex):
	srcName = noesis.getSelectedFile()
	if not srcName or not os.path.exists(srcName):
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0

	srcTex = noesis.loadImageRGBA(srcName)
	if not srcTex:
		noesis.messagePrompt("Failed to load image data from file.")
		return 0

	defaultSavePath = os.path.splitext(srcName)[0] + NOE_ROOMBA_EXTENSION	
	savePath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save File", "Select destination for NoeRoomba file.", defaultSavePath, None)
	if not savePath:
		return 0
		
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	
	try:
		rgbaPix = rapi.imageGetTexRGBA(srcTex)
		imageShiftDown = 2
		coordShiftUp = 2
		noeRoombaData = rapi.callExtensionMethod("imageToNoeRoomba", rgbaPix, srcTex.width, srcTex.height, imageShiftDown, coordShiftUp)
		with open(savePath, "wb") as f:
			f.write(noeRoombaData)
	except:
		noesis.messagePrompt("Failed to write NoeRoomba.")
		
	noesis.freeModule(noeMod)

	return 0


#====================================================================
# DOOMBA
# all of the following pertains to DOOMBA and has nothing to do with
# Roomba tracking.
#====================================================================


class DoombaCatSource:
	def __init__(self, name, nameReadable, valMin, valMax, type, spec, space, catType):
		self.name = name
		self.nameReadable = nameReadable
		self.valMin = valMin
		self.valMax = valMax
		self.type = type
		self.spec = spec
		self.space = space
		self.catType = catType

class DoombaCat:
	def __init__(self, noeWnd, catSource, startX, startY):
		self.source = catSource
		self.noeWnd = noeWnd
		noeWnd.createStatic(catSource.nameReadable + ":", startX, startY, 140, 20)
		noeWnd.createStatic("Min:", startX, startY + 24, 30, 20)
		self.minBoxIndex = noeWnd.createEditBox(startX + 32, startY + 22, 80, 20, repr(catSource.valMin), None, False)		
		noeWnd.createStatic("Max:", startX + 120, startY + 24, 30, 20)
		self.maxBoxIndex = noeWnd.createEditBox(startX + 152, startY + 22, 80, 20, repr(catSource.valMax), None, False)		
		noeWnd.createStatic("Placement:", startX, startY + 50, 80, 20)
		self.placementBoxIndex = createDoombaComboBox(noeWnd, DOOMBA_PLACEMENT_TYPES, catSource.type, startX + 82, startY + 46, 140, 20)
		noeWnd.createStatic("Special:", startX, startY + 77, 80, 20)
		self.specialBoxIndex = createDoombaComboBox(noeWnd, DOOMBA_PLACEMENT_SPECIALS, catSource.spec, startX + 82, startY + 74, 140, 20)
		noeWnd.createStatic("Spacing:", startX, startY + 103, 80, 20)
		self.spacingBoxIndex = noeWnd.createEditBox(startX + 82, startY + 102, 80, 20, repr(catSource.space), None, False)
	def retrieveValues(self):
		#the member names used here are important, the doomba engine looks for them explicitly.
		noeWnd = self.noeWnd
		self.doombaTypeName = self.source.name
		self.doombaMin = int(noeWnd.getControlByIndex(self.minBoxIndex).getText())
		self.doombaMax = int(noeWnd.getControlByIndex(self.maxBoxIndex).getText())
		placementBox = noeWnd.getControlByIndex(self.placementBoxIndex)
		specialBox = noeWnd.getControlByIndex(self.specialBoxIndex)
		self.doombaPlacementType = placementBox.getStringForIndex(placementBox.getSelectionIndex())
		self.doombaSpecialType = specialBox.getStringForIndex(specialBox.getSelectionIndex())
		self.doombaSpacing = int(noeWnd.getControlByIndex(self.spacingBoxIndex).getText())

#feel free to modify/add. you could also group things up by theme and randomize within the theme.
DOOMBA_DEFAULT_FLOORS = (
	"FLOOR0_3", "FLOOR1_1", "FLOOR3_3", "FLOOR4_6", "FLOOR4_8", "FLOOR5_1", "FLOOR5_2", "FLOOR6_1", "FLOOR6_2", "FLOOR7_1", "FLOOR7_2",
	"FLAT14", "FLAT5_5", "NUKAGE3", "FWATER4", "DEM1_6", "MFLR8_2", "MFLR8_3", "MFLR8_4", "BLOOD3", "FLAT5_1", "FLAT5_6", "FLAT5_7", "FLAT19"
)
DOOMBA_DEFAULT_CEILS = (
	"CEIL3_1", "CEIL3_5", "CEIL4_2", "CEIL5_1", "CEIL5_2", "FLAT5", "FLAT10", "MFLR8_1", "F_SKY1", "FLOOR7_2", "CEIL4_3", "FLAT5_5", "FLOOR6_1"
)
DOOMBA_DEFAULT_WALLS = (
	"STARTAN1", "STARTAN3", "STARG1", "STARG3", "STARGR1", "BROWN1", "BROWN96", "BROWNGRN", "BROWNHUG", "BROWNPIP", "COMPTILE", "GRAY7", "PIPE2",
	"STONE", "STONE2", "STONE3", "TEKWALL1", "TEKWALL4", "ASHWALL", "COMPBLUE", "CEMENT3", "CEMENT6", "FIREWALL", "FIRELAVA", "GSTONE1", "MARBLE1",
	"METAL", "REDWALL", "SKIN2", "SKINEDGE", "SKINFACE", "SKINLOW", "SKINMET1", "SKINSCAB", "SKINSYMB", "SKSPINE2", "SKULWAL3", "SKULWALL", "SP_FACE1",
	"SP_HOT1", "WOOD1", "WOOD5"
)
DOOMBA_PLACEMENT_TYPES = ("Random", "AtRoomba", "InView", "OutsideView" )
DOOMBA_PLACEMENT_SPECIALS = ( "None", "Player" )
DOOMBA_PLACEMENT_SPACE_SMALL = 8
DOOMBA_PLACEMENT_SPACE_DEFAULT = 24
DOOMBA_PLACEMENT_SPACE_MEDIUM = 38
DOOMBA_PLACEMENT_SPACE_LARGE = 56
#you can define an arbitrary number of categories, so if you'd like separate random generation for zombies and sarges,
#you could separate them each into their own categories instead of clumping them into "tier1" as we do here.
DOOMBA_CATEGORY_SOURCES = (
	DoombaCatSource("player", "Players", 4, 4, DOOMBA_PLACEMENT_TYPES[1], DOOMBA_PLACEMENT_SPECIALS[1], DOOMBA_PLACEMENT_SPACE_DEFAULT, 0),
	DoombaCatSource("barrel", "Barrels", 0, 20, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 0),
	DoombaCatSource("ammo", "Ammo", 4, 20, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 0),
	DoombaCatSource("decorations", "Decorations", 0, 0, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_MEDIUM, 0),
	DoombaCatSource("enemy_tier1", "Tier 1 Enemies", 10, 20, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_DEFAULT, 1),
	DoombaCatSource("enemy_tier2", "Tier 2 Enemies", 0, 10, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_DEFAULT, 1),
	DoombaCatSource("enemy_tier3", "Tier 3 Enemies", 0, 4, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_MEDIUM, 1),
	DoombaCatSource("enemy_tier4", "Tier 4 Enemies", 0, 4, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_MEDIUM, 1),
	DoombaCatSource("enemy_tier5", "Tier 5 Enemies", -2, 1, DOOMBA_PLACEMENT_TYPES[3], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_LARGE, 1),
	DoombaCatSource("weapon_tier1", "Tier 1 Weapons", 0, 1, DOOMBA_PLACEMENT_TYPES[3], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 2),
	DoombaCatSource("weapon_tier2", "Tier 2 Weapons", 1, 2, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 2),
	DoombaCatSource("weapon_tier3", "Tier 3 Weapons", 0, 2, DOOMBA_PLACEMENT_TYPES[0], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 2),
	DoombaCatSource("weapon_tier4", "Tier 4 Weapons", -2, 1, DOOMBA_PLACEMENT_TYPES[3], DOOMBA_PLACEMENT_SPECIALS[0], DOOMBA_PLACEMENT_SPACE_SMALL, 2)
)

#you could add doom 2 support pretty easily by adding some id's in here
DOOMBA_CAT_TO_IDS = {
	"player" : [ 1, 2, 3, 4 ], #player starts
	"barrel" : [ 2035 ], #explosive barrels
	"ammo" : [ 2048, 2049, 2046, 17 ], #clip box, shell box, rocket box, cell pack
	"decorations" : [ 15, 24, 25, 26, 27, 28, 30, 34, 36, 37, 44, 45, 46, 49 ], #dead marine, gibs, skewered dead, skewered live, head stick, ...
	"enemy_tier1" : [ 3004, 9 ], #zombie, shotgun guy
	"enemy_tier2" : [ 3001, 3006 ], #imp, lost soul
	"enemy_tier3" : [ 3002, 58 ], #pinky, inviso-pinky
	"enemy_tier4" : [ 3003, 3005 ], #baron, caco
	"enemy_tier5" : [ 16 ], #cyberdemon, spider=7 - needs another tier if we want to include him, he's too big
	"weapon_tier1" : [ 2005 ], #chainsaw
	"weapon_tier2" : [ 2001, 2002 ], #shotgun, chaingun
	"weapon_tier3" : [ 2003, 2004 ], #rocket launcher, plasma rifle
	"weapon_tier4" : [ 2006 ] #bfg
}

def buttonGenerateMethod(noeWnd, controlId, wParam, lParam):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	try:
		seedBox = noeWnd.getControlByIndex(noeWnd.seedBoxIndex)	
		seed = int(seedBox.getText())
		if seed == 0:
			seed = int(math.fmod(time.time(), 12345) * 12345)
			seedBox.setText(repr(seed))
			
		#make sure each object category object is up to date with user input
		for cat in noeWnd.cats:
			cat.retrieveValues()
		
		random.seed(seed) #for local random operations that we perform after the doomba engine hands the data back

		floorBox = noeWnd.getControlByIndex(noeWnd.floorBoxIndex)
		ceilBox = noeWnd.getControlByIndex(noeWnd.ceilBoxIndex)
		wallBox = noeWnd.getControlByIndex(noeWnd.wallBoxIndex)

		genBox = noeWnd.getControlByIndex(noeWnd.genBoxIndex)
		advBox = noeWnd.getControlByIndex(noeWnd.advBoxIndex)
		
		allOptions = genBox.getText() + " " + advBox.getText().replace("\n", " ").replace("\r", " ")
		
		optionsDict = dict(item.split("=") for item in allOptions.split(" "))
		
		paramDict = {
			"seed" : seed,
			"catObjects" : noeWnd.cats,
			"floors" : floorBox.getText(),
			"ceils" : ceilBox.getText(),
			"walls" : wallBox.getText(),
			"otherOptions" : optionsDict
		}
		doombaTuple = rapi.callExtensionMethod("doomba", noeWnd.noeRoombaData, paramDict)
		if not doombaTuple:
			noesis.messagePrompt("The DOOMBA engine could not produce a map with the given data.")
		else:
			objects, linedefData, sidedefData, vertData, sectorData = doombaTuple
			
			#we get objects back in a non-binary format, so that we can do our own game-specific stuff script-side to generate the things data.
			#this is where you could also go through the raw sector/linedef/etc. data to translate flags, types, etc. to support other games.
			
			#first make a list of ammo that's ok to spawn based weapons present
			preSelectedIds = {}
			goodAmmo = [2048, 2012] #bullet box is always ok due to starting pistol, and make medpacks randomly appear as ammo
			for objectIndex in range(0, len(objects)):
				object = objects[objectIndex]
				doombaName = object[4]
				if doombaName.startswith("weapon_"):
					#alright, pick the id now, then clear the associated ammo
					idList = DOOMBA_CAT_TO_IDS[doombaName]
					chosenId = idList[random.randint(0, len(idList) - 1)]
					if chosenId == 2001: #shotgun
						if 2049 not in goodAmmo: #add shell box
							goodAmmo.append(2049)
					#ignore chaingun, uses bullets
					elif chosenId == 2003: #rocket launcher
						if 2046 not in goodAmmo: #add rocket box
							goodAmmo.append(2046)
					elif chosenId == 2004 or chosenId == 2006: #plasma, bfg
						if 17 not in goodAmmo: #add cell pack
							goodAmmo.append(17)
					preSelectedIds[objectIndex] = chosenId
			
			thingsBs = NoeBitStream()
			playerCount = 0
			for objectIndex in range(0, len(objects)):
				object = objects[objectIndex]
				x, y, angle, spawnFlags, doombaName = object
				if doombaName in DOOMBA_CAT_TO_IDS:
					idList = DOOMBA_CAT_TO_IDS[doombaName]
					if doombaName == "player": #special-case, rotate these instead of picking randomly
						id = idList[playerCount]
						playerCount = (playerCount + 1) & 3
					elif doombaName.startswith("weapon_"):
						id = preSelectedIds[objectIndex]
					elif doombaName == "ammo":
						id = goodAmmo[random.randint(0, len(goodAmmo) - 1)]
					else:
						id = idList[random.randint(0, len(idList) - 1)]
				else:
					#special case, the engine is asking us to create a thing.
					#for now, just assume it's a teleport dest. (doombaName will be "teleport_dest")
					id = 14
					
				thingsBs.writeShort(x)
				thingsBs.writeShort(y)
				thingsBs.writeUShort(angle)
				thingsBs.writeUShort(id)
				thingsBs.writeUShort(spawnFlags)

			wadBs = NoeBitStream()
			lumpCount = 6
			wadBs.writeBytes(noePack("III", 0x44415750, lumpCount, 0)) #will go back and fix offset later
			thingsOffset = wadBs.tell()
			wadBs.writeBytes(thingsBs.getBuffer())
			linedefOffset = wadBs.tell()
			wadBs.writeBytes(linedefData)
			sidedefOffset = wadBs.tell()
			wadBs.writeBytes(sidedefData)
			vertOffset = wadBs.tell()
			wadBs.writeBytes(vertData)
			sectorOffset = wadBs.tell()
			wadBs.writeBytes(sectorData)
			#now write the lumps
			lumpsOffset = wadBs.tell()
			wadBs.writeBytes(noePack("II", thingsOffset, 0) + noePaddedByteArray(bytearray(optionsDict["MapName"], "ASCII"), 8))
			wadBs.writeBytes(noePack("II", thingsOffset, len(thingsBs.getBuffer())) + noePaddedByteArray(bytearray("THINGS", "ASCII"), 8))
			wadBs.writeBytes(noePack("II", linedefOffset, len(linedefData)) + noePaddedByteArray(bytearray("LINEDEFS", "ASCII"), 8))
			wadBs.writeBytes(noePack("II", sidedefOffset, len(sidedefData)) + noePaddedByteArray(bytearray("SIDEDEFS", "ASCII"), 8))
			wadBs.writeBytes(noePack("II", vertOffset, len(vertData)) + noePaddedByteArray(bytearray("VERTEXES", "ASCII"), 8))
			wadBs.writeBytes(noePack("II", sectorOffset, len(sectorData)) + noePaddedByteArray(bytearray("SECTORS", "ASCII"), 8))
			#go back and fix up the lumps offset
			wadBs.seek(8, NOESEEK_ABS)
			wadBs.writeBytes(noePack("I", lumpsOffset))
			#now invoke the nodebuilder separately.
			#this nodebuilder is based on Raphael Quinet's DEU code, because it isn't tainted by the fetid stench of the GPL.
			wadWithBsp = rapi.callExtensionMethod("nodebuilder", wadBs.getBuffer())

			defaultSavePath = os.path.splitext(noeWnd.noeRoombaPath)[0] + ".wad"
			savePath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save File", "Select destination for WAD file.", defaultSavePath, None)
			if savePath:
				with open(savePath, "wb") as wadFile:
					wadFile.write(wadWithBsp)
					noesis.messagePrompt("WAD file successfully generated.")
	except:
		noesis.messagePrompt("There was an error in DOOMBA data generation.")
	
	noesis.freeModule(noeMod)

def createDoombaComboBox(noeWnd, items, selItem, x, y, w, h):
	listIndex = noeWnd.createComboBox(x, y, w, h, None, noewin.CBS_DROPDOWNLIST)
	listBox = noeWnd.getControlByIndex(listIndex)
	for item in items:
		listBox.addString(item)
	if selItem:
		listBox.selectString(selItem)
	return listIndex
	
def doombaToolMethod(toolIndex):
	noeRoombaPath = noesis.getSelectedFile()
	with open(noeRoombaPath, "rb") as f:
		noeRoombaData = f.read()

	noeWnd = noewin.NoeUserWindow("DOOMBA", "DoombaWindowClass", 1320, 800)
	setDefaultWindowPos(noeWnd)
	noeWnd.noeRoombaPath = noeRoombaPath
	noeWnd.noeRoombaData = noeRoombaData
	if noeWnd.createWindow():
		noeWnd.setFont("Arial", 14)
	
		startX = 16
		startY = 90
		currentCatType = DOOMBA_CATEGORY_SOURCES[0].catType
		noeWnd.cats = []
		for catSource in DOOMBA_CATEGORY_SOURCES:
			if currentCatType != catSource.catType:
				currentCatType = catSource.catType
				startY += 150
				startX = 16
			noeWnd.cats.append(DoombaCat(noeWnd, catSource, startX, startY))
			startX += 260
	
		noeWnd.createStatic("Seed:", 16, 48, 40, 20)
		noeWnd.seedBoxIndex = noeWnd.createEditBox(58, 46, 120, 20, "0", None, False)		
	
		noeWnd.createButton("Generate", 16, 16, 96, 24, buttonGenerateMethod)		

		noeWnd.createStatic("Floors:", 16, 552, 60, 20)
		noeWnd.floorBoxIndex = noeWnd.createEditBox(16, 574, 200, 170, " ".join(DOOMBA_DEFAULT_FLOORS))
		
		noeWnd.createStatic("Ceilings:", 232, 552, 60, 20)
		noeWnd.ceilBoxIndex = noeWnd.createEditBox(232, 574, 200, 170, " ".join(DOOMBA_DEFAULT_CEILS))

		noeWnd.createStatic("Walls:", 448, 552, 60, 20)
		noeWnd.wallBoxIndex = noeWnd.createEditBox(448, 574, 200, 170, " ".join(DOOMBA_DEFAULT_WALLS))

		defaultGenParams = "FloorMin=-24 FloorMax=0 CeilMin=110 CeilMax=140 ObstacleFloorMin=12 ObstacleFloorMax=30 LightMin=128 LightMax=248 RoomToDoomScale=1.0 RoomToDoomOffset=0,0 LightProb=20 EnforceViewPref=0 ExitRandom=1 WallSwitchExit=0 IslandTeleports=0 IslandCircular=0"
		noeWnd.createStatic("Generation:", 680, 544, 100, 20)
		noeWnd.genBoxIndex = noeWnd.createEditBox(680, 566, 610, 80, defaultGenParams)

		defaultAdvParams = "MapName=E1M1 ExitHeight=12 ExitTexture=GATE3 WallSwitchExitTexture=SW1STON1 WallSwitchExitSize=64 ExitSepThresh=150 ExitCloserScale=0.75 ExitSnap=64 ExitSize=32 AreaMin=100000 AreaMax=200000 CollapseDistance=3.0 AltSampling=0 HardeningValue=-1 SampleExponent=2.0 SampleRad=32 MapShift=2 OccShift=2"
		noeWnd.createStatic("Advanced:", 680, 652, 100, 20)
		noeWnd.advBoxIndex = noeWnd.createEditBox(680, 674, 610, 80, defaultAdvParams)
		
		noeWnd.doModal()
	return 0
