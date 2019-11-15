#This format is used in Soldier of Fortune, and possibly some other raven games.
#Exported files have been tested to work ingame in SoF.

from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("M32 Image", ".m32")
	noesis.setHandlerTypeCheck(handle, m32CheckType)
	noesis.setHandlerLoadRGBA(handle, m32LoadRGBA)
	noesis.setHandlerWriteRGBA(handle, m32WriteRGBA)

	noesis.addOption(handle, "-m32detail", "<arg> is internal detail tex for m32", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-m32name", "<arg> is internal name for m32", noesis.OPTFLAG_WANTARG)
	return 1


class M32File:
	def __init__(self, reader):
		self.reader = reader

	def parseImageInfo(self):
		reader = self.reader
		if reader.dataSize <= 708:
			return 0
		reader.seek(0, NOESEEK_ABS)
		ver = reader.readInt()
		if ver != 4: #bad version
			return 0
		reader.seek(512, NOESEEK_REL) #skip over strings
		self.mipWidths = reader.read("<16i")
		self.mipHeights = reader.read("<16i")
		self.mipOfs = reader.read("<16i")
		if self.mipOfs[0] <= 0:
			return 0
		for i in range(0, 16):
			if self.mipOfs[i] >= reader.dataSize or self.mipWidths[i] > 4096 or self.mipWidths[i] < 0 or self.mipHeights[i] > 4096 or self.mipHeights[i] < 0:
				return 0
		return 1

#noesis passes in data as a bytearray
def m32CheckType(data):
	m32 = M32File(NoeBitStream(data))
	if m32.parseImageInfo() == 0:
		return 0
	return 1

#texList should be filled with NoeTexture objects, which will be read by Noesis
def m32LoadRGBA(data, texList):
	m32 = M32File(NoeBitStream(data))
	if m32.parseImageInfo() == 0:
		return 0
	#just grab the first mip in raw rgba form
	picDestSize = m32.mipWidths[0]*m32.mipHeights[0]*4
	texList.append(NoeTexture("m32tex", m32.mipWidths[0], m32.mipHeights[0], data[m32.mipOfs[0]:m32.mipOfs[0]+picDestSize], noesis.NOESISTEX_RGBA32))
	return 1

#data is a width*height*4 bytearray of rgba (32bpp) pixels
def m32WriteRGBA(data, width, height, bs):
	bs.writeBytes(noePack("<1i", 4))

	texName = rapi.getLocalFileName(rapi.getExtensionlessName(rapi.getOutputName())) if noesis.optWasInvoked("-m32name") == 0 else noesis.optGetArg("-m32name")
	texName = noePadByteString(texName, 128)
	bs.writeBytes(texName)

	#next 3 entries are unused
	bs.writeBytes(bytes(0 for i in range(0, 128*3)))

	#fill in and write the info arrays
	imgWidths = [0]*16
	imgHeights = [0]*16
	imgOfs = [0]*16
	w = width
	h = height
	ofs = 968 #start offset of the first mipmap
	for i in range(0, 16):
		imgWidths[i] = int(max(w, 1))
		imgHeights[i] = int(max(h, 1))
		imgOfs[i] = int(ofs)
		if w <= 1 and h <= 1 and i > 0:
			break
		ofs += imgWidths[i]*imgHeights[i]*4
		w /= 2
		h /= 2
	bs.writeBytes(noePack("<16i", *imgWidths))
	bs.writeBytes(noePack("<16i", *imgHeights))
	bs.writeBytes(noePack("<16i", *imgOfs))

	#detail texture properties and scaling factors. not 100% sure what all of it means.
	bs.writeBytes(noePack("<1i", 0x13000000))
	bs.writeBytes(noePack("<2i", 0, 0))
	bs.writeBytes(noePack("<2f", 1.0, 1.0)) #image scale
	bs.writeBytes(noePack("<1i", 1))
	if noesis.optWasInvoked("-m32detail"): #use this string if user specified, otherwise just write the base name again
		texName = noePadByteString(noesis.optGetArg("-m32detail"), 128)
	bs.writeBytes(texName)
	bs.writeBytes(noePack("<2f", 1.0, 1.0)) #typically this is higher than the first scale, it's the detail texture scale
	bs.writeBytes(noePack("<3i", 0, 0, 0))
	bs.writeBytes(noePack("<2i", 774, 768))
	bs.writeBytes(bytes(0 for i in range(0, 80)))

	#now write the image data
	for i in range(0, 16):
		if imgOfs[i] <= 0:
			break
		mipData = rapi.imageResample(data, width, height, imgWidths[i], imgHeights[i])
		bs.writeBytes(mipData)

	return 1
