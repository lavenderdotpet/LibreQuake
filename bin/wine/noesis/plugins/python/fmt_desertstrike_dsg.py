from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Desert Strike Graphic", ".dsg")
	noesis.setHandlerTypeCheck(handle, dsgCheckType)
	noesis.setHandlerLoadRGBA(handle, dsgLoadRGBA)
	return 1


class DSGSpriteInfo:
	def __init__(self, reader):
		self.bgW = reader.readUShort()
		self.bgH = reader.readUShort()
		self.ofsX = reader.readUShort()
		self.ofsY = reader.readUShort()
		self.w = reader.readUShort()
		self.h = reader.readUShort()
		self.dataOfs = reader.readInt()
		self.data = None

class DSGFile:
	def __init__(self, reader):
		self.reader = reader
		self.imageColorScale = (4.0, 4.0, 4.0, 1.0)

	def parseImageInfo(self):
		bs = self.reader
		if bs.getSize() < 32:
			return 0
		idA = bs.readInt()
		idB = bs.readInt()
		if idA != 0x50415247 or idB != 0x53434948:
			return 0
		self.unkA = bs.readShort()
		self.unkB = bs.readShort()
		self.sizeA = bs.readInt()
		self.unkC = bs.readInt()
		self.sizeB = bs.readInt()
		self.unkC = bs.readInt()
		self.unkD = bs.readInt()
		self.picOfs = bs.tell()
		picA = bs.readInt()
		picB = bs.readInt()
		if picA != 0x54434950 or picB != 0x20455255: #picture
			if picA != 0x49525053 or picB != 0x20534554: #sprites
				return 0
		return 1

	def loadPalette(self):
		bs = self.reader
		palA = bs.readInt()
		palB = bs.readInt()
		if palA != 0x454C4150 or palB != 0x20455454:
			return None
		numColors = bs.readInt()
		palSize = bs.readInt()
		resvA = bs.readInt()
		resvB = bs.readInt()
		resvC = bs.readInt()
		resvD = bs.readInt()
		pal = bytearray()
		palNum = palSize // 3
		for i in range(0, palNum):
			palEntry = bs.readBytes(3)
			pal += palEntry + noePack("B", 255)
		pal += noePack("BBBB", 0, 0, 0, 0) #clear entry
		return pal

	def loadPicture(self):
		bs = self.reader
		cofs = bs.tell()
		picA = bs.readInt()
		picB = bs.readInt()
		if picA != 0x54434950 or picB != 0x20455255:
			bs.seek(cofs)
			return None
		unk = bs.readInt()
		width = bs.readUShort()
		height = bs.readUShort()
		pix = bs.readBytes(width*height)
		pal = self.loadPalette()
		if pal is None:
			bs.seek(cofs)
			return None
		data = rapi.imageDecodeRawPal(pix, pal, width, height, 8, "r8g8b8a8")
		data = rapi.imageScaleRGBA32(data, self.imageColorScale, width, height)
		tex = NoeTexture("dsgtex", width, height, data, noesis.NOESISTEX_RGBA32)
		tex.flags |= noesis.NTEXFLAG_FILTER_NEAREST | noesis.NTEXFLAG_WRAP_CLAMP
		return tex

	def loadSprites(self, texList):
		bs = self.reader
		cofs = bs.tell()
		sprA = bs.readInt()
		sprB = bs.readInt()
		if sprA != 0x49525053 or sprB != 0x20534554:
			return 0
		numSpr = bs.readUShort()
		useTransparency = bs.readUShort()
		unkB = bs.readInt()
		spriteInfos = []
		for i in range(0, numSpr):
			spriteInfos.append(DSGSpriteInfo(bs))
		bs.seek(cofs+self.sizeA)
		pal = self.loadPalette()
		if pal is None:
			return 0
		clearIdx = (len(pal) // 4) - 1
		for spriteInfo in spriteInfos:
			if spriteInfo.w <= 0 or spriteInfo.h <= 0:
				continue #seems to be a valid case

			width = spriteInfo.w
			height = spriteInfo.h

			bs.seek(cofs+spriteInfo.dataOfs)
			if useTransparency & 1:
				pix = bytearray()
				if width & 7:
					width += (8 - (width&7))

				while len(pix) < width*height:
					b = bs.readUByte()
					for i in range(0, 8):
						if b & (1<<(7-i)):
							pix += bs.readBytes(1)
						else:
							pix += noePack("B", clearIdx)
			else:
				pix = bs.readBytes(width*height)

			data = rapi.imageDecodeRawPal(pix, pal, width, height, 8, "r8g8b8a8")
			data = rapi.imageScaleRGBA32(data, self.imageColorScale, width, height)
			tex = NoeTexture("dsgtex", width, height, data, noesis.NOESISTEX_RGBA32)
			tex.flags |= noesis.NTEXFLAG_FILTER_NEAREST | noesis.NTEXFLAG_WRAP_CLAMP
			texList.append(tex)
		return 1

	def loadPictures(self, texList):
		bs = self.reader
		bs.seek(self.picOfs)
		while bs.getOffset() < bs.getSize():
			tex = self.loadPicture()
			if tex is not None:
				texList.append(tex)
			else:
				if self.loadSprites(texList) != 1:
					break

#noesis passes in data as a bytearray
def dsgCheckType(data):
	dsg = DSGFile(NoeBitStream(data))
	if dsg.parseImageInfo() == 0:
		return 0
	return 1

def dsgLoadRGBA(data, texList):
	dsg = DSGFile(NoeBitStream(data))
	if dsg.parseImageInfo() == 0:
		return 0

	dsg.loadPictures(texList)
	if len(texList) > 0:
		return 1

	return 0
