from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Love Hina: Smile Again Images", ".pac")
	noesis.setHandlerTypeCheck(handle, hinaCheckRGBA)
	noesis.setHandlerLoadRGBA(handle, hinaLoadRGBA)
	return 1

class HinaImage:
	def __init__(self, offset, size, width, height, format):
		self.offset = offset
		self.size = size
		self.width = width
		self.height = height
		self.format = format
	
def hinaGetImages(bs):
	imageList = []
	bs.seek(0)
	numOfs = bs.readInt()
	ofsInfos = bs.read("<" + "i" * numOfs * 2)
	for i in range(0, numOfs):
		imageOffset = ofsInfos[i * 2]
		imageSize = ofsInfos[i * 2 + 1]
		if imageSize < 16:
			continue
		bs.seek(imageOffset)
		width = bs.readInt()
		height = bs.readInt()
		fmt = bs.readInt()
		expectedImageSize = width * height * 2
		if width < 4 or height < 4 or expectedImageSize != (imageSize - 12):
			#not image data, currently not handled
			continue
		imageList.append(HinaImage(bs.getOffset(), expectedImageSize, width, height, fmt))
	return imageList
	
def hinaCheckRGBA(data):
	#quick reject if data layout doesn't match
	bs = NoeBitStream(data)
	numOfs = bs.readInt()
	if numOfs <= 0 or bs.getOffset() + numOfs * 8 >= len(data):
		return 0
	bs.seek(4 + (numOfs - 1) * 8)
	lastOfs = bs.readInt()
	lastSize = bs.readInt()
	if (lastOfs + lastSize) != len(data):
		return 0
	#see if there are any loadable images if we got this far
	hinaImages = hinaGetImages(bs)
	if len(hinaImages) == 0:
		return 0
	return 1
	
def hinaLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	hinaImages = hinaGetImages(bs)
	for hinaImage in hinaImages:
		bs.seek(hinaImage.offset)
		fmtStr = "b5g5r5a1" if hinaImage.format == 2 else "b4g4r4a4"
		pix = rapi.imageDecodeRaw(bs.readBytes(hinaImage.size), hinaImage.width, hinaImage.height, fmtStr)
		texList.append(NoeTexture("hinatex", hinaImage.width, hinaImage.height, pix, noesis.NOESISTEX_RGBA32))
	return 1
