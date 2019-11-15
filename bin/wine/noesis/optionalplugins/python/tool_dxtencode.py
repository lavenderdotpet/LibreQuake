from inc_noesis import *
import os
import struct
import math

#alternately use _BC3 and _DXT5
DXT_ENCODE_FORMAT = noesis.NOE_ENCODEDXT_BC1
DXT_FOURCC_FORMAT = noesis.FOURCC_DXT1

DXT_GENERATE_MIPS = True

def registerNoesisTypes():
	handle = noesis.registerTool("Encode DXT", dxtEncodeToolMethod, "Encode DXT for image.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, dxtEncodeContextVisible)
	
	return 1

def dxtEncodeContextVisible(toolIndex, selectedFile):
	if selectedFile is None or (noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_IMGREAD) == 0:
		return 0
	return 1

def dxtEncodeToolMethod(toolIndex):
	srcName = noesis.getSelectedFile()
	if srcName is None or os.path.exists(srcName) is not True:
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0

	srcTex = noesis.loadImageRGBA(srcName)
	if srcTex is None:
		noesis.messagePrompt("Failed to load image data from file.")
		return 0

	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	dstName = os.path.splitext(srcName)[0] + "_dxt.dds"

	rgbaPix = rapi.imageGetTexRGBA(srcTex)

	mipCount = 0
	dxtData = rapi.imageEncodeDXT(rgbaPix, 4, srcTex.width, srcTex.height, DXT_ENCODE_FORMAT)
	if DXT_GENERATE_MIPS and (srcTex.width & 3) == 0 and (srcTex.height & 3) == 0: #generate mips if this is a proper block-aligned image
		lastMipW = srcTex.width
		lastMipH = srcTex.height
		mipPix = rgbaPix
		mipCount = int(math.log(max(srcTex.width, srcTex.height), 2)) + 1
		for i in range(1, mipCount):
			mipW = max(srcTex.width >> i, 1)
			mipH = max(srcTex.height >> i, 1)
			mipPix = rapi.imageResampleBox(mipPix, lastMipW, lastMipH, mipW, mipH)
			dxtMip = rapi.imageEncodeDXT(mipPix, 4, mipW, mipH, DXT_ENCODE_FORMAT)
			dxtData += dxtMip #append the dxt-encoded mip to the dxt data
			lastMipW = mipW
			lastMipH = mipH
	
	ddsData = rapi.imageGetDDSFromDXT(dxtData, srcTex.width, srcTex.height, mipCount, DXT_FOURCC_FORMAT)

	noesis.freeModule(noeMod)

	with open(dstName, "wb") as f:
		f.write(ddsData)
	
	noesis.openFile(dstName)
	return 0
	