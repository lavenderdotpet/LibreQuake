from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("PSO BML Archive", ".bml")
	noesis.setHandlerExtractArc(handle, bmlExtractArc)
	return 1

def bmlExportEntry(f, entryName, entryOffset, entryCompDataSize, entryDecompDataSize):
	print("Writing", entryName, "from offset", entryOffset, "at size", entryCompDataSize, "/", entryDecompDataSize)
	f.seek(entryOffset, NOESEEK_ABS)
	compData = f.read(entryCompDataSize)
	if entryCompDataSize == entryDecompDataSize or entryDecompDataSize == 0:
		rapi.exportArchiveFile(entryName, compData)
	else:
		decompData = rapi.decompPRS(compData, entryDecompDataSize)
		rapi.exportArchiveFile(entryName, decompData)
	
def bmlExtractArc(fileName, fileLen, justChecking):
	if fileLen < 64:
		return 0
		
	with open(fileName, "rb") as f:
		f.seek(4, NOESEEK_ABS)
		fileCount, version = noeUnpack("<II", f.read(8))
		verMajor = version & 0xFF
		verMinor = (version >> 8) & 0xFF
		if verMajor != 0x50:
			return 0
		if verMinor != 0 and verMinor != 1:
			return 0
		headerSize = 64 + 64 * fileCount
		if headerSize >= fileLen:
			return 0
			
		if justChecking:
			return 1

		alignedHeaderSize = (headerSize + 2047) & ~2047
		currentFileOffset = alignedHeaderSize
		f.seek(64, NOESEEK_ABS)
		bs = NoeBitStream(f.read(64 * fileCount))
		
		alignmentMinusOne = 31 if verMinor >= 1 else 2047
	
		for fileIndex in range(0, fileCount):
			entryName = bs.readBytes(32).decode("ASCII").rstrip("\0")
			entryOffset = currentFileOffset
			entryCompDataSize = bs.readUInt()
			bs.readUInt()
			entryDecompDataSize = bs.readUInt()

			entryPvmCompSize = bs.readUInt()
			entryPvmDecompSize = bs.readUInt()
			
			bs.seek(12, NOESEEK_REL)
			currentFileOffset = (currentFileOffset + entryCompDataSize + alignmentMinusOne) & ~alignmentMinusOne
	
			if entryPvmCompSize != 0:
				pvmOffset = currentFileOffset
				currentFileOffset = (currentFileOffset + entryPvmCompSize + alignmentMinusOne) & ~alignmentMinusOne
				pvmName = rapi.getExtensionlessName(entryName) + ".pvm"
				bmlExportEntry(f, pvmName, pvmOffset, entryPvmCompSize, entryPvmDecompSize)
	
			bmlExportEntry(f, entryName, entryOffset, entryCompDataSize, entryDecompDataSize)
			
		return 1
		
	return 0
