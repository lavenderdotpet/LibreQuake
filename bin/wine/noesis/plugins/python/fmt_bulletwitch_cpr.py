#Bullet Witch cpr extraction and dds conversion

from inc_noesis import *

import time

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Bullet Witch CPR Model/Textures", ".cpr;.czr")
	noesis.setHandlerTypeCheck(handle, cprCheckType)
	noesis.setHandlerLoadModel(handle, cprLoadModel)
	#noesis.logPopup()
	return 1


CPR_HEADER_ID = 0x31525043 #"CPR1"
CPR_ENTRY_SIZE = 48
CPR_TYPE_DDS = 0x20534444 #"DDS "
CPR_TYPE_RESU = 0x52455355 #"RESU"
CPR_TYPE_BVXD = 0x42565844 #"BVXD"
CPR_TYPE_BIXD = 0x42495844 #"BIXD"
CPR_MDLHDR_ID = 0x56465832 #"VFX2"
CPR_CHUNKHDR_ID = 0x434E4B48 #"CNKH"
CPR_TEXLISTHDR_ID = 0x544C5354 #"TLST"
CPR_SKELHDR_ID = 0x5F424C42 #"_BLB"
CZR_COMPRESSION_MARKER = 0x484C5A34 #"HLZ4"

class CprEntry:
	def __init__(self, data, nameStream):
		self.entryData = data
		entryInfo = noeUnpackFrom(">iii", data, 0)
		self.type = entryInfo[0]

		nameStream.seek(entryInfo[1], NOESEEK_ABS) #offset to name string
		self.name = nameStream.readString()
		nameStream.seek(entryInfo[2], NOESEEK_ABS) #offset to directory name string
		self.dirName = nameStream.readString().replace(".", "/")

		entryInfo = noeUnpackFrom(">ii", data, 24)
		self.infoOfs = entryInfo[0]
		self.infoSize = entryInfo[1]

		entryInfo = noeUnpackFrom(">ii", data, 32)
		self.dataOfs = entryInfo[0]
		self.dataSize = entryInfo[1]
	def __repr__(self):
		return self.name + "(" + repr(self.dataOfs) + "," + repr(self.dataSize) + ")"

class CprIDX:
	def __init__(self, bufferIndex):
		self.bufferIndex = bufferIndex

class CprVTX:
	def __init__(self, rawBytes, isShape):
		entryInfo = noeUnpackFrom(">iiii", rawBytes, 0)
		self.bufferIndex = entryInfo[1]
		self.vertSize = entryInfo[3]
		self.isShape = isShape

class CprTexRef:
	def __init__(self, texType, texIdx, texIdxB):
		self.texType = texType
		self.texIdx = texIdx
		self.texIdxB = texIdxB
	def __repr__(self):
		return "(tref:" + self.texType + ",idx:" + repr(self.texIdx) + ")"

class CprKNS2:
	def __init__(self, texRefs):
		self.texRefs = texRefs
	def __repr__(self):
		return repr(self.texRefs)

#contains information about each vertex component
class CprVDCLEntry:
	def __init__(self, rawBytes):
		dclInfo = noeUnpackFrom(">HHiHH", rawBytes, 0)
		self.shapeFlag = dclInfo[0]
		self.cmpOfs = dclInfo[1]
		self.cmpType = dclInfo[2]
		self.cmpElemType = dclInfo[3]
	def __repr__(self):
		return "(elemtype:" + repr(self.cmpElemType) + ",ofs:" + repr(self.cmpOfs) + ",type:" + repr(self.cmpType) + ",shape:" + repr(self.shapeFlag) + ")"
class CprVDCL:
	def __init__(self, rawBytes):
		self.decodedNormals = None #keep a decoded buffer on each vdcl
		self.entries = []
		self.shapeIndex = -1
		maxEntries = (len(rawBytes)-4) // 12
		for i in range(0, maxEntries):
			eofs = 4 + i*12
			self.entries.append(CprVDCLEntry(rawBytes[eofs:eofs+12]))
	def __repr__(self):
		return repr(self.entries)

	def createBuffers(self, cprFile, shapesOfs):
		idx = self.idx
		vtx = self.vtx
		if idx.bufferIndex < 0 or idx.bufferIndex >= len(cprFile.idxEntries):
			noesis.doException("Index buffer out of range")
		if vtx.bufferIndex < 0 or vtx.bufferIndex >= len(cprFile.vtxEntries):
			noesis.doException("Vertex buffer out of range")

		self.vdclPos = cprFindDecl(self.entries, 0, 2761657)
		if self.vdclPos is None:
			return

		self.vdclNrm = cprFindDecl(self.entries, 3, 2761095)
		if self.vdclNrm is not None and self.vdclNrm.shapeFlag != 0:
			print("WARNING: Found shape flag on normal component, this is not handled") #haven't seen this happen, but it seems possible/reasonable
			self.vdclNrm = None
		self.vdclUV = cprFindDecl(self.entries, 5, 2892639)
		self.vdclBoneIdx = cprFindDecl(self.entries, 1, 1712774)
		self.vdclBoneWgt = cprFindDecl(self.entries, 1, 1712262)

		vtxEntry = cprFile.vtxArEntries[vtx.bufferIndex]
		self.vtxSize = vtx.vertSize
		self.vtxBuffer = cprFile.getEntryBytes(vtxEntry)
		if self.vdclPos.shapeFlag != 0: #use a shape buffer
			if self.shapeIndex < 0:
				noesis.doException("Vertex decl unexpectedly sets shape flag without a shape index")
			vtxEntryPos = cprFile.vtxArEntries[shapesOfs + self.shapeIndex]
			self.vtxSizePos = 12
			self.vtxBufferPos = cprFile.getEntryBytes(vtxEntryPos)
		else:
			vtxEntryPos = cprFile.vtxArEntries[vtx.bufferIndex]
			self.vtxSizePos = vtx.vertSize
			self.vtxBufferPos = self.vtxBuffer
		idxEntry = cprFile.idxArEntries[idx.bufferIndex]
		self.idxBuffer = cprFile.getEntryBytes(idxEntry)

		if self.vdclNrm is not None:
			self.decodedNormals = rapi.decodeNormals32(self.vtxBuffer[self.vdclNrm.cmpOfs:], self.vtxSize, -10, -10, -10, NOE_BIGENDIAN) #convert encoded normals into an array of floats
			self.decodedNormals = rapi.swapEndianArray(self.decodedNormals, 4) #swap endianness back for each float before drawing in big-endian mode
		else:
			self.decodedNormals = None


class CprDIP:
	def __init__(self, rawBytes, boneMap):
		dipInfo = noeUnpackFrom(">iiiiii", rawBytes, 0)
		self.unkA = dipInfo[0]
		self.vertStart = dipInfo[1]
		self.unkC = dipInfo[2]
		self.unkD = dipInfo[3]
		self.triStart = dipInfo[4]
		self.numTris = dipInfo[5]
		self.boneMap = boneMap

class CprDGRP:
	def __init__(self, dipList, activeKNS2, activeVDCL):
		self.dipList = dipList
		self.kns2 = activeKNS2
		self.vdcl = activeVDCL

#see if the file in question is a valid cpr file
class CprFile:
	def __init__(self, bs):
		self.bs = bs
		self.texNameList = []
		self.boneList = []
		self.vtxArEntries = []
		self.idxArEntries = []
		self.entries = []
		self.vdclEntries = []
		self.vtxEntries = []
		self.svtxEntries = []
		self.idxEntries = []
		self.dgrpEntries = []

	def parseHeader(self):
		bs = self.bs
		if bs.getSize() < 96:
			return 0

		bs.seek(0, NOESEEK_ABS)
		ver = bs.read(">iiii")
		if ver[0] != CPR_HEADER_ID or ver[1] != 1 or ver[2] != 0x11223344 or ver[3] != 0:
			return 0
		hdrInfo = bs.read(">iiiiiiii")
		self.entriesSize = hdrInfo[0]
		self.unkSize = hdrInfo[1]
		self.namesSize = hdrInfo[2]
		self.finfoSize = hdrInfo[3]
		self.dataSize = hdrInfo[4]
		#self.dataOfs = hdrInfo[7]
		#hdrInfo[7] seemed to be correct for Bullet Witch, but that is no longer the case in Xegapain XOR
		self.dataOfs = self.entriesSize + self.unkSize + self.namesSize + self.finfoSize
		if self.entriesSize <= 0 or self.namesSize <= 0 or self.finfoSize <= 0 or self.dataSize <= 0 or self.dataOfs <= 0:
			return 0
		self.arcBase = bs.tell() + 16 + 32 #skip over archive name (always seems to be "unknown")
		return 1 #looks valid

	def decompressInPlace(self):
		bs = self.bs
		bs.seek(self.arcBase)

		decompSizes = (self.entriesSize+self.unkSize+self.namesSize+self.finfoSize, self.dataSize)

		decompData = bytearray()
		for decompSize in decompSizes:
			cmprId = bs.readInt()
			if cmprId != CZR_COMPRESSION_MARKER:
				break
			numChunks = bs.readInt()
			chunkSize = 0
			for i in range(0, numChunks):
				chunkSize += bs.readInt()
			cmpData = bs.readBytes(chunkSize)
			decompData += rapi.decompLZHMelt(cmpData, decompSize)
		#swap out the bitstream in place with the old header and the new decompressed data
		bs.seek(0, NOESEEK_ABS)
		self.bs = NoeBitStream(bs.readBytes(self.arcBase) + decompData, NOE_BIGENDIAN)

	def parseEntries(self):
		bs = self.bs
		bs.seek(self.arcBase, NOESEEK_ABS)
		cmprTest = bs.readInt()
		if cmprTest == CZR_COMPRESSION_MARKER:
			self.decompressInPlace()
			bs = self.bs

		bs.seek(self.arcBase+self.entriesSize+self.unkSize, NOESEEK_ABS)
		self.nameStream = NoeBitStream(bs.readBytes(self.namesSize), NOE_BIGENDIAN)
		self.finfoStream = NoeBitStream(bs.readBytes(self.finfoSize), NOE_BIGENDIAN)

		bs.seek(self.arcBase, NOESEEK_ABS)
		self.numEntries = self.entriesSize // CPR_ENTRY_SIZE
		print("Parsing", self.numEntries, "entries.")

		for i in range(0, self.numEntries):
			entry = CprEntry(bs.readBytes(CPR_ENTRY_SIZE), self.nameStream)
			self.entries.append(entry)
			#print(repr(i) + " - " + entry.dirName + "/" + entry.name)
			if entry.type == CPR_TYPE_BVXD:
				self.vtxArEntries.append(entry)
			elif entry.type == CPR_TYPE_BIXD:
				self.idxArEntries.append(entry)
		return 1

	def loadTextures(self, texList):
		bs = self.bs
		fi = self.finfoStream
		for i in range(0, self.numEntries):
			entry = self.entries[i]
			bs.seek(self.arcBase+self.dataOfs+entry.dataOfs, NOESEEK_ABS)
			if entry.type != CPR_TYPE_DDS:
				continue

			data = bs.readBytes(entry.dataSize)
			fi.seek(entry.infoOfs, NOESEEK_ABS)
			infoData = fi.readBytes(entry.infoSize)

			texture = cprLoadTexture(data, entry, infoData)
			if texture is not None:
				texList.append(texture)
		return 1

	def getEntryBytes(self, entry):
		hdrOfs = self.arcBase+self.dataOfs+entry.dataOfs
		self.bs.seek(hdrOfs, NOESEEK_ABS)
		#print(hdrOfs)
		return self.bs.readBytes(entry.dataSize)

	def findEntry(self, entryName):
		for entry in self.entries:
			if entry.name == entryName:
				return entry
		return None

	def parseVDCL(self, subSize):
		if (subSize-4)%12 != 0:
			noesis.doException("Unexpected VDCL chunk size: " + repr(subSize))
		return CprVDCL(self.bs.readBytes(subSize))

	def parseIDX(self, subSize):
		if subSize != 4:
			noesis.doException("Unexpected IDX chunk size: " + repr(subSize))
		return CprIDX(self.bs.readInt())

	def parseVTX(self, subSize, isShape):
		if subSize != 16:
			noesis.doException("Unexpected VTX chunk size: " + repr(subSize))
		return CprVTX(self.bs.readBytes(16), isShape)

	def parseKNS2(self, subSize):
		bs = NoeBitStream(self.bs.readBytes(subSize), NOE_BIGENDIAN)
		texRefs = []
		while bs.tell() < bs.getSize():
			knsType = bs.readBytes(4).decode("ASCII")
			knsLen = bs.readInt()
			if knsLen <= 0:
				noesis.doException("Unexpected sub-KNS2 length")
			knsStart = bs.tell()
			if knsType == "MCTL":
				bs.seek(0x08, NOESEEK_REL)
			elif knsType == "TR  ": #texture references
				bs.seek(0x04, NOESEEK_REL)
				numRefs = bs.readInt()
				for i in range(0, numRefs):
					texType = bs.readBytes(8).decode("ASCII").rstrip("\0")
					texIdx = bs.readInt()
					texIdx2 = bs.readInt()
					texRefs.append(CprTexRef(texType, texIdx, texIdx2))
			else:
				bs.seek(knsLen, NOESEEK_REL)
		return CprKNS2(texRefs)

	def parseCM1RBoneMap(self, rawBytes):
		bs = NoeBitStream(rawBytes, NOE_BIGENDIAN)
		bs.seek(0x04, NOESEEK_REL)
		numBones = bs.readInt()
		boneMap = []
		for i in range(0, numBones):
			type = bs.readBytes(4).decode("ASCII")
			if type != "JINT":
				print("WARNING: Prematurely ran out of JINT blocks")
				break
			unk = bs.readInt()
			mapTo = bs.readInt()
			mapFrom = bs.readInt()
			if len(boneMap) <= mapFrom:
				boneMap.extend([0]*(mapFrom+1-len(boneMap)))
			boneMap[mapFrom] = mapTo
		return boneMap

	def parseDGRP(self, subSize, activeKNS2, activeVDCL):
		if activeVDCL is None:
			noesis.doException("Encountered DGRP without active vertex info")
		bs = NoeBitStream(self.bs.readBytes(subSize), NOE_BIGENDIAN)
		bs.seek(0x04, NOESEEK_REL)
		dipList = []
		boneMap = None
		while bs.tell() < bs.getSize():
			grpType = bs.readBytes(4).decode("ASCII")
			grpLen = bs.readInt()
			if grpLen <= 0:
				noesis.doException("Unexpected sub-DGRP length")
			grpStart = bs.tell()
			if grpType == "DVOL":
				bs.seek(0x04, NOESEEK_REL)
			elif grpType == "knsC":
				bs.seek(0, NOESEEK_REL)
			elif grpType == "MCTL":
				bs.seek(0x08, NOESEEK_REL)
			elif grpType == "CM1R": #joint map
				boneMap = self.parseCM1RBoneMap(bs.readBytes(grpLen))
			elif grpType == "DIP ":
				if grpLen != 24:
					noesis.doException("Unexpected DIP size (that's what she said)")
				dipList.append(CprDIP(bs.readBytes(grpLen), boneMap))
			else:
				bs.seek(grpLen, NOESEEK_REL)
		return CprDGRP(dipList, activeKNS2, activeVDCL)

	def parseTexNameList(self, tlEntry, matList):
		bs = self.bs
		hdrOfs = self.arcBase+self.dataOfs+tlEntry.dataOfs
		bs.seek(hdrOfs, NOESEEK_ABS)
		hdrID = bs.readInt()
		if hdrID != CPR_TEXLISTHDR_ID:
			return 0
		numEntries = bs.readInt()
		for i in range(0, numEntries):
			unk = bs.readInt()
			str = bs.readBytes(32).decode("ASCII").rstrip("\0")
			self.texNameList.append(str)
		return 1

	def parseSkeleton(self, sklEntry):
		bs = self.bs
		hdrOfs = self.arcBase+self.dataOfs+sklEntry.dataOfs
		bs.seek(hdrOfs, NOESEEK_ABS)
		hdrID = bs.readInt()
		if hdrID != CPR_SKELHDR_ID:
			return 0
		numBones = bs.readInt()
		for i in range(0, numBones):
			unk = bs.readInt()
			boneParent = bs.readInt()
			unk = bs.readInt()
			unk = bs.readInt()
			unk = bs.readInt()
			unk = bs.readInt()
			bs.seek(0x28, NOESEEK_REL) #skip the first matrix - it's parent-relative, which is unnecessary (although a "self.boneList = rapi.multiplyBones(self.boneList)" would allow them to be used)
			quat = NoeQuat.fromBytes(bs.readBytes(16), NOE_BIGENDIAN)
			trn = NoeVec3.fromBytes(bs.readBytes(12), NOE_BIGENDIAN)
			scl = NoeVec3.fromBytes(bs.readBytes(12), NOE_BIGENDIAN)
			mat = quat.toMat43(1)
			mat[0] *= scl
			mat[1] *= scl
			mat[2] *= scl
			mat[3] = trn
			#mat = mat.swapHandedness()
			self.boneList.append(NoeBone(i, "bone%03i"%i, mat, None, boneParent))
		return 1

	def parseModelHeader(self, hdrEntry, matList):
		bs = self.bs
		hdrOfs = self.arcBase+self.dataOfs+hdrEntry.dataOfs
		bs.seek(hdrOfs, NOESEEK_ABS)
		hdrID = bs.readInt()
		if hdrID != CPR_MDLHDR_ID:
			noesis.doException("Unexpected model header: " + repr(hdrID))
		bs.seek(0x58, NOESEEK_REL)
		chunkOfsTo = bs.readInt()
		bs.seek(chunkOfsTo - 0x0C, NOESEEK_REL)
		while bs.tell() < bs.getSize():
			chunkIndex = bs.readInt()
			chunkID = bs.readInt()
			if chunkID != CPR_CHUNKHDR_ID:
				break
			chunkSize = bs.readInt()
			chunkDataOfs = bs.tell()
			activeVDCL = None
			activeKNS2 = None
			#fixme - VDCL etc. can actually be under DVOL/DGRP in some zegapain xor files, this chunk logic all needs to be restructured and put into a single switch
			while bs.tell() < chunkDataOfs+chunkSize:
				subType = bs.readBytes(4).decode("ASCII")
				subSize = bs.readInt()
				if subType == "VDCL":
					activeVDCL = self.parseVDCL(subSize)
					self.vdclEntries.append(activeVDCL)
				elif subType == "IDX ":
					activeVDCL.idx = self.parseIDX(subSize)
					self.idxEntries.append(activeVDCL.idx)
				elif subType == "VTX ":
					activeVDCL.vtx = self.parseVTX(subSize, 0)
					self.vtxEntries.append(activeVDCL.vtx)
				elif subType == "VTXS":
					activeVDCL.shapeIndex = len(self.svtxEntries)
					activeVDCL.vtx = self.parseVTX(subSize, 1)
					self.svtxEntries.append(activeVDCL.vtx)
				elif subType == "kns2" or subType == "knsC":
					activeKNS2 = self.parseKNS2(subSize)
				elif subType == "DGRP":
					self.dgrpEntries.append(self.parseDGRP(subSize, activeKNS2, activeVDCL))
				else:
					bs.seek(subSize, NOESEEK_REL)

		self.numMeshes = len(self.idxEntries)

		#print(len(self.idxEntries), len(self.vdclEntries), len(self.vtxEntries), len(self.svtxEntries))
		#print(len(self.idxArEntries), len(self.vtxArEntries))
		if len(self.vdclEntries) != self.numMeshes or len(self.vtxEntries) != self.numMeshes or len(self.idxArEntries) != self.numMeshes or len(self.vtxArEntries) < self.numMeshes:
			noesis.doException("Unexpected vdecl/buffer counts: " + repr(len(self.vdclEntries)) + "," + repr(self.numMeshes) + "," + repr(len(self.idxArEntries)) + "," + repr(len(self.vtxArEntries)) )
		shapesOfs = len(self.vdclEntries)

		for vdcl in self.vdclEntries:
			vdcl.createBuffers(self, shapesOfs)

		#no need to explicitly free the context (created contexts are auto-freed after the handler), but DO NOT hold any references to it outside of this method
		ctx = rapi.rpgCreateContext()
		rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
		#rapi.rpgSetOption(noesis.RPGOPT_SWAPHANDEDNESS, 1)
		for dgrp in self.dgrpEntries:
			vdcl = dgrp.vdcl

			material = NoeMaterial("bwitchmat%03i"%len(matList), "") #create a material for each dgrp
			if dgrp.kns2 != None:
				for tref in dgrp.kns2.texRefs:
					if tref.texIdx >= 0 and tref.texIdx < len(self.texNameList):
						if tref.texType == "BTX0":
							material.setTexture(self.texNameList[tref.texIdx])
						elif tref.texType == "NMAP":
							material.setNormalTexture(self.texNameList[tref.texIdx])
			rapi.rpgSetMaterial(material.name)
			matList.append(material)

			vdclPos = vdcl.vdclPos
			if vdclPos is None:
				print("WARNING: Couldn't find position element for vdecl")
				continue
			vdclUV = vdcl.vdclUV
			vdclBoneIdx = vdcl.vdclBoneIdx
			vdclBoneWgt = vdcl.vdclBoneWgt
			vtxSize = vdcl.vtxSize
			vtxSizePos = vdcl.vtxSizePos

			for dip in dgrp.dipList:
				rapi.rpgSetBoneMap(dip.boneMap)

				baseOfs = dip.vertStart*vtxSize
				baseOfsPos = dip.vertStart*vtxSizePos
				rapi.rpgBindPositionBufferOfs(vdcl.vtxBufferPos, noesis.RPGEODATA_FLOAT, vtxSizePos, baseOfsPos+vdclPos.cmpOfs)
				if vdcl.decodedNormals is not None:
					rapi.rpgBindNormalBufferOfs(vdcl.decodedNormals, noesis.RPGEODATA_FLOAT, 12, dip.vertStart*12)
				if vdclUV is not None:
					rapi.rpgBindUV1BufferOfs(vdcl.vtxBuffer, noesis.RPGEODATA_HALFFLOAT, vtxSize, baseOfs+vdclUV.cmpOfs)
				if vdclBoneIdx is not None and vdclBoneWgt is not None:
					rapi.rpgBindBoneIndexBufferOfs(vdcl.vtxBuffer, noesis.RPGEODATA_UBYTE, vtxSize, baseOfs+vdclBoneIdx.cmpOfs, 4)
					rapi.rpgBindBoneWeightBufferOfs(vdcl.vtxBuffer, noesis.RPGEODATA_UBYTE, vtxSize, baseOfs+vdclBoneWgt.cmpOfs, 4)

				numIdx = dip.numTris*3
				idxOfs = dip.triStart*2
				idxEnd = idxOfs + numIdx*2
				rapi.rpgCommitTriangles(vdcl.idxBuffer[idxOfs:idxEnd], noesis.RPGEODATA_USHORT, numIdx, noesis.RPGEO_TRIANGLE, 1)
				rapi.rpgClearBufferBinds()
		#rapi.rpgSmoothTangents()
		#rapi.rpgOptimize()
		#return rapi.rpgConstructModel()
		return rapi.rpgConstructModelSlim()


def cprCheckType(data):
	cpr = CprFile(NoeBitStream(data, NOE_BIGENDIAN))
	if cpr.parseHeader() == 0:
		return 0
	return 1

#load the model/textures
def cprLoadModel(data, mdlList):
	startTime = time.time()

	cpr = CprFile(NoeBitStream(data, NOE_BIGENDIAN))

	if cpr.parseHeader() == 0:
		return 0

	if cpr.parseEntries() == 0 or len(cpr.entries) <= 0:
		return 0

	texList = []
	if cpr.loadTextures(texList) == 0:
		return 0

	matList = []
	firstEntry = cpr.entries[0]
	if firstEntry.type == CPR_TYPE_RESU and firstEntry.name == "header.bin":
		tlEntry = cpr.findEntry("texlist.bin") #"anim_mat.bin" also sometimes seems to be a texture list
		if tlEntry is not None and tlEntry.type == CPR_TYPE_RESU:
			cpr.parseTexNameList(tlEntry, matList)
		sklEntry = cpr.findEntry("motion._bl")
		if sklEntry is not None and sklEntry.type == CPR_TYPE_RESU:
			cpr.parseSkeleton(sklEntry)
		mdl = cpr.parseModelHeader(firstEntry, matList)
		mdl.setBones(cpr.boneList)
		#this is an example of how to use procedural animations to test your weighting (this assumes bone 11=right shoulder and bone 16=left shoulder)
		#panims = [NoeProceduralAnim("bone011", 30.0, 1, 0.1), NoeProceduralAnim("bone016", 60.0, 1, 0.1)]
		#anims = rapi.createProceduralAnim(cpr.boneList, panims, 100)
		#mdl.setAnims(anims)
	else:
		mdl = NoeModel()

	if len(matList) > 0 and len(texList) <= 0: #try grabbing a texture package on a relative path
		cprTexData = None
		texFileName = rapi.getDirForFilePath(rapi.getInputName()) + "../texture/texture.cpr"
		if (rapi.checkFileExists(texFileName)):
			cprTexData = rapi.loadIntoByteArray(texFileName)
		else:
			texFileName = rapi.getDirForFilePath(rapi.getInputName()) + "../texture/texture.czr"
			if (rapi.checkFileExists(texFileName)):
				cprTexData = rapi.loadIntoByteArray(texFileName)
		if cprTexData is not None:
			texCpr = CprFile(NoeBitStream(cprTexData, NOE_BIGENDIAN))
			if texCpr.parseHeader() != 0 and texCpr.parseEntries() != 0 and len(texCpr.entries) > 0:
				print("Got texture package from relative path.")
				texCpr.loadTextures(texList)

	mdl.setModelMaterials(NoeModelMaterials(texList, matList))
	mdlList.append(mdl)

	timeTaken = time.time() - startTime
	print("Model loaded in", timeTaken, "seconds.")

	rapi.setPreviewOption("setAngOfs", "0 90 90")

	return 1

#take appropriate action to convert texture data
def cprLoadTexture(data, entry, infoData):
	imgDims = noeUnpackFrom(">i", infoData, 36)[0]
	imgWidth = (imgDims & 4095) + 1
	imgHeight = ((imgDims>>13) & 4095) + 1
	imgFmt = noeUnpackFrom(">B", infoData, 35)[0]

	texFmt = 0
	#DXT1
	if imgFmt == 0x52:
		data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
		texFmt = noesis.NOESISTEX_DXT1
	#DXT5
	elif imgFmt == 0x54:
		data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
		texFmt = noesis.NOESISTEX_DXT5
	#DXT5 packed normal map
	elif imgFmt == 0x71:
		data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
		data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI2)
		texFmt = noesis.NOESISTEX_RGBA32
	#DXT1 packed normal map
	elif imgFmt == 0x7C:
		data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
		data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_DXT1NORMAL)
		texFmt = noesis.NOESISTEX_RGBA32
	#raw
	elif imgFmt == 0x86:
		data = rapi.imageUntile360Raw(rapi.swapEndianArray(data, 4), imgWidth, imgHeight, 4)
		texFmt = noesis.NOESISTEX_RGBA32
	#unknown, not handled
	else:
		print("WARNING: Unhandled image format " + repr(imgFmt) + " - " + repr(imgWidth) + "x" + repr(imgHeight) + " - " + repr(len(data)))
		return None

	return NoeTexture(entry.name, imgWidth, imgHeight, data, texFmt)

def cprFindDecl(entries, elemType, type):
	for component in entries:
		if component.cmpElemType == elemType and component.cmpType == type:
			return component
	return None
