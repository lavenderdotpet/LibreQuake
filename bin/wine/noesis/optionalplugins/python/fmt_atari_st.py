from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("NEOchrome Image", ".neo")
	noesis.setHandlerTypeCheck(handle, neoCheckType)
	noesis.setHandlerLoadRGBA(handle, neoLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, neoWriteRGBA)
	noesis.addOption(handle, "-neoanim", "create color anim textures.", 0)

	handle = noesis.register("NEOchrome Animation", ".ani")
	noesis.setHandlerTypeCheck(handle, neoAnimCheckType)
	noesis.setHandlerLoadRGBA(handle, neoAnimLoadRGBA)
	
	handle = noesis.register("STX Disk Image", ".stx")
	noesis.setHandlerExtractArc(handle, stxExtractArc)
	noesis.addOption(handle, "-stxapplyfuzzy", "apply fuzzy mask to output.", 0)
	noesis.addOption(handle, "-stxwriteerr", "write sectors with error bit.", 0)
	noesis.addOption(handle, "-stxwriteover", "write track sector overrun.", 0)

	handle = noesis.register("MSA Disk Image", ".msa")
	noesis.setHandlerExtractArc(handle, msaExtractArc)
	
	return 1

NEOCHROME_MODE_LOW = 0 #320x200x16
NEOCHROME_MODE_MED = 1 #640x200x4
NEOCHROME_MODE_HIGH = 2 #640x400x2
NEOCHROME_ENDIAN = NOE_BIGENDIAN
NEOCHROME_ANIMLIMIT_VALID = (1 << 15)
NEOCHROME_ANIMLIMIT_UPPERMASK = 15
NEOCHROME_ANIMLIMIT_LOWERMASK = 240
NEOCHROME_ANIMLIMIT_LOWERSHIFT = 4
NEOCHROME_ANIMSPEED_VALID = (1 << 15)
NEOCHROME_ANIMSPEED_MASK = 255
NEOCHROME_BLOCKWIDTH = 16
NEOCHROME_PALETTE_FORMAT = "b3p1g3p1r3p5" #9-bit RGB 00000RRR0GGG0BBB
	
class NeochromeImage:
	def __init__(self, bs):
		self.bs = bs
		
	def parseImageHeader(self):
		bs = self.bs
		if bs.getSize() < 128:
			return -1
		
		self.flags = bs.readUShort()
		self.mode = bs.readUShort()
		if self.mode > NEOCHROME_MODE_HIGH:
			return -1
			
		self.palette = rapi.swapEndianArray(bs.readBytes(16 * 2), 2)
		self.decodedPalette = rapi.imageDecodeRaw(self.palette, 16, 1, NEOCHROME_PALETTE_FORMAT)
		#if you want the first entry to be transparent:
		#self.decodedPalette[3] = 0
			
		self.filename = bs.readBytes(12) #tends to be nothing but a bunch of ascii spaces in files in the wild
		self.colorAnimLimits = bs.readUShort() #Bit 15 is set if animation data is valid. Bit 0-3 right/upper limit, bit 4-7 left/lower limit. 
		self.colorAnimSpeedDir = bs.readUShort() #Bit 15 is set if animation is on. Least significant byte should be interpreted as a signed byte and defines the number of vertical blanks between cycles. If it's negative, the number of vertical blanks is |x|-1 and the direction is backwards.
		self.colorAnimSteps = bs.readUShort() #Number of steps to display before moving on to the next picture when the image is part of a slide show.
		self.offsetX = bs.readUShort()
		self.offsetY = bs.readUShort()
		self.width = bs.readUShort()
		self.height = bs.readUShort()
		bs.seek(33 * 2, NOESEEK_REL) #reserved
		self.dataOffset = bs.tell()
		
		if (self.colorAnimLimits & NEOCHROME_ANIMLIMIT_VALID) and noesis.optWasInvoked("-neoanim"):
			self.enableAnim = True
			self.animLowerLimit = (self.colorAnimLimits & NEOCHROME_ANIMLIMIT_LOWERMASK) >> NEOCHROME_ANIMLIMIT_LOWERSHIFT
			self.animUpperLimit = (self.colorAnimLimits & NEOCHROME_ANIMLIMIT_UPPERMASK)
			self.animFrameCount = (self.animUpperLimit - self.animLowerLimit) + 1
			if (self.colorAnimSpeedDir & NEOCHROME_ANIMSPEED_VALID):
				self.animSpeed = int(noeUnpack("b", noePack("B", (self.colorAnimSpeedDir & NEOCHROME_ANIMSPEED_MASK)))[0])
			else:
				self.animSpeed = 6 #10fps at 60hz
		else:
			self.enableAnim = False
			
		self.setPaletteShift(0)
		
		return 0
		
	def setPaletteShift(self, palShift):
		self.palShift = palShift
		
	def getWidth(self):
		if self.flags == 0xBABE and self.width != 0:
			return self.width
		elif self.mode == NEOCHROME_MODE_LOW:
			return 320
		else:
			return 640
	def getHeight(self):
		if self.flags == 0xBABE and self.height != 0:
			return self.height
		elif self.mode == NEOCHROME_MODE_LOW or self.mode == NEOCHROME_MODE_MED:
			return 200
		else:
			return 400
			
	def shiftedPaletteIndex(self, palIndex):
		if self.enableAnim:
			if palIndex >= self.animLowerLimit and palIndex <= self.animUpperLimit:
				offsetIndex = (palIndex - self.animLowerLimit) + self.palShift
				return self.animLowerLimit + (offsetIndex % self.animFrameCount)
				
		return palIndex
			
	def blockOffsetForPixelCoordinate(self, x, y):
		blockSize = self.getBlockSize()
		rowSize = self.getWidth() // NEOCHROME_BLOCKWIDTH * blockSize
		rowOffset = x // NEOCHROME_BLOCKWIDTH * blockSize
		return y * rowSize + rowOffset
		
	def pixelCoordinateForBlockOffset(self, blockOffset):
		blockSize = self.getBlockSize()
		rowSize = self.getWidth() // NEOCHROME_BLOCKWIDTH * blockSize
		x = (blockOffset % rowSize) // blockSize * NEOCHROME_BLOCKWIDTH
		y = blockOffset // rowSize
		return x, y
			
	def getBlockSize(self):
		if self.mode == NEOCHROME_MODE_HIGH:
			return 2
		elif self.mode == NEOCHROME_MODE_MED:
			return 4
		else:
			return 8
			
	def rasterizeData(self):
		bs = self.bs
		w = self.getWidth()
		h = self.getHeight()
		dst = NoeBitStream()
		blockCount = w * h // NEOCHROME_BLOCKWIDTH
		bs.seek(self.dataOffset, NOESEEK_ABS)
		if self.mode == NEOCHROME_MODE_HIGH:
			for blockIndex in range(0, blockCount):
				w0 = bs.readUShort()
				for x in range(0, NEOCHROME_BLOCKWIDTH):
					bitIndex = 15 - x
					palIndex = (w0 & (1 << bitIndex))
					palOffset = self.shiftedPaletteIndex(palIndex >> bitIndex) * 4
					dst.writeBytes(self.decodedPalette[palOffset : palOffset + 4])
		elif self.mode == NEOCHROME_MODE_MED:
			for blockIndex in range(0, blockCount):
				w0 = bs.readUShort()
				w1 = bs.readUShort()
				for x in range(0, NEOCHROME_BLOCKWIDTH):
					bitIndex = 15 - x
					palIndex = (w0 & (1 << bitIndex)) | ((w1 & (1 << bitIndex)) << 1)
					palOffset = self.shiftedPaletteIndex(palIndex >> bitIndex) * 4
					dst.writeBytes(self.decodedPalette[palOffset : palOffset + 4])
		else:
			for blockIndex in range(0, blockCount):
				w0 = bs.readUShort()
				w1 = bs.readUShort()
				w2 = bs.readUShort()
				w3 = bs.readUShort()
				for x in range(0, NEOCHROME_BLOCKWIDTH):
					bitIndex = 15 - x
					palIndex = (w0 & (1 << bitIndex)) | ((w1 & (1 << bitIndex)) << 1) | ((w2 & (1 << bitIndex)) << 2) | ((w3 & (1 << bitIndex)) << 3)
					palOffset = self.shiftedPaletteIndex(palIndex >> bitIndex) * 4
					dst.writeBytes(self.decodedPalette[palOffset : palOffset + 4])
					
		return dst.getBuffer()
			
def neoCheckType(data):
	neo = NeochromeImage(NoeBitStream(data, NEOCHROME_ENDIAN))
	if neo.parseImageHeader() != 0:
		return 0
	return 1

def neoLoadRGBA(data, texList):
	neo = NeochromeImage(NoeBitStream(data, NEOCHROME_ENDIAN))
	if neo.parseImageHeader() != 0:
		return 0
		
	imageData = neo.rasterizeData()
	if imageData is None:
		print("Unsupported image mode:", neo.mode)
		return 0
	noeTex = NoeTexture("neochrometex", neo.getWidth(), neo.getHeight(), imageData, noesis.NOESISTEX_RGBA32)
	noeTex.flags |= noesis.NTEXFLAG_FILTER_NEAREST | noesis.NTEXFLAG_WRAP_CLAMP
	texList.append(noeTex)
	
	if neo.enableAnim:
		for offset in range(1, neo.animFrameCount - 1):
			#should probably expose texture frame data to python one of these days.
			animOffset = neo.animFrameCount - offset - 1 if neo.animSpeed > 0 else offset
			neo.setPaletteShift(animOffset)
			imageData = neo.rasterizeData()
			noeTex = NoeTexture("neochrometex%02i"%offset, neo.getWidth(), neo.getHeight(), imageData, noesis.NOESISTEX_RGBA32)
			noeTex.flags |= noesis.NTEXFLAG_FILTER_NEAREST | noesis.NTEXFLAG_WRAP_CLAMP
			texList.append(noeTex)
	
	return 1
	
def neoWriteRGBA(data, width, height, bs):
	exportWidth = 320
	exportHeight = 200
	
	if width != exportWidth or height != exportHeight:
		data = rapi.imageResample(data, width, height, exportWidth, exportHeight)
	
	#encode and then decode in order to quantize colors into neo range - this will give us a more effective palettization
	data = rapi.imageEncodeRaw(data, exportWidth, exportHeight, NEOCHROME_PALETTE_FORMAT)
	data = rapi.imageDecodeRaw(data, exportWidth, exportHeight, NEOCHROME_PALETTE_FORMAT)
	
	dataPal = rapi.imageGetPalette(data, exportWidth, exportHeight, 16, 0, 0)
	dataIdx = rapi.imageApplyPalette(data, exportWidth, exportHeight, dataPal, 16) #just leave as 8 bits, we'll encode into planar format

	neoPal = rapi.imageEncodeRaw(dataPal, 16, 1, NEOCHROME_PALETTE_FORMAT)
	neoPal = rapi.swapEndianArray(neoPal, 2)
	
	bs.setEndian(NEOCHROME_ENDIAN)
	
	bs.writeUShort(0)
	bs.writeUShort(NEOCHROME_MODE_LOW)
	bs.writeBytes(neoPal)
	bs.writeString("        .   ", 0)
	bs.writeBytes(bytes(80))
	
	indexBs = NoeBitStream(dataIdx)
	blockCount = exportWidth * exportHeight // NEOCHROME_BLOCKWIDTH
	for blockIndex in range(0, blockCount):
		w0 = 0
		w1 = 0
		w2 = 0
		w3 = 0
		#this is just the way my brain happened to shit this out, it can certainly be faster!
		for x in range(0, NEOCHROME_BLOCKWIDTH):
			bitIndex = 15 - x
			palIndex = indexBs.readUByte() & 0xF
			b0 = (palIndex & 1)
			b1 = (palIndex & 2) >> 1
			b2 = (palIndex & 4) >> 2
			b3 = (palIndex & 8) >> 3
			w0 |= (b0 << bitIndex)
			w1 |= (b1 << bitIndex)
			w2 |= (b2 << bitIndex)
			w3 |= (b3 << bitIndex)
		bs.writeUShort(w0)
		bs.writeUShort(w1)
		bs.writeUShort(w2)
		bs.writeUShort(w3)
				
	return 1

class NeochromeAnim:
	def __init__(self, bs, pathName):
		self.bs = bs
		self.pathName = pathName
		
	def parseImageHeader(self):
		bs = self.bs
		if bs.readUInt() != 0xBABEEBEA:
			return -1
			
		self.palette = None
		self.widthInBytes = bs.readUShort()
		self.height = bs.readUShort()
		self.sizePlusTen = bs.readUShort() #unsure why +10, files don't appear to be capable of housing this * frameCount
		self.size = self.widthInBytes * self.height
		self.x = bs.readUShort()
		self.y = bs.readUShort()
		self.frameCount = bs.readUShort()
		self.animSpeed = bs.readUShort() #can this be signed?
		bs.readUInt() #unused
		self.dataOffset = bs.tell()
		self.totalSize = self.size * self.frameCount
		if self.widthInBytes == 0 or self.height == 0 or self.frameCount == 0:
			return -1
		if (self.dataOffset + self.totalSize) > bs.getSize():
			return -1
		self.mode = NEOCHROME_MODE_LOW #just assume for purposes of rasterization that we're targeting low-res mode
		return 0

	def getWidth(self):
		#assumes NEOCHROME_MODE_LOW
		return self.widthInBytes * 2
	def getHeight(self):
		return self.height

	def attemptPaletteLoad(self):
		#check for a .neo file of the same name to grab the palette. could get more elaborate, but for now we don't really care.
		neoName = rapi.getExtensionlessName(self.pathName) + ".neo"
		if os.path.exists(neoName):
			neoData = rapi.loadIntoByteArray(neoName)
			neo = NeochromeImage(NoeBitStream(neoData, NEOCHROME_ENDIAN))
			if neo.parseImageHeader() == 0:
				self.palette = neo.decodedPalette
		
	def rasterizeData(self, frameIndex):
		bs = self.bs
		if self.mode != NEOCHROME_MODE_LOW: #if aiming to support other modes, just unify with .neo rasterizing
			return None
			
		w = self.getWidth()
		h = self.getHeight()
		dst = NoeBitStream()
		blockCount = w * h // NEOCHROME_BLOCKWIDTH
		for blockIndex in range(0, blockCount):
			w0 = bs.readUShort()
			w1 = bs.readUShort()
			w2 = bs.readUShort()
			w3 = bs.readUShort()
			for x in range(0, NEOCHROME_BLOCKWIDTH):
				bitIndex = 15 - x
				palIndex = (w0 & (1 << bitIndex)) | ((w1 & (1 << bitIndex)) << 1) | ((w2 & (1 << bitIndex)) << 2) | ((w3 & (1 << bitIndex)) << 3)
				if self.palette:
					palOffset = (palIndex >> bitIndex) * 4
					dst.writeBytes(self.palette[palOffset : palOffset + 4])		
				else:
					monoColor = (palIndex >> bitIndex) << 4
					dst.writeBytes(noePack("BBBB", monoColor, monoColor, monoColor, 255))
		return dst.getBuffer()
	
def neoAnimCheckType(data):
	neoAnim = NeochromeAnim(NoeBitStream(data, NEOCHROME_ENDIAN), rapi.getLastCheckedName())
	if neoAnim.parseImageHeader() != 0:
		return 0
	return 1
	
def neoAnimLoadRGBA(data, texList):
	neoAnim = NeochromeAnim(NoeBitStream(data, NEOCHROME_ENDIAN), rapi.getLastCheckedName())
	if neoAnim.parseImageHeader() != 0:
		return 0
		
	neoAnim.attemptPaletteLoad()
		
	for frameIndex in range(0, neoAnim.frameCount):
		#should probably expose texture frame data to python one of these days.
		imageData = neoAnim.rasterizeData(frameIndex)
		if imageData:
			noeTex = NoeTexture("neochromeani%02i"%frameIndex, neoAnim.getWidth(), neoAnim.getHeight(), imageData, noesis.NOESISTEX_RGBA32)
			noeTex.flags |= noesis.NTEXFLAG_FILTER_NEAREST | noesis.NTEXFLAG_WRAP_CLAMP
			texList.append(noeTex)
		
	return 1
	
STX_TRACKBIT_PROTECTED = (1 << 0)
STX_TRACKBIT_FILLGAPS = (1 << 6)
STX_TRACKBIT_SYNCOFFSET = (1 << 7)

STX_FDCBIT_NOTFOUND = (1 << 4)
STX_FDCBIT_CRCERROR = (1 << 3)
STX_FDCBIT_FUZZYMASK = (1 << 7)
	
class STXSectorHeader:
	def __init__(self, bs, track, sectorsByTrack):
		self.track = track
		self.dataOffset = bs.readUInt()
		self.headerPosAsTime = bs.readUShort()
		self.readTiming = bs.readUShort()
		self.trackNumber = bs.readUByte()
		self.side = bs.readUByte()
		self.id = bs.readUByte()
		self.size = (128 << bs.readUByte())
		self.crc = bs.readUShort()
		self.fdcStatusReg = bs.readUByte()
		self.flags = bs.readUByte()
		self.applyFuzzyMask = False
		sectorsByTrack.setdefault(self.trackNumber, []).append(self)
		
	def readSectorData(self, bs, sectorsPerTrack):
		track = self.track
		data = None
		if (self.fdcStatusReg & STX_FDCBIT_NOTFOUND) or ((self.fdcStatusReg & STX_FDCBIT_CRCERROR) and not noesis.optWasInvoked("-stxwriteerr")):
			#fill out with zeroes if necessary
			if self.id <= sectorsPerTrack:
				data = bytearray(self.size)
		elif self.id <= sectorsPerTrack or noesis.optWasInvoked("-stxwriteover"):
			bs.seek(track.dataOffset + self.dataOffset, NOESEEK_ABS)
			sectorData = bs.readBytes(self.size)
			if self.applyFuzzyMask:
				fuzzyData = bytearray(sectorData)
				if (self.fuzzyOffset + len(track.fuzzyMask)) >= self.size:
					for offset in range(0, self.size):
						fuzzyData[offset] = (fuzzyData[offset] & track.fuzzyMask[self.fuzzyOffset + offset])
				else:
					print("Warning: Fuzzy mask too small for sector data:", self.size)
				data = fuzzyData
			else:
				data = sectorData
		return data
		
	def Compare(a, b):
		if a.trackNumber == b.trackNumber:
			if a.side == b.side:
				return a.id - b.id
			return a.side - b.side
		return a.trackNumber - b.trackNumber
	
class STXTrack:
	def __init__(self, bs, uid, sectorsByTrack):
		self.headerOffset = bs.tell()
		self.uid = uid
		self.trackLength = bs.readUInt()
		fuzzyMaskLength = bs.readUInt()
		self.sectorCount = bs.readUShort()
		self.flags = bs.readUShort()
		self.tdSize = bs.readUShort()
		self.trackIndex = bs.readUByte()
		self.trackImageType = bs.readUByte()
		self.sectorHeaders = []
		self.fuzzyOffset = 0
		
		#we don't really care since sector offsets work out just fine without handling this data.
		#if (self.flags & (STX_TRACKBIT_FILLGAPS | STX_TRACKBIT_SYNCOFFSET)):
		#	print("Warning: STX_TRACKBIT_FILLGAPS / STX_TRACKBIT_SYNCOFFSET not implemented:", self.trackIndex, self.flags)
		
		if (self.flags & STX_TRACKBIT_PROTECTED):
			for sectorIndex in range(0, self.sectorCount):
				self.sectorHeaders.append(STXSectorHeader(bs, self, sectorsByTrack))
				
		self.sectorHeaders = sorted(self.sectorHeaders, key=noeCmpToKey(STXSectorHeader.Compare))
				
		self.maxSide = 0
		for sectorHeader in self.sectorHeaders:
			self.maxSide = max(self.maxSide, sectorHeader.side)
				
		self.fuzzyMask = bs.readBytes(fuzzyMaskLength) if fuzzyMaskLength > 0 else None
		if self.fuzzyMask and noesis.optWasInvoked("-stxapplyfuzzy"):
			for sectorHeader in self.sectorHeaders:
				if (sectorHeader.fdcStatusReg & STX_FDCBIT_FUZZYMASK):
					sectorHeader.fuzzyOffset = self.fuzzyOffset
					self.fuzzyOffset += sectorHeader.size
					sectorHeader.applyFuzzyMask = True
		
		self.dataOffset = bs.tell()
		self.headerSize = self.dataOffset - self.headerOffset
		bs.seek(self.headerOffset + self.trackLength, NOESEEK_ABS)
			
	def readData(self, bs, sectorsPerTrack, sectorsByTrack):
		data = bytearray()
		expectedSectorSize = 512
		
		if len(self.sectorHeaders) == 0:
			bs.seek(self.dataOffset, NOESEEK_ABS)
			data += bs.readBytes(self.sectorCount * expectedSectorSize)
		else:
			if self.trackIndex in sectorsByTrack:
				allSectors = sectorsByTrack[self.trackIndex]
			else:
				return None
			allSectors = sorted(allSectors, key=noeCmpToKey(STXSectorHeader.Compare))
			
			side = -1
			dataIndex = -1
			dataBySide = []
			for sectorHeader in allSectors:
				sectorData = sectorHeader.readSectorData(bs, sectorsPerTrack)
				if sectorData:
					if sectorHeader.side != side:
						side = sectorHeader.side
						dataBySide.append(bytearray())
						dataIndex = len(dataBySide) - 1
					dataBySide[dataIndex] += sectorData

			for sideData in dataBySide:
				if not noesis.optWasInvoked("-stxwriteover"):
					expectedTrackSize = expectedSectorSize * sectorsPerTrack
					if len(sideData) < expectedTrackSize:
						print("Padding sector data for track", self.trackIndex, "-", len(sideData), "to", expectedTrackSize)
						sideData += bytearray(expectedTrackSize - len(sideData))
				data += sideData
					
		return data
		
	def Compare(a, b):
		if a.trackIndex == b.trackIndex:
			return a.maxSide - b.maxSide
		return a.trackIndex - b.trackIndex		
	
def stxExtractArc(fileName, fileLen, justChecking):
	if fileLen < 16:
		return 0
	with open(fileName, "rb") as f:
		bs = NoeFileStream(f)
		id = bs.readInt()
		if id != 0x595352:
			return 0
		version = bs.readUShort()
		if version != 3:
			return 0
		bs.readUShort() #0x01 or 0xCC?
		bs.readUShort() #0x00
		trackCount = bs.readUByte()
		if trackCount <= 0:
			return 0
		bs.readUByte() #?
		bs.readUInt() #?
		if (16 + trackCount * 16) >= fileLen:
			return 0
		
		if justChecking:
			return 1
			

		sectorsByTrack = {}
			
		tracks = []
		for trackIndex in range(0, trackCount):
			tracks.append(STXTrack(bs, trackIndex, sectorsByTrack))
			
		sectorsPerTrack = 10
		#try to pull intended sectors per track out of the boot sector
		if len(tracks) > 0:
			bootSector = tracks[0].readData(bs, 1, sectorsByTrack)
			if bootSector:
				sectorsPerTrack = noeUnpack("H", bootSector[0x18 : 0x1A])[0]
			
		imageData = bytearray()
		for track in tracks:
			trackData = track.readData(bs, sectorsPerTrack, sectorsByTrack)
			if trackData:
				print("Track data", track.trackIndex, "-", track.dataOffset, "-", len(trackData))
				imageData += trackData
			
		imageFilename = "diskimage.fat12"
		print("Writing", imageFilename)
		rapi.exportArchiveFile(imageFilename, imageData)
			
	return 1

def msaExtractArc(fileName, fileLen, justChecking):
	if fileLen < 20:
		return 0
	with open(fileName, "rb") as f:
		bs = NoeFileStream(f, NOE_BIGENDIAN)
		if bs.readUShort() != 0xE0F:
			return 0
		sectorsPerTrack = bs.readUShort()
		sideCount = 1 + bs.readUShort()
		startTrack = bs.readUShort()
		endTrack = bs.readUShort()
		uncompressedTrackSize = sectorsPerTrack * 512
		if sectorsPerTrack == 0 or endTrack <= startTrack or sideCount > 2:
			return 0
			
		if justChecking:
			return 1
		
		imageData = bytearray()
		for trackIndex in range(startTrack * sideCount, endTrack * sideCount):
			trackSize = bs.readUShort()
			trackData = bs.readBytes(trackSize)
			if trackSize == uncompressedTrackSize:
				imageData += trackData
			else:
				dbs = NoeBitStream()
				cbs = NoeBitStream(trackData, NOE_BIGENDIAN)
				while not cbs.checkEOF():
					b = cbs.readUByte()
					if b == 0xE5:
						r = cbs.readUByte()
						rLength = cbs.readUShort()
						dbs.writeBytes(noePack("B" * rLength, *([r] * rLength)))
					else:
						dbs.writeUByte(b)
				imageData += dbs.getBuffer()
		
		imageFilename = "diskimage.fat12"
		print("Writing", imageFilename)
		rapi.exportArchiveFile(imageFilename, imageData)
		
		return 1
