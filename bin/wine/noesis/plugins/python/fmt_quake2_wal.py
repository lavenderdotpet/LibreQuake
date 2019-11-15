from inc_noesis import *
import data_quake2

def registerNoesisTypes():
	handle = noesis.register("Quake II WAL Texture", ".wal")
	noesis.setHandlerTypeCheck(handle, walCheckType)
	noesis.setHandlerLoadRGBA(handle, walLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, walWriteRGBA)

	noesis.addOption(handle, "-walanim", "<arg> is next anim frame name for wal", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-walname", "<arg> is internal name for wal", noesis.OPTFLAG_WANTARG)
	return 1

WAL_HEADER_SIZE = 100

class WalFile:
	def __init__(self, bs):
		self.bs = bs

	def parseImageInfo(self):
		bs = self.bs
		if bs.dataSize < WAL_HEADER_SIZE:
			return 0
		bs.seek(0, NOESEEK_ABS)
		self.name = noeStrFromBytes(bs.readBytes(32))
		self.width = bs.readInt()
		self.height = bs.readInt()
		if self.width <= 0 or self.height <= 0:
			return 0
		self.mipOfs = (bs.readInt(), bs.readInt(), bs.readInt(), bs.readInt())
		bs.seek(32, NOESEEK_REL) #anim chain name isn't preserved
		bs.seek(12, NOESEEK_REL) #flags/contents/value according to spec, but 0 in stock q2 data
		for ofs in self.mipOfs:
			if ofs < 0 or ofs >= bs.dataSize:
				return 0
		return 1

	def getMipData(self, mipLevel):
		bs = self.bs
		if mipLevel < 0 or mipLevel > 3:
			noesis.doException("Mip level out of range.")
		bs.seek(self.mipOfs[mipLevel], NOESEEK_ABS)
		mipSize = (self.width>>mipLevel)*(self.height>>mipLevel)
		return bs.readBytes(mipSize)

def walCheckType(data):
	wal = WalFile(NoeBitStream(data))
	if wal.parseImageInfo() == 0:
		return 0
	return 1

def walLoadRGBA(data, texList):
	wal = WalFile(NoeBitStream(data))
	if wal.parseImageInfo() == 0:
		return 0
	mipLevel = 0
	pixWidth = wal.width>>mipLevel
	pixHeight = wal.height>>mipLevel
	pix = wal.getMipData(mipLevel)
	pix = rapi.imageDecodeRawPal(pix, data_quake2.palette, pixWidth, pixHeight, 8, "r8g8b8a8")
	texList.append(NoeTexture(wal.name, pixWidth, pixHeight, pix, noesis.NOESISTEX_RGBA32))
	return 1

def walWriteRGBA(data, width, height, bs):
	texName = rapi.getLocalFileName(rapi.getExtensionlessName(rapi.getOutputName())) if noesis.optWasInvoked("-walname") == 0 else noesis.optGetArg("-walname")
	texName = noePadByteString(texName[:31], 32)
	bs.writeBytes(texName)
	bs.writeInt(width)
	bs.writeInt(height)
	pixData = bytes()
	for i in range(0, 4):
		mipW = max(width>>i, 1)
		mipH = max(height>>i, 1)
		mipPix = rapi.imageResample(data, width, height, mipW, mipH)
		mipPix = rapi.imageApplyPalette(mipPix, mipW, mipH, data_quake2.palette, 256)
		bs.writeInt(WAL_HEADER_SIZE + len(pixData))
		pixData += mipPix
	texName = "" if noesis.optWasInvoked("-walanim") == 0 else noesis.optGetArg("-walanim")
	texName = noePadByteString(texName[:31], 32)
	bs.writeBytes(texName)
	bs.writeInt(0)
	bs.writeInt(0)
	bs.writeInt(0)
	bs.writeBytes(pixData)
	return 1
