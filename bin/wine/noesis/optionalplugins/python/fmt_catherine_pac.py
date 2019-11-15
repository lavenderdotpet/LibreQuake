from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Catherine PAC", ".pac")
	noesis.setHandlerExtractArc(handle, pacExtractArc)
	return 1

def pacExtractArc(fileName, fileLen, justChecking):
	with open(fileName, "rb") as f:
		if justChecking:
			return 1
		while f.tell() < fileLen:
			fileName = noeStrFromBytes(noeParseToZero(f.read(252)))
			fileSize = noeUnpack("<I", f.read(4))[0]
			if fileSize == 0:
				break
			print("Writing", fileName)
			rapi.exportArchiveFile(fileName, f.read(fileSize))
			f.seek(((fileSize+63) & ~63) - fileSize, 1)
	return 1
