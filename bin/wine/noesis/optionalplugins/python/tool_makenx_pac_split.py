from inc_noesis import *
import os

DUMP_AS_IMAGES = False

def registerNoesisTypes():
	handle = noesis.registerTool("Split Maken-X PAC", spToolMethod, "Split Maken-X NJ PAC")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, spContextVisible)
	return 1

def spContextVisible(toolIndex, selectedFile):
	if selectedFile is None or os.path.exists(selectedFile) is not True:
		return 0
	lname = selectedFile.lower()
	if lname.endswith(".pac") is not True and lname.endswith(".pak") is not True:
		return 0
	return 1

def spTagForStr(str):
	r = 0
	shift = 0
	for c in str:
		r |= (ord(c)<<shift)
		shift += 8
	return r
	
def spToolMethod(toolIndex):
	fileName = noesis.getSelectedFile()
	
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	data = rapi.loadIntoByteArray(fileName)
	bs = NoeBitStream(data)
	
	nameBase = rapi.getExtensionlessName(fileName) + "_"
	
	try:
		noesis.logPopup()
		writtenFiles = 0
		doneParsing = False
		bsOut = NoeBitStream()
		supportedTags = (spTagForStr("NJTL"), spTagForStr("NJCM"), spTagForStr("POF0"), spTagForStr("CGTM"),
						spTagForStr("CMCK"), spTagForStr("NMDM"), spTagForStr("GBIX"), spTagForStr("PVRT"))
		if DUMP_AS_IMAGES is True:
			splitTag = spTagForStr("GBIX")
			dumpExt = ".pvr"
		else:
			splitTag = spTagForStr("NJTL")
			dumpExt = ".nj"
		while doneParsing is False:
			doneParsing = bs.checkEOF()
			curOfs = bs.tell()
			dataSize = 0
			if doneParsing is False:
				tag = bs.readUInt()
				if tag == 0: #skip by padding
					continue
				elif tag == 0x4649:
					bs.seek(60, NOESEEK_REL)
					continue
				elif tag in supportedTags:
					dataSize = bs.readUInt()
			bs.seek(dataSize, NOESEEK_REL)
				
			if doneParsing is True or tag == splitTag:
				if bsOut.getSize() > 0:
					writeName = nameBase + "%04i"%writtenFiles + dumpExt
					writtenFiles += 1
					with open(writeName, "wb") as f:
						print("Writing", writeName)
						f.write(bsOut.getBuffer())
						bsOut = NoeBitStream()
					
			if dataSize > 0:
				bsOut.writeBytes(data[curOfs:bs.tell()])
	except:
		print("Parsing exception. Aborting.")
		pass
		
	noesis.freeModule(noeMod)
	return 0
