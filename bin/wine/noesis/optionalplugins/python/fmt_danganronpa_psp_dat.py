from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Danganronpa PSP DAT Archive", ".dat")
	noesis.setHandlerExtractArc(handle, datExtractArc)

	handle = noesis.register("Danganronpa PSP PAK Archive", ".pak")
	noesis.setHandlerExtractArc(handle, pakExtractArc)
	
	return 1
	
#these constants may change depending on game distribution/sku.
#more foolproof thing to do here is probably to checksum some code that references the table, found that code, then dig
#the correct offset out of the given instruction to get at the elf section offset containing the offsets we want.
UMDIMAGE_DAT_FTOFS = 1016392
UMDIMAGE_DAT_BESTVER_FTOFS = 1004032
UMDIMAGE2_DAT_FTOFS_FROM_END_OF_FIRST = 32

def datExtractArc(fileName, fileLen, justChecking):
	if fileLen < 4:
		return 0
	arcName = rapi.getLocalFileName(fileName).lower()
	if arcName != "umdimage.dat" and arcName != "umdimage2.dat":
		return 0

	ebootPath = rapi.getDirForFilePath(fileName) + "../SYSDIR/EBOOT.BIN"
	try:
		with open(fileName, "rb") as datFile:
			with open(ebootPath, "rb") as ebootFile:
				fileCount = noeUnpack("<i", datFile.read(4))[0]
				if fileCount <= 0:
					noesis.doException("Unexpected file count.")
					
				if justChecking: #it's valid
					return 1
					
				ebootData = ebootFile.read()
				elfDec = NoeBitStream(rapi.callExtensionMethod("decrypt_eboot", ebootData))
				elfDec.seek(56, NOESEEK_ABS)
				elfHeaderSize = elfDec.readUInt()
				if elfHeaderSize <= 0:
					noesis.doException("Unexpected ELF header size.")

				isBestVer = elfHeaderSize == 160
				firstImageName = "umdimage2.dat" if isBestVer else "umdimage.dat"
				secondImageName = "umdimage.dat" if isBestVer else "umdimage2.dat"
				isSecondImage = arcName == secondImageName

				baseNameOfs = elfHeaderSize
				baseOfs = 0
				ftOfs = UMDIMAGE_DAT_BESTVER_FTOFS if isBestVer else UMDIMAGE_DAT_FTOFS

				if isSecondImage: #offset for second image
					with open(rapi.getDirForFilePath(fileName) + firstImageName, "rb") as firstDatFile:
						firstFileCount = noeUnpack("<i", firstDatFile.read(4))[0]
						baseOfs = firstFileCount * 12 + UMDIMAGE2_DAT_FTOFS_FROM_END_OF_FIRST
						print("Base offset for second image entries:", ftOfs + baseOfs)
						
				elfDec.seek(ftOfs + baseOfs, NOESEEK_ABS)
				fileEntries = []
				print("Parsing offset", ftOfs + baseOfs, "for", fileCount, "file entries...")
				for fileIndex in range(0, fileCount):
					entryNameOfsWithoutOffset = elfDec.readUInt()
					entryNameOfs = baseNameOfs + entryNameOfsWithoutOffset
					entryOfs = elfDec.readUInt()
					entrySize = elfDec.readUInt()
					fileEntries.append((entryNameOfs, entryOfs, entrySize))
					
				extractedCount = 0
				for entryNameOfs, entryOfs, entrySize in fileEntries:
					if entrySize > 0:
						elfDec.seek(entryNameOfs, NOESEEK_ABS)
						entryName = bytearray()
						while True:
							c = elfDec.readByte()
							if c == 0:
								break
							entryName.append(c)
						entryNameStr = entryName.decode("ASCII").rstrip("\0")
						extractedCount += 1
						print("Writing", entryNameStr, "at offset", entryOfs, "and size", entrySize, "-", extractedCount, "/", fileCount)
						datFile.seek(entryOfs, NOESEEK_ABS)
						rapi.exportArchiveFile(entryNameStr, datFile.read(entrySize))
					
				return 1
	except:
		return 0

	return 0

def pakExtractArc(fileName, fileLen, justChecking):
	if fileLen < 4:
		return 0

	try:
		with open(fileName, "rb") as pakFile:
			fileCount = noeUnpack("<i", pakFile.read(4))[0]
			if fileCount <= 0 or (4 + fileCount * 4) >= fileLen:
				return 0

			fileOffsets = noeUnpack("<" + "i" * fileCount, pakFile.read(4 * fileCount))
			for fileOffsetIndex in range(0, fileCount):
				fileOffset = fileOffsets[fileOffsetIndex]
				if fileOffsetIndex < 0 or fileOffsetIndex >= fileLen:
					return 0
					
			if justChecking:
				return 1
				
			for fileOffsetIndex in range(0, fileCount):
				fileOffset = fileOffsets[fileOffsetIndex]
				nextFileOffset = fileOffsets[fileOffsetIndex + 1] if fileOffsetIndex < (fileCount - 1) else fileLen
				fileSize = nextFileOffset - fileOffset
				pakFile.seek(fileOffset, NOESEEK_ABS)
				fileData = pakFile.read(fileSize)
				fileExt = ".bin"
				if len(fileData) >= 11:
					if fileData[:11] == "MIG.00.1PSP".encode("ASCII"):
						fileExt = ".gim"
					elif fileData[:11] == "OMG.00.1PSP".encode("ASCII"):
						fileExt = ".gmo"
				fileName = "%04i"%fileOffsetIndex + fileExt
				print("Writing", fileName)
				rapi.exportArchiveFile(fileName, fileData)
				
			return 1
	except:
		return 0

	return 0
