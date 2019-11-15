from inc_noesis import *
import data_quake2

def registerNoesisTypes():
	handle = noesis.register("Ys AIA", ".aia")
	noesis.setHandlerTypeCheck(handle, aiaCheckType)
	noesis.setHandlerLoadRGBA(handle, aiaLoadRGBA)
	return 1


class AIAUNP:
	def __init__(self, bs):
		self.unpIndexA = bs.readUInt()
		self.unpIndexB = bs.readUInt()
		self.unpCountA = bs.readUInt()
		self.unpCountB = bs.readUInt()


class AIARegion:
	def __init__(self, bs):
		self.imageOfs = bs.readUInt()
		self.palIndex = (bs.readUInt() & 32767)
		self.rectUV = (bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())
		self.rect = (bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort())


class AIAFile:
	def __init__(self):
		self.numPalettes = 0
		self.numImages = 0

	def parseHeader(self, bs):
		if bs.getSize() < 16:
			return 0
		if bs.readUInt() != 0x414941:
			return 0
		self.rvAMin = bs.readUByte()
		self.rvAMaj = bs.readUByte()
		self.rvB = bs.readUShort()
		self.numPalettes = bs.readUInt()
		self.numImages = bs.readUInt()
		if self.numPalettes <= 0 or self.numImages <= 0:
			return 0
			
		self.numRegions = bs.readUInt()
		self.width = bs.readUShort()
		self.height = bs.readUShort()
		if self.rvAMin >= 0x50:
			bs.readUShort()
			bs.readUShort()
		self.rvD = bs.readFloat()
		if self.rvAMin >= 0x50:
			self.rvE = bs.readFloat()
		self.imageDataSize = bs.readUInt()

		self.unpList = []
		for i in range(0, self.numImages):
			self.unpList.append(AIAUNP(bs))
		self.regionList = []
		for i in range(0, self.numRegions):
			self.regionList.append(AIARegion(bs))
			
		self.palettesOfs = bs.tell()
		self.imagesOfs = self.palettesOfs + self.numPalettes*256*4
		
		return 1


def aiaCheckType(data):
	aiaFile = AIAFile()
	bs = NoeBitStream(data)
	if aiaFile.parseHeader(bs) != 1:
		return 0
	return 1


def aiaLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	aiaFile = AIAFile()
	bs = NoeBitStream(data)
	if aiaFile.parseHeader(bs) != 1:
		return 0
	
	bs.seek(aiaFile.imagesOfs)
	encodedData = bs.readBytes(aiaFile.imageDataSize)
	
	for region in aiaFile.regionList:
		regionWidth = region.rect[2] - region.rect[0]
		regionHeight = region.rect[3] - region.rect[1]
		if regionWidth <= 0 or regionHeight <= 0:
			continue
			
		if regionWidth > aiaFile.width or regionHeight > aiaFile.height:
			noesis.doException("Region size should be less than main texture size")

		#read the palette
		bs.seek(aiaFile.palettesOfs + region.palIndex*256*4)
		pal = bs.readBytes(256*4)
		#convert from bgr to rgb, don't use alpha (masking is done as part of encoded pixel data)
		pal = rapi.imageDecodeRaw(pal, 256, 1, "b8g8r8p8")
			
		#decode the pixel data
		decodedData = rapi.callExtensionMethod("ys_aia_decode", encodedData[region.imageOfs:], pal, regionWidth, regionHeight)

		#create texture from aia size and blit the region to it
		imageData = noePack("BBBB", 0, 0, 0, 0)*aiaFile.width*aiaFile.height
		rapi.imageBlit32(imageData, aiaFile.width, aiaFile.height, region.rect[0], region.rect[1], decodedData, regionWidth, regionHeight, 0, 0)
	
		texName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName())) + "_frame" + repr(len(texList))
		tex = NoeTexture(texName, aiaFile.width, aiaFile.height, imageData, noesis.NOESISTEX_RGBA32)
		texList.append(tex)
		
	return 1

