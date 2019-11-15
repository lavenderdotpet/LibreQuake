#Duke Nukem 3D grp extraction and .art image import.

from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Duke3D GRP Archive", ".grp")
	noesis.setHandlerExtractArc(handle, grpExtractArc)

	handle = noesis.register("Duke3D ART Images", ".art")
	noesis.setHandlerTypeCheck(handle, artCheckType)
	noesis.setHandlerLoadRGBA(handle, artLoadRGBA)

	return 1


class GrpEntry:
	def __init__(self, fileName, fileSize):
		self.name = fileName
		self.size = fileSize

#see if the file in question is a valid grp file
def grpExtractArc(fileName, fileLen, justChecking):
	if fileLen < 16:
		return 0
	with open(fileName, "rb") as f:
		try:
			id = noeStrFromBytes(f.read(12))
			if id != "KenSilverman":
				return 0
			numFiles = noeUnpack("<i", f.read(4))[0]
			if numFiles <= 0:
				return 0
		except:
			return 0

		if justChecking: #it's valid
			return 1

		print("Extracting", numFiles, "files.")
		files = []
		for i in range(0, numFiles):
			grpe = GrpEntry(noeStrFromBytes(f.read(12)), noeUnpack("<i", f.read(4))[0])
			files.append(grpe)
		for i in range(0, numFiles):
			print("Writing", files[i].name)
			fdata = f.read(files[i].size)
			rapi.exportArchiveFile(files[i].name, fdata)

	return 1


class ArtFile:
	def __init__(self, reader):
		self.reader = reader
		self.numTiles = -1
		self.tileStart = 0
		self.tileEnd = 0

	def isValid(self):
		if self.numTiles <= 0 or self.tileStart < 0 or self.tileEnd <= 0 or self.tileStart > self.tileEnd: #bad range
			return 0
		self.tileCount = (self.tileEnd-self.tileStart+1)
		if self.tileCount <= 0 or self.tileCount > 16384:
			return 0
		return 1

	def parseTileInfo(self):
		reader = self.reader
		if reader.dataSize <= 16:
			return 0
		reader.seek(0, NOESEEK_ABS)

		ver = reader.readInt()
		if ver == 0x4C495542 and reader.readInt() == 0x54524144: #skip over BUILDART if necessary
			ver = reader.readInt()
			
		if ver != 1: #bad version
			return 0

		self.numTiles = reader.readInt()
		self.tileStart = reader.readInt()
		self.tileEnd = reader.readInt()
		if self.isValid() == 0:
			return 0

		tileSizeFmt = "<%ih" % (self.tileCount)
		if reader.checkOverrun(self.tileCount<<1):
			return 0
		self.tileSizeX = reader.read(tileSizeFmt)
		if reader.checkOverrun(self.tileCount<<1):
			return 0
		self.tileSizeY = reader.read(tileSizeFmt)

		tileSizeFmt = "<%ii" % (self.tileCount)
		if reader.checkOverrun(self.tileCount<<2):
			return 0
		self.picAnim = reader.read(tileSizeFmt)

		self.picDataOfs = reader.tell()

		#make sure there's enough room for all the tiles in the file
		for i in range(0, self.tileCount):
			picSize = self.tileSizeX[i] * self.tileSizeY[i]
			if picSize < 0:
				return 0
			if reader.checkOverrun(picSize):
				return 0
			reader.seek(picSize, NOESEEK_REL)

		if reader.tell() != reader.dataSize:
			#print(reader.tell(), "!=", reader.dataSize)
			return 0 #doesn't appear to be the correct expected size for an art file
		return 1


#noesis passes in data as a bytearray
def artCheckType(data):
	af = ArtFile(NoeBitStream(data))
	if af.parseTileInfo() == 0:
		return 0

	return 1

def artLoadRGBA(data, texList):
	af = ArtFile(NoeBitStream(data))
	if af.parseTileInfo() == 0:
		return 0

	palFileName = rapi.getDirForFilePath(rapi.getInputName()) + "PALETTE.DAT"
	if (rapi.checkFileExists(palFileName)):
		palData = rapi.loadIntoByteArray(palFileName)
	else:
		palData = rapi.loadPairedFile("Duke3D Palette", ".dat")
		
	needCorrection = True
	for i in range(0, 768):
		if palData[i] >= 64:
			needCorrection = False
			break
	
	#correct the palette data, if necessary
	if needCorrection:
		for i in range(0, 768):
			palData[i] = (palData[i] << 2) | (palData[i] >> 4)

	af.reader.seek(af.picDataOfs, NOESEEK_ABS)
	for i in range(0, af.tileCount):
		picWidth = int(af.tileSizeX[i])
		picHeight = int(af.tileSizeY[i])
		picSize = picWidth * picHeight
		if picSize <= 0:
			continue

		picOfs = af.reader.tell()
		af.reader.seek(picSize, NOESEEK_REL)
		picDestSize = picWidth*picHeight*4
		picDest = noesis.allocBytes(picDestSize)

		for x in range(0, picWidth):
			for y in range(0, picHeight):
				clrIdx = int(af.reader.data[picOfs + y + x*picHeight]) * 3
				dstPix = (x + y*picWidth) * 4
				picDest[dstPix + 0] = palData[clrIdx + 0]
				picDest[dstPix + 1] = palData[clrIdx + 1]
				picDest[dstPix + 2] = palData[clrIdx + 2]
				picDest[dstPix + 3] = 0 if (clrIdx == 765) else 255

		texList.append(NoeTexture("arttex%04i" % i, picWidth, picHeight, picDest, noesis.NOESISTEX_RGBA32))
	return 1
