from inc_noesis import *
import os

NoeImg_TrackType_Data = 0
NoeImg_TrackType_Audio = 1

class NoeImgTrack:
	def __init__(self, stream, index, baseLba, sectorSize, userSize, userOffset, trackType = NoeImg_TrackType_Data, streamOwner = True):
		self.index = index
		self.stream = stream
		self.baseLba = baseLba
		self.sectorSize = sectorSize
		self.userSize = userSize
		self.userOffset = userOffset
		self.trackType = trackType
		self.streamOwner = streamOwner
		
	def close(self):
		if self.streamOwner and self.stream:
			self.stream.close()
		self.stream = None
		self.streamOwner = False
			
class NoeImgReader:
	def __init__(self, tracks):
		self.tracks = sorted(tracks, key=noeCmpToKey(lambda a,b: a.baseLba - b.baseLba))
		self.currentSector = 0
		self.currentTrack = 0
		
	def setSector(self, sectorIndex):
		self.currentTrack = len(self.tracks) - 1
		self.currentSector = sectorIndex
		while self.currentTrack > 0:
			t = self.tracks[self.currentTrack]
			if sectorIndex >= t.baseLba:
				break
			self.currentTrack -= 1
		t = self.tracks[self.currentTrack]
		if sectorIndex >= t.baseLba:
			f = t.stream
			f.seek((sectorIndex - t.baseLba) * t.sectorSize, os.SEEK_SET)
		
	def readSectors(self, sectorCount):
		out = bytearray()
		t = self.tracks[self.currentTrack]
		f = t.stream
		nextT = self.tracks[self.currentTrack + 1] if self.currentTrack < (len(self.tracks) - 1) else None
		for i in range(0, sectorCount):
			s = f.read(t.sectorSize)
			if s:
				out += s[t.userOffset : t.userOffset + t.userSize]
			else: #if not s, we ran off the last track or there's a gap between tracks, so pad with 0
				out += bytearray(t.userSize)
				
			self.currentSector += 1
			if nextT and self.currentSector >= nextT.baseLba:
				#hop to the next track
				t = nextT
				f = t.stream
				self.currentTrack += 1
				nextT = self.tracks[self.currentTrack + 1] if self.currentTrack < (len(self.tracks) - 1) else None

		return out

	def readBytes(self, size):
		t = self.tracks[self.currentTrack]	
		sectorCount = (size + (t.userSize - 1)) // t.userSize
		rawData = self.readSectors(sectorCount)
		return rawData[:size]
		
	def readFileSystemVolume(self, trackIndex = 0):
		if self.containsIso9660(trackIndex):
			return self.readIso9660(trackIndex)
		#potentially add other filesystem support here
		return None
		
	def readFileData(self, imgFile):
		self.setSector(imgFile.lba)
		return self.readBytes(imgFile.size)
		
	def trackByIndex(self, trackIndex):
		for track in self.tracks:
			if track.index == trackIndex:
				return track
		return None
		
	def containsIso9660(self, trackIndex = 0):
		t = self.trackByIndex(trackIndex)
		if not t:
			return False
			
		previousSector = self.currentSector
		r = False
		try:
			self.setSector(t.baseLba + 16)
			data = self.readSectors(1)
			if data:
				id = data[1:6]
				if id == "CD001".encode("ASCII"):
					#could do further validation, but for now consider this good enough
					r = True
		except:
			pass
	
		#restore the previous position
		self.setSector(previousSector)
		return r
		
	def readIso9660(self, trackIndex = 0, volumeDescType = 1):
		t = self.trackByIndex(trackIndex)
		if not t:
			return None
			
		previousSector = self.currentSector
		r = None

		self.setSector(t.baseLba + 16)
		foundVolume = False
		while not foundVolume:
			volDesc = Iso9660VolumeDescriptor(self.readSectors(1))
			if volDesc.type == volumeDescType:
				foundVolume = True
				break
			elif volDesc.type == 0xFF:
				break
				
		if foundVolume:
			if volDesc.blockSize != t.userSize:
				print("Warning: ISO-9660 logical block size != track's user data size:", volDesc.blockSize, "vs", t.userSize)
			rootRecord = volDesc.rootRecord
			if not (rootRecord.flags & Iso9660_DirFlag_Directory):
				print("Warning: Expected root record to be a directory.")

			files = []
			processRecords = [rootRecord]
			while len(processRecords) > 0:
				record = processRecords.pop()
				if record.flags & Iso9660_DirFlag_Directory:
					self.setSector(record.dataLba)
					recordData = self.readSectors(volDesc.sizeToSectorCount(record.dataSize))
					if recordData:
						recordBs = NoeBitStream(recordData)
						while recordBs.tell() < record.dataSize:
							newRecord = Iso9660Record(recordBs, record)
							if newRecord.recordSize == 0:
								break
							if not newRecord.isSpecial():
								#note that we don't track directory records, so empty directories are ignored entirely
								processRecords.append(newRecord)
				else:
					imgFile = NoeImgFile(record.getFullPath(), record.dataLba, record.dataSize)
					imgFile.createDate = repr(record.recDate)
					files.append(imgFile)
					
			r = NoeImgVolume(volDesc.volId, repr(volDesc.createDate), repr(volDesc.modDate), files)
			
		#restore the previous position
		self.setSector(previousSector)
		return r
		
	def close(self):
		for track in self.tracks:
			track.close()
		
class NoeImgFile:
	def __init__(self, path, lba, size, flags = 0):
		self.path = path
		self.lba = lba
		self.size = size
		self.flags = flags
		self.createDate = ""
		self.modifyDate = ""
		
class NoeImgVolume:
	def __init__(self, volId, createDate, modifyDate, files):
		self.volId = volId
		self.createDate = createDate
		self.modifyDate = modifyDate
		self.files = files
		self.fileDict = None
		
	#assumes case-insensitive path
	def findFile(self, path):
		if not self.fileDict:
			self.fileDict = {}
			for file in self.files:
				self.fileDict[file.path.lower()] = file
				
		lPath = path.lower()
		if lPath not in self.fileDict:
			return None
		return self.fileDict[lPath]
		
class Iso9660VolumeDescriptor:
	def __init__(self, data):
		bs = NoeBitStream(data)
		self.type = bs.readUByte()
		self.id = bs.readBytes(5)
		self.version = bs.readUByte()
		if self.type == 0xFF:
			return
		bs.readUByte() #reserved
		self.sysId = noeAsciiFromBytes(bs.readBytes(32)).rstrip(" ")
		self.volId = noeAsciiFromBytes(bs.readBytes(32)).rstrip(" ")
		bs.readBytes(8) #reserved
		self.volSpace = bs.readUInt()
		bs.readUInt() #BE
		bs.readBytes(32) #reserved
		self.volSetSize = bs.readUInt()
		self.volSeqNum = bs.readUInt()
		self.blockSize = bs.readUShort()
		bs.readUShort() #BE
		self.pathTableSize = bs.readUInt()
		bs.readUInt() #BE
		self.pathTableLba = bs.readUInt()
		self.optionalPathTableLba = bs.readUInt()
		bs.readUInt() #BE
		bs.readUInt() #BE
		self.rootRecord = Iso9660Record(bs)
		self.volSetId = bs.readBytes(128)
		self.pubId = bs.readBytes(128)
		self.prepId = bs.readBytes(128)
		self.appId = bs.readBytes(128)
		self.copyrightId = bs.readBytes(37)
		self.abstractId = bs.readBytes(37)
		self.biblioId = bs.readBytes(37)
		self.createDate = Iso9660Date(bs)
		self.modDate = Iso9660Date(bs)
		self.expirDate = Iso9660Date(bs)
		self.effDate = Iso9660Date(bs)
		#currently discard the rest
		
	def sizeToSectorCount(self, size):
		return (size + (self.blockSize - 1)) // self.blockSize

Iso9660_DirFlag_Hidden = (1 << 0)
Iso9660_DirFlag_Directory = (1 << 1)
Iso9660_DirFlag_AssociatedFile = (1 << 2)
Iso9660_DirFlag_ExtendedAttr = (1 << 3)
Iso9660_DirFlag_Permissions = (1 << 4)
Iso9660_DirFlag_NotFinal = (1 << 7)
		
class Iso9660Record:
	def __init__(self, bs, parentRecord = None):
		ofs = bs.tell()
		self.recordSize = bs.readUByte()
		self.extendedSize = bs.readUByte()
		self.dataLba = bs.readUInt()
		bs.readUInt() #BE
		self.dataSize = bs.readUInt()
		bs.readUInt() #BE
		self.recDate = Iso9660Date()
		self.recDate.parseDirFormat(bs)
		self.flags = bs.readUByte() #Iso9660_DirFlag_*
		self.unitSize = bs.readUByte()
		self.gapSize = bs.readUByte()
		self.volSeqNum = bs.readUShort()
		bs.readUShort() #BE
		self.idLen = bs.readUByte()
		idData = bs.readBytes(self.idLen)
		self.id = noeAsciiFromBytes(idData)
		if self.idLen == 1 and idData[0] == 0:
			self.specialType = 1
		elif self.idLen == 1 and idData[0] == 1:
			self.specialType = 2
		else:
			self.specialType = 0
			si = self.id.rfind(";")
			if si >= 0:
				self.id = self.id[:si]
		#no need to read pad unless we actually want to parse extended data, since we're using the record size to skip ahead
		#if not (self.idLen & 1):
		#	bs.readUByte() #pad
		self.parentRecord = parentRecord
		bs.seek(ofs + self.recordSize, NOESEEK_ABS)
		
	def isSpecial(self):
		return self.specialType > 0
		
	def getFullPath(self):
		recs = [self]
		parent = self.parentRecord
		while parent:
			recs.append(parent)
			parent = parent.parentRecord
		path = ""
		for i in range(0, len(recs)):
			index = len(recs) - i - 1
			rec = recs[index]
			path += rec.id
			if index > 0 and len(path) > 0:
				path += "/"
		return path
		
class Iso9660PathTableEntry:
	def __init__(self, bs):
		self.idLen = bs.readUByte()
		self.extendedSize = bs.readUByte()
		self.recordLba = bs.readUInt()
		self.parentDirectoryIndex = bs.readUShort()
		self.id = noeAsciiFromBytes(bs.readBytes(self.idLen))
		if self.idLen & 1:
			bs.readUByte() #pad
		
class Iso9660Date:
	def __init__(self, bs = None):
		if bs:
			self.parseVDFormat(bs)
			
	def parseVDFormat(self, bs):
		self.year = int(noeAsciiFromBytes(bs.readBytes(4)))
		self.month = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.day = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.hour = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.minute = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.second = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.centisecond = int(noeAsciiFromBytes(bs.readBytes(2)))
		self.gmtOffset = bs.readByte() #in 15 minute intervals, starting at interval -48 (west) and running up to interval 52 (east)
		
	def parseDirFormat(self, bs):
		self.year = 1900 + bs.readUByte()
		self.month = bs.readUByte()
		self.day = bs.readUByte()
		self.hour = bs.readUByte()
		self.minute = bs.readUByte()
		self.second = bs.readUByte()
		self.centisecond = 0
		self.gmtOffset = bs.readByte()
		
	def __repr__(self):
		return "%04i-%02i-%02i %02i:%02i:%02i.%i"%(self.year, self.month, self.day, self.hour, self.minute, self.second, self.centisecond)
