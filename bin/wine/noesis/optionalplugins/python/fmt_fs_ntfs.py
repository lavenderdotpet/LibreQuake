#barebones NTFS implementation, only intended for extraction. lacking functionality for more advanced/uncommon use cases.
#the NTFS documentation I was able to find by googling was mostly garbage and missing lots of vital bits. the actual
#implementations I was able to find were tainted by GPL, which means I won't touch them with a 50 foot pole. as such, the
#lznt1 stuff is mostly guesswork based on example behavior I was able to observe from an image of one of my old drives.

from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("NTFS Disk Image", ".ntfs")
	noesis.setHandlerExtractArc(handle, ntfsExtractArc)
	return 1
	
NTFS_SIG_FILE = 0x454C4946
NTFS_ATTR_TYPE_STANDARD_INFORMATION = 0x10
NTFS_ATTR_TYPE_ATTRIBUTE_LIST = 0x20
NTFS_ATTR_TYPE_FILE_NAME = 0x30
NTFS_ATTR_TYPE_OBJECT_ID = 0x40
NTFS_ATTR_TYPE_SECURITY_DESCRIPTOR = 0x50
NTFS_ATTR_TYPE_VOLUME_NAME = 0x60
NTFS_ATTR_TYPE_VOLUME_INFORMATION = 0x70
NTFS_ATTR_TYPE_DATA = 0x80
NTFS_ATTR_TYPE_INDEX_ROOT = 0x90
NTFS_ATTR_TYPE_INDEX_ALLOCATION = 0xA0
NTFS_ATTR_TYPE_BITMAP = 0xB0
NTFS_ATTR_TYPE_REPARSE_POINT = 0xC0
NTFS_ATTR_TYPE_EA_INFORMATION = 0xD0
NTFS_ATTR_TYPE_EA = 0xE0
NTFS_ATTR_TYPE_PROPERTY_SET = 0xF0
NTFS_ATTR_TYPE_LOGGED_UTILITY_STREAM = 0x100

NTFS_RECORD_FLAG_INUSE = 0x01
NTFS_RECORD_FLAG_DIRECTORY = 0x02

NTFS_PERM_FLAG_SPARSE = 0x200
NTFS_PERM_FLAG_COMPRESSED = 0x800
NTFS_PERM_FLAG_ENCRYPTED = 0x4000
NTFS_ATTR_FLAG_COMPRESSED_NONE = 0x0
NTFS_ATTR_FLAG_COMPRESSED_LZNT1 = 0x1
NTFS_ATTR_FLAG_COMPRESSED_ANY = 0xFF
NTFS_ATTR_FLAG_ENCRYPTED = 0x4000
NTFS_ATTR_FLAG_SPARSE = 0x8000

NTFS_FILE_MFT = 0
NTFS_FILE_MFTMIRROR = 1
NTFS_FILE_LOGFILE = 2
NTFS_FILE_VOLUME = 3
NTFS_FILE_ATTRDEF = 4
NTFS_FILE_ROOTDIR = 5
NTFS_FILE_BITMAP = 6
NTFS_FILE_BOOT = 7
NTFS_FILE_BADCLUS = 8
NTFS_FILE_SECURE = 9
NTFS_FILE_UPCASE = 10
NTFS_FILE_EXTEND = 11

class NtfsDataRun:
	def __init__(self, bs):
		c = bs.readUByte()
		if c != 0:
			self.isTerminator = False
			self.offsetSize = c >> 4
			self.lenSize = c & 15
			self.runLength = ntfsReadVariableSized(bs, self.lenSize)
			self.runOffset = noesis.signedBits(ntfsReadVariableSized(bs, self.offsetSize), self.offsetSize << 3) if self.offsetSize != 0 else 0
		else:
			self.isTerminator = True

	def isSparse(self):
		return self.offsetSize == 0
			
	def isValid(self):
		return not self.isTerminator
		
class NtfsCompressedChunkContext:
	def __init__(self, dataRuns, attr):
		self.runs = dataRuns
		self.attr = attr
		self.resetContext()

	def resetContext(self):
		self.currentIndex = 0
		self.currentRunOffset = 0
		self.isCompressed = False
		
	def readCluster(self):
		if self.currentIndex >= len(self.runs):
			return None
		ntfsImage = self.attr.ntfsImage
		clusterSize = ntfsImage.clusterSize
		imageBs = ntfsImage.bs
		dataRun = self.runs[self.currentIndex]
		if dataRun.isSparse():
			data = bytearray(clusterSize)
		else:
			imageBs.seek(dataRun.lcn * clusterSize + self.currentRunOffset, NOESEEK_ABS)
			data = imageBs.readBytes(clusterSize)
		self.currentRunOffset += clusterSize
		if self.currentRunOffset >= dataRun.runLength * clusterSize:
			self.currentRunOffset = 0
			self.currentIndex += 1
		return data
		
	def readChunk(self):
		if self.currentIndex >= len(self.runs):
			return None
		attr = self.attr
		clusterSize = attr.ntfsImage.clusterSize
		chunkSize = clusterSize * attr.compressionUnitSize
		chunkData = bytearray()
		self.isCompressed = False
		startSparse = self.runs[self.currentIndex].isSparse()
		while self.currentIndex < len(self.runs) and len(chunkData) < chunkSize:
			if not startSparse and self.runs[self.currentIndex].isSparse():
				self.isCompressed = True
			chunkData += self.readCluster()
		return chunkData

class NtfsAttribute:
	def __init__(self, bs, record):
		self.bs = bs
		self.record = record
		self.ntfsImage = record.ntfsImage
		self.offset = bs.tell()
		self.attrType = bs.readUInt()
		if self.isValid():
			self.attrSize = bs.readUShort()
			bs.readUShort() #unknown
			self.resident = bs.readUByte() == 0
			self.nameSize = bs.readUByte()
			self.nameOffset = bs.readUShort()

			self.flags = bs.readUShort()
			self.attrID = bs.readUShort()
			if self.resident:
				self.contentSize = bs.readUInt()
				self.contentOffset = bs.readUShort()
				bs.readUShort() #unused
			else:
				self.vcnStart = bs.readUInt64()
				self.vcnEnd = bs.readUInt64()
				self.runListOffset = bs.readUShort()
				self.compressionUnitSize = 1 << bs.readUShort()
				bs.readUInt() #unused
				self.contentAllocSize = bs.readUInt64()
				self.contentSize = bs.readUInt64() & 0xFFFFFFFFFFFF
				self.contentInitSize = bs.readUInt64()
				
			if self.attrType == NTFS_ATTR_TYPE_FILE_NAME:
				dataBs = NoeBitStream(self.readDataMemory())
				self.parentDirRef = dataBs.readInt64()
				self.cTime = dataBs.readUInt64()
				self.aTime = dataBs.readUInt64()
				self.mTime = dataBs.readUInt64()
				self.rTime = dataBs.readUInt64()
				self.allocFileSize = dataBs.readUInt64()
				self.realFileSize = dataBs.readUInt64()
				self.fileFlags = dataBs.readUInt()
				dataBs.readUInt()
				fileNameSize = dataBs.readUByte()
				self.fileNameSpace = dataBs.readUByte()				
				self.fileName = ntfsReadUnicodeString(dataBs, fileNameSize)
			elif self.attrType == NTFS_ATTR_TYPE_STANDARD_INFORMATION:
				dataBs = NoeBitStream(self.readDataMemory())
				self.cTime = dataBs.readUInt64()
				self.aTime = dataBs.readUInt64()
				self.mTime = dataBs.readUInt64()
				self.rTime = dataBs.readUInt64()
				self.permissions = dataBs.readUInt()
				self.maxVerNum = dataBs.readUInt()
				self.verNum = dataBs.readUInt()
				self.classId = dataBs.readUInt()
				self.ownerId = dataBs.readUInt()
				self.secId = dataBs.readUInt()
				self.quotaCharged = dataBs.readUInt64()
				self.updateSeqNum = dataBs.readUInt64()

			bs.seek(self.offset + self.attrSize, NOESEEK_ABS)

	def isValid(self):
		return self.attrType != 0xFFFFFFFF and self.attrType != 0
	
	def getAttrName(self):
		bs = self.bs
		prevOffset = bs.tell()
		bs.seek(self.offset + self.nameOffset, NOESEEK_ABS)
		name = ntfsReadUnicodeString(bs, self.nameSize)
		bs.seek(prevOffset, NOESEEK_ABS)
		return name
		
	def getFileName(self):
		return self.fileName if self.attrType == NTFS_ATTR_TYPE_FILE_NAME else ""

	def readDataGeneric(self, readHandler):	
		bs = self.bs
		prevOffset = bs.tell()
		if self.resident:
			bs.seek(self.offset + self.contentOffset, NOESEEK_ABS)
			readHandler.readData(bs.readBytes(self.contentSize))
		elif self.runListOffset > 0:
			bs.seek(self.offset + self.runListOffset, NOESEEK_ABS)
			clusterSize = self.ntfsImage.clusterSize

			dataRuns = self.readDataRuns()
			if self.flags & NTFS_ATTR_FLAG_COMPRESSED_LZNT1:
				chunkContext = NtfsCompressedChunkContext(dataRuns, self)
				while True:
					chunkData = chunkContext.readChunk()
					if not chunkData:
						break
					if chunkContext.isCompressed:
						readHandler.readData(rapi.decompLZNT1(chunkData, self.compressionUnitSize * clusterSize))
					else:
						readHandler.readData(chunkData)
			else:
				imageBs = self.ntfsImage.bs
				for dataRun in dataRuns:
					if dataRun.isSparse():
						readHandler.readData(bytearray(dataRun.runLength * clusterSize))
					else:
						imageBs.seek(dataRun.lcn * clusterSize, NOESEEK_ABS)
						readHandler.readData(imageBs.readBytes(dataRun.runLength * clusterSize))

		bs.seek(prevOffset, NOESEEK_ABS)
		
	def readDataRuns(self):
		bs = self.bs
		dataRuns = []
		currentLcn = 0
		while True:
			dataRun = NtfsDataRun(bs)
			if not dataRun.isValid():
				break
			currentLcn += dataRun.runOffset
			dataRun.lcn = currentLcn
			dataRuns.append(dataRun)
		return dataRuns
		
	def readDataMemory(self, cropToContent = False):
		data = bytearray()
		readHandler = NtfsReadMemory()
		self.readDataGeneric(readHandler)
		if not self.resident and cropToContent:
			readHandler.data = readHandler.data[:self.contentSize] #cluster size probably doesn't align to file size
		return readHandler.data
		
	def Compare(a, b):
		if a.resident:
			return -1
		if b.resident:
			return 1
		return a.vcnStart - b.vcnStart
		
class NtfsReadMemory:
	def __init__(self):
		self.data = bytearray()
	def readData(self, data):
		self.data += data
	def getCurrentSize(self):
		return len(self.data)

class NtfsReadToExportFile:
	def __init__(self, f, targetSize):
		self.f = f
		self.targetSize = targetSize
		self.writeSize = 0
	def readData(self, data):
		remainingSize = self.targetSize - self.writeSize
		if remainingSize > 0:
			if len(data) > remainingSize:
				data = data[:remainingSize]
			self.f.write(data)
			self.writeSize += len(data)
	def getCurrentSize(self):
		return self.writeSize
		
class NtfsMftRecord:
	def __init__(self, bs, ntfsImage):
		self.bs = bs
		self.ntfsImage = ntfsImage
		self.offset = bs.tell()
		self.attrs = None
		self.signature = bs.readUInt()
		self.fixupOffset = bs.readUShort()
		self.fixupCount = bs.readUShort()
		self.lsnSeq = bs.readUInt64()
		self.recordUsage = bs.readUShort()
		self.hardLinkCount = bs.readUShort()
		self.attrOffset = bs.readUShort()
		self.flags = bs.readUShort()
		self.entrySize = bs.readUInt()
		self.allocatedSize = bs.readUInt()
		self.fileRef = bs.readUInt64()
		self.nextId = bs.readUShort()
		bs.readUShort() #unknown
		self.mftRecordNumber = bs.readUInt()
		if self.isValid():
			self.performFixup()
			bs.seek(self.offset + self.allocatedSize, NOESEEK_ABS)

	def isValid(self):
		return self.signature == NTFS_SIG_FILE
			
	def performFixup(self):
		if self.fixupCount > 0:
			bs = self.bs
			fixups = []
			bs.seek(self.offset + self.fixupOffset)
			for fixupIndex in range(0, self.fixupCount):
				fixups.append(bs.readUShort())
			sectorSize = self.ntfsImage.sectorSize
			expectedCount = self.allocatedSize // sectorSize
			if expectedCount + 1 != self.fixupCount:
				print("Warning: Expected a fixup count of", expectedCount + 1, "but got", self.fixupCount, "with array:", fixups)
			else:
				for sectorIndex in range(0, expectedCount):
					bs.seek(self.offset + sectorIndex * sectorSize + sectorSize - 2, NOESEEK_ABS)
					testData = bs.readUShort()
					if testData != fixups[0]:
						print("Warning: Did not get expected fixup value, record entry may be corrupt.")
					else:
						bs.seek(-2, NOESEEK_REL)
						bs.writeUShort(fixups[sectorIndex + 1])
		
	def readAttributes(self):
		if self.attrs is None:
			self.attrs = []
			bs = self.bs
			prevOffset = bs.tell()
			bs.seek(self.offset + self.attrOffset, NOESEEK_ABS)
			listAttrs = []
			while True:
				attr = NtfsAttribute(bs, self)
				if not attr.isValid():
					break
				self.attrs.append(attr)
				if attr.attrType == NTFS_ATTR_TYPE_ATTRIBUTE_LIST:
					listAttrs.append(attr)
			#pile on external attributes
			for listAttr in listAttrs:
				data = listAttr.readDataMemory()
				attrBs = NoeBitStream(data)
				while True:
					subAttrOffset = attrBs.tell()
					subAttrType = attrBs.readUInt()
					if subAttrType == 0 or subAttrType == 0xFFFFFFFF:
						break
					subAttrSize = attrBs.readUShort()
					subAttrNameLength = attrBs.readUByte()
					subAttrNameOffset = attrBs.readUByte()
					subAttrVcn = attrBs.readUInt64()
					subAttrFileRef = attrBs.readUInt64()
					subRecordIndex = ntfsRecordIndex(subAttrFileRef)
					subRecord = self.ntfsImage.mftDict[subRecordIndex] if subRecordIndex in self.ntfsImage.mftDict else None
					newOffset = subAttrOffset + subAttrSize
					attrBs.seek((newOffset + 7) & ~7, NOESEEK_ABS)
					if subRecord != self:
						if subRecord:
							subRecord.readAttributes()
							#pile on the attributes from the referenced record
							for attr in subRecord.attrs:
								self.attrs.append(attr)
						else:
							print("Warning: ATTRIBUTE_LIST record has an invalid MFT record index:", subRecordIndex, subAttrFileRef, subAttrVcn, subAttrType)
			bs.seek(prevOffset, NOESEEK_ABS)
		
	def getFileNameAttribute(self):
		fileNameAttr = None
		for attr in self.attrs:
			if attr.attrType == NTFS_ATTR_TYPE_FILE_NAME:
				if fileNameAttr is None or len(attr.getFileName()) > len(fileNameAttr.getFileName()):
					fileNameAttr = attr
		return fileNameAttr

	def getFileName(self):
		attr = self.getFileNameAttribute()
		return attr.getFileName() if attr else None

	def getDataAttributes(self):
		dataAttribs = []
		for attr in self.attrs:
			if attr.attrType == NTFS_ATTR_TYPE_DATA:
				dataAttribs.append(attr)
		return sorted(dataAttribs, key=noeCmpToKey(NtfsAttribute.Compare))
		
	def getStandardInfoAttribute(self):
		for attr in self.attrs:
			if attr.attrType == NTFS_ATTR_TYPE_STANDARD_INFORMATION:
				return attr
		
class NtfsImage:
	def __init__(self, bs, imageSize):
		self.bs = bs
		self.imageSize = imageSize

	def parseHeader(self):
		bs = self.bs
		if self.imageSize <= 84:
			return -1
		bs.seek(3, NOESEEK_ABS)
		if bs.readUInt64() != 0x202020205346544E: #NTFS + four trailing spaces
			return -1
			
		self.sectorSize = bs.readUShort()
		self.sectorsPerCluster = bs.readUByte()
		self.clusterSize = self.sectorSize * self.sectorsPerCluster
		bs.seek(7, NOESEEK_REL) #unused
		self.mediaDescriptor = bs.readUByte()
		bs.seek(2, NOESEEK_REL) #unused
		self.sectorsPerTrack = bs.readUShort()
		self.headCount = bs.readUShort()
		self.hiddenSectorCount = bs.readUInt()
		bs.seek(8, NOESEEK_REL) #unused
		self.sectorCount = bs.readUInt64()
		self.mftClusterIndex = bs.readUInt64()
		self.mftMirrorClusterIndex = bs.readUInt64()
		self.clusterCount = self.sectorCount // self.sectorsPerCluster
		if self.mftClusterIndex >= self.clusterCount or self.mftMirrorClusterIndex >= self.clusterCount:
			return -1
		self.bytesPerFileRecord = bs.readByte()
		if self.bytesPerFileRecord < 0:
			self.bytesPerFileRecord = 1 << (-self.bytesPerFileRecord)
		bs.seek(3, NOESEEK_REL) #unused
		self.bytesPerIndexBuffer = bs.readByte()
		if self.bytesPerIndexBuffer < 0:
			self.bytesPerIndexBuffer = 1 << (-self.bytesPerIndexBuffer)
		bs.seek(3, NOESEEK_REL) #unused
		self.volumeSerialNumber = bs.readUInt64()
		
		return 0
		
	def parseMFT(self):
		bs = self.bs
		mftOffset = self.mftClusterIndex * self.clusterSize
		bs.seek(mftOffset, NOESEEK_ABS)

		print("Reading MFT data.")
		
		#read the root entry into a memory stream first, so we can do the fixup
		rootRecordBs = NoeBitStream(bs.readBytes(self.bytesPerFileRecord))
		rootRecord = NtfsMftRecord(rootRecordBs, self)
		rootRecord.readAttributes()
		rootDatas = rootRecord.getDataAttributes()
		if len(rootDatas) == 0: #always expect a data attribute for the MFT record
			return -1

		#mft may be fragmented, so we need to read it all into contiguous memory first
		rootDataRaw = bytearray()
		recordCount = rootDatas[0].contentSize // self.bytesPerFileRecord
		for dataAttr in rootDatas:
			rootDataRaw += dataAttr.readDataMemory()
		recordBs = NoeBitStream(rootDataRaw)
		
		self.mftDict = {}
		self.mftRecords = []
		for recordIndex in range(0, recordCount):
			record = NtfsMftRecord(recordBs, self)
		
			print("Reading record", recordIndex + 1, "of", recordCount, "records.")
			if record.isValid():
				if record.flags & NTFS_RECORD_FLAG_INUSE and recordIndex != NTFS_FILE_BADCLUS:
					recordNumber = record.mftRecordNumber #recordIndex
					self.mftDict[recordNumber] = record
					self.mftRecords.append(record)
			else: #if the record doesn't look valid, make sure we skip directly over by the expected record size
				recordBs.seek(record.offset + self.bytesPerFileRecord, NOESEEK_ABS)

		for recordIndex in range(0, len(self.mftRecords)):
			print("Reading attributes for record", recordIndex + 1, "of", len(self.mftRecords), "active records.")
			record = self.mftRecords[recordIndex]
			record.readAttributes()			

		return 0
		
	def exportFiles(self):
		badFiles = []
		totalProcessed = 0
		for record in self.mftRecords:
			if not (record.flags & NTFS_RECORD_FLAG_DIRECTORY):
				attrInfo = record.getStandardInfoAttribute()
				attrFn = record.getFileNameAttribute()
				attrDatas = record.getDataAttributes()
				if attrInfo and attrFn and len(attrDatas) > 0:
					path = ntfsGetFullPath(attrFn, self.mftDict)

					totalProcessed += 1
					print("Writing", path)
					try:
						absPath = rapi.exportArchiveFileGetName(path)
						with open(absPath, "wb") as fw:
							lastVcn = -1
							readHandler = NtfsReadToExportFile(fw, attrDatas[0].contentSize)
							for attrData in attrDatas:
								compressionType = attrData.flags & NTFS_ATTR_FLAG_COMPRESSED_ANY
								if not attrData.resident and lastVcn >= 0 and (lastVcn + 1) < attrData.vcnStart:
									print("Warning: Unexpected VCN gap.") #unsure if this can/does happen, or if the file needs to be padded if it does
									break
								elif compressionType != NTFS_ATTR_FLAG_COMPRESSED_NONE and compressionType != NTFS_ATTR_FLAG_COMPRESSED_LZNT1:
									print("Warning: Compression type not currently supported:", compressionType)
									break
								elif attrData.flags & NTFS_ATTR_FLAG_ENCRYPTED:
									print("Warning: Encryption not currently supported.")
									break

								attrData.readDataGeneric(readHandler)

								lastVcn = attrData.vcnEnd if not attrData.resident else -1

							if readHandler.getCurrentSize() != attrDatas[0].contentSize:
								print("Warning: Content size mismatch:", readHandler.getCurrentSize(), "vs", attrDatas[0].contentSize)
								badFiles.append(path)
					except:
						print("Warning: Exception during file write, possible problem with path length or invalid characters.")
						badFiles.append(path)
						
		print("Processed", totalProcessed, "file(s).")
		if len(badFiles) > 0:
			print("There were errors writing the following", len(badFiles), "file(s):")
			for badFile in badFiles:
				print("  " + badFile)

def ntfsGetFullPath(attr, mftDict):
	parentRefIndex = ntfsRecordIndex(attr.parentDirRef)
	basePath = ""
	if parentRefIndex in mftDict:
		parent = mftDict[parentRefIndex]
		parentAttr = parent.getFileNameAttribute()
		if parentAttr and parentAttr != attr:
			basePath = ntfsGetFullPath(parentAttr, mftDict) + "\\"
	attrFileName = attr.getFileName()
	if attrFileName:
		basePath += attrFileName
	return basePath

def ntfsReadUnicodeString(bs, charCount):
	return str(bs.readBytes(charCount * 2), "UTF-16")

def ntfsRecordIndex(ref):
	return ref & 0xFFFFFFFFFF
	
def ntfsReadVariableSized(bs, offsetSize):
	value = 0
	for index in range(0, offsetSize):
		value |= bs.readUByte() << (index << 3)
	return value
	
def ntfsExtractArc(fileName, fileLen, justChecking):
	with open(fileName, "rb") as f:
		bs = NoeFileStream(f)
		ntfs = NtfsImage(bs, fileLen)
		if ntfs.parseHeader() != 0:
			return 0
			
		if justChecking:
			return 1

		if ntfs.parseMFT() != 0:
			print("Error parsing MFT records.")
			return 0
			
		ntfs.exportFiles()
			
	return 1
