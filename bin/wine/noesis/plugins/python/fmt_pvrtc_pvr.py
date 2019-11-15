from inc_noesis import *
import os

#set to True in order to enable the pvr reordering context menu tools
ENABLE_PVR_REORDERING_TOOL = False

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("PVRTC Image", ".pvr")
	noesis.setHandlerTypeCheck(handle, pvrCheckType)
	noesis.setHandlerLoadRGBA(handle, pvrLoadRGBA)
	if ENABLE_PVR_REORDERING_TOOL:
		toolHandle = noesis.registerTool("PVR to Morton", pvrToMortonToolMethod, "Converts PVR block order from linear to Morton.")
		noesis.setToolFlags(toolHandle, noesis.NTOOLFLAG_CONTEXTITEM)
		noesis.setToolVisibleCallback(toolHandle, pvrReorderContextVisible)
		toolHandle = noesis.registerTool("PVR to Linear", pvrToLinearToolMethod, "Converts PVR block order from Morton to linear.")
		noesis.setToolFlags(toolHandle, noesis.NTOOLFLAG_CONTEXTITEM)
		noesis.setToolVisibleCallback(toolHandle, pvrReorderContextVisible)
	
	return 1


class PVRTCImage:
	def __init__(self, reader):
		self.reader = reader

	def parseV2(self):
		self.reader.seek(4, NOESEEK_ABS)
		self.w = self.reader.readInt()
		self.h = self.reader.readInt()
		self.fmt = self.reader.readInt()
		self.flags = self.reader.readInt()
		self.isPVR2 = False
		#pvr 2bpp = 24, pvr 4bpp = 25
		#pvr2 bpp = 28, pvr2 4bpp = 29
		pixelFormat = self.flags & 255
		if pixelFormat == 28 or pixelFormat == 29:
			self.isPVR2 = True #pvr2
		elif pixelFormat != 24 and pixelFormat != 25:
			return 0 #not supported
		self.dataSize = self.reader.readInt()
		self.bpp = self.reader.readInt()
		self.reader.seek(44, NOESEEK_ABS)
		if self.reader.readInt() != 0x21525650: #"PVR!"
			return 0
		if self.flags & 0x10000:
			self.flip = 1
		self.dataOfs = 52
		return 1

	def parseV3(self):
		if self.reader.getSize() < 68:
			return 0
		self.reader.seek(4, NOESEEK_ABS)
		self.asz = self.reader.readInt()
		self.fmt = self.reader.readInt()
		
		self.isPVR2 = False
		if self.fmt == 0 or self.fmt == 1:
			self.bpp = 2
		elif self.fmt == 2 or self.fmt == 3:
			self.bpp = 4
		elif self.fmt == 4:
			self.bpp = 2
			self.isPVR2 = True
		elif self.fmt == 5:
			self.bpp = 4
			self.isPVR2 = True
		else:
			return 0
		self.fmtTag = self.reader.readInt()
		self.colorSpace = self.reader.readInt()
		self.chanType = self.reader.readInt()
		
		#self.reader.seek(24, NOESEEK_ABS)
		self.h = self.reader.readInt()
		self.w = self.reader.readInt()
		self.depth = self.reader.readInt()
		self.surfCount = self.reader.readInt()
		self.faceCount = self.reader.readInt()
		self.mipCount = self.reader.readInt()
		
		#self.reader.seek(48, NOESEEK_ABS)
		self.metaLen = self.reader.readInt()
		if self.metaLen > 4:
			metaDataEnd = self.reader.getOffset() + self.metaLen
			while self.reader.getOffset() < (metaDataEnd - 4):
				metaFourCC = self.reader.readInt()
				if metaFourCC != 0x3525650:
					break
				metaKey = self.reader.readInt()
				metaKeySize = self.reader.readInt()
				metaKeyData = self.reader.readBytes(metaKeySize)
				if metaKey == 3: #logical orientation - todo, support flipping other axes
					if metaKeyData[1] != 0:
						self.flip = 1
				
		self.dataOfs = 52+self.metaLen
		return 1

	def parseImageInfo(self):
		if self.reader.getSize() < 52:
			return 0

		self.flip = 0
		self.ver = 0
		self.rawVer = self.reader.readInt()
		if self.rawVer == 52:
			self.ver = 2
			return self.parseV2()
		elif self.rawVer == 0x3525650:
			self.ver = 3
			return self.parseV3()

		return 0

	def decode(self):
		self.reader.seek(self.dataOfs, NOESEEK_ABS)
		d = 4 if self.bpp == 2 else 2
		decodeFlags = noesis.PVRTC_DECODE_PVRTC2 if self.isPVR2 else 0
		
		#not sure if this is correct, but v3 pvrtc2's produced by PvrTexTool seem to not be morton ordered
		if self.ver >= 3 and self.isPVR2:
			decodeFlags |= noesis.PVRTC_DECODE_LINEARORDER
		
		#this seems to be PvrTexTool's decoding behavior, but it's wrong - verified on hardware with the SGX543
		#if self.bpp == 4 and self.isPVR2:
		#	decodeFlags |= noesis.PVRTC_DECODE_PVRTC2_NO_OR_WITH_0_ALPHA
		
		r = rapi.imageDecodePVRTC(self.reader.readBytes((self.w*self.h) // d), self.w, self.h, self.bpp, decodeFlags)
		if self.flip == 1:
			r = rapi.imageFlipRGBA32(r, self.w, self.h, 0, 1)
		return r


#noesis passes in data as a bytearray
def pvrCheckType(data):
	pvr = PVRTCImage(NoeBitStream(data))
	if pvr.parseImageInfo() != 1:
		return 0
	if pvr.bpp != 2 and pvr.bpp != 4:
		return 0 #not supported in this script
	return 1

#texList should be filled with NoeTexture objects, which will be read by Noesis
def pvrLoadRGBA(data, texList):
	pvr = PVRTCImage(NoeBitStream(data))
	if pvr.parseImageInfo() != 1:
		return 0

	texList.append(NoeTexture("pvrtex", pvr.w, pvr.h, pvr.decode(), noesis.NOESISTEX_RGBA32))
	return 1

#see if the pvr reorder context tool should be visible
def pvrReorderContextVisible(toolIndex, selectedFile):
	if (selectedFile is None or
		os.path.splitext(selectedFile)[1].lower() != ".pvr" or
		(noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_IMGREAD) == 0):
		return 0
	return 1

#perform the block order change
def pvrReorderBlocks(reorderMethod):
	srcPath = noesis.getSelectedFile()
	if srcPath is None or os.path.exists(srcPath) is not True:
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0

	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	with open(srcPath, "rb") as fSrc:
		pvrData = fSrc.read()
		pvr = PVRTCImage(NoeBitStream(pvrData))
		if pvr.parseImageInfo() == 1:
			pvrImageData = pvrData[pvr.dataOfs:]
			pvrImageDataSize = len(pvrImageData)
			blockW = 8 if pvr.bpp == 2 else 4
			blockH = 4
			blocksW = pvr.w // blockW
			blocksH = pvr.h // blockH
			#possible todo - support individual mips/faces
			pvrImageData = reorderMethod(pvrImageData, blocksW, blocksH, 8, 2)
			
			dstPathDefault = os.path.splitext(srcPath)[0] + "_reordered.pvr"
			dstPath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save File", "Select destination for the reordered PVR file.", dstPathDefault, None)
			if dstPath is not None:	
				with open(dstPath, "wb") as fDst:
					fDst.write(pvrData[:pvr.dataOfs])
					fDst.write(pvrImageData)
	noesis.freeModule(noeMod)
	return 0

#to morton method
def pvrToMortonToolMethod(toolIndex):
	return pvrReorderBlocks(rapi.imageToMortonOrder)

#to linear method
def pvrToLinearToolMethod(toolIndex):
	return pvrReorderBlocks(rapi.imageFromMortonOrder)
