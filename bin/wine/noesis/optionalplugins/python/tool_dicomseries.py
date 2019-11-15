from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.registerTool("DICOM Series Finder", dsToolMethod, "Group DICOM files into series.")
	return 1

def dsToolMethod(toolIndex):
	if noesis.getWindowHandle():	
		noesis.logPopup()
		path = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select a folder to search.", noesis.getSelectedDirectory(), None)
	else:
		path = noesis.getSelectedFile()
		print("Got path argument:", path)
	if not path:
		return 0
		
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	try:
		#the list will be sorted by unique series, then by various criteria within the series in order to best order slices
		seriesList = rapi.callExtensionMethod("getDicomSeriesInDirectory", path)
		if seriesList:
			for entryIndex in range(0, len(seriesList)):
				entry = seriesList[entryIndex]
				print("Entry", entryIndex + 1, "/", len(seriesList))
				for key, val in entry.items():
					print("   ", key, "=", val)
		else:
			print("No DICOM files were found on the path:", path)
	except:
		print("Encountered an error while gathering series.")
		
	noesis.freeModule(noeMod)
		
	return 0
