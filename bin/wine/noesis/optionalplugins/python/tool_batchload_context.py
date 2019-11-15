from inc_noesis import *
import os

#MERGE_BONES
#0 = no collapsing
#1 = collapse by name
#2 = collapse by name and reapply relative transforms
#3 = collapse by name and reapply relative transforms, retransforming geometry as well
#4 = 3, but transpose relative transform
MERGE_BONES = 0

globalLoadList = []

def registerNoesisTypes():
	handle = noesis.registerTool("Batch Load - Queue File", batchLoadAddToolMethod, "Queue the file in the batch load list")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, batchLoadAddContextVisible)

	handle = noesis.registerTool("Batch Load - List", batchLoadListToolMethod, "List all queued files")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, batchLoadListContextVisible)
	
	handle = noesis.registerTool("Batch Load - Load", batchLoadLoadToolMethod, "Load all queued files")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, batchLoadListContextVisible)
	
	handle = noesis.registerTool("Batch Load - Clear", batchLoadClearToolMethod, "Clear all queued files")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, batchLoadListContextVisible)
	return 1

def batchLoadAddContextVisible(toolIndex, selectedFile):
	if selectedFile is None or (noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_MODELREAD) == 0:
		return 0
	return 1

def batchLoadListContextVisible(toolIndex, selectedFile):
	global globalLoadList
	if len(globalLoadList) == 0:
		return 0
	return 1
	
def batchLoadLoadToolMethod(toolIndex):
	global globalLoadList
	if len(globalLoadList) == 0:
		noesis.messagePrompt("No files are queued up.")
		return 0
		
	dstFilePath = noesis.getScenesPath() + "batchload.noesis"
	with open(dstFilePath, "w") as f:
		f.write("NOESIS_SCENE_FILE\r\nversion 1\r\nphysicslib		\"\"\r\ndefaultAxis		\"0\"\r\n\r\n")
		numObj = 0
		for fileName in globalLoadList:
			f.write("object\r\n{\r\n")
			f.write("	name		\"node" + "%i"%numObj + "\"\r\n")
			f.write("	model		\"" + fileName + "\"\r\n")
			if numObj > 0:
				f.write("	mergeTo		\"node0\"\r\n")
				if MERGE_BONES != 0:
					f.write("	mergeBones	\"" + "%i"%MERGE_BONES + "\"\r\n")
			f.write("}\r\n")
			numObj += 1
	if noesis.openAndRemoveTempFile(dstFilePath) is not True:
		noesis.messagePrompt("Could not open merged model file!")

	#clear the queue after generating the .noesis file
	globalLoadList = []
	return 0

def batchLoadAddToolMethod(toolIndex):
	global globalLoadList
	selectedFile = noesis.getSelectedFile()
	if selectedFile is not None:
		globalLoadList.append(selectedFile)
	return 0
		
def batchLoadClearToolMethod(toolIndex):
	global globalLoadList
	globalLoadList = []
	return 0

def batchLoadListToolMethod(toolIndex):
	global globalLoadList
	str = "Files queued for Batch Load:\r\n"
	for fileName in globalLoadList:
		str += fileName + "\r\n"
	noesis.messagePrompt(str)
	return 0
