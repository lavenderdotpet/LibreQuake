from inc_noesis import *

#this script is designed to handle aladdin and some pre-release builds of the jungle book.
#other virgin games using chopper look to have received large modifications to the both data
#structure and organization after perry's departure.
def registerNoesisTypes():
	handle = noesis.register("Virgin MD Chopper ROM", ".bin;.md")
	noesis.setHandlerExtractArc(handle, chopperExtractArc)
	return 1

REQUIRED_MATCH_COUNT = 8
MAX_VALID_PART_COUNT = 128
MAX_TILE_SIZE = 16
BANK_OFFSETS = (0x9500, 0x9600, 0x9700)
SEARCH_FOR_POINTERS = True
CHOPPER_RT_VERSION = 1 #used in aladdin
#note that this is the default "mans" palette from Aladdin. there's not a nice way to correlate palette with frame within the rom, short of doing
#deep instruction and data-association analysis.
#you'll have to manually dig out and specify appropriate palettes for other games and frames.
DEFAULT_PALETTE_TEXT0 = r";	PALETTE $707,$763,$751,$642,$531,$420,$310,$200 ; Pens 0-7"
DEFAULT_PALETTE_TEXT1 = r";	PALETTE $401,$347,$236,$202,$444,$222,$777,$000 ; Pens 8-15"
	
class ChopperPart:
	def __init__(self, bs):
		self.infoAddr = bs.readUShort()
		if CHOPPER_RT_VERSION > 1:
			self.offset = (bs.readUShort(), bs.readUShort())
		else:
			self.offset = (bs.readUByte(), bs.readUByte())
		z0 = bs.readUShort()
		z1 = bs.readUShort()
		z2 = bs.readUShort()
		self.tileAddr = ((z0 - BANK_OFFSETS[0]) << 1) | ((z1 - BANK_OFFSETS[1]) << 9) | ((z2 - BANK_OFFSETS[2]) << 17)
		self.tileSize = bs.readUShort()
		
class ChopperTileInfo:
	def __init__(self, bs):
		self.addr = bs.readUInt() #actually 2 words, but unused here
		self.memSize = bs.readUShort()
		self.tileSize = bs.readUShort()
		self.tilePixelWidth = bs.readUByte()
		self.tilePixelHeight = bs.readUByte()
	def getTileWidth(self):
		return self.tilePixelWidth >> 3
	def getTileHeight(self):
		return self.tilePixelHeight >> 3
	def getTileKey(self):
		return (self.getTileWidth() << 16) | self.getTileHeight()
		
class ChopperFrame:
	def __init__(self, bs, fileLen):
		startOffset = bs.tell()
		partCount = bs.readUShort() + 1
		
		self.isValid = True
		self.offset = startOffset
		if partCount > MAX_VALID_PART_COUNT:
			self.isValid = False
		else:
			self.cboxMin = (bs.readUByte(), bs.readUByte())
			self.cboxMax = (bs.readUByte(), bs.readUByte())
			if CHOPPER_RT_VERSION > 1:
				self.glasses = (bs.readUByte(), bs.readUByte())
			self.parts = []
			for partIndex in range(0, partCount):
				part = ChopperPart(bs)
				if part.infoAddr >= fileLen or part.tileAddr >= fileLen:
					self.isValid = False
					break
				self.parts.append(part)

			if self.isValid:
				endOffset = bs.tell()
				self.structSize = endOffset - startOffset
				for part in self.parts:
					bs.seek(part.infoAddr, NOESEEK_ABS)
					part.info = ChopperTileInfo(bs)
					info = part.info
					if info.getTileWidth() <= 0 or info.getTileHeight() <= 0 or info.getTileWidth() > MAX_TILE_SIZE or info.getTileHeight() > MAX_TILE_SIZE:
						self.isValid = False
						break
				bs.seek(endOffset, NOESEEK_ABS)

class ChopperTileSet:
	def __init__(self, tileWidth, tileHeight):
		self.tileWidth = tileWidth
		self.tileHeight = tileHeight
		self.tileSize = (tileWidth * 8 * tileHeight * 8) >> 1
		self.data = NoeBitStream()
		self.addrDict = {}
	def getTileIndex(self, romStream, tileAddr):
		if tileAddr in self.addrDict:
			return self.addrDict[tileAddr]

		#if it's not cached by address, read the tile from rom data and write it into this tileset's stream
		tileIndex = self.data.tell() // self.tileSize
		self.addrDict[tileAddr] = tileIndex
		romStream.seek(tileAddr, NOESEEK_ABS)
		self.data.writeBytes(romStream.readBytes(self.tileSize))

		return tileIndex;
					
def chopperExtractArc(fileName, fileLen, justChecking):
	with open(fileName, "rb") as f:
		if fileLen <= 0x1000 or fileLen > 0x1000000:
			return 0
			
		bs = NoeBitStream(f.read(), NOE_BIGENDIAN)
		
		#expect pointer list to be word-aligned, and that pointers are somewhere near the beginning of rom.
		#note that there are distributions where the table is not longword-aligned, and doesn't necessarily
		#have to be word-aligned either.
		offset = 0x200
		
		bs.seek(0x100, NOESEEK_ABS)
		tag = bs.readUInt();
		if tag != 0x53454741:
			return 0
					
		#note that not all Chopper games will actually use a pointer list. for games that don't, you would
		#have to try to find the start of ChopperFrame data and parse from there. some games may also use
		#data structure variants of the frame structures. this script will not work as-is on those.
		satisfiedMatches = False
		if SEARCH_FOR_POINTERS:
			endOffset = 0x1000
			validStartOffset = -1
			expectedSize = -1
			lastPtr = -1
			while offset < endOffset:
				if validStartOffset >= 0 and (offset - validStartOffset) >= 4 * REQUIRED_MATCH_COUNT:
					satisfiedMatches = True
					break

				bs.seek(offset, NOESEEK_ABS)
				ptr = bs.readUInt()

				if validStartOffset >= 0:
					actualSize = (ptr - lastPtr)
					if actualSize != expectedSize:
						validStartOffset = -1
				
				if ptr > offset and ptr < (fileLen - 16):
					bs.seek(ptr, NOESEEK_ABS)
					frame = ChopperFrame(bs, fileLen)
					if frame.isValid:
						expectedSize = frame.structSize
						lastPtr = ptr
						if validStartOffset < 0:
							validStartOffset = offset
					else:
						validStartOffset = -1						
				else:
					validStartOffset = -1
				#note that this could potentially miss the start of valid data by running over from an invalid start
				offset += 4 if validStartOffset >= 0 else 2
		else:
			while offset < fileLen:
				bs.seek(offset, NOESEEK_ABS)
				matchCount = 0
				validStartOffset = offset
				while matchCount < REQUIRED_MATCH_COUNT:
					frame = ChopperFrame(bs, fileLen)
					if not frame.isValid:
						break
					matchCount += 1
				if matchCount >= REQUIRED_MATCH_COUNT:
					satisfiedMatches = True
					break
				offset += 2
		
		if not satisfiedMatches:
			return 0
		
		if justChecking:
			return 1
			
		frames = []
		if SEARCH_FOR_POINTERS:	
			offset = validStartOffset
			while offset <= (fileLen - 4):
				bs.seek(offset, NOESEEK_ABS)
				ptr = bs.readUInt()
				if ptr >= (fileLen - 16):
					break
				bs.seek(ptr, NOESEEK_ABS)
				frame = ChopperFrame(bs, fileLen)
				if not frame.isValid:
					break
				frames.append(frame)
				offset += 4
		else:
			bs.seek(validStartOffset, NOESEEK_ABS)
			while bs.tell() <= (fileLen - 16):
				frame = ChopperFrame(bs, fileLen)
				if not frame.isValid:
					break
				frames.append(frame)
				
		print("Parsed", len(frames), "Chopper frames. Ended at offset:", offset)

		textBs = NoeBitStream()
		tileSets = {}
		
		#now we spit out the higher-level representation of this data with tiles split across multiple files sorted by size.
		#this resembles (although still omits a few things) data directly exported by Chopper for a Mega Drive target, and
		#noesis can load this data directly.
		textBs.writeString(DEFAULT_PALETTE_TEXT0 + "\n", 0)
		textBs.writeString(DEFAULT_PALETTE_TEXT1 + "\n\n", 0)
		
		for frameIndex in range(0, len(frames)):
			frame = frames[frameIndex]
			textBs.writeString("UN_FRAME%04i:\n"%frameIndex, 0)
			textBs.writeString("	PRTS %i\n"%len(frame.parts), 0)
			textBs.writeString("	T_LF %i,%i\n"%(frame.cboxMin[0], frame.cboxMin[1]), 0)
			textBs.writeString("	B_RT %i,%i\n\n"%(frame.cboxMax[0], frame.cboxMax[1]), 0)
			for part in frame.parts:
				info = part.info
				tileKey = info.getTileKey()
				if tileKey not in tileSets:
					tileSets[tileKey] = ChopperTileSet(info.getTileWidth(), info.getTileHeight())
				tileNum = tileSets[tileKey].getTileIndex(bs, part.tileAddr) + 1
				textBs.writeString("	SIZE %i,%i\n"%(info.getTileWidth(), info.getTileHeight()), 0)
				textBs.writeString("	CORD %i,%i\n"%(part.offset[0], part.offset[1]), 0)
				textBs.writeString("	NUMB %i\n\n"%tileNum, 0)
				
		print("Writing SPRTLIST.68K")
		rapi.exportArchiveFile("SPRTLIST.68K", textBs.getBuffer())
		
		for tileSet in tileSets.values():
			setName = "SPR_%iX%iA.SEG"%(tileSet.tileWidth, tileSet.tileHeight)
			print("Writing", setName)
			rapi.exportArchiveFile(setName, tileSet.data.getBuffer())
	return 1
