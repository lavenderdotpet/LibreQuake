from inc_noesis import *
import os

def registerNoesisTypes():
	handle = noesis.registerTool("Apply to Preview", apToolMethod, "Applies the file to the preview scene.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, apContextVisible)
	return 1

def apContextVisible(toolIndex, selectedFile):
	if (selectedFile is None or
		(noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_MODELREAD) == 0 or
		noesis.isPreviewModuleRAPIValid() <= 0):
		return 0
	return 1
	
def apToolMethod(toolIndex):
	fileName = noesis.getSelectedFile()
	if fileName is None or os.path.exists(fileName) is not True:
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0

	try:
		noesis.setPreviewModuleRAPI()
		rapi.simulateDragAndDrop(fileName)
	except:
		noesis.messagePrompt("The selected file could not be applied to the preview scene.")
		return 0
		
	return 0
