#F2A implementation - much of this is based on original code/specs by Ulrich Hecht.
#i sniffed the ez-usb firmware binary and associated commands out of my linker cable with a filter driver under a WinXP VM. there are various things in the multiboot
#upload that need to happen in a certain way, which doesn't appear to be reflected by Ulrich Hecht's code. may have something to do with the firmware i'm using.
#this isn't particularly user-friendly, doesn't give good indications of progress on the host, and will allow you to cause ruination if you don't know what you're doing.
#
#i have no idea if there are variants of the linker that may require variants of the firmware, but you can swap out binaries this script uses easily enough.
#this code might technically be GPL-infected due to taking direct inspiration (and occasionally sharing naming conventions with) Ulrich Hecht's code. so there's that.
#as a side note, GPL is a terrible license. for the sake of the children, use BSD or MIT, or LGPL if you really must.

from inc_noesis import *
import os
import time
import noewin
from noewin import user32, gdi32, kernel32

def registerNoesisTypes():
	handle = noesis.registerTool("F2A Interface", f2aToolMethod, "Launch F2A Interface.")
	return 1

F2A_EZUSBFW = "tool_f2ainterface_ti01.bin"
F2A_MULTIBOOT = "tool_f2ainterface_ti02.bin"
F2A_CMD_GETINF = 5
F2A_CMD_WRITEDATA = 6
F2A_CMD_READDATA = 7
F2A_CMD_MULTIBOOT1 = 0xFF
F2A_CMD_MULTIBOOT2 = 0
F2A_SUBCMD_WRITE = 6
F2A_SUBCMD_READ = 7
F2A_SUBCMD_WRITEROM = 10
F2A_MAGIC = 0xA46E5B91
F2A_STATUS_NOTREADY = 0
F2A_STATUS_READY = 4
F2A_RESPONSE_SIZE = 64
F2A_EP_READ = 3 | 0x80
F2A_EP_WRITE = 4

F2A_TARGET_EWRAM = 0x02000000
F2A_TARGET_VRAM = 0x06000000
F2A_TARGET_OAM = 0x07000000
F2A_TARGET_ROM = 0x08000000
F2A_TARGET_SRAM = 0x0E000000

F2A_RECONNECT_LIMIT = 5
F2A_EP_TIMEOUT = 3000
F2A_EP_BOOTWAIT_TIMEOUT = 30000

F2A_DEVINTGUID = "{a5dcbf10-6530-11d2-901f-00c04fb951ed}"
F2A_CLASSGUID = "{028d7162-699a-4271-acad-d0234c3f2497}" #GUID specified by the WinUSB driver

def loadBin(binName):
	fullPath = noesis.getPluginsPath() + "python\\" + binName
	f = open(fullPath, "rb")
	r = f.read()
	f.close()
	return r

class F2ACommand:
	def __init__(self):
		self.command = 0
		self.dataSize = 0
		self.reserved0 = 0
		self.reserved1 = 0
		self.magic = 0 #F2A_MAGIC
		self.reserved2 = 0
		self.reserved3 = 0
		self.reserved4 = 0
		self.subCommand = 0
		self.address = 0
		self.dataSizeKb = 0
		self.reserved5 = 0
		self.reserved6 = 0
		self.reserved7 = 0
		self.reserved8 = 0
		self.reserved9 = 0
	def getBytes(self):
		#return noePack("IIIIIIIIIIIIIIII", self.command, self.dataSize, self.reserved0, self.reserved1, self.magic, self.reserved2, self.reserved3, self.reserved4, self.subCommand, self.address, self.dataSizeKb, self.reserved5, self.reserved6, self.reserved7, self.reserved8, self.reserved9)
		#if I don't strip the last byte off, the linker seems to get bitchy and become unresponsive.
		return noePack("IIIIIIIIIIIIIIIBBB", self.command, self.dataSize, self.reserved0, self.reserved1, self.magic, self.reserved2, self.reserved3, self.reserved4, self.subCommand, self.address, self.dataSizeKb, self.reserved5, self.reserved6, self.reserved7, self.reserved8, self.reserved9 & 255, (self.reserved9 >> 8) & 255, (self.reserved9 >> 16) & 255)
	def fromBytes(self, bytes): #assumes input of 64 bytes, not 63
		values = noeUnpack("IIIIIIIIIIIIIIII", bytes)
		self.command = values[0]
		self.dataSize = values[1]
		self.reserved0 = values[2]
		self.reserved1 = values[3]
		self.magic = values[4]
		self.reserved2 = values[5]
		self.reserved3 = values[6]
		self.reserved4 = values[7]
		self.subCommand = values[8]
		self.address = values[9]
		self.dataSizeKb = values[10]
		self.reserved5 = values[11]
		self.reserved6 = values[12]
		self.reserved7 = values[13]
		self.reserved8 = values[14]
		self.reserved9 = values[15]
		
def getDeviceStatus(handle):
	statusCmd = F2ACommand()					
	statusCmd.command = F2A_CMD_GETINF
	noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, statusCmd.getBytes())
	return noesis.usbReadEndpointId(handle, F2A_EP_READ, F2A_RESPONSE_SIZE)

def chunkedRead(handle, dataSize):
	totalData = bytearray()
	for offset in range(0, dataSize // 1024):
		data = noesis.usbReadEndpointId(handle, F2A_EP_READ, 1024)
		if data:
			totalData += data
		else:
			break
	return totalData
	
def chunkedWrite(handle, data):
	writeSize = 0
	for offset in range(0, len(data) // 1024):
		chunkSize = noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, data[offset * 1024 : offset * 1024 + 1024])
		if chunkSize < 0:
			break
		writeSize += chunkSize
	return writeSize

def buttonAddMethod(noeWnd, controlId, wParam, lParam):
	imagePath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open Image", "Specify a GBA ROM image.", noesis.getSelectedFile(), None)
	if imagePath and os.path.exists(imagePath):
		listBox = noeWnd.getControlByIndex(noeWnd.romListIndex)
		listBox.addString(imagePath)
	return True

def buttonRemoveMethod(noeWnd, controlId, wParam, lParam):
	listBox = noeWnd.getControlByIndex(noeWnd.romListIndex)
	listIndex = listBox.getSelectionIndex()
	if listIndex < 0:
		print("No ROM selected.")
	else:
		listBox.removeString(listBox.getStringForIndex(listIndex))
	return True

def buttonWriteListMethod(noeWnd, controlId, wParam, lParam):
	listBox = noeWnd.getControlByIndex(noeWnd.romListIndex)
	fileCount = listBox.getStringCount()
	if fileCount <= 0:
		noesis.messagePrompt("There's nothing in the list.")
	else:
		cmd = F2ACommand()
		cmd.command = F2A_CMD_WRITEDATA
		cmd.subCommand = F2A_SUBCMD_WRITEROM
		cmd.magic = F2A_MAGIC
		cmd.address = F2A_TARGET_ROM
		for fileIndex in range(0, fileCount):
			filePath = listBox.getStringForIndex(fileIndex)
			with open(filePath, "rb") as f:
				data = f.read()
				#possible todo - bother to pad or check for expected size(s), check for ROM overrun
				cmd.dataSize = len(data)
				cmd.dataSizeKb = len(data) // 1024		
				noesis.usbWriteEndpointId(noeWnd.usbHandle, F2A_EP_WRITE, cmd.getBytes())
				if chunkedWrite(noeWnd.usbHandle, data) == len(data):
					cmd.address += len(data)
				
def buttonDumpSramMethod(noeWnd, controlId, wParam, lParam):
	dumpSize = noesis.userPrompt(noesis.NOEUSERVAL_INT, "Dump Size", "Enter size of data to dump.", "262144", None)
	if dumpSize:
		cmd = F2ACommand()
		cmd.command = F2A_CMD_READDATA
		cmd.subCommand = F2A_SUBCMD_READ
		cmd.magic = F2A_MAGIC
		cmd.address = F2A_TARGET_SRAM
		cmd.dataSize = dumpSize
		cmd.dataSizeKb = dumpSize // 1024
		noesis.usbWriteEndpointId(noeWnd.usbHandle, F2A_EP_WRITE, cmd.getBytes())
		sramData = chunkedRead(noeWnd.usbHandle, dumpSize)
		savePath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Save Image", "Specify path to save binary.", "", None)
		if savePath:
			with open(savePath, "wb") as f:
				f.write(sramData)
	return True

def buttonDumpRomMethod(noeWnd, controlId, wParam, lParam):
	dumpSize = noesis.userPrompt(noesis.NOEUSERVAL_INT, "Dump Size", "Enter size of data to dump.", "4194304", None)
	if dumpSize:
		cmd = F2ACommand()
		cmd.command = F2A_CMD_READDATA
		cmd.subCommand = F2A_SUBCMD_READ
		cmd.magic = F2A_MAGIC
		cmd.address = F2A_TARGET_ROM
		cmd.dataSize = dumpSize
		cmd.dataSizeKb = dumpSize // 1024
		noesis.usbWriteEndpointId(noeWnd.usbHandle, F2A_EP_WRITE, cmd.getBytes())
		sramData = chunkedRead(noeWnd.usbHandle, dumpSize)
		savePath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Save Image", "Specify path to save binary.", "", None)
		if savePath:
			with open(savePath, "wb") as f:
				f.write(sramData)
	return True
	

def buttonClearSramMethod(noeWnd, controlId, wParam, lParam):
	verifyIt = (user32.MessageBoxW(noeWnd.hWnd, "This will clear the contents of SRAM, destroying any save data on the cart. Are you sure?", "F2A Interface", noewin.MB_YESNO) == noewin.IDYES)
	if verifyIt:
		clearSize = noesis.userPrompt(noesis.NOEUSERVAL_INT, "Clear Size", "Enter size of data to clear.", "262144", None)
		if clearSize:
			cmd = F2ACommand()
			cmd.command = F2A_CMD_WRITEDATA
			cmd.subCommand = F2A_SUBCMD_WRITE
			cmd.magic = F2A_MAGIC
			cmd.address = F2A_TARGET_SRAM
			cmd.dataSize = clearSize
			cmd.dataSizeKb = clearSize // 1024
			noesis.usbWriteEndpointId(noeWnd.usbHandle, F2A_EP_WRITE, cmd.getBytes())
			chunkedWrite(noeWnd.usbHandle, bytearray([0] * clearSize))
	return True

def buttonWriteSramMethod(noeWnd, controlId, wParam, lParam):
	loadPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Load Image", "Specify binary image.", "", None)
	if loadPath:
		with open(loadPath, "rb") as f:
			data = f.read()
			cmd = F2ACommand()
			cmd.command = F2A_CMD_WRITEDATA
			cmd.subCommand = F2A_SUBCMD_WRITE
			cmd.magic = F2A_MAGIC
			cmd.address = F2A_TARGET_SRAM
			cmd.dataSize = len(data)
			cmd.dataSizeKb = len(data) // 1024
			noesis.usbWriteEndpointId(noeWnd.usbHandle, F2A_EP_WRITE, cmd.getBytes())
			chunkedWrite(noeWnd.usbHandle, data)
	
def createInterfaceWindow(noeWnd):
	noeWnd.setFont("Arial", 14)
	noeWnd.createStatic("ROM List", 16, 16, 80, 20)
	listIndex = noeWnd.createListBox(16, 36, 500, 188)
	noeWnd.romListIndex = listIndex
	
	noeWnd.createButton("Add", 16, 226, 96, 32, buttonAddMethod)
	noeWnd.createButton("Remove", 116, 226, 96, 32, buttonRemoveMethod)

	noeWnd.createButton("Write List", 528, 16, 96, 32, buttonWriteListMethod)	
	noeWnd.createButton("Dump SRAM", 528, 52, 96, 32, buttonDumpSramMethod)
	noeWnd.createButton("Dump ROM", 528, 88, 96, 32, buttonDumpRomMethod)	
	noeWnd.createButton("Write SRAM", 528, 124, 96, 32, buttonWriteSramMethod)
	noeWnd.createButton("Clear SRAM", 528, 160, 96, 32, buttonClearSramMethod)
	
def f2aToolMethod(toolIndex):
	noesis.logPopup()
	handle = noesis.usbOpenDevice(F2A_DEVINTGUID, F2A_CLASSGUID)
			
	riskIt = (user32.MessageBoxW(noesis.getWindowHandle(), "Found what appears to be the target F2A device. However, if this is not the correct device, the device could be damaged. Are you sure you want to continue?", "F2A Interface", noewin.MB_YESNO) == noewin.IDYES)
	if riskIt:
		if noesis.usbGetEndpointCount(handle) == 0:
			#try uploading the ez-usb firmware, then reconnect
			print("Endpoint count is 0, attempting vendor-specific EZ-USB FW upload.")
			
			#usbControlTransfer params = handle, data, requestType, request, index, value
			noesis.usbControlTransfer(handle, bytearray([0x01]), 0x40, 0xA0, 0, 0x7F92)

			fw = loadBin(F2A_EZUSBFW)
			chunkSize = 512
			for offset in range(0, len(fw) // chunkSize):
				chunkData = fw[offset * chunkSize : offset * chunkSize + chunkSize]
				noesis.usbControlTransfer(handle, chunkData, 0x40, 0xA0, 0, offset * chunkSize)			
			
			#upload complete
			noesis.usbControlTransfer(handle, bytearray([0x00]), 0x40, 0xA0, 0, 0x7F92)

			time.sleep(1)
			noesis.usbCloseDevice(handle)
			handle = None

			#spin here for a bit - uploading the firmware effectively reconnects the device with a different interface,
			#so it may take a little while for Windows to prepare it again.
			for attemptCount in range(0, F2A_RECONNECT_LIMIT):
				try:
					handle = noesis.usbOpenDevice(F2A_DEVINTGUID, F2A_CLASSGUID)
					print("Successfully re-opened device.")
					break
				except:
					print("Cannot re-open device. Waiting before trying again.")
					time.sleep(3)

		if handle is None:
			noesis.messagePrompt("Could not re-establish connection to device. Aborting.")
		elif noesis.usbGetEndpointCount(handle) != 5:
			noesis.messagePrompt("The device does not have the expected number of endpoints. Aborting.")
		else:
			noesis.usbSetEndpointTimeoutId(handle, F2A_EP_WRITE, F2A_EP_TIMEOUT)
			noesis.usbSetEndpointTimeoutId(handle, F2A_EP_READ, F2A_EP_TIMEOUT)

			response = getDeviceStatus(handle)
			while response[0] != F2A_STATUS_NOTREADY:
				tryAgain = (user32.MessageBoxW(noesis.getWindowHandle(), "Your GBA must be turned off to continue. Ready to try again?", "F2A Interface", noewin.MB_YESNO) == noewin.IDYES)
				if not tryAgain:
					break
				response = getDeviceStatus(handle)
			if response[0] == F2A_STATUS_NOTREADY:
				mb = loadBin(F2A_MULTIBOOT)
				
				bootCmd = F2ACommand()
				
				#if we don't do this bit, the linker gets angry again and stops accepting writes. particular to my hardware/firmware?
				bootCmd.fromBytes(response)
				bootCmd.command |= F2A_CMD_GETINF #keep the high bytes from the response data
				noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, bootCmd.getBytes())
				response = noesis.usbReadEndpointId(handle, F2A_EP_READ, F2A_RESPONSE_SIZE)
		
				noesis.usbSetEndpointTimeoutId(handle, F2A_EP_WRITE, F2A_EP_BOOTWAIT_TIMEOUT)

				readyToGo = (user32.MessageBoxW(noesis.getWindowHandle(), "After continuing (do not turn the GBA on before proceeding), you will connect your GBA, turn it on, and hold start+select during startup. Are you ready?", "F2A Interface", noewin.MB_YESNO) == noewin.IDYES)
				if readyToGo: #make sure they didn't turn it on prematurely
					response = getDeviceStatus(handle)
					if response[0] == F2A_STATUS_READY:
						readyToGo = False
						noesis.messagePrompt("You turned the GBA on prematurely. Aborting.")
				
				if readyToGo:
					#spin until we detect the GBA is on, then take a run at it
					response = getDeviceStatus(handle)
					while response[0] != F2A_STATUS_READY:
						time.sleep(0.1)
						response = getDeviceStatus(handle)
			
					bootCmd.command = F2A_CMD_MULTIBOOT1
					bootCmd.dataSize = 0
					bootCmd.reserved0 &= ~255
					noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, bootCmd.getBytes())
					bootCmd.command = F2A_CMD_MULTIBOOT2
					bootCmd.dataSize = len(mb) #my sniffing reveals this is actually 1024 bytes less than the data sent. writer bug?
					noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, bootCmd.getBytes())
				
					writeSize = chunkedWrite(handle, mb)
					
					print("MB write:", writeSize, "/", len(mb))
					if writeSize != len(mb):
						noesis.messagePrompt("Could not upload multiboot image. Aborting.")
					else:
						noesis.usbSetEndpointTimeoutId(handle, F2A_EP_WRITE, F2A_EP_TIMEOUT)
						
						#just write black to the background. sniffed out the original bg, or we could make our own, but eh.
						bgCmd = F2ACommand()
						bgCmd.magic = F2A_MAGIC
						bgCmd.address = F2A_TARGET_VRAM
						bgCmd.command = F2A_CMD_WRITEDATA
						bgCmd.subCommand = F2A_SUBCMD_WRITE
						bgCmd.dataSize = 76800 #packet sniffing shows this to be size & 0xFFFF, does it matter? (doesn't seem to)
						bgCmd.dataSizeKb = 76800 // 1024
						noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, bgCmd.getBytes())
						bgUploadSize = 0
						for offset in range(0, bgCmd.dataSizeKb):
							chunkSize = noesis.usbWriteEndpointId(handle, F2A_EP_WRITE, bytearray([0] * 1024))
							if chunkSize < 0:
								break
							bgUploadSize += chunkSize
						print("BG write:", bgUploadSize)
					
						time.sleep(1)
										
						noeWnd = noewin.NoeUserWindow("F2A Interface", "F2AWindowClass", 644, 300)
						#offset a bit into the noesis window
						noeWindowRect = noewin.getNoesisWindowRect()
						if noeWindowRect:
							windowMargin = 64
							noeWnd.x = noeWindowRect[0] + windowMargin
							noeWnd.y = noeWindowRect[1] + windowMargin
						if noeWnd.createWindow():
							noeWnd.usbHandle = handle
							createInterfaceWindow(noeWnd)
							noeWnd.doModal()
							
	if handle:
		noesis.usbCloseDevice(handle)
	return 0
	
