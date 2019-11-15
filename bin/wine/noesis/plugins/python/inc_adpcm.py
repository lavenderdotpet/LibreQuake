from inc_noesis import *

#see nocash PSX Specifications, "CDROM XA Audio ADPCM Compression"
psxFilterUTS = 1.0/64.0
psxFilter0Table = (0.0*psxFilterUTS, 60.0*psxFilterUTS, 115.0*psxFilterUTS, 98.0*psxFilterUTS, 122.0*psxFilterUTS)
psxFilter1Table = (0.0*psxFilterUTS, 0.0*psxFilterUTS, -52.0*psxFilterUTS, -55.0*psxFilterUTS, -60.0*psxFilterUTS)

def decodeShiftAndFilterPSX(shiftFilterByte):
	shiftOfs = (shiftFilterByte & 15)
	if shiftOfs >= 13:
		shiftOfs = 9
	filter = (((shiftFilterByte >> 4) & 15) & 7)
	if filter > 4:
		filter = 0 #should not occur
	return shiftOfs, filter

def decodeBlockPSXSPU(srcData, bps, sampleCount, oldSamples):
	shiftOfs, filter = decodeShiftAndFilterPSX(srcData[0])
	#srcData[1] is flags, but we're ignoring them
	shiftBase = 8 if bps == 8 else 12
	samplesInBytes = (sampleCount*bps)//8
	return rapi.decodeADPCMBlock(srcData[2:2+samplesInBytes], bps, sampleCount, shiftBase-shiftOfs, filter, psxFilter0Table, psxFilter1Table, oldSamples)
	
def getSectorInfoPSXCDXA(sectorData):
	#0-11 - sync data
	#12-15 - header
	#16-19 - sub-header
	#	16 - file number
	#	17 - channel number
	#	18 - bits: 0=eor, 1=video, 2=audio, 3=data, 4=trigger, 5=form2, 6=realtime, 7=eof
	#	19 - bits: 0-1=chan (0=mono, 1=stereo), 2-3=sample rate(0=37800, 1=18900), 4-5=bps(0=4, 1=8), 6=emphasis(0=off, 1=on), 7=unused 
	#20-24 - sub-header copy
	channelNum = sectorData[17]
	isStereo = (sectorData[19] & (1<<0)) != 0
	sampleRate = 18900 if (sectorData[19] & (1<<2)) != 0 else 37800
	bps = 8 if (sectorData[19] & (1<<4)) != 0 else 4
	return channelNum, isStereo, sampleRate, bps
	
def decodeSectorPSXCDXA(sectorData, oldSamplesLeft, oldSamplesRight, sampleScale = 0.0):
	pcmData = bytearray()
	if sectorData[15] == 2:
		#expecting mode 2
		channelNum, isStereo, sampleRate, bps = getSectorInfoPSXCDXA(sectorData)
		shiftBase = 8 if bps == 8 else 12
		
		#8bps may or may not work, documentation isn't clear on some points and i don't know of any games using it
		blockGroupSize = 128
		blockGroupCount = 18
		blockCount = 2 if bps == 8 else 4
	
		blockPCMDataList = []
		for blockGroupIndex in range(0, blockGroupCount):
			for blockIndex in range(0, blockCount):
				blockHeaderOfs = 24 + blockGroupIndex*blockGroupSize + 4
				blockDataOfs = blockHeaderOfs + 12
				blockGroupData = sectorData[blockDataOfs:blockDataOfs+blockGroupSize]
				#samples are all interleaved in blocks. stereo and mono are handled the same at this stage, except for mono we always use oldSamplesLeft.
				shiftOfs, filter = decodeShiftAndFilterPSX(sectorData[blockHeaderOfs+blockIndex*2])
				blockPCMData = rapi.decodeADPCMBlock(blockGroupData, bps, 28, shiftBase-shiftOfs, filter, psxFilter0Table, psxFilter1Table, oldSamplesLeft, blockIndex*8, 32, sampleScale)
				blockPCMDataList.append(blockPCMData)
				shiftOfs, filter = decodeShiftAndFilterPSX(sectorData[blockHeaderOfs+blockIndex*2 + 1])
				blockPCMData = rapi.decodeADPCMBlock(blockGroupData, bps, 28, shiftBase-shiftOfs, filter, psxFilter0Table, psxFilter1Table, oldSamplesRight if isStereo else oldSamplesLeft, blockIndex*8 + bps, 32, sampleScale)
				blockPCMDataList.append(blockPCMData)
				
		if isStereo:
			#interleave stereo samples
			for blockPairIndex in range(0, len(blockPCMDataList)//2):
				leftChannel = blockPCMDataList[blockPairIndex*2]
				rightChannel = blockPCMDataList[blockPairIndex*2 + 1]
				sampleCount = len(leftChannel)//2
				for sampleIndex in range(0, sampleCount): #2 bytes per sample
					pcmData += leftChannel[sampleIndex*2:sampleIndex*2+2]
					pcmData += rightChannel[sampleIndex*2:sampleIndex*2+2]
		else:
			for blockPCMData in blockPCMDataList:
				pcmData += blockPCMData
			
	return pcmData
