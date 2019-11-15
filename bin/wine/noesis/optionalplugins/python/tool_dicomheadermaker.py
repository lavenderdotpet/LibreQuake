from inc_noesis import *
import os

def registerNoesisTypes():
	handle = noesis.registerTool("DICOM Header Maker", dicomToolMethod, "Put a raw implicit VR header on a headless DICOM file.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, dicomContextVisible)
	return 1

def dicomContextVisible(toolIndex, selectedFile):
	if selectedFile is None or os.path.splitext(selectedFile)[1].lower() != ".dcm":
		return 0
	return 1

def dicomToolMethod(toolIndex):
	srcPath = noesis.getSelectedFile()
	with open(srcPath, "rb") as fSrc:
		srcData = fSrc.read()
		if len(srcData) >= 132 and noeUnpack("<I", srcData[128:132])[0] == 0x4D434944:
			noesis.messagePrompt("DICOM file already has a DICOM header.")
		else:
			dstPathDefault = os.path.splitext(srcPath)[0] + "_header.dcm"	
			dstPath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save File", "Select destination for new DICOM file.", dstPathDefault, None)
			if dstPath is not None:	
				with open(dstPath, "wb") as fDst:
					fDst.write(noePack("B"*128, *[0]*128))
					fDst.write(bytearray("DICM", "ASCII"))
					#denote group 2 length of 18 + 8
					fDst.write(noePack("BBBBBBBBI", 0x02, 0x00, 0x00, 0x00, 0x55, 0x4C, 0x04, 0x00, 26))					
					#transfer syntax UID header for 18 byte (1 byte pad to even) string
					fDst.write(noePack("BBBBBBBB", 0x02, 0x00, 0x10, 0x00, 0x55, 0x49, 0x12, 0x00))
					fDst.write(bytearray("1.2.840.10008.1.2", "ASCII"))
					fDst.write(noePack("B", 0))
					fDst.write(srcData)
	return 0
