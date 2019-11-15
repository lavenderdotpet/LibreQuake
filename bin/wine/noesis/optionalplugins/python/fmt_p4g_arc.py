from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("P4G Vita Archive", ".arc")
	noesis.setHandlerExtractArc(handle, p4gExtractArc)
	return 1
	
def p4gExtractArc(fileName, fileLen, justChecking):
	if fileLen < 40:
		return 0
		
	with open(fileName, "rb") as f:
		if justChecking:
			return 1

		fileCount = noeUnpack("<I", f.read(4))[0]
		for i in range(0, fileCount):
			entryName = noeStrFromBytes(f.read(32))
			entrySize = noeUnpack("<I", f.read(4))[0]
			entryData = f.read(entrySize)
			print("Writing", entryName)
			rapi.exportArchiveFile(entryName, entryData)
		return 1
		
	return 0
