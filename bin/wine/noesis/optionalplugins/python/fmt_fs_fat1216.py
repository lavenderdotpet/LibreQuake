from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("FAT12 Disk Image", ".fat12")
	noesis.setHandlerExtractArc(handle, fat12ExtractArc)
	noesis.addOption(handle, "-fatnousefc", "use 2 instead of provided fat count.", 0)
	noesis.addOption(handle, "-fatwritee5", "write entries beginning with 0xE5.", 0)
	noesis.addOption(handle, "-fatmaskfs", "24-bit mask for filesize.", 0)
	noesis.addOption(handle, "-fatnolfn", "ignore LFN for FAT32.", 0)
	
	handle = noesis.register("FAT16 Disk Image", ".fat16")
	noesis.setHandlerExtractArc(handle, fat16ExtractArc)

	handle = noesis.register("FAT32 Disk Image", ".fat32")
	noesis.setHandlerExtractArc(handle, fat32ExtractArc)
	
	return 1

#for debugging, tell us when files exist across noncontiguous clusters due to fragmentation.
DETECT_NONCONTIGUOUS_FILES = False

FAT_ATTRIB_READONLY = (1 << 0)
FAT_ATTRIB_HIDDN = (1 << 1)
FAT_ATTRIB_SYSTEM = (1 << 2)
FAT_ATTRIB_VOLUMELABEL = (1 << 3)
FAT_ATTRIB_DIRECTORY = (1 << 4)
FAT_ATTRIB_ARCHIVE = (1 << 5)
	
FAT_CLUSTER_ROOT = 0
FAT_CLUSTER_FIRST = 2

class LFNEntry:
	def __init__(self, bs):
		self.order = bs.readByte()
		self.wideNameBytes = bs.readBytes(2 * 5)
		self.attrib = bs.readByte()
		self.type = bs.readByte()
		self.checksum = bs.readByte()
		self.wideNameBytes += bs.readBytes(2 * 6)
		self.cluster = bs.readUShort()
		self.wideNameBytes += bs.readBytes(2 * 2)
		for offset in range(1, len(self.wideNameBytes) // 2):
			c = noeUnpack("H", self.wideNameBytes[offset * 2 : offset * 2 + 2])[0]
			if c == 0 or c == 0xFFFF: #terminate
				self.wideNameBytes = self.wideNameBytes[:offset * 2]
				break
	def Compare(a, b):
		return a.order - b.order

class FATEntry:
	def __init__(self, bs, parentDirectory, fatBits, lfnEntries):
		filenameBytes = bs.readBytes(8)
		fileExtBytes = bs.readBytes(3)

		self.attributes = bs.readUByte()

		if fatBits == 32 and self.attributes == 0x0F:
			#long filename data
			self.filename = None
			self.isLfnData = True
			if noesis.optWasInvoked("-fatnolfn"):
				bs.seek(20, NOESEEK_REL)
			else:
				bs.seek(-12, NOESEEK_REL)
				lfnEntries.append(LFNEntry(bs))
		else:
			self.isLfnData = False
			if filenameBytes[0] == 0xE5:
				if noesis.optWasInvoked("-fatwritee5"):
					filenameBytes = bytearray(filenameBytes)
					filenameBytes[0] = bytes("!", "ASCII")[0]
					self.filename = noeAsciiFromBytes(filenameBytes).rstrip(" ")
				else:
					self.filename = ""
			elif filenameBytes[0] != 0:
				self.filename = noeAsciiFromBytes(filenameBytes).rstrip(" ")
			else:
				self.filename = None
			fileExt = noeAsciiFromBytes(fileExtBytes).rstrip(" ")
			if self.isValid() and not (self.attributes & FAT_ATTRIB_DIRECTORY) and len(fileExt) > 0:
				self.filename += "." + fileExt
					
			if len(lfnEntries) > 0:
				#opt to use the long name
				lfnEntries = sorted(lfnEntries, key=noeCmpToKey(LFNEntry.Compare))
				allWideBytes = bytearray()
				for lfnEntry in lfnEntries:
					allWideBytes += lfnEntry.wideNameBytes
				self.filename = str(allWideBytes, "UTF-16")
					
			bs.readUShort() #reserved
			self.createTime = bs.readUShort()
			self.createDate = bs.readUShort()
			self.accessDate = bs.readUShort()
			reservedWord = bs.readUShort() #reserved
			self.writeTime = bs.readUShort()
			self.writeDate = bs.readUShort()
			self.firstCluster = bs.readUShort()
			if fatBits == 32:
				self.firstCluster |= (reservedWord << 16)
			fileSizeMask = 0xFFFFFF if noesis.optWasInvoked("-fatmaskfs") else 0xFFFFFFFF
			self.fileSize = bs.readUInt() & fileSizeMask
			self.parentDirectory = parentDirectory
		
	def getFullPath(self):
		basePath = self.parentDirectory.getFullPath() + "\\" if self.parentDirectory else ""
		return basePath + self.filename
		
	def isValid(self):
		return self.filename and len(self.filename) > 0 and self.filename[0] != "."
		
	def isTerminator(self):
		return self.filename is None and not self.isLfnData

class FATImage:
	def __init__(self, bs, imageSize, fatBits):
		self.bs = bs
		self.imageSize = imageSize
		self.fatBits = fatBits
		self.entries = []
		
	def parseFAT(self):
		bs = self.bs
		bs.seek(11, NOESEEK_ABS)
		self.sectorSize = bs.readUShort()
		self.sectorsPerCluster = max(bs.readUByte(), 1)
		self.reservedSectorCount = max(bs.readUShort(), 1)
		self.fatCount = bs.readUByte()
		self.rootDirEntryCount = bs.readUShort()
		if self.fatBits == 32:
			self.rootDirEntryCount = 0
		self.sectorCount = bs.readUShort()
			
		bs.readUByte() #unused - media descriptor
		self.sectorsPerFat = bs.readUShort()
		self.sectorsPerTrack = bs.readUShort()
		self.headCount = bs.readUShort()
		bs.readUInt() #unused - number of hidden sectors in partition
		largeSectorCount = bs.readUInt()
		if self.sectorCount == 0:
			self.sectorCount = largeSectorCount
		
		if self.sectorSize == 0 or self.sectorSize > 8192 or self.fatCount == 0 or self.sectorCount == 0:# or self.sectorSize * self.sectorCount > self.imageSize:
			return -1

		if noesis.optWasInvoked("-fatnousefc"):
			self.fatCount = 2
			
		self.clusterSize = self.sectorsPerCluster * self.sectorSize
			
		if self.fatBits == 32:
			self.sectorsPerFat = bs.readUInt()
			self.fatFlags = bs.readUShort()
			self.fatVersion = bs.readUShort()
			self.rootClusterIndex = bs.readUInt()
			self.infoSectorIndex = bs.readUShort()
			self.backupBootSectorIndex = bs.readUShort()
			bs.readBytes(12) #unused
			bs.readUShort() #unused - logical drive number of partition
			self.bootSig = bs.readUByte()
			if self.bootSig == 0x29:
				self.volumeId = bs.readUInt()
				self.volumeLabel = bs.readBytes(11)
				self.fsType = bs.readBytes(8)
		else:
			bs.readUShort() #unused - logical drive number of partition
			self.bootSig = bs.readUByte()
			if self.bootSig == 0x29:
				self.volumeId = bs.readUInt()
				self.volumeLabel = bs.readBytes(11)
				self.fsType = bs.readBytes(8)

		self.reservedSectorsSize = self.reservedSectorCount * self.sectorSize
		
		self.fatOffset = self.reservedSectorsSize
		self.fatSize = self.sectorsPerFat * self.sectorSize
				
		self.rootDirOffset = self.fatOffset + self.fatSize * self.fatCount
		rootDirSize = 32 * self.rootDirEntryCount
		if (rootDirSize % self.sectorSize) != 0:
			rootDirSize += self.sectorSize - (rootDirSize % self.sectorSize)
			
		self.dataOffset = self.rootDirOffset + rootDirSize

		if self.fatBits == 32:
			#this should generally match, but get the root offset explicitly just in case
			self.rootDirOffset = self.getClusterDataOffset(self.rootClusterIndex)
		
		return 0
		
	def clusterIsValid(self, clusterIndex):
		return clusterIndex >= 0 and clusterIndex < len(self.fatEntries)
		
	def getClusterDataOffset(self, clusterIndex):
		if clusterIndex == FAT_CLUSTER_ROOT:
			return self.rootDirOffset
		else:
			return self.dataOffset + (clusterIndex - FAT_CLUSTER_FIRST) * self.clusterSize

	def getNextCluster(self, clusterIndex):
		return self.fatEntries[clusterIndex]
			
	def recursivelyReadEntries(self, clusterIndex, parentDirectory):
		self.bs.seek(self.getClusterDataOffset(clusterIndex), NOESEEK_ABS)
		entryCount = self.rootDirEntryCount if clusterIndex == FAT_CLUSTER_ROOT else self.clusterSize // 32
		newDirectories = []
		lfnEntries = []
		while True:
			for entryIndex in range(0, entryCount):
				entry = FATEntry(self.bs, parentDirectory, self.fatBits, lfnEntries)
				if entry.isTerminator():
					break
				elif not entry.isValid():
					continue
					
				if entry.attributes & FAT_ATTRIB_DIRECTORY:
					newDirectories.append(entry)
				self.entries.append(entry)
				lfnEntries = [] #reset lfn list
				
			if clusterIndex == FAT_CLUSTER_ROOT:
				break
			else:
				if not self.clusterIsValid(clusterIndex):
					break
				clusterIndex = self.getNextCluster(clusterIndex)
		for newDirectory in newDirectories:
			self.recursivelyReadEntries(newDirectory.firstCluster, newDirectory)
			
	def readEntries(self):
		bs = self.bs
		
		print("Reading FAT image. Sector size:", self.sectorSize, "- Cluster size:", self.clusterSize)
		
		print("Reading FAT of size", self.fatSize, "from", self.fatOffset)
		#seek over to FAT sector
		bs.seek(self.fatOffset, NOESEEK_ABS)
		fatData = bs.readBytes(self.fatSize)
		fatBs = NoeBitStream(fatData)
		self.fatEntries = []
		maxFatEntryCount = (self.fatSize * 8) // self.fatBits
		for i in range(0, maxFatEntryCount):
			if fatBs.checkEOF():
				break
			fatValue = fatBs.readBits(self.fatBits)
			#print("FAT:", len(self.fatEntries), fatValue)
			self.fatEntries.append(fatValue)

		print("Reading root directory from", self.rootDirOffset)			
		#seek over to root directory
		if self.fatBits == 32:
			self.recursivelyReadEntries(self.rootClusterIndex, None)
		else:
			self.recursivelyReadEntries(FAT_CLUSTER_ROOT, None)

		for entry in self.entries:
			if (entry.attributes & FAT_ATTRIB_DIRECTORY):
				continue
			entryName = entry.getFullPath()
			print("Writing", entryName)
			
			clusterIndex = entry.firstCluster
			remainingSize = entry.fileSize
			entryData = bytearray()

			if DETECT_NONCONTIGUOUS_FILES:
				currentClusterOffset = self.getClusterDataOffset(clusterIndex)
				nonContiguousCount = 0
				
			while remainingSize > 0:
				bs.seek(self.getClusterDataOffset(clusterIndex), NOESEEK_ABS)
				readSize = min(remainingSize, self.clusterSize)
				entryData += bs.readBytes(readSize)
				remainingSize -= readSize
				if not self.clusterIsValid(clusterIndex):
					break
				clusterIndex = self.getNextCluster(clusterIndex)
				if DETECT_NONCONTIGUOUS_FILES and remainingSize > 0:
					expectedOffset = currentClusterOffset + self.clusterSize
					currentClusterOffset = self.getClusterDataOffset(clusterIndex)
					if expectedOffset != currentClusterOffset:
						nonContiguousCount += 1

			if DETECT_NONCONTIGUOUS_FILES and nonContiguousCount > 0:
				print("File", entryName, "has", nonContiguousCount, "noncontiguous breaks.")
						
			if remainingSize > 0:
				print("Warning: Failed to read expected file size, bad cluster index on:", entryName, "-", entry.attributes)
				print(len(entryData), "vs", entry.fileSize, "with cluster size", self.clusterSize, "and index", clusterIndex)
			elif len(entryData) != entry.fileSize:
				print("Bad entry size on", entryName, "- probably tried to read off end of image:", len(entryData), "vs", entry.fileSize)
				
			rapi.exportArchiveFile(entryName, entryData)
			
	
def fatGenericExtractArc(fileName, fileLen, justChecking, fatBits):
	if fileLen < 40:
		return 0
	with open(fileName, "rb") as f:
		bs = NoeFileStream(f)
		fat = FATImage(bs, fileLen, fatBits)
		if fat.parseFAT() != 0:
			return 0

		if justChecking:
			return 1

		fat.readEntries()
		
	return 1
	
def fat12ExtractArc(fileName, fileLen, justChecking):
	return fatGenericExtractArc(fileName, fileLen, justChecking, 12)

def fat16ExtractArc(fileName, fileLen, justChecking):
	return fatGenericExtractArc(fileName, fileLen, justChecking, 16)

def fat32ExtractArc(fileName, fileLen, justChecking):
	return fatGenericExtractArc(fileName, fileLen, justChecking, 32)
