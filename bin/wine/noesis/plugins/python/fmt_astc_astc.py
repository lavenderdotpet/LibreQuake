from inc_noesis import *

ASTC_FLIP = True #flip image on import by default

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("ASTC Image", ".astc")
	noesis.setHandlerTypeCheck(handle, astcCheckType)
	noesis.setHandlerLoadRGBA(handle, astcLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, astcWriteRGBA)
	return 1

ASTC_HEADER_ID = 0x5CA1AB13
	
class ASTCImage:
	def __init__(self, reader):
		self.reader = reader

	def parseImageInfo(self):
		bs = self.reader
		if bs.getSize() < 16:
			return -1
		bs.seek(0, NOESEEK_ABS)
		magic = bs.readUInt()
		if magic != ASTC_HEADER_ID:
			return -1
		self.blockWidth = bs.readByte()
		self.blockHeight = bs.readByte()
		self.blockDepth = bs.readByte()
		#not bothering to validate block sizes, let the decoder itself determine if it wants to handle what we give it
		self.imageWidth = bs.readByte() | (bs.readByte() << 8) | (bs.readByte() << 16)
		self.imageHeight = bs.readByte() | (bs.readByte() << 8) | (bs.readByte() << 16)
		self.imageDepth = bs.readByte() | (bs.readByte() << 8) | (bs.readByte() << 16)
		if self.imageWidth <= 0 or self.imageHeight <= 0 or self.imageDepth <= 0:
			return -1
		self.dataOffset = bs.tell()
		return 0
		
	def decode(self):
		bs = self.reader
		remainingBuffer = bs.getBuffer()[self.dataOffset:]
		data = rapi.callExtensionMethod("astc_decoderaw32", remainingBuffer, self.blockWidth, self.blockHeight, self.blockDepth, self.imageWidth, self.imageHeight, self.imageDepth)
		if ASTC_FLIP:
			data = rapi.imageFlipRGBA32(data, self.imageWidth, self.imageHeight, 0, 1)
		return data
	
def astcCheckType(data):
	astc = ASTCImage(NoeBitStream(data))
	if astc.parseImageInfo() != 0:
		return 0
	return 1

def astcLoadRGBA(data, texList):
	astc = ASTCImage(NoeBitStream(data))
	if astc.parseImageInfo() != 0:
		return 0
	texList.append(NoeTexture("astctex", astc.imageWidth, astc.imageHeight, astc.decode(), noesis.NOESISTEX_RGBA32))
	return 1

def astcWriteRGBA(data, width, height, bs):
	bs.writeUInt(ASTC_HEADER_ID)
	#possible todo - expose via noesis.addOption
	blockWidth = 8
	blockHeight = 8
	bs.writeByte(blockWidth)
	bs.writeByte(blockHeight)
	bs.writeByte(1) #block depth
	bs.writeByte(width & 255)
	bs.writeByte((width >> 8) & 255)
	bs.writeByte((width >> 16) & 255)
	bs.writeByte(height & 255)
	bs.writeByte((height >> 8) & 255)
	bs.writeByte((height >> 16) & 255)
	bs.writeByte(1) #depth
	bs.writeByte(0) #depth
	bs.writeByte(0) #depth
	if ASTC_FLIP: #would also be a good idea to expose this as an option
		data = rapi.imageFlipRGBA32(data, width, height, 0, 1)
	data = rapi.callExtensionMethod("astc_encoderaw32", data, blockWidth, blockHeight, 1, width, height, 1, 2)
	bs.writeBytes(data)
	return 1
