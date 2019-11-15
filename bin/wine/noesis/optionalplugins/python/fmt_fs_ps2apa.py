from inc_noesis import *

def registerNoesisTypes():
	#APA = Aligned Partition Allocation
	handle = noesis.register("PS2 APA Image", ".ps2apa")
	noesis.setHandlerExtractArc(handle, ps2apaExtractArc)
	return 0
	
WRITE_CHUNK_SIZE = 32 * 1024 * 1024

class APATime:
	def __init__(self, bs):
		self.resv = bs.readByte()
		self.sec = bs.readByte()
		self.min = bs.readByte()
		self.hour = bs.readByte()
		self.day = bs.readByte()
		self.month = bs.readByte()
		self.year = bs.readUShort()
	
class APAHeader:
	def __init__(self, bs, imageSize):
		self.bs = bs
		self.imageSize = imageSize
		self.sectorSize = 512 #implementation allows to change per partition, but it never actually needs to
		self.parented = False
	def parseAPA(self):
		if self.imageSize < 1024:
			return -1
		bs = self.bs
		self.headerOffset = bs.tell()
		self.dataOffset = self.headerOffset + 1024
		self.checkSum = bs.readUInt()
		self.id = bs.readUInt()
		if self.id != 0x415041:
			return -1
		self.nextPart = bs.readUInt()
		self.prevPart = bs.readUInt()
		self.name = noeAsciiFromBytes(bs.readBytes(32))
		self.rPass = bs.readBytes(8)
		self.fPass = bs.readBytes(8)
		mainPartOffset = bs.readUInt() * self.sectorSize
		mainPartSize = bs.readUInt() * self.sectorSize
		self.dataSize = mainPartSize - 1024		
		self.type = bs.readUShort()
		self.flags = bs.readUShort()
		self.subPartCount = bs.readUInt()
		if self.subPartCount > 64: #shouldn't be allowed by spec, although this loader could cope just fine
			return -1
		self.createTime = APATime(bs)
		self.parentPartOffset = bs.readUInt() * self.sectorSize
		self.partIndex = bs.readUInt()
		self.ver = bs.readUInt()
		bs.seek(28 + 128, NOESEEK_REL)
		self.bootId = bs.readBytes(32)
		self.bootVer = bs.readUInt()
		self.bootSectorCount = bs.readUInt()
		self.bootCreateTime = APATime(bs)
		self.osdOffset = bs.readUInt()
		self.osdSize = bs.readUInt()
		bs.seek(200, NOESEEK_REL)
		self.children = []
		self.parts = []
		if mainPartSize > 0:
			self.parts.append((mainPartOffset, mainPartSize))
		for subIndex in range(0, self.subPartCount):
			subOffset = bs.readUInt() * self.sectorSize
			subSize = bs.readUInt() * self.sectorSize
			if subSize > 0:
				self.parts.append((subOffset, subSize))			
		return 0
	def Compare(a, b):
		return a.partIndex - b.partIndex
	
def ps2apaExtractArc(fileName, fileLen, justChecking):
	with open(fileName, "rb") as f:
		bs = NoeFileStream(f)
		bs.seek(0, NOESEEK_ABS)
		rootApa = APAHeader(bs, fileLen)
		if rootApa.parseAPA() != 0:
			return 0
			
		if justChecking:
			return 1
			
		apaList = [rootApa]
		apaOffset = rootApa.nextPart * rootApa.sectorSize
		while apaOffset != 0:
			bs.seek(apaOffset, NOESEEK_ABS)
			apa = APAHeader(bs, fileLen - apaOffset)
			#print("Parsing APA at", apaOffset)
			if apa.parseAPA() != 0:
				break
			apaList.append(apa)
			apaOffset = apa.nextPart * apa.sectorSize
			
		print("Parsed", len(apaList), "APA headers.")
	
		offsetDict = {}
		for apa in apaList:
			offsetDict[apa.headerOffset] = apa
		for apa in apaList:
			if apa.parentPartOffset > 0 and apa.parentPartOffset in offsetDict:
				apaParent = offsetDict[apa.parentPartOffset]
				apaParent.children.append(apa)
				apa.parented = True
	
		exportCount = 0
		for apa in apaList:
			if apa.parented:
				continue
				
			#smash everything into a list including the root apa, then sort by index
			exportList = [apa] + apa.children
			exportList = sorted(exportList, key=noeCmpToKey(APAHeader.Compare))
				
			exportName = "%04i - "%exportCount + apa.name + ".bin"
			exportCount += 1
			print("Writing", exportName)
			absPath = rapi.exportArchiveFileGetName(exportName)
			with open(absPath, "wb") as fw:
				for export in exportList:
					bs.seek(export.dataOffset, NOESEEK_ABS)
					remaining = export.dataSize
					while remaining > 0:
						writeSize = min(remaining, WRITE_CHUNK_SIZE)
						remaining -= writeSize
						data = bs.readBytes(writeSize)
						fw.write(data)
		return 1
