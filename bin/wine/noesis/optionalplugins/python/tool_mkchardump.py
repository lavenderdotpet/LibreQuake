from inc_noesis import *
import sys

MK_OBEY_FLIP = True

def registerNoesisTypes():
	handle = noesis.registerTool("MK1 Dump", mk1DumpToolMethod, "Dump frames from MK1 revision 5.0.")
	handle = noesis.registerTool("MK2 Dump", mk2DumpToolMethod, "Dump frames from MK2 revision 3.1.")
	handle = noesis.registerTool("UMK3 Dump", umk3DumpToolMethod, "Dump frames from UMK3 revision 1.2.")
	return 1
	
def readAndInterleaveSet(imageBasePath, imageSet, imageSize):
	imageCount = len(imageSet)
	interleavedData = bytearray(imageSize * imageCount)
	for imageIndex in range(0, imageCount):
		imagePath = imageSet[imageIndex]
		imageFilePath = imageBasePath + "\\" + imagePath
		imageFileSize = os.path.getsize(imageFilePath)
		if imageFileSize != imageSize:
			print("Bad/no code image -", imageFileSize, "-", imageFilePath)
			return None
		print("Loading", imageFilePath)
		with open(imageFilePath, "rb") as f:
			imageData = f.read()
			for offset in range(0, imageSize):
				interleavedData[offset * imageCount + imageIndex] = imageData[offset]
	return interleavedData

def readStandardSets(imageBasePath, codeImageSize, codeImages, gfxImageSize, gfxImageSetSize, gfxImageSets):
	codeData = readAndInterleaveSet(imageBasePath, codeImages, codeImageSize)
	if codeData is None:
		return None
	gfxData = bytearray()
	for gfxImageSet in gfxImageSets:
		gfxSetData = readAndInterleaveSet(imageBasePath, gfxImageSet, gfxImageSize)
		if gfxSetData is None:
			return None
		gfxData += gfxSetData
	return codeData, gfxData
	
MK_FRAME_EXTENT = 4096
	
MK_ANIM_FLAG_FLIPX = (1 << 0)
	
MK_TITLE_MK1 = 0
MK_TITLE_MK2 = 1
MK_TITLE_MK3 = 2
MK_TITLE_UMK3 = 3
	
class MkAnimPart:
	def __init__(self, bs, mkTitle):
		self.width = bs.readUShort()
		self.height = bs.readUShort()
		self.x = -bs.readShort()
		self.y = -bs.readShort()
		self.gfxAddr = bs.readUInt()
		if mkTitle == MK_TITLE_MK1: #dma not explicitly stored, gfx address absolute
			self.dmaControl = 0x502 + (6 << 12)
			if self.gfxAddr < 0x2000000:
				noesis.doException("Expected gfx address to be absolute.")
			self.gfxAddr -= 0x2000000
		else:
			self.dmaControl = bs.readUShort() | 2
		
class MkAnimFrame:
	def __init__(self, animIndex, animFlags):
		self.animParts = []
		self.mins = [MK_FRAME_EXTENT, MK_FRAME_EXTENT]
		self.maxs = [-MK_FRAME_EXTENT, -MK_FRAME_EXTENT]
		self.animIndex = animIndex
		self.animFlags = animFlags
	def addPart(self, part):
		self.animParts.append(part)
		self.mins = [min(part.x, self.mins[0]), min(part.y, self.mins[1])]
		self.maxs = [max(part.x + part.width, self.maxs[0]), max(part.y + part.height, self.maxs[1])]

def mkGenericDump(imageBasePath, codeData, gfxData, tableSetCount, charCount, charAnimCounts, bossCharAnimCounts, tableBaseAddr, palAddr, addrBase, firstBossIndex, mkTitle):
	codeBs = NoeBitStream(codeData)
	for tableIndex in range(0, tableSetCount):
		tableAddr = tableBaseAddr + tableIndex * 4 * charCount
		for charIndex in range(0, charCount):
			codeBs.seek(tableAddr + charIndex * 4, NOESEEK_ABS)
			charTableAddr = codeBs.readUInt() - addrBase
			
			codeBs.seek(palAddr + charIndex * 4, NOESEEK_ABS)
			charPalAddr = codeBs.readUInt() - addrBase
			
			#assume all these addresses are byte-aligned
			codeBs.seek(charPalAddr >> 3, NOESEEK_ABS)
			colorCount = codeBs.readUShort()
			palData = rapi.imageDecodeRaw(codeBs.readBytes(colorCount * 2), colorCount, 1, "b5g5r5p1")
			
			codeBs.seek(charTableAddr >> 3, NOESEEK_ABS)

			print("Parsing table", tableIndex, "character", charIndex)
	
			animAddrs = []
			animCounts = charAnimCounts if charIndex < firstBossIndex else bossCharAnimCounts
			for animIndex in range(0, animCounts[tableIndex]):
				animAddr = codeBs.readUInt()
				if animAddr >= addrBase:
					if mkTitle != MK_TITLE_UMK3 or animIndex != 63: #special-case, ignore 63, list isn't always terminated
						if mkTitle != MK_TITLE_MK2 or animIndex != 61: #another special-case, dismembered head lists appear to point directly to MkAnimPart
							if mkTitle != MK_TITLE_MK1 or (animIndex != 24 and animIndex != 26 and animIndex != 60 and animIndex != 67 and animIndex != 85): #similar cases for mk1
								animAddrs.append(animAddr - addrBase)
				
			print("Parsing", len(animAddrs), "animations.")
			
			allFramesMins = [MK_FRAME_EXTENT, MK_FRAME_EXTENT]
			allFramesMaxs = [-MK_FRAME_EXTENT, -MK_FRAME_EXTENT]
			animFrames = []
			
			for animIndex in range(0, len(animAddrs)):
				animAddr = animAddrs[animIndex]
				codeBs.seek(animAddr >> 3, NOESEEK_ABS)
				if animAddr & 7:
					print("Expected anim address to be byte-aligned.")
					return -1
				
				animPartListAddrs = []
				animFlags = 0
				while True:
					animPartListAddr = codeBs.readUInt()
					if animPartListAddr <= 1: #for now, let "jump" end parsing immediately
						break
					#possible todo - deal with other meaningful values
					if animPartListAddr >= addrBase:
						animPartListAddrs.append([animPartListAddr - addrBase, animFlags])
					else:
					#try to skip over currently-unused data. only up to 6 used in mk1, but seems in keeping with the same values all the way up through umk3.
						if animPartListAddr == 1 or animPartListAddr == 4 or animPartListAddr == 6 or animPartListAddr == 7 or animPartListAddr == 10 or animPartListAddr == 11 or animPartListAddr == 12 or animPartListAddr == 14:
							codeBs.readUInt()
						elif animPartListAddr == 3 or animPartListAddr == 15:
							codeBs.readUShort()
						elif animPartListAddr == 8:
							if mkTitle == MK_TITLE_MK2:
								codeBs.readUShort()
							else:
								codeBs.readUInt()
							codeBs.readUInt()
						elif animPartListAddr == 2 and MK_OBEY_FLIP:
							animFlags ^= MK_ANIM_FLAG_FLIPX
							if len(animPartListAddrs) > 0: #seems to also apply to previous frame
								animPartListAddrs[len(animPartListAddrs) - 1][1] ^= MK_ANIM_FLAG_FLIPX
						
				for animPartListAddr, animFlags in animPartListAddrs:
					codeBs.seek(animPartListAddr >> 3, NOESEEK_ABS)
					if animPartListAddr & 7:
						print("Expected anim part list address to be byte-aligned.")
						return -1
					
					frame = MkAnimFrame(animIndex, animFlags)
					
					animPartAddrs = []
					while True:
						animPartAddr = codeBs.readUInt()
						if animPartAddr == 0:
							break
						animPartAddrs.append(animPartAddr - addrBase)
					
					for animPartAddr in animPartAddrs:
						codeBs.seek(animPartAddr >> 3, NOESEEK_ABS)
						if animPartAddr & 7:
							print("Expected anim part address to be byte-aligned.")
							return -1
						frame.addPart(MkAnimPart(codeBs, mkTitle))
					
					if len(frame.animParts) > 0:
						#print("frame bounds:", frame.mins, frame.maxs)
						allFramesMins = [min(frame.mins[0], allFramesMins[0]), min(frame.mins[1], allFramesMins[1])]
						allFramesMaxs = [max(frame.maxs[0], allFramesMaxs[0]), max(frame.maxs[1], allFramesMaxs[1])]
						animFrames.append(frame)
			
			if len(animFrames) > 0:
				outDir = imageBasePath + "\\" + "noesis_gfxdump\\"
				if not os.path.exists(outDir):
					os.makedirs(outDir)
					
				print("Writing character", charIndex, "frames to", outDir)
			
				allFramesSize = [allFramesMaxs[0] - allFramesMins[0], allFramesMaxs[1] - allFramesMins[1]]
				allFramesOffset = [-allFramesMins[0], -allFramesMins[1]]
				lastAnimIndex = -1
				firstFrameIndex = 0
				for animFrameIndex in range(0, len(animFrames)):
					frame = animFrames[animFrameIndex]
					if frame.animIndex != lastAnimIndex:
						firstFrameIndex = animFrameIndex
						lastAnimIndex = frame.animIndex
					
					extraDmaBits = 0
					if frame.animFlags & MK_ANIM_FLAG_FLIPX:
						extraDmaBits |= 16
						
					canvasRgba = bytearray([0] * allFramesSize[0] * allFramesSize[1] * 4)
					for part in frame.animParts:
						if frame.animFlags & MK_ANIM_FLAG_FLIPX:
							offset = part.x - frame.mins[0]
							frameWidth = frame.maxs[0] - frame.mins[0]
							partX = frame.mins[0] + (frameWidth - offset - part.width)
						else:
							partX = part.x
						rapi.mw_tw_dmagfxcopy(canvasRgba, allFramesOffset[0] + partX, allFramesOffset[1] + part.y, allFramesSize[0], allFramesSize[1], palData, gfxData, part.dmaControl | extraDmaBits, part.gfxAddr, part.width, part.height)
						
					texName = outDir + "_gfx_char%02i_anim%02i_frame%02i.png"%(charIndex, frame.animIndex, animFrameIndex - firstFrameIndex)
					tex = NoeTexture(texName, allFramesSize[0], allFramesSize[1], canvasRgba, noesis.NOESISTEX_RGBA32)
					noesis.saveImageRGBA(texName, tex)						
	return 0
		

def umk3Dump(imageBasePath):
	codeImageSize = 512 * 1024
	codeImages = ("l1.2_mortal_kombat_3_u54_ultimate.u54", "l1.2_mortal_kombat_3_u63_ultimate.u63")
	gfxImageSize = 1024 * 1024
	gfxImageSetSize = 4
	gfxImageSets = (
		("l1_mortal_kombat_3_u133_game_rom.u133", "l1_mortal_kombat_3_u132_game_rom.u132", "l1_mortal_kombat_3_u131_game_rom.u131", "l1_mortal_kombat_3_u130_game_rom.u130"),
		("l1_mortal_kombat_3_u129_game_rom.u129", "l1_mortal_kombat_3_u128_game_rom.u128", "l1_mortal_kombat_3_u127_game_rom.u127", "l1_mortal_kombat_3_u126_game_rom.u126"),
		("l1_mortal_kombat_3_u125_game_rom.u125", "l1_mortal_kombat_3_u124_game_rom.u124", "l1_mortal_kombat_3_u123_game_rom.u123", "l1_mortal_kombat_3_u122_game_rom.u122"),
		("umk-u121.bin", "umk-u120.bin", "umk-u119.bin", "umk-u118.bin"),
		("umk-u121.bin", "umk-u120.bin", "umk-u119.bin", "umk-u118.bin"), #intentionally duplicated to fill gap
		("umk-u113.bin", "umk-u112.bin", "umk-u111.bin", "umk-u110.bin")
	)
	
	dataSet = readStandardSets(imageBasePath, codeImageSize, codeImages, gfxImageSize, gfxImageSetSize, gfxImageSets)
	if dataSet is None:
		return -1
	codeData, gfxData = dataSet

	#feel free to point this at other addresses if you want to dig around for some additional tables
	tableSetCount = 1 #2 (second table is good for a lot of characters, but seems to have some garbage data for others)
	charCount = 26
	charAnimCounts = (73, 5)
	bossCharAnimCounts = (26, 0)
	tableBaseAddr = 0x60572
	palAddr = 0x6091C
	#address list for alt palettes follows palette list directly, could use this for alternate colors
	#palAddr = 0x60984
	addrBase = 0xFF800000
	firstBossIndex = 24
	
	return mkGenericDump(imageBasePath, codeData, gfxData, tableSetCount, charCount, charAnimCounts, bossCharAnimCounts, tableBaseAddr, palAddr, addrBase, firstBossIndex, MK_TITLE_UMK3)
				

def mk2Dump(imageBasePath):
	codeImageSize = 512 * 1024
	codeImages = ("uj12.l31", "ug12.l31")
	gfxImageSize = 1024 * 1024
	gfxImageSetSize = 4
	gfxImageSets = (
		("ug14-vid", "uj14-vid", "ug19-vid", "uj19-vid"),
		("ug16-vid", "uj16-vid", "ug20-vid", "uj20-vid"),
		("ug17-vid", "uj17-vid", "ug22-vid", "uj22-vid")
	)
	
	dataSet = readStandardSets(imageBasePath, codeImageSize, codeImages, gfxImageSize, gfxImageSetSize, gfxImageSets)
	if dataSet is None:
		return -1
	codeData, gfxData = dataSet

	#feel free to point this at other addresses if you want to dig around for some additional tables
	tableSetCount = 1
	charCount = 17
	charAnimCounts = (65, 0)
	bossCharAnimCounts = (10, 0) #possible fixme - bogus, varying counts for Kintaro and Shao Kahn
	tableBaseAddr = 0x20C2A
	palAddr = 0x20F22
	#as with umk3, alternate colors directly follow the above palette table
	addrBase = 0xFF800000
	firstBossIndex = 12 #possible fixme - Smoke/Noob/Jade come after Kintaro and Shao Kahn
	
	return mkGenericDump(imageBasePath, codeData, gfxData, tableSetCount, charCount, charAnimCounts, bossCharAnimCounts, tableBaseAddr, palAddr, addrBase, firstBossIndex, MK_TITLE_MK2)

	
def mk1r4Dump(imageBasePath):
	codeImageSize = 512 * 1024
	codeImages = ("mkr4uj12.bin", "mkr4ug12.bin")
	gfxImageSize = 512 * 1024
	gfxImageSetSize = 4
	gfxImageSets = (
		("mkt-ug14.bin", "mkt-uj14.bin", "mkt-ug19.bin", "mkt-uj19.bin"),
		("mkt-ug16.bin", "mkt-uj16.bin", "mkt-ug20.bin", "mkt-uj20.bin"),
		("mkt-ug17.bin", "mkt-uj17.bin", "mkt-ug22.bin", "mkt-uj22.bin")
	)
	
	dataSet = readStandardSets(imageBasePath, codeImageSize, codeImages, gfxImageSize, gfxImageSetSize, gfxImageSets)
	if dataSet is None:
		return -1
	codeData, gfxData = dataSet

	#feel free to point this at other addresses if you want to dig around for some additional tables
	tableSetCount = 1
	charCount = 9
	charAnimCounts = (86, 0)
	bossCharAnimCounts = (4, 0) #possible fixme - bogus, varying counts for Goro and Shang Tsung - also need to support entries that point directly to frame data, which are unique per-boss
	tableBaseAddr = 0x9C984
	palAddr = 0x90734
	#as with umk3, alternate colors directly follow the above palette table
	addrBase = 0xFF800000
	firstBossIndex = 7
	
	return mkGenericDump(imageBasePath, codeData, gfxData, tableSetCount, charCount, charAnimCounts, bossCharAnimCounts, tableBaseAddr, palAddr, addrBase, firstBossIndex, MK_TITLE_MK1)


def mk1Dump(imageBasePath):
	codeImageSize = 512 * 1024
	codeImages = ("mkt-uj12.bin", "mkt-ug12.bin")
	gfxImageSize = 512 * 1024
	gfxImageSetSize = 4
	gfxImageSets = (
		("mkt-ug14.bin", "mkt-uj14.bin", "mkt-ug19.bin", "mkt-uj19.bin"),
		("mkt-ug16.bin", "mkt-uj16.bin", "mkt-ug20.bin", "mkt-uj20.bin"),
		("mkt-ug17.bin", "mkt-uj17.bin", "mkt-ug22.bin", "mkt-uj22.bin")
	)
	
	dataSet = readStandardSets(imageBasePath, codeImageSize, codeImages, gfxImageSize, gfxImageSetSize, gfxImageSets)
	if dataSet is None:
		return -1
	codeData, gfxData = dataSet

	#feel free to point this at other addresses if you want to dig around for some additional tables
	tableSetCount = 1
	charCount = 9
	charAnimCounts = (86, 0)
	bossCharAnimCounts = (4, 0) #possible fixme - bogus, varying counts for Goro and Shang Tsung - also need to support entries that point directly to frame data, which are unique per-boss
	tableBaseAddr = 0x9C972
	palAddr = 0x90734
	#as with umk3, alternate colors directly follow the above palette table
	addrBase = 0xFF800000
	firstBossIndex = 7
	
	return mkGenericDump(imageBasePath, codeData, gfxData, tableSetCount, charCount, charAnimCounts, bossCharAnimCounts, tableBaseAddr, palAddr, addrBase, firstBossIndex, MK_TITLE_MK1)


def mkDumpToolMethod(dumpMethod):
	imageBasePath = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Load Image", "Select location of ROM data.", noesis.getSelectedDirectory(), None)
	if not imageBasePath:
		return 0

	noesis.logPopup()
		
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
		
	r = dumpMethod(imageBasePath)

	noesis.freeModule(noeMod)
	
	return r

def mk1r4DumpToolMethod(toolIndex):
	return mkDumpToolMethod(mk1r4Dump)

def mk1DumpToolMethod(toolIndex):
	return mkDumpToolMethod(mk1Dump)
	
def mk2DumpToolMethod(toolIndex):
	return mkDumpToolMethod(mk2Dump)
	
def umk3DumpToolMethod(toolIndex):
	return mkDumpToolMethod(umk3Dump)
