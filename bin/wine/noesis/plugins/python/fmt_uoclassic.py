#UO Classic Client formats
#thanks to http://uo.stratics.com/heptazane/fileformats.shtml

from inc_noesis import *
import time
import os
import re

UO_NEW_MULTI_VER = True #set to false to load legacy multi files

def registerNoesisTypes():
	handle = noesis.register("Ultima Online UOP Archive", ".uop")
	noesis.setHandlerExtractArc(handle, extractUOP)
	
	handle = noesis.register("Ultima Online MUL Archive", ".mul")
	noesis.setHandlerExtractArc(handle, extractMUL)
	
	handle = noesis.register("Ultima Online Anim", ".uo_anim")
	noesis.setHandlerTypeCheck(handle, uoAnimCheckType)
	noesis.setHandlerLoadRGBA(handle, uoAnimLoadRGBA)

	handle = noesis.register("Ultima Online Gump", ".uo_gump")
	noesis.setHandlerTypeCheck(handle, uoGumpCheckType)
	noesis.setHandlerLoadRGBA(handle, uoGumpLoadRGBA)

	handle = noesis.register("Ultima Online Tex", ".uo_tex")
	noesis.setHandlerTypeCheck(handle, uoTexCheckType)
	noesis.setHandlerLoadRGBA(handle, uoTexLoadRGBA)

	handle = noesis.register("Ultima Online Art Tile", ".uo_art_tile")
	noesis.setHandlerTypeCheck(handle, uoArtTileCheckType)
	noesis.setHandlerLoadRGBA(handle, uoArtTileLoadRGBA)

	handle = noesis.register("Ultima Online Multi-Tile", ".uo_multi_tile")
	noesis.setHandlerTypeCheck(handle, uoMultiTileCheckType)
	noesis.setHandlerLoadRGBA(handle, uoMultiTileLoadRGBA)

	handle = noesis.register("Ultima Online Map", ".uo_map")
	noesis.setHandlerTypeCheck(handle, uoMapCheckType)
	noesis.setHandlerLoadRGBA(handle, uoMapLoadRGBA)
	
	return 1

class UOPEntry:
	def __init__(self, explicitId, nameHash, dataOfs, compType, readSize, decompSize):
		self.explicitId = explicitId
		self.nameHash = nameHash
		self.dataOfs = dataOfs
		self.compType = compType
		self.readSize = readSize
		self.decompSize = decompSize
	def Compare(a, b):
		val = a.explicitId - b.explicitId
		if val == 0:
			val = a.dataOfs - b.dataOfs
		return val
	
def parseUOPEntries(f, baseName, blockOfs, totalFileCount):
	uopEntries = []
	#this could work for maps, but we don't need it since we're able to derive the index from the hash.
	#if hashes are failing for maps, enabling it will probably fix the problem. otherwise the map slices
	#will end up out of order.
	useSortKey = False #baseName.startswith("map")

	while blockOfs != 0 and len(uopEntries) < totalFileCount:
		f.seek(blockOfs, os.SEEK_SET)
		fileCount, blockOfs = noeUnpack("<IQ", f.read(12))
		blockFileData = f.read(34 * fileCount)
		for fileIndex in range(0, fileCount):
			entryData = blockFileData[34 * fileIndex : 34 * fileIndex + 34]
			hdrOfs, hdrSize, compSize, decompSize, nameHash, dataHash, compType = noeUnpack("<QIIIQIH", entryData)
			f.seek(hdrOfs, os.SEEK_SET)
			dataType, dataOfs = noeUnpack("<HH", f.read(4))
			f.seek(dataOfs, os.SEEK_CUR)
			readSize = compSize if compSize > 0 else decompSize

			if useSortKey:
				sortKey = noeUnpack("<I", f.read(4))[0] // 4096 if useSortKey else 0
				f.seek(-4, os.SEEK_CUR)

			if readSize > 0:
				explicitId = sortKey if useSortKey else rapi.callExtensionMethod("uo_id_for_hash", nameHash)					
				uopEntry = UOPEntry(explicitId, nameHash, f.tell(), compType, readSize, decompSize)
				uopEntries.append(uopEntry)
				if len(uopEntries) >= totalFileCount:
					break
	return uopEntries

def extractUOP(fileName, fileLen, justChecking):
	if fileLen < 28:
		return 0

	with open(fileName, "rb") as f:
		id, ver, unk, blockOfs, maxFilesPerBlock, totalFileCount = noeUnpack("<IIIQII", f.read(28))
		if id != 0x50594D: #"MYP\0"
			return 0
		if ver < 4 or ver > 5:
			return 0
		if totalFileCount == 0:
			return 0
			
		if justChecking:
			return 1
			
		baseName = rapi.getExtensionlessName(rapi.getLocalFileName(fileName)).lower()
		
		#the typical form used is:
		#hash = rapi.callExtensionMethod("uo_hash_war", "build/uop/########.*", 0xDEADBEEF)
		#however, many uop's use explicit names and/or different extensions. for our purposes we only care about trying to preserve id's.
		#this will at least cover everything in artLegacyMUL (at the moment), so that multi's can map correctly.
		print("Priming hash...")
		rapi.callExtensionMethod("uo_reset_hash")
		rapi.callExtensionMethod("uo_prime_hash", "build/" + baseName + "/", ".bin", 0, 131072, 8, 0xDEADBEEF)
		rapi.callExtensionMethod("uo_prime_hash", "build/" + baseName + "/", ".dds", 0, 131072, 8, 0xDEADBEEF)
		rapi.callExtensionMethod("uo_prime_hash", "build/" + baseName + "/", ".tga", 0, 131072, 8, 0xDEADBEEF)
		rapi.callExtensionMethod("uo_prime_hash", "build/" + baseName + "/", ".dat", 0, 131072, 8, 0xDEADBEEF)
		#explicit hashes can be associated with id's like this:
		#rapi.callExtensionMethod("uo_hash_for_id", "build/whatever/balls.bin", 0xDEADBEEF, 1337)
		
		uopEntries = parseUOPEntries(f, baseName, blockOfs, totalFileCount) 

		if len(uopEntries) == 0:
			print("No exportable files found in UOP.")
			return 1

		uopEntries = sorted(uopEntries, key=noeCmpToKey(UOPEntry.Compare))
		
		#create index and mul data bytearrays, then just export them as archive files (convenience)
		idxData = bytearray()
		idxDataNonExplicit = bytearray()
		mulData = bytearray()
		for uopEntry in uopEntries:
			f.seek(uopEntry.dataOfs, os.SEEK_SET)
			srcData = f.read(uopEntry.readSize)
			if uopEntry.compType == 1:
				dstData = rapi.decompInflate(srcData, uopEntry.decompSize)
			else:
				dstData = srcData					
			print("Writing data at", uopEntry.dataOfs, "-", "id:", uopEntry.explicitId, "size:", len(dstData), "hash:", uopEntry.nameHash)
			packedIdx = noePack("III", len(mulData), len(dstData), 0)
			if uopEntry.explicitId != 0xFFFFFFFF:
				desiredOfs = uopEntry.explicitId * 12
				if len(idxData) <= desiredOfs:
					#pad out up to the desired entry
					padCount = ((desiredOfs - len(idxData)) + 1) // 12
					idxData += noePack("III", 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF) * padCount
				idxData[desiredOfs : desiredOfs + 12] = packedIdx
			else:
				#make sure anything with a non-explicit id gets tacked onto the end
				idxDataNonExplicit += packedIdx
			mulData += dstData

		print("Writing " + baseName + ".idx and .mul...")
		if baseName.startswith("map"):
			print("Exporting MUL data as uo_map due to filename.")
			uoMapHeader = noePack("II", len(idxData) + len(idxDataNonExplicit), len(mulData))
			rapi.exportArchiveFile(baseName + ".uo_map", uoMapHeader + idxData + idxDataNonExplicit + mulData)
		else:
			rapi.exportArchiveFile(baseName + ".idx", idxData + idxDataNonExplicit)
			rapi.exportArchiveFile(baseName + ".mul", mulData)
		
		return 1

	return 0

def findIDXForMUL(baseName):
	testName = baseName + ".idx"
	if os.path.exists(testName):
		return testName
	testName = baseName + "idx.mul"
	if os.path.exists(testName):
		return testName
		
	path, name = os.path.split(baseName)
	if name.startswith("statics"):
		testName = path + "/" + name.replace("statics", "staidx") + ".mul"
		if os.path.exists(testName):
			return testName
	elif name.startswith("texmaps"):
		testName = path + "/" + name.replace("texmaps", "texidx") + ".mul"
		if os.path.exists(testName):
			return testName
	elif name == "gumpart":
		testName = path + "/" + "gumpidx.mul"
		if os.path.exists(testName):
			return testName
	
	return None
	
def mulPassthroughHandler(rawData, rawIndex, mulName, offsetInMul, sizeInMul, resvValue):
	#applies to any format that doesn't require export processing
	return rawData

def mulGumpHandler(rawData, rawIndex, mulName, offsetInMul, sizeInMul, resvValue):
	#pack the dimensions from the index into the output binary
	return noePack("HH", (resvValue & 0xFFFF), ((resvValue >> 16) & 0xFFFF)) + rawData

def mulSoundHandler(rawData, rawIndex, mulName, offsetInMul, sizeInMul, resvValue):
	#sample/bit rate of all sounds is fixed, so just plop it out with a RIFF WAVE header
	waveHeaderData = rapi.createPCMWaveHeader(len(rawData), 16, 22050, 1)
	return waveHeaderData + rawData
	
def extractMUL(fileName, fileLen, justChecking):
	baseName = rapi.getExtensionlessName(fileName).lower()
	idxName = findIDXForMUL(baseName)
	if idxName is None:
		return 0
		
	if justChecking:
		return 1
		
	supportedPrefixHandlers = (
		("__raw__", ".uo_raw", mulPassthroughHandler), #must remain as first entry
		("animationframe", ".uo_animframe", mulPassthroughHandler),
		("anim", ".uo_anim", mulPassthroughHandler),
		("gump", ".uo_gump", mulGumpHandler),
		("tex", ".uo_tex", mulPassthroughHandler),
		("art", ".uo_art_tile", mulPassthroughHandler),
		("multi", ".uo_multi_tile", mulPassthroughHandler),
		("sound", ".wav", mulSoundHandler)
	)
	localName = rapi.getLocalFileName(baseName)
	useHandler = None
	for handler in supportedPrefixHandlers:
		handlerPrefix = handler[0]
		if localName.startswith(handlerPrefix):
			useHandler = handler
			break
		
	if useHandler is None:
		print("No resource handlers found, extracting as unknown/raw.")
		useHandler = supportedPrefixHandlers[0]
	else:
		print("Using MUL handler:", useHandler[0])

	useHandlerPrefix, useHandlerExt, useHandlerFn = useHandler

	exFileCount = 0
	rawIndex = 0
	with open(fileName, "rb") as fMul:
		with open(idxName, "rb") as fIdx:
			while True:
				idxData = fIdx.read(12)
				if not idxData:
					break
				ofs, size, resv = noeUnpack("<III", idxData)
				if ofs != 0xFFFFFFFF and size > 0:
					fMul.seek(ofs, os.SEEK_SET)
					mulData = useHandlerFn(fMul.read(size), rawIndex, localName, ofs, size, resv)
					if mulData is not None:
						exName = localName + "%06i"%exFileCount + useHandlerExt
						exFileCount += 1
						print("Writing", exName)
						rapi.exportArchiveFile(exName, mulData)
				rawIndex += 1

	return 1


def uoAnimCheckType(data):
	if len(data) < 516:
		return 0
	bs = NoeBitStream(data)
	bs.seek(512, NOESEEK_ABS)
	frameCount = bs.readInt()
	if frameCount <= 0 or (516 + frameCount * 4) >= len(data):
		return 0
	for frameIndex in range(0, frameCount):
		ofs = bs.readInt()
		if ofs < 0 or ofs >= len(data):
			return 0
	return 1

def uoAnimLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	palData = bs.readBytes(512)
	palRgba = rapi.imageDecodeRaw(palData, 256, 1, "b5g5r5p1")
	frameCount = bs.readInt()
	frameOffsets = []
	for frameIndex in range(0, frameCount):
		frameOffsets.append(bs.readInt())

	#loop through to get the canvas dimensions first
	maxXOffset = 0
	maxYOffset = 0
	canvasWidth = 0
	canvasHeight = 0
	for frameOffset in frameOffsets:
		bs.seek(512 + frameOffset, NOESEEK_ABS)
		maxXOffset = max(maxXOffset, bs.readShort())
		centerY = bs.readShort()
		maxYOffset = max(maxYOffset, -centerY)
		canvasWidth = max(canvasWidth, bs.readShort())
		height = bs.readShort()
		canvasHeight = max(canvasHeight, height + centerY)
	canvasHeight += maxYOffset
	
	baseTexName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
	for frameOffset in frameOffsets:
		bs.seek(512 + frameOffset, NOESEEK_ABS)
		centerX = bs.readShort()
		centerY = bs.readShort()
		width = bs.readShort()
		height = bs.readShort()
		
		encodedDataOfs = bs.getOffset()
		encodedData = bs.getBuffer()[encodedDataOfs:]
		#decode the pixel data
		decodedData = rapi.callExtensionMethod("uo_anim_decode", encodedData, palRgba, centerX, centerY, width, height, maxXOffset, maxYOffset, canvasWidth, canvasHeight)
		texName = baseTexName + "_frame" + repr(len(texList))
		tex = NoeTexture(texName, canvasWidth, canvasHeight, decodedData, noesis.NOESISTEX_RGBA32)
		texList.append(tex)
	
	return 1

def uoGumpCheckType(data):
	#unique extension will have to be enough for now
	return 1
	
def uoGumpLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	height = bs.readUShort()
	width = bs.readUShort()
	#we read the dimensions as they were embedded from the idx on extraction
	if height == 0 or width == 0:
		#if the resv value was 0 it probably came from a uop, which means it's the new format with embedded width/height
		width = bs.readUInt()
		height = bs.readUInt()
		if height == 0 or width == 0:
			print("Error: Gump has 0 dimensions.") #seems valid, there are some 8-byte stub files
			return 0

	dataOfs = bs.getOffset()
	#decode the pixel data
	decodedData = rapi.callExtensionMethod("uo_gump_decode", bs.getBuffer()[dataOfs:], width, height)
	decodedData = rapi.imageDecodeRaw(decodedData, width, height, "b5g5r5a1")
	tex = NoeTexture("uo_gump_tex", width, height, decodedData, noesis.NOESISTEX_RGBA32)
	texList.append(tex)
	return 1

def uoTexCheckType(data):
	if len(data) != 0x2000 and len(data) != 0x8000:
		return 0
	return 1
	
def uoTexLoadRGBA(data, texList):
	width = 64 if len(data) == 0x2000 else 128
	height = width
	
	rgbaData = rapi.imageDecodeRaw(data, width, height, "b5g5r5p1")
	tex = NoeTexture("uo_tex_tex", width, height, rgbaData, noesis.NOESISTEX_RGBA32)
	texList.append(tex)
	return 1

def uoArtTileCheckType(data):
	#unique extension will have to be enough for now
	return 1
	
def uoArtTileLoadRGBADirect(data):
	bs = NoeBitStream(data)
	
	rawFlag = bs.readUInt()
	#is this really correct? seems pretty flaky, since a raw might have first pixel non-black and second black.
	#seems like doc is wrong here, and should be using tile data to determine type instead.
	if rawFlag > 0 and rawFlag < 0xFFFF:
		#rle
		width = bs.readUShort()
		height = bs.readUShort()
		decodedData = rapi.callExtensionMethod("uo_arttile_decode", bs.getBuffer()[bs.getOffset():], width, height)
		decodedData = rapi.imageDecodeRaw(decodedData, width, height, "b5g5r5a1")
		tex = NoeTexture("uo_art_rle_tex", width, height, decodedData, noesis.NOESISTEX_RGBA32)
		return tex
	else:
		#raw
		bs.seek(0, NOESEEK_ABS)
		width = 44
		height = 44
		halfWidth = width // 2
		
		startOfs = 1
		startIncr = 1
		imageData = [0] * width * height
		
		y = 0
		while startOfs != 0:
			x = halfWidth - startOfs
			for i in range(0, startOfs * 2): #set the alpha bit on every pixel we write to
				imageData[y * width + x + i] = bs.readUShort() | (1 << 15)

			#possible todo - could optimize, structured this way for easy experimentation (doesn't really matter if these are always 44x44)
			y += 1
			startOfs += startIncr
			if startOfs > halfWidth: #flip
				startOfs = halfWidth
				startIncr = -startIncr

		rgbaData = rapi.imageDecodeRaw(noePack("H" * width * height, *imageData), width, height, "b5g5r5a1")
		tex = NoeTexture("uo_art_raw_tex", width, height, rgbaData, noesis.NOESISTEX_RGBA32)
		return tex
	
	return None
	
def uoArtTileLoadRGBA(data, texList):
	tex = uoArtTileLoadRGBADirect(data)
	if tex is not None:
		texList.append(tex)
		return 1
	return 0

def uoMultiTileCheckType(data):
	#unique extension will have to be enough for now
	return 1
	
def findMulRelativeToFile(fileName, mulName):
	localPath = rapi.getDirForFilePath(fileName)
	for attemptCount in range(1, 4):
		testPath = localPath + "../" * attemptCount
		if os.path.exists(testPath + mulName):
			return testPath
	return None
	
UO_OBJFL_BACKGROUND		= (1 << 0)
UO_OBJFL_WEAPON			= (1 << 1)
UO_OBJFL_TRANSPARENT	= (1 << 2)
UO_OBJFL_TRANSLUCENT	= (1 << 3)
UO_OBJFL_WALL			= (1 << 4)
UO_OBJFL_DAMAGING		= (1 << 5)
UO_OBJFL_IMPASSABLE		= (1 << 6)
UO_OBJFL_WET			= (1 << 7)
UO_OBJFL_UNKNOWN1		= (1 << 8)
UO_OBJFL_SURFACE		= (1 << 9)
UO_OBJFL_BRIDGE			= (1 << 10)
UO_OBJFL_GENERIC		= (1 << 11)
UO_OBJFL_WINDOW			= (1 << 12)
UO_OBJFL_NOSHOOT		= (1 << 13)
UO_OBJFL_ARTICLEA		= (1 << 14)
UO_OBJFL_ARTICLEAN		= (1 << 15)
UO_OBJFL_INTERNAL		= (1 << 16)
UO_OBJFL_FOLIAGE		= (1 << 17)
UO_OBJFL_PARTIALHUE		= (1 << 18)
UO_OBJFL_UNKNOWN2		= (1 << 19)
UO_OBJFL_MAP			= (1 << 20)
UO_OBJFL_CONTAINER		= (1 << 21)
UO_OBJFL_WEARABLE		= (1 << 22)
UO_OBJFL_LIGHTSOURCE	= (1 << 23)
UO_OBJFL_ANIMATION		= (1 << 24)
UO_OBJFL_NODIAGONAL		= (1 << 25)
UO_OBJFL_UNKNOWN3		= (1 << 26)
UO_OBJFL_ARMOR			= (1 << 27)
UO_OBJFL_ROOF			= (1 << 28)
UO_OBJFL_DOOR			= (1 << 29)
UO_OBJFL_STAIRBACK		= (1 << 30)
UO_OBJFL_STAIRRIGHT		= (1 << 31)

class UOTileItem:
	def __init__(self, flags, height, itemName):
		self.flags = flags
		self.height = height
		self.itemName = itemName

class UODrawBlock:
	def __init__(self, drawX, drawY, sort1, blockX, blockY, blockAltitude, tileHeight, flags, tex):
		self.drawX = drawX
		self.drawY = drawY
		self.sort1 = sort1
		self.blockX = blockX
		self.blockY = blockY
		self.blockAltitude = blockAltitude
		self.tileHeight = tileHeight
		self.flags = flags
		self.tex = tex
	def __repr__(self):
		return "(x:" + repr(self.drawX) + " y:" + repr(self.drawY) + " sort1:" + repr(self.sort1) + " z:" + repr(self.blockAltitude) + " th:" + repr(self.tileHeight) + " fl:" + repr(self.flags) + ")"
	def Compare(a, b):
		val = (a.blockX + a.blockY) - (b.blockX + b.blockY)
		if val == 0:
			val = (a.blockAltitude + a.sort1) - (b.blockAltitude + b.sort1)
			if val == 0:
				val = a.sort1 - b.sort1
		return val

def uoLoadTileData(basePath):
	tileData = []
	relPath = findMulRelativeToFile(basePath, "tiledata.mul")
	#older format not currently supported
	if relPath is None or os.path.getsize(relPath + "tiledata.mul") < 3188736:
		return tileData
	with open(relPath + "tiledata.mul", "rb") as fTileData:
		landDataCount = 0x4000
		itemDataCount = 0x10000
		fTileData.seek(4, os.SEEK_CUR)
		expectedLandSize = landDataCount * 30 + (landDataCount // 32) * 4
		fTileData.seek(expectedLandSize, os.SEEK_CUR)
		#currently land data is unused
		"""
		for landIndex in range(0, landDataCount):
			if landIndex > 0 and (landIndex & 31) == 0:
				fTileData.seek(4, os.SEEK_CUR)

			flags, texID = noeUnpack("<QH", fTileData.read(10));
			fTileData.seek(20, os.SEEK_CUR)
		"""
		for itemIndex in range(0, itemDataCount):
			if itemIndex > 0 and (itemIndex & 31) == 0:
				fTileData.seek(4, os.SEEK_CUR)
			flags, weight, quality, unk1, unk2, unk3, quantity, animID = noeUnpack("<QBBBBBBH", fTileData.read(16))
			unk4, unk5, val, height = noeUnpack("<HBBB", fTileData.read(5))
			itemName = noeStrFromBytes(fTileData.read(20))
			itemData = UOTileItem(flags, height, itemName)
			tileData.append(itemData)			
	return tileData
	
def uoMultiTileLoadRGBA(data, texList):
	loadStartTime = time.time()

	relPath = findMulRelativeToFile(rapi.getLastCheckedName(), "artidx.mul")
	if relPath is None:
		print("Error: Could not find artidx.mul on any relative path.")
		return 0

	bs = NoeBitStream(data)
	
	loadTileStart = time.time()
	tileMulData = uoLoadTileData(rapi.getLastCheckedName())
	loadTileTime = time.time() - loadTileStart
	
	loadArtStart = time.time()	
	canvasWidth = 0
	canvasHeight = 0
	minX = 0
	minY = 0
	drawBlocks = []
	texDict = {}
	with open(relPath + "artidx.mul", "rb") as fIdx:
		with open(relPath + "art.mul", "rb") as fMul:
			while bs.getOffset() < bs.getSize():
				itemId = bs.readShort()
				blockNum = 16384 + itemId
				blockX = bs.readShort()
				blockY = bs.readShort()
				blockAltitude = bs.readShort()
				flags = bs.readUInt()
				if UO_NEW_MULTI_VER:
					resv = bs.readUInt()
				if blockNum >= 0:
					tex = texDict.get(blockNum)
					if tex is None:
						fIdx.seek(12 * blockNum, os.SEEK_SET)
						tileOfs, tileSize = noeUnpack("<II", fIdx.read(8))
						if tileOfs != 0xFFFFFFFF:
							fMul.seek(tileOfs, os.SEEK_SET)
							tileData = fMul.read(tileSize)
							tex = uoArtTileLoadRGBADirect(tileData)
							texDict[blockNum] = tex

					if tex is not None:
						tileHeight = 0 if itemId >= len(tileMulData) else tileMulData[itemId].height
						drawX = (blockX - blockY) * 22 - (tex.width >> 1)
						drawY = (blockX + blockY) * 22 - tex.height - blockAltitude * 4
						minX = min(minX, drawX)
						minY = min(minY, drawY)
						canvasWidth = max(canvasWidth, drawX + tex.width)
						canvasHeight = max(canvasHeight, drawY + tex.height)
						sort1 = (0 if tileHeight <= 0 else 1) + (0 if (flags & UO_OBJFL_BACKGROUND) else 1)
						drawBlock = UODrawBlock(drawX, drawY, sort1, blockX, blockY, blockAltitude, tileHeight, flags, tex)
						drawBlocks.append(drawBlock)
	loadArtTime = time.time() - loadArtStart

	if len(drawBlocks) == 0:
		return 0

	blockBlitStart = time.time()	
		
	drawBlocks = sorted(drawBlocks, key=noeCmpToKey(UODrawBlock.Compare))
	ofsX = 0
	ofsY = 0
	if minX < 0:
		ofsX = -minX
		canvasWidth += ofsX
	if minY < 0:
		ofsY = -minY
		canvasHeight += ofsY
		
	#draw the blocks into the canvas
	imageData = noePack("BBBB", 0, 0, 0, 0) * canvasWidth * canvasHeight
	for drawBlock in drawBlocks:
		tex = drawBlock.tex
		rapi.imageBlit32(imageData, canvasWidth, canvasHeight, ofsX + drawBlock.drawX, ofsY + drawBlock.drawY, tex.pixelData, tex.width, tex.height, 0, 0, 0, 0, noesis.BLITFLAG_ALPHABLEND)
		
	blockBlitTime = time.time()	- blockBlitStart
		
	tex = NoeTexture("uo_multi_tex", canvasWidth, canvasHeight, imageData, noesis.NOESISTEX_RGBA32)
	texList.append(tex)

	loadTotalTime = time.time() - loadStartTime
	
	print("Load complete.")
	print("Tile:", loadTileTime)
	print("Art:", loadArtTime)
	print("Draw:", blockBlitTime)
	print("Total:", loadTotalTime)
	
	return 1

def uoMapCheckType(data):
	if len(data) < 8:
		return 0
	bs = NoeBitStream(data)
	idxSize = bs.readUInt()
	dataSize = bs.readUInt()
	if len(data) != 8 + idxSize + dataSize:
		return 0
	return 1

def uoMapLoadRGBA(data, texList):
	bs = NoeBitStream(data)
	idxSize = bs.readUInt()
	dataSize = bs.readUInt()

	mapFileName = rapi.getLastCheckedName()
	relPath = findMulRelativeToFile(mapFileName, "radarcol.mul")
	if relPath is None:
		return 0
	radarColors = rapi.loadIntoByteArray(relPath + "radarcol.mul")

	dataOfs = 8 + idxSize

	mapHeights = (512, 512, 200, 256, 181, 512)	
	
	mapNumberName = "0"
	baseName = rapi.getLocalFileName(mapFileName).lower()
	mapIndexExpr = re.search("\d", baseName)
	if not mapIndexExpr:
		print("WARNING: Could not determine map index from filename, assuming 0.")
		mapIndex = 0
	else:
		numOfs = mapIndexExpr.start()
		mapIndex = int(baseName[numOfs])
		if mapIndex < 0 or mapIndex >= len(mapHeights):
			print("WARNING: Map index from filename is out of known range, assuming 0.")
			mapIndex = 0
		else:
			#special case, preserve the x after the number
			copyCount = 2 if baseName[numOfs + 1] == 'x' else 1
			mapNumberName = baseName[numOfs:numOfs + copyCount]
				
	mapHeight = mapHeights[mapIndex]
	mapWidth = dataSize // 196 // mapHeight

	staticIdxData = None
	staticMulData = None
	
	#let's try to load the statics (optional)
	staticsIdxName = "staidx" + mapNumberName + ".mul"
	staticsMulName = "statics" + mapNumberName + ".mul"
	relPath = findMulRelativeToFile(mapFileName, staticsIdxName)
	if relPath is not None:
		staticIdxData = rapi.loadIntoByteArray(relPath + staticsIdxName)
		staticMulData = rapi.loadIntoByteArray(relPath + staticsMulName)
	
	imageWidth = mapWidth * 8
	imageHeight = mapHeight * 8
	#this is broken out into a native extension, because it just takes too long to do in python despite its simplicity.
	#the 4 parameters before static data are to allow rendering a sub-region of the map, if desired.
	imageData = rapi.callExtensionMethod("uo_map_render_radar", data[dataOfs : dataOfs + dataSize], radarColors, mapWidth, mapHeight, 0, 0, mapWidth, mapHeight, staticIdxData, staticMulData)
	
	rgbaData = rapi.imageDecodeRaw(imageData, imageWidth, imageHeight, "b5g5r5p1")
	tex = NoeTexture("uo_map_tex", imageWidth, imageHeight, rgbaData, noesis.NOESISTEX_RGBA32)
	texList.append(tex)

	return 1
