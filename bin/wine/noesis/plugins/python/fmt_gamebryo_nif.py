#crude Noesis NIF importer.
#written in part using http://niftools.sourceforge.net/doc/nif/ as a reference, and in part staring at binary.
#object types are all encapsulated in a single class, but some data types are broken out into separate classes
#where it's more convenient to do so.
#when scavenging parts (or all) of this file, please lovingly mention Rich Whitehouse and Noesis.

from inc_noesis import *
import os

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Gamebryo NIF", ".nif")
	noesis.setHandlerTypeCheck(handle, nifCheckType)
	noesis.setHandlerLoadModel(handle, nifLoadModel)
	noesis.addOption(handle, "-nifloadskel", "map skeleton from another nif, loaded from path <arg>.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-nifforceenv", "force env texture on all materials to <arg>.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-niflmindex", "specify texture index to treat as lightmap.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-nifpbrtest", "test pbr materials, when applicable.", 0)
	noesis.addOption(handle, "-nifnostaticweights", "if invoked, static geometry will not be weighted to mesh nodes.", 0)
	noesis.addOption(handle, "-nifforcenodenames", "forces node/bone names to node#.", 0)
	noesis.addOption(handle, "-nifnotransform", "doesn't perform geometry transform into skeleton space.", 0)
	noesis.addOption(handle, "-nifusevcolors", "uses vertex colors", 0)
	noesis.addOption(handle, "-nifnoversionhacks", "don't use version hacks", 0)

	handle = noesis.register("Gamebryo KF", ".kf")
	noesis.setHandlerTypeCheck(handle, nifCheckType)
	noesis.setHandlerLoadModel(handle, kfLoadModel)
	
	return 1


def nifVersion(major, minor, patch, internal):
	return (major<<24) | (minor<<16) | (patch<<8) | internal


def nifStrFromBytes(data):
	try:
		str = noeStrFromBytes(data)
	except:
		print("WARNING: Non-ASCII string data:", data)
		str = "not_an_ascii_string"
	return str

	
def nifNoeDataTypeForNifDataType(nifType):
	if nifType > 56:
		#seems to represent packed normal types, noesis can decode these, but I'm too lazy to support it
		return -1
	type = (nifType-1)>>2
	if type == 0 or type == 2:
		return noesis.RPGEODATA_BYTE
	elif type == 1 or type == 3:
		return noesis.RPGEODATA_UBYTE
	elif type == 4 or type == 6:
		return noesis.RPGEODATA_SHORT
	elif type == 5 or type == 7:
		return noesis.RPGEODATA_USHORT
	elif type == 8 or type == 10:
		return noesis.RPGEODATA_INT
	elif type == 9 or type == 11:
		return noesis.RPGEODATA_UINT
	elif type == 12:
		return noesis.RPGEODATA_HALFFLOAT
	elif type == 13:
		return noesis.RPGEODATA_FLOAT
	return -1


def nifScaleMatrix(matrix, scale):
	clampedScale = max(abs(scale), 0.0001)
	if scale < 0.0:
		clampedScale = -clampedScale
	matrix[0] *= clampedScale
	matrix[1] *= clampedScale
	matrix[2] *= clampedScale


def nifImageExpandMonoColorKernel(imageData, offset, kernelData, userData):
	kernelData[1] = kernelData[2] = kernelData[0]


NIF_MAX_SANE_STRING_SIZE = 1024
NIF_MAX_SANE_LINK_ID_COUNT = 8192
NIF_MAX_SANE_TEX_LIST_SIZE = 256
NIF_MAX_SANE_STRING_LENGTH = 16384

NIF_INVALID_LINK_ID = 0xFFFFFFFF
NIF_INVALID_LINK_ID_COUNT = 0xFFFFFFFF
NIF_INVALID_STRING_INDEX = 0xFFFFFFFF

NIFTEX_RGB = 0
NIFTEX_RGBA = 1
NIFTEX_DXT1 = 4
NIFTEX_DXT3 = 5
NIFTEX_DXT5 = 6
NIFTEX_MONO = 11

NIF_HACK_NONE = 0
NIF_HACK_SKYRIM = 1
NIF_HACK_OBLIVION = 2
NIF_HACK_SPLATTERHOUSE = 3
NIF_HACK_FO4 = 4

NIF_PLATFORM_UNKNOWN = -1
NIF_PLATFORM_XBOX360 = 0
NIF_PLATFORM_PS3 = 1
NIF_PLATFORM_VITA = 7


class NifStreamElement:
	def __init__(self, count, size, dataType, offset):
		self.count = count
		self.size = size
		self.dataType = dataType
		self.offset = offset

	def __repr__(self):
		return "(count:" + repr(self.count) + " size:" + repr(self.size) + " dataType:" + repr(self.dataType) + " offset:" + repr(self.offset) + ")"


class NifMeshStream:
	def __init__(self, nif, bs):
		#parse out the stream element descriptions (to coincide with elements in the datastream header)
		self.streamLinkID = bs.readUInt()
		self.instanced = bs.readUByte() > 0
		numStreamSubmeshRegionMapEntries = bs.readUShort()
		self.submeshRegionMap = []
		for j in range(0, numStreamSubmeshRegionMapEntries):
			self.submeshRegionMap.append(bs.readUShort())
		numElementDescs = bs.readUInt()
		self.elementDescs = []
		#print("num elem descs:", numElementDescs, "stream ID:", self.streamLinkID)
		for j in range(0, numElementDescs):
			descNameIndex = bs.readUInt()
			descName = nif.stringTable[descNameIndex]
			descIndex = bs.readUInt()
			#print("elem:", descName, descIndex)
			self.elementDescs.append( (descName, descIndex) )


class NifTexMap:
	def __init__(self, nif, bs):
		#each texture map in a texturingproperty references a source texture
		self.sourceTexLinkID = nif.loadLinkID(bs)
		
		if nif.fileVer < nifVersion(20, 1, 0, 2):
			unusedClamp = bs.readUInt()
			unusedFilter = bs.readUInt()
			#only texcoord index is contained in flags
			self.flags = bs.readUInt() & 255
		else:
			self.flags = bs.readUShort()

		if nif.fileVer >= nifVersion(20, 5, 0, 4):
			self.maxAniso = bs.readUShort()

		if nif.fileVer < nifVersion(10, 3, 0, 4):
			bs.readShort()
			bs.readShort()
		self.hasTransform = bs.readUByte() > 0
		if self.hasTransform:
			#unused
			translation = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			scale = bs.readFloat()
			rotate = bs.readFloat()
			method = bs.readUInt()
			center = (bs.readFloat(), bs.readFloat())


class NifPixelFormat:
	def __init__(self, nif, bs):
		#parse out pixel formats, we don't bother with mask info currently
		self.format = bs.readUInt()
		if nif.fileVer < nifVersion(10, 3, 0, 3):
			#dds-style color masks
			self.colorMasks = (bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt())
			self.bpp = bs.readUInt()
			unused = bs.readUInt()
			unused = bs.readUInt()
			self.tiling = bs.readUInt()
		else:
			self.bpp = bs.readUByte()
			unused = bs.readUInt()
			self.extraData = bs.readUInt()
			self.flags = bs.readUByte()
			self.tiling = bs.readUInt()
			if nif.fileVer >= nifVersion(20, 3, 0, 4):
				self.srgb = bs.readUByte() > 0
			else:
				self.srgb = False
			#component data currently unused
			for i in range(0, 4):
				componentType = bs.readUInt()
				componentRep = bs.readUInt()
				componentBits = bs.readUByte()
				componentSigned = bs.readUByte() > 0


#skin partition object
class NifSkinPartition:
	def __init__(self, nif, bs):
		self.numVerts = bs.readUShort()
		self.numTris = bs.readUShort()
		self.numBones = bs.readUShort()
		self.numStrips = bs.readUShort()
		self.weightsPerVert = bs.readUShort()
		
		self.skinBonesList = []
		for i in range(0, self.numBones):
			self.skinBonesList.append(bs.readUShort())
		
		hasVertMap = bs.readUByte() > 0
		self.vertMap = None
		if hasVertMap is True:
			vertMapData = bs.readBytes(self.numVerts*2)
			self.vertMap = rapi.dataToIntList(vertMapData, self.numVerts, noesis.RPGEODATA_USHORT, NOE_LITTLEENDIAN if nif.isLittleEndian else NOE_BIGENDIAN)

		hasWeights = bs.readUByte() > 0
		if hasWeights is True:
			self.weightData = bs.readBytes(self.numVerts*self.weightsPerVert*4)
			
		if self.numStrips > 0:
			stripLengthData = bs.readBytes(self.numStrips*2)
			self.stripLengths = rapi.dataToIntList(stripLengthData, self.numStrips, noesis.RPGEODATA_USHORT, NOE_LITTLEENDIAN if nif.isLittleEndian else NOE_BIGENDIAN)
			self.triListLen = 0
			for i in range(0, self.numStrips):
				self.triListLen += self.stripLengths[i]
		else:
			self.triListLen = self.numTris*3
			
		hasTriList = bs.readUByte() > 0
		if hasTriList is True:
			self.triListData = bs.readBytes(self.triListLen*2)
		
		hasBonePalette = bs.readUByte() > 0
		if hasBonePalette is True:
			self.bonePalData = bs.readBytes(self.numVerts*self.weightsPerVert)


#handles loading all types of object data into a single container
class NifObject:
	def __init__(self, nif, index):
		self.nif = nif
		self.index = index
		self.typeName = ""
		self.nifSize = -1
		self.flags = 0
		self.platform = NIF_PLATFORM_UNKNOWN
		self.isBone = False
		self.hasMaterialProps = False
		self.matrix = None
		self.childLinks = []
		self.parentIndex = -1
		
	def loadGenericString(self, bs):
		str = ""
		#read from stream directly or by using a stringtable index depending on the file version
		if self.nif.fileVer < nifVersion(20, 1, 0, 1):
			strLen = bs.readUInt()
			if strLen > 0:
				if strLen > NIF_MAX_SANE_STRING_LENGTH:
					noesis.doException("Unreasonable string length:" + repr(strLen))
				str = nifStrFromBytes(bs.readBytes(strLen))
		else:
			strIndex = bs.readUInt()
			str = self.nif.stringTable[strIndex] if strIndex != NIF_INVALID_STRING_INDEX else ""
		return str

	def loadObject(self, bs):
		#core object stream
		#print("base load", bs.tell(), "size", self.nifSize)
		if self.nif.fileVer < nifVersion(10, 1, 0, 114):
			self.uniqueID = bs.readUInt()
	
	def loadObjectNET(self, bs):
		#base object stream
		self.loadObject(bs)
		self.name = self.loadGenericString(bs)
		self.extraDataIDs = self.nif.loadLinkIDs(bs)
		self.nif.loadLinkID(bs)
		
	def loadAVObject(self, bs):
		#oriented object stream
		self.loadObjectNET(bs)
		self.flags = bs.readUShort()
		if self.nif.nifHack == NIF_HACK_SKYRIM or self.nif.nifHack == NIF_HACK_FO4:
			bs.readUShort()
		translation = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
		self.matrix = NoeMat43( ( NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), translation ) )
		self.scale = bs.readFloat()
		nifScaleMatrix(self.matrix, self.scale)
		if self.nif.nifHack == NIF_HACK_SKYRIM or self.nif.nifHack == NIF_HACK_FO4:
			unknown = bs.readUInt()
			self.nodePropertyIDs = []
		else:
			self.nodePropertyIDs = self.nif.loadLinkIDs(bs)
			#for id in self.nodePropertyIDs:
			#	print(self.index, self.typeName, "ori prop id:", id, self.nif.objects[id].typeName)
			self.nif.loadLinkID(bs) #collision node id, unused
		#treat all oriented objects as bones
		self.isBone = True
		
	def loadNode(self, bs):
		#standard node stream
		self.loadAVObject(bs)
		
		self.childLinks = self.nif.loadLinkIDs(bs)
		if self.nif.nifHack != NIF_HACK_FO4:
			self.nif.loadLinkIDs(bs)
	
	def loadExtraData(self, bs):
		#extra data stream
		self.loadObject(bs)
		self.extraData = self.loadGenericString(bs)

	def loadStringExtraData(self, bs):
		#extra data stream + string
		self.loadExtraData(bs)
		self.stringExtraData = self.loadGenericString(bs)
		
	def loadBinaryExtraData(self, bs):
		#extra data stream + binary
		self.loadExtraData(bs)
		binaryDataSize = bs.readUInt()
		if binaryDataSize > 0:
			self.binaryExtraData = bs.readBytes(binaryDataSize)

	def loadIntegerExtraData(self, bs):
		#extra data stream + int
		self.loadExtraData(bs)
		self.intExtraData = bs.readUInt()

	def loadFloatExtraData(self, bs):
		#extra data stream + float
		self.loadExtraData(bs)
		self.floatExtraData = bs.readFloat()

	def loadBooleanExtraData(self, bs):
		#extra data stream + bool
		self.loadExtraData(bs)
		self.boolExtraData = bs.readUByte() > 0

	def loadColorExtraData(self, bs):
		#extra data stream + rgba
		self.loadExtraData(bs)
		self.colorExtraData = (bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())
		
	def loadProperty(self, bs):
		#base property
		self.loadObjectNET(bs)
		
	def loadMaterialProperty(self, bs):
		#material properties
		self.loadProperty(bs)
		self.matAmbient = (bs.readFloat(), bs.readFloat(), bs.readFloat(), 1.0)
		self.matDiffuse = (bs.readFloat(), bs.readFloat(), bs.readFloat(), 1.0)
		self.matSpecular = (bs.readFloat(), bs.readFloat(), bs.readFloat(), 1.0)
		self.matEmit = (bs.readFloat(), bs.readFloat(), bs.readFloat(), 1.0)
		self.matShine = bs.readFloat()
		self.matAlpha = bs.readFloat()
		self.hasMaterialProps = True

	def loadVertexColorProperty(self, bs):
		#vertex color properties
		self.loadProperty(bs)
		self.vclrFlags = bs.readUShort()

	def loadShadeProperty(self, bs):
		#shader properties
		self.loadProperty(bs)
		self.shadeFlags = bs.readUShort()

	def loadTexturingProperty(self, bs):
		#texturing properties
		self.loadProperty(bs)
		if self.nif.fileVer < nifVersion(20, 1, 0, 2):
			bs.readUInt()
			self.texPropFlags = 0
		else:
			self.texPropFlags = bs.readUShort()
			
		#run through the list of associated texture(s)
		texListSize = bs.readUInt()
		if texListSize > NIF_MAX_SANE_TEX_LIST_SIZE:
			noesis.doException("Unreasonable texture list size: " + repr(texListSize))

		self.texList = []
		for i in range(0, texListSize):
			hasMap = bs.readUByte() > 0
			if hasMap:
				tex = NifTexMap(self.nif, bs)
				if i == 5:
					#additional bump info
					tex.bumpLumaScale = bs.readFloat()
					tex.bumpLumaOffset = bs.readFloat()
					tex.bumpMat = (bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())
				elif i == 7 and self.nif.fileVer >= nifVersion(20, 2, 0, 5):
					#additional offset info
					tex.offsetMapOfs = bs.readFloat()
			else:
				tex = None
			self.texList.append(tex)
			
		shaderMapListSize = bs.readUInt()
		if shaderMapListSize > NIF_MAX_SANE_TEX_LIST_SIZE:
			noesis.doException("Unreasonable shader map list size: " + repr(shaderMapListSize))

		self.shaderMapList = []
		for i in range(0, shaderMapListSize):
			hasMap = bs.readUByte() > 0
			if hasMap:
				smap = NifTexMap(self.nif, bs)
				smap.uniqueID = bs.readUInt()
			else:
				smap = None
			self.shaderMapList.append(smap)

	def loadStencilProperty(self, bs):
		#stencil properties
		self.loadProperty(bs)
		if self.nif.fileVer >= nifVersion(20, 1, 0, 2):
			self.stencilFlags = bs.readUShort()
			self.stencilRef = bs.readUInt()
			self.stencilMask = bs.readUInt()
			self.cullMode = (self.stencilFlags & 0xC00)>>10
		else:
			stencilEnabled = bs.readUByte() > 0
			stencilFunction = bs.readUInt()
			stencilRef = bs.readUInt()
			stencilMask = bs.readUInt()
			stencilFail = bs.readUInt()
			stencilPassZFail = bs.readUInt()
			stencilPass = bs.readUInt()
			self.cullMode = bs.readUInt()
			
	def loadAlphaProperty(self, bs):
		#alpha properties
		self.loadProperty(bs)
		self.alphaFlags = bs.readUShort()
		self.alphaRef = bs.readUByte()
			
	def loadBSLightingShaderProperty(self, bs):
		#bethesda lighting/shading properties
		self.bsShaderType = bs.readUInt()
		self.loadProperty(bs)
		self.bsFlags1 = bs.readUInt()
		self.bsFlags2 = bs.readUInt()
		self.uvOfs = (bs.readFloat(), bs.readFloat())
		self.uvScale = (bs.readFloat(), bs.readFloat())
		self.bsTexSetID = self.nif.loadLinkID(bs)
		self.emissiveColor = (bs.readFloat(), bs.readFloat(), bs.readFloat())
		self.emissiveMul = bs.readFloat()
		self.clampMode = bs.readUInt()
		self.opacity = bs.readFloat()
		self.unknown1 = bs.readFloat()
		self.specExponent = bs.readFloat()
		self.specColor = (bs.readFloat(), bs.readFloat(), bs.readFloat())
		self.specScale = bs.readFloat()
		self.unknown2 = bs.readFloat()
		self.unknown3 = bs.readFloat()
		if self.bsShaderType == 1:
			self.envScale = bs.readFloat()
		elif self.bsShaderType == 5:
			self.skinColor = (bs.readFloat(), bs.readFloat(), bs.readFloat())
		elif self.bsShaderType == 6:
			self.hairColor = (bs.readFloat(), bs.readFloat(), bs.readFloat())
			
	def loadBSShaderTextureSet(self, bs):
		#bethesda texture set
		self.loadObject(bs)
		numTextures = bs.readUInt()
		self.texNames = []
		for i in range(0, numTextures):
			strLen = bs.readUInt()
			texName = ""
			if strLen > 0:
				if strLen > NIF_MAX_SANE_STRING_LENGTH:
					noesis.doException("Unreasonable string length:" + repr(strLen))
				texName = nifStrFromBytes(bs.readBytes(strLen))
			self.texNames.append(texName)

	def loadRenderable(self, bs):
		#renderable object properties
		self.loadAVObject(bs)
		numMaterials = bs.readUInt()
		self.materialExtraData = []
		self.materialNames = []
		for i in range(0, numMaterials):
			matNameIndex = bs.readUInt()
			matName = self.nif.stringTable[matNameIndex]
			self.materialExtraData.append(bs.readUInt())
			self.materialNames.append(matName)
		#print("mats:", self.materialNames, self.materialExtraData)
	
		self.materialIndex = bs.readUInt()
		self.materialNeedsUpdate = bs.readUByte() > 0
	
	def loadMesh(self, bs):
		#mesh properties
		self.loadRenderable(bs)
		self.meshPrimType = bs.readUInt()
		self.numSubMeshes = bs.readUShort()
		self.isInstanced = bs.readUByte() > 0
		self.boundsCenter = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
		self.boundsRad = bs.readFloat()
		numStreamRefs = bs.readUInt()
		#stream reference list references stream data objects
		self.streamRefs = []
		for i in range(0, numStreamRefs):
			self.streamRefs.append(NifMeshStream(self.nif, bs))

		self.modLinks = self.nif.loadLinkIDs(bs)
		self.nif.nifMeshes.append(self)

	def loadTriShape(self, bs):
		#geometry shape
		self.loadAVObject(bs)
		self.geomMdlLinkID = self.nif.loadLinkID(bs)
		self.geomSkinLinkID = self.nif.loadLinkID(bs)
		if self.nif.fileVer >= nifVersion(20, 2, 0, 5):
			numMaterials = bs.readUInt()
			for i in range(0, numMaterials):
				mtlName = self.loadGenericString(bs)
				mtlExtra = bs.readUInt()
			activeMaterial = bs.readUInt()
			if self.nif.fileVer >= nifVersion(20, 2, 0, 7):
				unused = bs.readUByte()
				
			if self.nif.nifHack == NIF_HACK_SKYRIM or self.nif.nifHack == NIF_HACK_FO4:
				l1 = self.nif.loadLinkID(bs)
				if l1 != NIF_INVALID_LINK_ID:
					self.nodePropertyIDs.append(l1)
				l2 = self.nif.loadLinkID(bs)
				if l2 != NIF_INVALID_LINK_ID:
					self.nodePropertyIDs.append(l2)
		else:
			hasShader = bs.readUByte() > 0
			if hasShader is True:
				shaderName = self.loadGenericString(bs)
				unused = bs.readUInt()
				
		self.nif.nifTriGeom.append(self)

	def loadBSTriShape(self, bs):
		if self.nif.nifHack != NIF_HACK_FO4:
			return
		self.loadAVObject(bs)
		bs.readFloat()
		bs.readFloat()
		bs.readFloat()
		bs.readFloat()
		self.skinInstID = self.nif.loadLinkID(bs)
		self.lightingPropID = self.nif.loadLinkID(bs)
		self.alphaPropID = self.nif.loadLinkID(bs)
		
		#add the lighting and alpha properties into the main properties list
		if self.lightingPropID != NIF_INVALID_LINK_ID:
			self.nodePropertyIDs.append(self.lightingPropID)
		if self.alphaPropID != NIF_INVALID_LINK_ID:
			self.nodePropertyIDs.append(self.alphaPropID)

		self.vertFlags = bs.readUInt64()
		self.vertSizeFromFlags = ((self.vertFlags & 0xFF) << 2)
		self.vertInfo = ((self.vertFlags >> 8) & 0xFF)
		self.vertFlags = (self.vertFlags >> 16)
		if self.vertSizeFromFlags == 0:
			return #possible todo
		self.numTris = bs.readUInt()
		self.numVerts = bs.readUShort()
		self.gpuBufferSize = bs.readUInt()
		if self.gpuBufferSize == 0:
			return #possible todo
		indexDataSize = 2 * 3 * self.numTris
		vertDataSize = self.gpuBufferSize - indexDataSize
		#or vertSizeFromFlags, but we don't respect bad gpu buffer size.
		#programs producing bad sizes should be fixed for console compatibility.
		self.vertSize = vertDataSize // self.numVerts
		
		self.vertData = bs.readBytes(vertDataSize)
		self.triData = bs.readBytes(indexDataSize)

		self.posOffset = 0
		self.posType = noesis.RPGEODATA_HALFFLOAT
		self.uvOffset = -1
		self.uvType = noesis.RPGEODATA_HALFFLOAT
		self.normalOffset = -1
		self.normalType = noesis.RPGEODATA_UBYTE
		self.tangentOffset = -1
		self.tangentType = noesis.RPGEODATA_UBYTE
		self.colorOffset = -1
		self.colorType = noesis.RPGEODATA_UBYTE
		self.blendIdxOffset = -1
		self.blendIdxType = noesis.RPGEODATA_UBYTE
		self.blendWgtOffset = -1
		self.blendWgtType = noesis.RPGEODATA_HALFFLOAT

		#bitangent looks to be stored in various w components, in addition to storing an explicit tangent, because they apparently had
		#nothing better to pack in their interpolants. jonwd seems to think this is amazingly difficult to observe, but this is likely
		#because he's a silly bitch. we could just recalculate, as FO4 doesn't look to be using hand modified bitangents for anisotropy,
		#and i've verified this in most models by ensuring that abs(nxt.dot(bt)) == 1. but we go ahead and plug the data in anyway for
		#posterity's sake.
		#these bits cover the components we currently care about, but because there are some unused components in after the ones we care
		#about and before the weights, we reach around from the end for the weights.
		vertOfs = 0
		if self.vertFlags & 0x4000000000:
			self.posType = noesis.RPGEODATA_FLOAT
			vertOfs += 16
		else:
			vertOfs += 8
			
		if self.vertFlags & 0x0020000000:
			self.uvOffset = vertOfs
			vertOfs += 4
			
		if self.vertFlags & 0x0080000000:
			self.normalOffset = vertOfs
			vertOfs += 4
		
		if self.vertFlags & 0x0000000040:
			self.tangentOffset = vertOfs
			vertOfs += 4
			
		if self.vertFlags & 0x0200000000:
			self.colorOffset = vertOfs
			vertOfs += 4
			
		if self.skinInstID != NIF_INVALID_LINK_ID:
			self.blendIdxOffset = self.vertSize - 4
			self.blendWgtOffset = self.blendIdxOffset - 8
			#still a few of these (looks to be primarily triggered by 0x1000000000), but none in between components we're using.
			#if vertOfs != self.blendWgtOffset:
			#	print("WARNING:", vertOfs, "!=", self.blendIdxOffset, "- unhandled vertFlags:", self.vertFlags)
		
		self.nif.bsTriShapes.append(self)
		
	def loadBSSubIndexTriShape(self, bs):
		if self.nif.nifHack != NIF_HACK_FO4:
			return	
		self.loadBSTriShape(bs)
		bs.readUInt() #unknown, numTris?
		#followed by some more values and link id's, perhaps dismemberment-related
		
	def loadBSSkinInstance(self, bs):
		if self.nif.nifHack != NIF_HACK_FO4:
			return	
		bs.readUInt() #unknown, always 0?
		self.boneDataID = self.nif.loadLinkID(bs)
		self.numBones = bs.readUInt()
		self.boneNodeIDs = []
		for i in range(0, self.numBones):
			nodeID = self.nif.loadLinkID(bs)
			self.boneNodeIDs.append(nodeID)
		#additional 4 bytes of unknown, always 0?

	def loadBSSkinBoneData(self, bs):
		if self.nif.nifHack != NIF_HACK_FO4:
			return
		self.numBones = bs.readUInt()
		self.invBindTransforms = []
		for i in range(0, self.numBones):
			#68 bytes per bone
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			v0 = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			v1 = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			v2 = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			v3 = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			bs.readFloat()
			self.invBindTransforms.append(NoeMat43( (v0, v1, v2, v3) ))
		
	def loadTriBasedGeomData(self, bs):
		#geometry data
		self.loadObject(bs)
		if self.nif.fileVer >= nifVersion(10, 1, 0, 114):
			groupID = bs.readUInt()
		self.geomNumVerts = bs.readUShort()
		self.geomKeepFlags = bs.readUByte()
		self.geomCompressFlags = bs.readUByte()

		self.geomPositions = None
		self.geomNormals = None
		self.geomBinormals = None
		self.geomTangents = None
		self.geomColors = None
		self.geomUVSets = None
		
		geomHasPos = bs.readUByte() > 0
		if geomHasPos is True:
			self.geomPositions = bs.readBytes(self.geomNumVerts*12)
			
		self.geomDataFlags = bs.readUShort()
		
		if self.nif.nifHack == NIF_HACK_SKYRIM or self.nif.nifHack == NIF_HACK_FO4:
			bs.readUInt()
			#bs.readUInt()
		
		geomHasNrm = bs.readUByte() > 0
		if geomHasNrm is True:
			self.geomNormals = bs.readBytes(self.geomNumVerts*12)
			if self.geomDataFlags & 0xF000:
				self.geomBinormals = bs.readBytes(self.geomNumVerts*12)
				self.geomTangents = bs.readBytes(self.geomNumVerts*12)
		
		center = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
		rad = bs.readFloat()
		
		geomHasColors = bs.readUByte() > 0
		if geomHasColors is True:
			self.geomColors = bs.readBytes(self.geomNumVerts*16) #float rgba

		numGeomUVSets = (self.geomDataFlags & 0x3F)
		if numGeomUVSets > 0:
			self.geomUVSets = []
			for i in range(0, numGeomUVSets):
				geomUVData = bs.readBytes(self.geomNumVerts*8)
				self.geomUVSets.append(geomUVData)
				
		unused = bs.readUShort()
		if self.nif.fileVer >= nifVersion(10, 3, 0, 7):
			self.geomExtraDataID = self.nif.loadLinkID(bs)
			
		self.geomNumTriangles = bs.readUShort()

	def loadTriShapeData(self, bs):
		#geometry shape data
		self.loadTriBasedGeomData(bs)
		self.geomNumTriIndices = bs.readUInt()
		if self.geomNumTriangles*3 != self.geomNumTriIndices:
			print("WARNING: Unexpected tri/index count:", self.geomNumTriangles, "and", self.geomNumTriIndices)
		self.geomTriListData = None
		hasTriList = bs.readUByte() > 0
		if hasTriList is True and self.geomNumTriIndices > 0: #seems silly, but ok
			self.geomTriListData = bs.readBytes(self.geomNumTriIndices*2)

	def loadTriStripsData(self, bs):
		#geometry strip data
		self.loadTriBasedGeomData(bs)
		self.geomNumStrips = bs.readUShort()
		self.geomStripListData = None
		if self.geomNumStrips > 0:
			geomStripLensData = bs.readBytes(self.geomNumStrips*2)
			self.geomStripLens = rapi.dataToIntList(geomStripLensData, self.geomNumStrips, noesis.RPGEODATA_USHORT, NOE_LITTLEENDIAN if self.nif.isLittleEndian else NOE_BIGENDIAN)
			geomHasStripList = bs.readUByte() > 0
			if geomHasStripList is True:
				geomStripListDataCount = self.geomNumTriangles + self.geomNumStrips*2
				self.geomStripListData = bs.readBytes(geomStripListDataCount*2)
		
	def loadSourceTexture(self, bs):
		#source texture data, references pixel data object
		self.loadObjectNET(bs)
		
		self.externalTex = bs.readUByte() > 0
		self.texFileName = self.loadGenericString(bs)
		self.pixLinkID = self.nif.loadLinkID(bs)
			
		self.pixelLayout = bs.readUInt()
		self.mipMapped = bs.readUInt()
		self.alphaFormat = bs.readUInt()
		self.texStatic = bs.readUByte() > 0
		if self.nif.fileVer >= nifVersion(10, 1, 0, 103):
			unused = bs.readUByte()
		if self.nif.fileVer >= nifVersion(20, 2, 0, 4):
			unused = bs.readUByte()

		#noeTexIndex will be set later if this object is referencing usable pixel data
		self.noeTexIndex = -1
		self.nif.nifTextures.append(self)
	
	def loadSourceCubeMap(self, bs):
		#source texture data for cubemap
		if self.nif.fileVer >= nifVersion(10, 3, 0, 6):
			self.loadSourceTexture(bs)
		else:
			#previous gamebryo versions stored multiple pixel link id's per cubemap
			self.loadObjectNET(bs)
			
			self.externalTex = bs.readUByte() > 0
			self.cubeTexFileNames = []
			for i in range(0, 6):
				self.cubeTexFileNames.append(self.loadGenericString(bs))
			#provide first face filename as the filename for anything that expects a texture to have one
			self.texFileName = self.cubeTexFileNames[0]
			self.cubePixLinkIDs = []
			for i in range(0, 6):
				self.cubePixLinkIDs.append(self.nif.loadLinkID(bs))
			#provide first pixel link id as the linkid for anything that expects a texture to have one
			self.pixLinkID = self.cubePixLinkIDs[0]
			self.pixelLayout = bs.readUInt()
			self.mipMapped = bs.readUInt()
			self.alphaFormat = bs.readUInt()
			self.texStatic = bs.readUByte() > 0
			
			self.noeTexIndex = -1
			self.nif.nifTextures.append(self)
		
			
	def loadPixelDataGeneric(self, bs, persVersion):
		#raw pixel data object
		self.loadObject(bs)
		self.pixelFormat = NifPixelFormat(self.nif, bs)
		self.palLinkID = self.nif.loadLinkID(bs)
		self.mipLevels = bs.readUInt()
		self.pixelStride = bs.readUInt()
		self.width = 0
		self.height = 0
		if self.nif.nifHack == NIF_HACK_SPLATTERHOUSE:
			unused = bs.readUInt()
			
		tempMipInfo = []
		for i in range(0, self.mipLevels):
			mipW = bs.readUInt()
			mipH = bs.readUInt()
			if mipW > self.width:
				self.width = mipW
			if mipH > self.height:
				self.height = mipH
			tempMipInfo.append((mipW, mipH, bs.readUInt()))
		self.mipsTotalSize = bs.readUInt()
		
		#pre-determine mip sizes as well now that we've read all the data we need to figure them out
		self.mipInfo = []
		for i in range(0, self.mipLevels):
			mipW, mipH, mipOfs = tempMipInfo[i]
			mipSize = tempMipInfo[i+1][2]-mipOfs if i < self.mipLevels-1 else self.mipsTotalSize-mipOfs
			self.mipInfo.append((mipW, mipH, mipOfs, mipSize))
		
		if persVersion:
			if self.nif.fileVer >= nifVersion(20, 2, 0, 6):
				unused = bs.readUInt()
				
		if self.nif.fileVer >= nifVersion(10, 3, 0, 6):
			self.numFaces = bs.readUInt()
		else:
			self.numFaces = 1
			
		if persVersion:
			if self.nif.fileVer < nifVersion(30, 1, 0, 1):
				self.platform = bs.readUInt()
				if self.platform == 1:
					self.platform = NIF_PLATFORM_XBOX360
				elif self.platform == 2:
					self.platform = NIF_PLATFORM_PS3
			else:
				self.renderPlatform = bs.readUInt()
				if self.renderPlatform == 0:
					self.platform = NIF_PLATFORM_XBOX360
				elif self.renderPlatform == 1:
					self.platform = NIF_PLATFORM_PS3
				elif self.renderPlatform == 7:
					self.platform = NIF_PLATFORM_VITA

		self.imageData = bs.readBytes(self.mipsTotalSize*self.numFaces)

	def loadPixelData(self, bs):
		self.loadPixelDataGeneric(bs, False)

	def loadPersistentSrcTextureRendererData(self, bs):
		self.loadPixelDataGeneric(bs, True)
	
	def loadMeshModifier(self, bs):
		#base mesh modifier
		self.loadObject(bs)
		syncCount = bs.readUInt()
		for i in range(0, syncCount):
			bs.readUShort()
		syncCount = bs.readUInt()
		for i in range(0, syncCount):
			bs.readUShort()
	
	def loadSkinningMeshModifier(self, bs):
		#skinned mesh modifier
		self.loadMeshModifier(bs)
		self.skinFlags = bs.readUShort()
		self.rootBoneLinkID = self.nif.loadLinkID(bs)
		self.boneParentToSkinMat = NoeMat43( ( NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ) ) )
		self.boneParentToSkinScale = bs.readFloat()
		nifScaleMatrix(self.boneParentToSkinMat, self.boneParentToSkinScale)
		self.numBones = bs.readUInt()
		self.boneLinkIDs = []
		for i in range(0, self.numBones):
			boneLinkID = self.nif.loadLinkID(bs)
			self.boneLinkIDs.append(boneLinkID)
			
		self.skinToBoneMats = []
		for i in range(0, self.numBones):
			mat = NoeMat43( ( NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ) ) )
			scale = bs.readFloat()
			nifScaleMatrix(mat, scale)
			self.skinToBoneMats.append(mat)
		if self.skinFlags & 2:
			#bounds are unused
			for i in range(0, self.numBones):
				center = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
				rad = bs.readFloat()
				
	def loadSkinInstance(self, bs):
		#skin instance
		self.loadObject(bs)
		self.skinDataID = self.nif.loadLinkID(bs)
		if self.nif.fileVer >= nifVersion(10, 1, 0, 101):
			self.skinPartitionID = self.nif.loadLinkID(bs)
		self.skinRootID = self.nif.loadLinkID(bs)
		self.skinBoneIDs = self.nif.loadLinkIDs(bs)

	def loadSkinData(self, bs):
		#skin data
		self.loadObject(bs)
		self.boneParentToSkinMat = NoeMat43( ( NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ) ) )
		self.boneParentToSkinScale = bs.readFloat()
		nifScaleMatrix(self.boneParentToSkinMat, self.boneParentToSkinScale)
		self.numSkinBones = bs.readUInt()
		if self.nif.fileVer < nifVersion(10, 1, 0, 101):
			self.skinPartitionID = self.nif.loadLinkID(bs)
		self.skinHasVertData = bs.readUByte() > 0
		self.skinToBoneMats = []
		self.skinBoneVertOfsAndLen = []
		self.skinBoneWeightDataList = []
		self.weightsPerVert = 0
		curWeightOfs = 0
		weightCounts = [0]
		for i in range(0, self.numSkinBones):
			skinToBoneMat = NoeMat43( ( NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ), NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) ) ) )
			skinToBoneScale = bs.readFloat()
			nifScaleMatrix(skinToBoneMat, skinToBoneScale)
			self.skinToBoneMats.append(skinToBoneMat)
			
			boneCenter = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
			boneRad = bs.readFloat()
			
			numBoneVerts = bs.readUShort()
			self.skinBoneVertOfsAndLen.append( (curWeightOfs, numBoneVerts) )
			curWeightOfs += numBoneVerts
			if self.skinHasVertData is True:
				#add to the list of vertex index and weight tuples
				for j in range(0, numBoneVerts):
					vertIndex = bs.readUShort()
					vertWeight = bs.readFloat()
					#keep track of the max weights per vert
					if vertIndex >= len(weightCounts):
						dif = (vertIndex-len(weightCounts))+1
						weightCounts += [0]*dif
					weightCounts[vertIndex] += 1
					if weightCounts[vertIndex] > self.weightsPerVert:
						self.weightsPerVert = weightCounts[vertIndex]
					self.skinBoneWeightDataList.append( (vertIndex, vertWeight) )

	def loadSkinPartition(self, bs):
		#skin partition
		self.loadObject(bs)
		numPartitions = bs.readUInt()
		self.skinPartitions = []
		for i in range(0, numPartitions):
			self.skinPartitions.append(NifSkinPartition(self.nif, bs))

	def loadDataStream(self, bs):
		#element data stream
		self.loadObject(bs)
		self.streamSize = bs.readUInt()
		self.streamClone = bs.readUInt()
		numRegions = bs.readUInt()
		self.streamRegions = []
		for i in range(0, numRegions):
			#sub-mesh regions in the form of base index (offset = base index * elem stride), and count
			#number of regions should == number of submeshes in the mesh referencing the stream, for every stream referenced by the mesh
			self.streamRegions.append( (bs.readUInt(), bs.readUInt()) )
			
		numElements = bs.readUInt()
		self.streamElems = []
		self.elemStride = 0
		for i in range(0, numElements):
			elemData = bs.readUInt()
			elem = NifStreamElement((elemData & 0xFF0000)>>16, (elemData & 0xFF00)>>8, elemData & 0xFF, self.elemStride)
			self.elemStride += elem.count*elem.size
			#print("elem count:", elem.count, "size:", elem.size, "data type:", elem.dataType)
			self.streamElems.append(elem)
		
		#print(self.typeName, "numelems:", len(self.streamElems), "size:", self.streamSize, "regions:", len(self.streamRegions), "stride:", self.elemStride, "data ofs:", bs.tell())
		self.streamData = bs.readBytes(self.streamSize)
		self.streamable = bs.readUByte() > 0

	def loadTimeController(self, bs):
		self.loadObject(bs)
		self.timeContNextID = self.nif.loadLinkID(bs)
		self.timeContFlags = bs.readUShort()
		self.timeContFreq = bs.readFloat()
		self.timeContPhase = bs.readFloat()
		self.timeContLoKeyTime = bs.readFloat()
		self.timeContHiKeyTime = bs.readFloat()
		self.timeContTargetID = self.nif.loadLinkID(bs)
		#print("timecontroller nextid:", self.nif.objects[self.timeContNextID].name if self.timeContNextID != NIF_INVALID_LINK_ID else "none", "targetid:", self.nif.objects[self.timeContTargetID].name)
		
	def loadTransformController(self, bs):
		self.loadTimeController(bs)
		self.transformInterpolatorID = bs.readUInt()

	def loadSequenceData(self, bs):
		if self.nif.fileVer >= nifVersion(20, 5, 0, 2):
			self.loadObject(bs)
			self.seqName = self.loadGenericString(bs)
			numEval = bs.readUInt()
			self.seqEvalIDList = []
			for i in range(0, numEval):
				self.seqEvalIDList.append(bs.readUInt())
			self.nif.nifSequences.append(self)

	def loadEvaluator(self, bs):
		self.loadObject(bs)
		self.evalName = self.loadGenericString(bs) #name of the target node
		self.evalPropType = self.loadGenericString(bs)
		self.evalCtrlType = self.loadGenericString(bs)
		self.evalCtrlID = self.loadGenericString(bs)
		self.evalEvalID = self.loadGenericString(bs)
		self.evalChanTypes = (bs.readUByte(), bs.readUByte(), bs.readUByte(), bs.readUByte())

	def loadTransformEvaluator(self, bs):
		self.loadEvaluator(bs)
		self.evalTranslate = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
		w = bs.readFloat()
		self.evalRotate = NoeQuat( (bs.readFloat(), bs.readFloat(), bs.readFloat(), w) )
		self.evalScale = bs.readFloat()
		self.evalDataID = bs.readUInt()
		self.evalConstData = False

	def loadConstTransformEvaluator(self, bs):
		self.loadEvaluator(bs)
		self.evalTranslate = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
		w = -bs.readFloat()
		self.evalRotate = NoeQuat( (bs.readFloat(), bs.readFloat(), bs.readFloat(), w) )
		self.evalScale = bs.readFloat()
		self.evalConstData = True
		
	def loadTransformData(self, bs):
		if self.nif.fileVer >= nifVersion(20, 5, 0, 2):
			self.loadObject(bs)
			self.rotKeys = []
			self.trnKeys = []
			self.sclKeys = []
			self.rotKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
			self.trnKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
			self.sclKeyType = noesis.NOEKF_INTERPOLATE_LINEAR

			numKeys = bs.readUInt()
			if numKeys > 0:
				rotKeyType = bs.readUInt()
				if rotKeyType == 0 or rotKeyType == 1 or rotKeyType == 4:
					self.rotKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
				else:
					print("WARNING: Unsupported rotation key type:", rotKeyType)
					return
				for i in range(0, numKeys):
					if rotKeyType == 0 or rotKeyType == 1:
						#quats
						keyTime = bs.readFloat()
						w = bs.readFloat()
						keyVal = NoeQuat( (bs.readFloat(), bs.readFloat(), bs.readFloat(), w) ).toMat43(1).toQuat()
						self.rotKeys.append(NoeKeyFramedValue(keyTime, keyVal))
					elif rotKeyType == 4:
						#radians
						xyz = [ [], [], [] ]
						for i in range(0, 3):
							numSubKeys = bs.readUInt()
							if numSubKeys > 0:
								radianKeyType = bs.readUInt()
								for j in range(0, numSubKeys):
									keyTime = bs.readFloat()
									if radianKeyType == 0 or radianKeyType == 1:
										xyz[i].append(NoeKeyFramedValue(keyTime, bs.readFloat()*noesis.g_flRadToDeg))
									elif radianKeyType == 2:
										#possible todo - interpolate as bezier
										xyz[i].append(NoeKeyFramedValue(keyTime, bs.readFloat()*noesis.g_flRadToDeg))
										bezierIn = bs.readFloat()
										bezierOut = bs.readFloat()
									else:
										print("WARNING: Unsupported radian rotation type:", radianKeyType)
										return
						#this is largely untested, because the model i found using it only used it for the eyes,
						#and it's hard to tell if it really works just based on eyes. (that's what she said)
						xyz = rapi.mergeKeyFramedFloats(xyz)
						for anglesKey in xyz:
							self.rotKeys.append(NoeKeyFramedValue(anglesKey.time, NoeAngles(anglesKey.value).toMat43_XYZ().toQuat()))

			numKeys = bs.readUInt()
			if numKeys > 0:
				trnKeyType = bs.readUInt()
				if trnKeyType == 0 or trnKeyType == 1:
					self.trnKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
				elif trnKeyType == 2:
					#possible todo - interpolate as bezier
					self.trnKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
				else:
					print("WARNING: Unsupported translation key type:", trnKeyType)
					return
				for i in range(0, numKeys):
					keyTime = bs.readFloat()
					if trnKeyType == 0 or trnKeyType == 1:
						keyVal = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
					elif trnKeyType == 2:
						keyVal = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
						bezierIn = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
						bezierOut = NoeVec3( (bs.readFloat(), bs.readFloat(), bs.readFloat()) )
					self.trnKeys.append(NoeKeyFramedValue(keyTime, keyVal))
				
			numKeys = bs.readUInt()
			if numKeys > 0:
				sclKeyType = bs.readUInt()
				if sclKeyType == 0 or sclKeyType == 1:
					self.sclKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
				elif sclKeyType == 2:
					#possible todo - interpolate as bezier
					self.sclKeyType = noesis.NOEKF_INTERPOLATE_LINEAR
				else:
					print("WARNING: Unsupported scale key type:", sclKeyType)
					return
				for i in range(0, numKeys):
					keyTime = bs.readFloat()
					if sclKeyType == 0 or sclKeyType == 1:
						keyVal = bs.readFloat()
					elif sclKeyType == 2:
						keyVal = bs.readFloat()
						bezierIn = bs.readFloat()
						bezierOut = bs.readFloat()
					self.sclKeys.append(NoeKeyFramedValue(keyTime, keyVal))
			
	#======================================================================
	#Utility methods
	#======================================================================
	
	#get stream and element objects for a mesh
	def getStreamAndElement(self, elementName, preferredIndex = -1):
		for streamRef in self.streamRefs:
			for i in range(0, len(streamRef.elementDescs)):
				elemCheckName, elemCheckIndex = streamRef.elementDescs[i]
				if preferredIndex == -1 or elemCheckIndex == preferredIndex:
					if elemCheckName.startswith(elementName):
						dataStream = self.nif.objects[streamRef.streamLinkID]
						if i >= len(dataStream.streamElems):
							print("WARNING: Data stream does not have enough elements.")
						else:
							elem = dataStream.streamElems[i]
							return streamRef, elem, dataStream
		return None, None, None
	

nifObjectLoaderDict = {
	"NiNode" : NifObject.loadNode,
	"NiSortAdjustNode" : NifObject.loadNode,
	"NiBillboardNode" : NifObject.loadNode,
	"NiRoom" : NifObject.loadNode,
	"NiRoomGroup" : NifObject.loadNode,
	"NiStringExtraData" : NifObject.loadStringExtraData,
	"NiBinaryExtraData" : NifObject.loadBinaryExtraData,
	"NiIntegerExtraData" : NifObject.loadIntegerExtraData, 
	"BSXFlags" : NifObject.loadIntegerExtraData,
	"NiFloatExtraData" : NifObject.loadFloatExtraData, 
	"NiBooleanExtraData" : NifObject.loadBooleanExtraData, 
	"NiColorExtraData" : NifObject.loadColorExtraData, 
	"NiMaterialProperty" : NifObject.loadMaterialProperty,
	"NiVertexColorProperty" : NifObject.loadVertexColorProperty,
	"NiShadeProperty" : NifObject.loadShadeProperty,
	"NiTexturingProperty" : NifObject.loadTexturingProperty,
	"NiStencilProperty" : NifObject.loadStencilProperty,
	"NiAlphaProperty" : NifObject.loadAlphaProperty,
	"BSLightingShaderProperty" : NifObject.loadBSLightingShaderProperty,
	"BSShaderTextureSet" : NifObject.loadBSShaderTextureSet,
	"NiMesh" : NifObject.loadMesh,
	"NiTriShape" : NifObject.loadTriShape,
	"BSTriShape" : NifObject.loadBSTriShape,
	"BSSubIndexTriShape" : NifObject.loadBSSubIndexTriShape,
	"BSSkin::Instance" : NifObject.loadBSSkinInstance,
	"BSSkin::BoneData" : NifObject.loadBSSkinBoneData,
	"NiTriStrips" : NifObject.loadTriShape,
	"NiTriShapeData" : NifObject.loadTriShapeData,
	"NiTriStripsData" : NifObject.loadTriStripsData,
	"NiSourceTexture" : NifObject.loadSourceTexture,
	"NiSourceCubeMap" : NifObject.loadSourceCubeMap,
	"NiPixelData" : NifObject.loadPixelData,
	"NiPersistentSrcTextureRendererData" : NifObject.loadPersistentSrcTextureRendererData,
	"NiSkinningMeshModifier" : NifObject.loadSkinningMeshModifier,
	"NiSkinInstance" : NifObject.loadSkinInstance,
	"BSDismemberSkinInstance" : NifObject.loadSkinInstance, #currently don't care about the bethesda-specific stuff at the end of the object
	"NiSkinData" : NifObject.loadSkinData,
	"NiSkinPartition" : NifObject.loadSkinPartition,
	"NiTransformController" : NifObject.loadTransformController,
	"NiSequenceData" : NifObject.loadSequenceData,
	"NiTransformEvaluator" : NifObject.loadTransformEvaluator,
	"NiConstTransformEvaluator" : NifObject.loadConstTransformEvaluator,
	"NiTransformData" : NifObject.loadTransformData
}


class NifFile:
	def __init__(self, bs):
		self.bs = bs
		self.nifTextures = []
		self.nifMeshes = []
		self.nifTriGeom = []
		self.nifSequences = []
		self.bsTriShapes = []
		self.nifHack = NIF_HACK_NONE
		
	def loadHeader(self):
		bs = self.bs
		self.isNDSNIF = False
		try:
			headerInfo = bytearray()
			while not bs.checkEOF():
				b = bs.readBytes(1)
				if b[0] == 0x0A:
					break
				headerInfo += b
			headerString = nifStrFromBytes(headerInfo)
			if "File Format" not in headerString:
				if "NDSNIF" in headerString:
					bs.setOffset((bs.getOffset() + 15) & ~15)
					self.isNDSNIF = True
					#default the file version of NDSNIF, then try to parse it out of the string if possible
					self.fileVer = nifVersion(20, 2, 0, 8)
					verPos = headerString.find("Version ")
					if verPos >= 0:
						verString = headerString[verPos + 8:]
						versionValues = [int(x) for x in verString.split('.')]
						self.fileVer = nifVersion(*versionValues)
				else:
					return 0
			self.header = headerString
		except:
			return 0

		if self.isNDSNIF:
			self.isLittleEndian = True
			self.userVersion = 0
		else:
			self.fileVer = bs.readUInt()
			if self.fileVer >= nifVersion(20, 0, 0, 3):
				self.isLittleEndian = bs.readUByte() > 0
			else:
				self.isLittleEndian = True
			
			if self.fileVer >= nifVersion(10, 0, 1, 8):
				self.userVersion = bs.readUInt()
			else:
				self.userVersion = 0
			
		self.numObjects = bs.readInt()
		if self.numObjects <= 0:
			return 0
		
		if self.userVersion == nifVersion(0, 0, 0, 12) and self.fileVer == nifVersion(20, 2, 0, 7):
			self.userVersion2 = bs.readUInt()
		else:
			self.userVersion2 = 0
		
		self.objects = []
		for i in range(0, self.numObjects):
			self.objects.append(NifObject(self, i))

		if self.isLittleEndian is not True:
			bs.setEndian(NOE_BIGENDIAN)
			
		return 1
		
	def loadMetaData(self):
		bs = self.bs
		metaDataSize = bs.readUInt()
		if metaDataSize == 0:
			self.metaData = None
		else:
			self.metaData = bs.readBytes(metaDataSize)
		return 1
	
	def tryParsingTypes(self, bs):
		self.numTypes = bs.readUShort()
		if self.numTypes <= 0:
			#can't have a nif with no type names
			noesis.doException("No type entries.")
		typeNameList = []
		for i in range(0, self.numTypes):
			strLen = bs.readUInt()
			if strLen > NIF_MAX_SANE_STRING_SIZE:
				noesis.doException("Error: Suspiciously large value for length in string table: " + repr(strLen))
			typeName = nifStrFromBytes(bs.readBytes(strLen))
			typeNameList.append(typeName)
		return typeNameList

	def loadTypeNames(self):
		bs = self.bs
		typesOfs = bs.tell()
		
		noVersionHacks = noesis.optWasInvoked("-nifnoversionhacks")
		
		try:
			typeNameList = self.tryParsingTypes(bs)
		except:
			#if something went wrong, check for non-standard hack modes.
			#only applying bethesda hacks here because all bethesda nif's have added header garbage.
			if noVersionHacks is not True:
				if self.userVersion == nifVersion(0, 0, 0, 12):
					if self.userVersion2 == 130:
						print("FO4 mode.")
						self.nifHack = NIF_HACK_FO4
					else:
						print("Skyrim mode.")
						self.nifHack = NIF_HACK_SKYRIM
				elif self.userVersion == nifVersion(0, 0, 0, 11):
					print("Oblivion mode.")
					self.nifHack = NIF_HACK_OBLIVION

			print("An error occurred when parsing the type table, trying to find it manually.")
			#if anything went wrong, it's probably a custom version of the format. let's do some horrible hackery.
			bs.seek(typesOfs)
			lastCheckedByte = bs.readUByte()
			while not bs.checkEOF():
				if lastCheckedByte == 0x4E:
					lastCheckedByte = bs.readUByte()
					if lastCheckedByte == 0x69:
						lastCheckedByte = bs.readUByte()
						if lastCheckedByte != 0x66: #don't hit on "Nif"
							print("Found Ni:", bs.tell())
							bs.seek(bs.tell()-9)
							typeNameList = self.tryParsingTypes(bs)
							break
				elif lastCheckedByte == 0x42:
					lastCheckedByte = bs.readUByte()
					if lastCheckedByte == 0x53:
						print("Found BS:", bs.tell())
						bs.seek(bs.tell()-8)
						typeNameList = self.tryParsingTypes(bs)
						break
				elif lastCheckedByte == 0x62:
					lastCheckedByte = bs.readUByte()
					if lastCheckedByte == 0x68:
						lastCheckedByte = bs.readUByte()
						if lastCheckedByte == 0x6B:
							print("Found bhk:", bs.tell())
							bs.seek(bs.tell()-9)
							typeNameList = self.tryParsingTypes(bs)
							break
				lastCheckedByte = bs.readUByte()

		#check for fixed-version hacks
		if noVersionHacks is not True:
			if self.fileVer == nifVersion(20, 5, 0, 0) and self.userVersion == nifVersion(0, 0, 0, 2):
				print("Splatterhouse mode.")
				self.nifHack = NIF_HACK_SPLATTERHOUSE

		for i in range(0, self.numObjects):
			typeIndex = bs.readUShort()
			if self.fileVer >= nifVersion(20, 2, 0, 5):
				typeIndex &= ~32768
				
			if typeIndex > self.numTypes:
				print("ERROR: Typeindex out of bounds:", typeIndex, "versus", self.numTypes)
				return 0
			self.objects[i].typeName = typeNameList[typeIndex]
		return 1

	def loadObjectSizes(self):
		bs = self.bs
		for object in self.objects:
			object.nifSize = bs.readUInt()
		return 1

	def loadStringTable(self):
		bs = self.bs
		numStrings = bs.readUInt()
		self.stringTable = []
		self.maxStringSize = bs.readUInt()
		for i in range(0, numStrings):
			strLen = bs.readUInt()
			if strLen > 0:
				self.stringTable.append(nifStrFromBytes(bs.readBytes(strLen)))
			else:
				self.stringTable.append("")
		return 1

	def loadObjectGroups(self):
		bs = self.bs
		numGroups = bs.readUInt()
		self.groupSizes = []
		self.groupSizes.append(0) #null entry at 0
		for i in range(0, numGroups):
			self.groupSizes.append(bs.readUInt())
		return 1

	def loadObjects(self):
		bs = self.bs
		for i in range(0, self.numObjects):
			object = self.objects[i]

			object.streamOffset = bs.tell()

			if object.typeName in nifObjectLoaderDict:
				nifObjectLoaderDict[object.typeName](object, bs)
			elif object.typeName.startswith("NiDataStream"):
				object.loadDataStream(bs)
			else:
				#print("Unhandled object type", object.typeName, "at index", i, "offset", object.streamOffset)
				if object.nifSize < 0:
					print("Unknown object", object.typeName, "has unknown size, breaking.")
					break

			#if object sizes are available, explicitly seek to next
			if object.nifSize > 0:
				bs.seek(object.streamOffset+object.nifSize)
		
		dupNodeNames = False
		uniqueNames = set()
		#after all objects have been loaded, loop through and set parents based on child lists
		for object in self.objects:
			if object.isBone:
				objName = noeSafeGet(object, "name")
				if objName is not None:
					if objName in uniqueNames:
						dupNodeNames = True
					else:
						uniqueNames.add(objName)
					
			for childID in object.childLinks:
				if childID != NIF_INVALID_LINK_ID:
					if self.objects[childID].parentIndex != -1:
						print("WARNING: Node is parented by more than one other node.")
					self.objects[childID].parentIndex = object.index

		#if necessary, run through all objects after loading and rename them
		if noesis.optWasInvoked("-nifforcenodenames"):
			for object in self.objects:
				object.name = "node%i"%object.index
		elif dupNodeNames:
			print("NIF contains duplicate node names. Using prefix.")
			for object in self.objects:
				objName = noeSafeGet(object, "name")
				object.name = "object%04i"%object.index
				if objName:
					object.name += "_" + objName
		return 1

	def loadLinkID(self, bs):
		linkID = bs.readUInt()
		return linkID
	
	def loadLinkIDs(self, bs):
		numLinkIDs = bs.readUInt()
		if numLinkIDs == NIF_INVALID_LINK_ID_COUNT:
			return []
		if numLinkIDs > NIF_MAX_SANE_LINK_ID_COUNT:
			noesis.doException("Error: Suspiciously large link ID list: " + repr(numLinkIDs))

		linkIDs = []
		for i in range(0, numLinkIDs):
			linkIDs.append(self.loadLinkID(bs))
		return linkIDs

	def loadAll(self):
		if self.loadHeader() == 0:
			return 0
			
		print("NIF version:", ((self.fileVer>>24) & 255), ((self.fileVer>>16) & 255), ((self.fileVer>>8) & 255), (self.fileVer & 255))
		print("User version:", ((self.userVersion>>24) & 255), ((self.userVersion>>16) & 255), ((self.userVersion>>8) & 255), (self.userVersion & 255))

		if self.fileVer >= nifVersion(20, 9, 0, 1):
			if self.loadMetaData() == 0:
				return 0
			
		if self.fileVer >= nifVersion(5, 0, 0, 1):
			if self.loadTypeNames() == 0:
				return 0

		if self.fileVer >= nifVersion(20, 2, 0, 5):
			if self.loadObjectSizes() == 0:
				return 0
				
		if self.fileVer >= nifVersion(20, 1, 0, 1):
			if self.loadStringTable() == 0:
				return 0

		if self.fileVer >= nifVersion(5, 0, 0, 6):
			if self.loadObjectGroups() == 0:
				return 0
		
		if self.loadObjects() == 0:
			return 0

		return 1
	
	def createNoeMatFromProperties(self, noeMatList, noeTexList, mesh):
		matPropObj = None
		texPropObj = None
		noFaceCull = False
		bsShaderProp = None
		alphaPropObj = None
		#run through all the property objects and dig out the stuff we care about
		for id in mesh.nodePropertyIDs:
			propObj = self.objects[id]
			if propObj.hasMaterialProps:
				matPropObj = propObj
			texPropFlags = noeSafeGet(propObj, "texPropFlags")
			if texPropFlags is not None:
				texPropObj = propObj
			cullMode = noeSafeGet(propObj, "cullMode")
			if cullMode is not None and cullMode == 3:
				noFaceCull = True
			#check for an alpha property
			alphaFlags = noeSafeGet(propObj, "alphaFlags")
			if alphaFlags is not None:
				alphaPropObj = propObj
			#if we haven't come across a bethesda shader property yet, see if this is one
			if bsShaderProp is None:
				bsTexSetID = noeSafeGet(propObj, "bsTexSetID")
				if bsTexSetID is not None:
					bsShaderProp = propObj

		if matPropObj is None or matPropObj.name == "":
			matName = "mesh" + repr(mesh.index) + "material"
		else:
			#intentionally create a material for each mesh object, since materials with the same name can have different properties
			matName = matPropObj.name + "_" + repr(mesh.index)

		noeMat = NoeMaterial(matName, "")
		noeMatList.append(noeMat)
		if bsShaderProp is not None:
			#apply bethesda shader properties if possible
			#possible todo - apply other properties from the bsshader
			if bsShaderProp.bsTexSetID != NIF_INVALID_LINK_ID:
				bsTexSet = self.objects[bsShaderProp.bsTexSetID]
				if len(bsTexSet.texNames) >= 5:
					noeMat.setTexture(bsTexSet.texNames[0])
					noeMat.setNormalTexture(bsTexSet.texNames[1])
					
					if self.nifHack == NIF_HACK_FO4:
						if noesis.optWasInvoked("-nifpbrtest") and len(bsTexSet.texNames) >= 7 and rapi.getExtensionlessName(bsTexSet.texNames[7]).lower().endswith("_s"):
							#for now, assume everything is metal (with metalness in red channel)
							noeMat.setSpecularTexture(bsTexSet.texNames[7])
							noeMat.flags |= noesis.NMATFLAG_PBR_SPEC_IR_RG | noesis.NMATFLAG_PBR_METAL
							#flip gloss into roughness
							noeMat.setRoughness(-1.0, 1.0)
						else:
							#if no pbr, just do some arbitrary scaling on the envmap
							envScale = 0.25
							fresnelScale = 0.5
							noeMat.setEnvColor(NoeVec4( (envScale, envScale, envScale, fresnelScale) ))

						noeMat.flags |= noesis.NMATFLAG_ENV_FLIP
						#FO4 makes extensive use of NiAlphaProperty, so disable default blending if alpha blend and alpha test bits are unset
						if alphaPropObj is None or (alphaPropObj.alphaFlags & (1 | 512)) == 0:
							noeMat.setDefaultBlend(0)
						
					if noesis.optWasInvoked("-nifforceenv"):
						envTex = noesis.optGetArg("-nifforceenv")
						noeMat.setEnvTexture(envTex)
					else:
						noeMat.setEnvTexture(bsTexSet.texNames[4])

		if matPropObj:
			#noeMat.setDiffuseColor((matPropObj.matDiffuse[0], matPropObj.matDiffuse[1], matPropObj.matDiffuse[2], matPropObj.matAlpha))
			#kind of a hack to deal with 0-diffuse 1-emissive materials
			noeMat.setDiffuseColor((max(matPropObj.matDiffuse[0], matPropObj.matEmit[0]), max(matPropObj.matDiffuse[1], matPropObj.matEmit[1]), max(matPropObj.matDiffuse[2], matPropObj.matEmit[2]), matPropObj.matAlpha))
			noeMat.setSpecularColor((matPropObj.matSpecular[0], matPropObj.matSpecular[1], matPropObj.matSpecular[2], matPropObj.matShine))
						
		#standard texture properties path
		if texPropObj is not None and len(texPropObj.texList) > 0:
			diffuseIndex = 0
			normalIndex = 6
			specIndex = 3
			#possible todo - emissive is 4 by standard, could set a nextpass on the material to deal with this
			#some version 20.6 files have lightmaps stuffed into 2, but this conflicts with what some other files report, so it has to be forced
			lmIndex = -1
			if noesis.optWasInvoked("-niflmindex"):
				lmIndex = int(noesis.optGetArg("-niflmindex"))

			tex0 = texPropObj.texList[diffuseIndex] if len(texPropObj.texList) > diffuseIndex else None
			tex3 = texPropObj.texList[specIndex] if len(texPropObj.texList) > specIndex else None
			tex6 = texPropObj.texList[normalIndex] if len(texPropObj.texList) > normalIndex else None
			tex2 = texPropObj.texList[lmIndex] if len(texPropObj.texList) > lmIndex and lmIndex >= 0 else None
			if tex0 is None and len(texPropObj.texList) > 1:
				#if no diffuse, try applying any lightmaps as diffuse
				tex0 = texPropObj.texList[1]
			if tex0 is not None and tex0.sourceTexLinkID != NIF_INVALID_LINK_ID:
			#can be none if the source texture is not in this file
				tex0Source = self.objects[tex0.sourceTexLinkID]
				if tex0Source.noeTexIndex >= 0:
					noeTex = noeTexList[tex0Source.noeTexIndex]
					noeMat.setTexture(noeTex.name)
					"""
					untested:
					if (tex0.flags & 0xFF) != 0:
						preferTexCoord = (tex0.flags & 0xFF)
					"""
				else:
					#set the name to reference external textures if necessary
					noeMat.setTexture(tex0Source.texFileName)
			#assign normal map too if it's available
			if tex6 is not None and tex6.sourceTexLinkID != NIF_INVALID_LINK_ID:
				tex6Source = self.objects[tex6.sourceTexLinkID]
				if tex6Source.noeTexIndex >= 0:
					noeTex = noeTexList[tex6Source.noeTexIndex]
					noeMat.setNormalTexture(noeTex.name)
				else:
					#set the name to reference external textures if necessary
					noeMat.setNormalTexture(tex6Source.texFileName)
			#assign spec map too if it's available
			if tex3 is not None and tex3.sourceTexLinkID != NIF_INVALID_LINK_ID:
				tex3Source = self.objects[tex3.sourceTexLinkID]
				if tex3Source.noeTexIndex >= 0:
					noeTex = noeTexList[tex3Source.noeTexIndex]
					noeMat.setSpecularTexture(noeTex.name)
				else:
					#set the name to reference external textures if necessary
					noeMat.setSpecularTexture(tex3Source.texFileName)
			#lightmap
			if tex2 is not None and tex2.sourceTexLinkID != NIF_INVALID_LINK_ID:
				tex2Source = self.objects[tex2.sourceTexLinkID]
				if tex2Source.noeTexIndex >= 0:
					noeTex = noeTexList[tex2Source.noeTexIndex]
					noeMat.setOcclTexture(noeTex.name)
				else:
					#set the name to reference external textures if necessary
					noeMat.setOcclTexture(tex2Source.texFileName)
				noeMat.setFlags2(noeMat.flags2 | noesis.NMATFLAG2_OCCL_UV1 | noesis.NMATFLAG2_OCCL_ISLM | noesis.NMATFLAG2_PREFERPPL)
				
			if noesis.optWasInvoked("-nifpbrtest"):
				#pbr test on standard path. this is bogus, don't think anything actually uses this convention.
				noeMat.flags |= noesis.NMATFLAG_PBR_SPEC
				noeMat.setFlags2(noeMat.flags2 | noesis.NMATFLAG2_PREFERPPL)
				#flip gloss into roughness
				glossScale = min(matPropObj.matShine / 100.0, 1.0) if matPropObj else 1.0
				defaultSpec = 0.01
				noeMat.setSpecularColor((defaultSpec, defaultSpec, defaultSpec, 1.0))
				noeMat.pbrFresnelScale = defaultSpec
				
				noeMat.setRoughness(-glossScale, 1.0)				
				noeMat.setEnvTexture(noesis.getScenesPath() + "sample_pbr_e4.dds")
			
		if alphaPropObj and alphaPropObj.alphaFlags & 1:
			blendStrings = (
				"GL_ONE",
				"GL_ZERO",
				"GL_SRC_COLOR",
				"GL_ONE_MINUS_SRC_COLOR",
				"GL_DST_COLOR",
				"GL_ONE_MINUS_DST_COLOR",
				"GL_SRC_ALPHA",
				"GL_ONE_MINUS_SRC_ALPHA",
				"GL_DST_ALPHA",
				"GL_ONE_MINUS_DST_ALPHA",
				"GL_SRC_ALPHA_SATURATE"
			)
			blendSrc = (alphaPropObj.alphaFlags >> 1) & 15
			blendDst = (alphaPropObj.alphaFlags >> 5) & 15
			if blendSrc < len(blendStrings) and blendDst < len(blendStrings):
				if blendSrc != 6 or blendDst != 7: #just let "default blend" handle this
					if not alphaPropObj.alphaFlags & 512:
						noeMat.setDefaultBlend(0)
					noeMat.setBlendMode(blendStrings[blendSrc], blendStrings[blendDst])
					noeMat.disableLighting = 1
				
		if noFaceCull is True:
			noeMat.flags |= noesis.NMATFLAG_TWOSIDED

		return noeMat
	
	def rpgBindWeightsForStaticNode(self, geomNode, noeBones, bindCorrectionBones, numVerts):
		didSetBindTransform = False
		#ensure that there's no map set
		rapi.rpgSetBoneMap(None)
		geomNodeIndex = 0
		#all oriented nodes are part of the skeleton, which should include this geom node
		noeBoneIndex = noeSafeGet(geomNode, "noeBoneIndex")
		if noeBoneIndex is not None:
			geomNodeIndex = noeBoneIndex
			#set the relative transform matrix to the modelspace matrix, because unskinned geometry is already in "bone" space
			bindCorrectionBones[noeBoneIndex].setMatrix(noeBones[noeBoneIndex].getMatrix())
			didSetBindTransform = True
		else:
			print("WARNING: Geometry node is not part of the Noesis skeleton.")
		endianStr = "<" if self.isLittleEndian else ">"
		idxData = noePack(endianStr + "%ii"%numVerts, *[geomNodeIndex]*numVerts)
		valData = noePack(endianStr + "%if"%numVerts, *[1.0]*numVerts)
		rapi.rpgBindBoneIndexBuffer(idxData, noesis.RPGEODATA_INT, 4, 1)
		rapi.rpgBindBoneWeightBuffer(valData, noesis.RPGEODATA_FLOAT, 4, 1)
		return didSetBindTransform
	
	def rpgCommitTriangleGeometry(self, noeBones, bindCorrectionBones, noeMatList, noeTexList):
		noStaticWeights = noesis.optWasInvoked("-nifnostaticweights")
		useVertColors = noesis.optWasInvoked("-nifusevcolors")

		#run through and draw the triangle geometry
		for geom in self.nifTriGeom:
			if geom.geomMdlLinkID < 0 or geom.geomMdlLinkID >= len(self.objects):
				print("WARNING: Invalid geometry model link ID.")
				continue

			triData = self.objects[geom.geomMdlLinkID]
			if triData.geomPositions is None:
				#nothing to do without at least some position data
				continue
				
			#clear bound data
			rapi.rpgClearBufferBinds()
			rapi.rpgSetBoneMap(None)	
				
			rapi.rpgBindPositionBuffer(triData.geomPositions, noesis.RPGEODATA_FLOAT, 12)
			if triData.geomNormals is not None:
				rapi.rpgBindNormalBuffer(triData.geomNormals, noesis.RPGEODATA_FLOAT, 12)
			if triData.geomColors is not None and useVertColors > 0:
				rapi.rpgBindColorBuffer(triData.geomColors, noesis.RPGEODATA_FLOAT, 16, 4)
			if triData.geomUVSets is not None and len(triData.geomUVSets) > 0:
				rapi.rpgBindUV1Buffer(triData.geomUVSets[0], noesis.RPGEODATA_FLOAT, 8)
				if len(triData.geomUVSets) > 1:
					rapi.rpgBindUV2Buffer(triData.geomUVSets[1], noesis.RPGEODATA_FLOAT, 8)

			#create the material
			noeMat = self.createNoeMatFromProperties(noeMatList, noeTexList, geom)

			rapi.rpgSetMaterial(noeMat.name)
			rapi.rpgSetName(geom.name)
			
			vertBoneIndices = None
			vertBoneWeights = None
			weightsPerVertex = 0
			skinBoneIDToNoeBoneIDMap = []
			needSkinTransform = False
			if geom.geomSkinLinkID != NIF_INVALID_LINK_ID:
				skinInstance = self.objects[geom.geomSkinLinkID]
				if skinInstance.skinDataID != NIF_INVALID_LINK_ID:
					skinData = self.objects[skinInstance.skinDataID]
					if skinData.skinHasVertData is True:
						if skinData.numSkinBones != len(skinInstance.skinBoneIDs):
							print("WARNING: Number of bones in SkinData does not match bone ID count:", skinData.numSkinBones, "versus", len(skinInstance.skinBoneIDs))
						else:
							numVerts = len(triData.geomPositions)
							weightsPerVertex = skinData.weightsPerVert
							vertIndices = [0]*weightsPerVertex*numVerts
							vertWeights = [0]*weightsPerVertex*numVerts
							vertWeightCounts = [0]*numVerts
							for i in range(0, skinData.numSkinBones):
								boneID = skinInstance.skinBoneIDs[i]
								boneObj = self.objects[boneID]
								noeBoneIndex = noeSafeGet(boneObj, "noeBoneIndex")
								localBoneIndex = len(skinBoneIDToNoeBoneIDMap)
								if noeBoneIndex is None or noeBoneIndex < 0:
									print("WARNING: SkinData specified a bone object that is not part of the skeleton.")
									skinBoneIDToNoeBoneIDMap.append(0)
								else:
									skinBoneIDToNoeBoneIDMap.append(noeBoneIndex)

								baseWeightIndex, numBoneWeights = skinData.skinBoneVertOfsAndLen[i]
								for j in range(0, numBoneWeights):
									vertIndex, vertWeight = skinData.skinBoneWeightDataList[baseWeightIndex+j]
									weightOffset = vertIndex*weightsPerVertex + vertWeightCounts[vertIndex]
									vertIndices[weightOffset] = localBoneIndex
									vertWeights[weightOffset] = noeBoneIndex
									vertWeightCounts[vertIndex] += 1
									if vertWeightCounts[vertIndex] > weightsPerVertex:
										noesis.doException("Ended up with more weights for a vertex than expected: " + repr(weightsPerVertex) + " versus " + repr(vertWeightCounts[vertIndex]))
									
								noeBone = noeBones[noeBoneIndex] if noeBoneIndex >= 0 else None
								if bindCorrectionBones is not None and noeBone is not None:
									#(reference in bone list by index because rapi.multiplyBones has copied the bones off)
									bindCorrectionBones[noeBone.index].setMatrix(skinData.skinToBoneMats[i] * noeBone.getMatrix())
									needSkinTransform = True
							#generate the bytearrays to feed to noesis for the indices and weights								
							vertBoneIndices = noePack("%ii"%weightsPerVertex*numVerts, *vertIndices)
							vertBoneWeights = noePack("%if"%weightsPerVertex*numVerts, *vertWeights)								
					
			if weightsPerVertex > 0:
				rapi.rpgBindBoneIndexBuffer(vertBoneIndices, noesis.RPGEODATA_UINT, weightsPerVertex*4, weightsPerVertex)
				rapi.rpgBindBoneWeightBuffer(vertBoneWeights, noesis.RPGEODATA_FLOAT, weightsPerVertex*4, weightsPerVertex)
				rapi.rpgSetBoneMap(skinBoneIDToNoeBoneIDMap)
			elif noStaticWeights == 0:
				#if there's no weighting, skin this thing to its own node
				needSkinTransform = self.rpgBindWeightsForStaticNode(geom, noeBones, bindCorrectionBones, len(triData.geomPositions))
				
			numPreCommitVerts = rapi.rpgGetVertexCount()

			numStrips = noeSafeGet(triData, "geomNumStrips")
			if numStrips is not None:
				#strips
				if numStrips <= 0 or triData.geomStripListData is None:
					#nothing to draw
					continue
				currentStripOfs = 0
				for i in range(0, numStrips):
					stripLen = triData.geomStripLens[i]
					stripData = triData.geomStripListData[currentStripOfs:currentStripOfs+stripLen*2]
					rapi.rpgCommitTriangles(stripData, noesis.RPGEODATA_USHORT, stripLen, noesis.RPGEO_TRIANGLE_STRIP, 1)					
					currentStripOfs += stripLen*2
			else:
				#lists
				if triData.geomNumTriIndices <= 0 or triData.geomTriListData is None:
					#nothing to draw
					continue
				rapi.rpgCommitTriangles(triData.geomTriListData, noesis.RPGEODATA_USHORT, triData.geomNumTriIndices, noesis.RPGEO_TRIANGLE, 1)					

			#skin verts into bone space as needed.
			if needSkinTransform is True and not noesis.optWasInvoked("-nifnotransform"):
				numVertsToSkin = rapi.rpgGetVertexCount()-numPreCommitVerts
				rapi.rpgSkinPreconstructedVertsToBones(bindCorrectionBones, numPreCommitVerts, numVertsToSkin)
				#reset matrices
				for bindCorrectionBone in bindCorrectionBones:
					bindCorrectionBone.setMatrix(NoeMat43())

	def rpgCommitMeshes(self, noeBones, bindCorrectionBones, noeMatList, noeTexList):
		noStaticWeights = noesis.optWasInvoked("-nifnostaticweights")
		useVertColors = noesis.optWasInvoked("-nifusevcolors")
		
		#run through and draw the meshes
		for mesh in self.nifMeshes:
			#if "collision" in mesh.name:
			#	continue
			if mesh.meshPrimType == 0:
				primType = noesis.RPGEO_TRIANGLE
			elif mesh.meshPrimType == 1:
				primType = noesis.RPGEO_TRIANGLE_STRIP
			elif mesh.meshPrimType == 4:
				primType = noesis.RPGEO_QUAD_ABC_ACD
			else:
				print("WARNING: Unsupported primitive type", mesh.meshPrimType)
				continue

			#index and position streams are mandatory
			indexStreamRef, indexElem, indexStream = mesh.getStreamAndElement("INDEX")
			if indexStreamRef is None:
				print("WARNING: Could not find element for INDEX")
				continue
			posStreamRef, posElem, posStream = mesh.getStreamAndElement("POSITION")
			if posStreamRef is None:
				print("WARNING: Could not find element for POSITION")
				continue

			indexDataType = nifNoeDataTypeForNifDataType(indexElem.dataType)
			if indexDataType < 0:
				print("WARNING: Index data in unsupported data type")
				continue
			posDataType = nifNoeDataTypeForNifDataType(posElem.dataType)
			if posDataType < 0:
				print("WARNING: Position data in unsupported data type")
				continue

			#go through mesh modifiers and find skinning modifiers in order to determine bone objects,
			#and subsequently their mapping to noesis bones
			needSkinTransform = False
			skinBoneIDToNoeBoneIDMap = []
			for modID in mesh.modLinks:
				modObj = self.objects[modID]
				boneLinkIDs = noeSafeGet(modObj, "boneLinkIDs")
				if boneLinkIDs is not None:
					for i in range(0, len(boneLinkIDs)):
						boneID = boneLinkIDs[i]
						boneObj = self.objects[boneID]
						noeBoneIndex = noeSafeGet(boneObj, "noeBoneIndex")
						if noeBoneIndex is None or noeBoneIndex < 0:
							print("WARNING: Mesh specified a bone object that is not part of the skeleton.")
							skinBoneIDToNoeBoneIDMap.append(0)
						else:
							skinBoneIDToNoeBoneIDMap.append(noeBoneIndex)

						noeBone = noeBones[noeBoneIndex] if noeBoneIndex >= 0 else None
						if bindCorrectionBones is not None and noeBone is not None:
							#(reference in bone list by index because rapi.multiplyBones has copied the bones off)
							bindCorrectionBones[noeBone.index].setMatrix(modObj.skinToBoneMats[i] * noeBone.getMatrix())
							needSkinTransform = True
					#break out after encountering a skin modifier
					break

			preferTexCoord = -1
					
			#create the material
			noeMat = self.createNoeMatFromProperties(noeMatList, noeTexList, mesh)

			#skip rendering in material if mesh node is hidden
			noeMat.setSkipRender(mesh.flags & 1)

			#possible todo - use matPropObj properties on noeMat

			rapi.rpgSetMaterial(noeMat.name)
			rapi.rpgSetName(mesh.name)

			#get optional streams
			uvStreamRef, uvElem, uvStream = mesh.getStreamAndElement("TEXCOORD", preferTexCoord)
			uv2StreamRef, uv2Elem, uv2Stream = mesh.getStreamAndElement("TEXCOORD", 1)
			nrmStreamRef, nrmElem, nrmStream = mesh.getStreamAndElement("NORMAL")
			clrStreamRef, clrElem, clrStream = mesh.getStreamAndElement("COLOR")
			widxStreamRef, widxElem, widxStream = mesh.getStreamAndElement("BLENDINDICES")
			wvalStreamRef, wvalElem, wvalStream = mesh.getStreamAndElement("BLENDWEIGHT")
			bonePalStreamRef, bonePalElem, bonePalStream = mesh.getStreamAndElement("BONE_PALETTE")
		
			numPreCommitVerts = rapi.rpgGetVertexCount()
	
			for i in range(0, mesh.numSubMeshes):
				#clear bound data
				rapi.rpgClearBufferBinds()
				rapi.rpgSetBoneMap(None)	
			
				#set bone map if applicable
				if bonePalStreamRef is not None:
					bonePalDataType = nifNoeDataTypeForNifDataType(bonePalElem.dataType)
					if bonePalDataType < 0:
						print("WARNING: Bone palette in unsupported data type")
					else:
						bonePalRegion = bonePalStream.streamRegions[bonePalStreamRef.submeshRegionMap[i]]
						bonePalOffset = bonePalRegion[0]*bonePalStream.elemStride+bonePalElem.offset
						bonePal = rapi.dataToIntList(bonePalStream.streamData[bonePalOffset:], bonePalRegion[1], bonePalDataType, NOE_LITTLEENDIAN if self.isLittleEndian else NOE_BIGENDIAN)
						#take the provided bone palette and map it to the noesis skeleton
						bonePalMapped = []
						for index in bonePal:
							bonePalMapped.append(skinBoneIDToNoeBoneIDMap[index])
						rapi.rpgSetBoneMap(bonePalMapped)
				elif len(skinBoneIDToNoeBoneIDMap) > 0:
					#if there was no bone palette, we still need to map the blend indices directly to the noesis skeleton
					rapi.rpgSetBoneMap(skinBoneIDToNoeBoneIDMap)
		
				#bind mandatory position stream
				posRegion = posStream.streamRegions[posStreamRef.submeshRegionMap[i]]
				rapi.rpgBindPositionBufferOfs(posStream.streamData, posDataType, posStream.elemStride, posRegion[0]*posStream.elemStride+posElem.offset)

				#try binding optional blend weight streams
				if widxStreamRef is not None and wvalStreamRef is not None:
					widxDataType = nifNoeDataTypeForNifDataType(widxElem.dataType)
					wvalDataType = nifNoeDataTypeForNifDataType(wvalElem.dataType)
					if widxDataType < 0 or wvalDataType < 0:
						print("WARNING: Blend weight data in unsupported data type")
					else:
						widxRegion = widxStream.streamRegions[widxStreamRef.submeshRegionMap[i]]
						rapi.rpgBindBoneIndexBufferOfs(widxStream.streamData, widxDataType, widxStream.elemStride, widxRegion[0]*widxStream.elemStride+widxElem.offset, widxElem.count)
						wvalRegion = wvalStream.streamRegions[wvalStreamRef.submeshRegionMap[i]]
						rapi.rpgBindBoneWeightBufferOfs(wvalStream.streamData, wvalDataType, wvalStream.elemStride, wvalRegion[0]*wvalStream.elemStride+wvalElem.offset, wvalElem.count)
				elif noStaticWeights == 0:
					#if there's no weighting, skin this thing to its own node
					#ensure that there's no map set
					rapi.rpgSetBoneMap(None)
					meshNodeIndex = 0
					#all oriented nodes are part of the skeleton, which should include this mesh node
					noeBoneIndex = noeSafeGet(mesh, "noeBoneIndex")
					if noeBoneIndex is not None:
						meshNodeIndex = noeBoneIndex
						#set the relative transform matrix to the modelspace matrix, because unskinned geometry is already in "bone" space
						bindCorrectionBones[noeBoneIndex].setMatrix(noeBones[noeBoneIndex].getMatrix())
						needSkinTransform = True
					else:
						print("WARNING: Mesh node is not part of the Noesis skeleton.")
					endianStr = "<" if self.isLittleEndian else ">"
					idxData = noePack(endianStr + "%ii"%posRegion[1], *[meshNodeIndex]*posRegion[1])
					valData = noePack(endianStr + "%if"%posRegion[1], *[1.0]*posRegion[1])
					rapi.rpgBindBoneIndexBuffer(idxData, noesis.RPGEODATA_INT, 4, 1)
					rapi.rpgBindBoneWeightBuffer(valData, noesis.RPGEODATA_FLOAT, 4, 1)

				#try binding optional UV stream
				if uvStreamRef is not None:
					uvDataType = nifNoeDataTypeForNifDataType(uvElem.dataType)
					if uvDataType < 0:
						print("WARNING: UV data in unsupported data type")
					else:
						uvRegion = uvStream.streamRegions[uvStreamRef.submeshRegionMap[i]]
						rapi.rpgBindUV1BufferOfs(uvStream.streamData, uvDataType, uvStream.elemStride, uvRegion[0]*uvStream.elemStride+uvElem.offset)

				#try binding optional UV2 stream
				if uv2StreamRef is not None and preferTexCoord != 1:
					uv2DataType = nifNoeDataTypeForNifDataType(uv2Elem.dataType)
					if uv2DataType < 0:
						print("WARNING: UV2 data in unsupported data type")
					else:
						uv2Region = uv2Stream.streamRegions[uv2StreamRef.submeshRegionMap[i]]
						rapi.rpgBindUV2BufferOfs(uv2Stream.streamData, uv2DataType, uv2Stream.elemStride, uv2Region[0]*uv2Stream.elemStride+uv2Elem.offset)

				#try binding optional normal stream
				if nrmStreamRef is not None:
					nrmDataType = nifNoeDataTypeForNifDataType(nrmElem.dataType)
					if nrmDataType < 0:
						print("WARNING: Normal data in unsupported data type")
					else:
						nrmRegion = nrmStream.streamRegions[nrmStreamRef.submeshRegionMap[i]]
						rapi.rpgBindNormalBufferOfs(nrmStream.streamData, nrmDataType, nrmStream.elemStride, nrmRegion[0]*nrmStream.elemStride+nrmElem.offset)

				#try binding optional color stream
				if clrStreamRef is not None and useVertColors > 0:
					if clrElem.count != 3 and clrElem.count != 4:
						print("Unsupported color element count:", clrElem.count)
					else:
						clrDataType = nifNoeDataTypeForNifDataType(clrElem.dataType)
						if clrDataType < 0:
							print("WARNING: Color data in unsupported data type")
						else:
							clrRegion = clrStream.streamRegions[clrStreamRef.submeshRegionMap[i]]
							rapi.rpgBindColorBufferOfs(clrStream.streamData, clrDataType, clrStream.elemStride, clrRegion[0]*clrStream.elemStride+clrElem.offset, clrElem.count)

				#commit the triangles for the submesh
				idxRegion = indexStream.streamRegions[indexStreamRef.submeshRegionMap[i]]
				idxOfs = idxRegion[0]*indexStream.elemStride
				idxEnd = idxOfs + idxRegion[1]*indexStream.elemStride
				rapi.rpgCommitTriangles(indexStream.streamData[idxOfs:idxEnd], indexDataType, idxRegion[1], primType, 1)
				
			#skin verts into bone space as needed.
			if needSkinTransform is True and not noesis.optWasInvoked("-nifnotransform"):
				numVertsToSkin = rapi.rpgGetVertexCount()-numPreCommitVerts
				rapi.rpgSkinPreconstructedVertsToBones(bindCorrectionBones, numPreCommitVerts, numVertsToSkin)
				#reset matrices
				for bindCorrectionBone in bindCorrectionBones:
					bindCorrectionBone.setMatrix(NoeMat43())

	def rpgCommitBsShapes(self, noeBones, bindCorrectionBones, noeMatList, noeTexList):
		noStaticWeights = noesis.optWasInvoked("-nifnostaticweights")
		useVertColors = noesis.optWasInvoked("-nifusevcolors")
	
		#run through and draw the meshes
		for triShape in self.bsTriShapes:
			rapi.rpgClearBufferBinds()
			rapi.rpgSetBoneMap(None)
			
			skinInst = None if triShape.skinInstID == NIF_INVALID_LINK_ID else self.objects[triShape.skinInstID]
			isSkinned = skinInst is not None and triShape.blendWgtOffset >= 0 and triShape.blendIdxOffset >= 0
			
			#create the material
			noeMat = self.createNoeMatFromProperties(noeMatList, noeTexList, triShape)

			rapi.rpgSetMaterial(noeMat.name)
			rapi.rpgSetName(triShape.name)
			
			rapi.rpgBindPositionBufferOfs(triShape.vertData, triShape.posType, triShape.vertSize, triShape.posOffset)	

			if triShape.uvOffset >= 0:
				rapi.rpgBindUV1BufferOfs(triShape.vertData, triShape.uvType, triShape.vertSize, triShape.uvOffset)

			if triShape.normalOffset >= 0:
				rapi.rpgBindNormalBufferOfs(triShape.vertData, triShape.normalType, triShape.vertSize, triShape.normalOffset)
				if triShape.tangentOffset >= 0:
					#this calculates the tangent w based on the intended bitangent
					tangentData = rapi.callExtensionMethod("recombine_fo4_tangents", triShape.vertData, triShape.vertSize, triShape.numVerts,
															triShape.posType, triShape.posOffset, triShape.normalType, triShape.normalOffset, triShape.tangentType, triShape.tangentOffset)
					rapi.rpgBindTangentBufferOfs(tangentData, noesis.RPGEODATA_FLOAT, 16, 0)

			if triShape.colorOffset >= 0 and useVertColors > 0:
				rapi.rpgBindColorBufferOfs(triData.geomColors, triShape.colorType, triShape.vertSize, triShape.colorOffset, 4)
				
			if isSkinned:
				rapi.rpgBindBoneIndexBufferOfs(triShape.vertData, triShape.blendIdxType, triShape.vertSize, triShape.blendIdxOffset, 4)
				rapi.rpgBindBoneWeightBufferOfs(triShape.vertData, triShape.blendWgtType, triShape.vertSize, triShape.blendWgtOffset, 4)

			needSkinTransform = False
			numPreCommitVerts = rapi.rpgGetVertexCount()
				
			if isSkinned:
				#construct a bonemap from the referenced skin instance
				boneMap = []
				for boneNodeID in skinInst.boneNodeIDs:
					boneNode = self.objects[boneNodeID]
					noeBoneIndex = noeSafeGet(boneNode, "noeBoneIndex")
					boneIndex = noeBoneIndex if noeBoneIndex is not None else 0
					boneMap.append(boneIndex)
				rapi.rpgSetBoneMap(boneMap)
				if skinInst.boneDataID != NIF_INVALID_LINK_ID:
					#if we've got the inverse bind transforms, use them to transform onto the actual nodes
					boneData = self.objects[skinInst.boneDataID]
					if boneData.numBones == skinInst.numBones:
						for i in range(0, skinInst.numBones):
							boneIndex = boneMap[i]
							noeBone = noeBones[boneIndex]
							bindCorrectionBones[boneIndex].setMatrix(boneData.invBindTransforms[i] * noeBone.getMatrix())
						needSkinTransform = True							
			elif noStaticWeights == 0:
				#if there's no weighting, skin this thing to its own node
				needSkinTransform = self.rpgBindWeightsForStaticNode(triShape, noeBones, bindCorrectionBones, triShape.numVerts)
	
			rapi.rpgCommitTriangles(triShape.triData, noesis.RPGEODATA_USHORT, triShape.numTris * 3, noesis.RPGEO_TRIANGLE, 1)			

			#skin verts into bone space as needed.
			if needSkinTransform is True and not noesis.optWasInvoked("-nifnotransform"):
				numVertsToSkin = rapi.rpgGetVertexCount()-numPreCommitVerts
				rapi.rpgSkinPreconstructedVertsToBones(bindCorrectionBones, numPreCommitVerts, numVertsToSkin)
				#reset matrices
				for bindCorrectionBone in bindCorrectionBones:
					bindCorrectionBone.setMatrix(NoeMat43())
	
	def mapObjectsFromSkeletonNif(self, skelNif):
		skelNifBoneObjects = {}
		for object in skelNif.objects:
			if object.isBone is True:
				skelNifBoneObjects[object.name] = object
		nifBoneObjectIndicesByName = {}
		for i in range(0, len(self.objects)):
			object = self.objects[i]
			if object.isBone is True:
				nifBoneObjectIndicesByName[object.name] = i
				
		for object in self.objects:
			if object.isBone is True:
				if object.name in skelNifBoneObjects:
					skelObject = skelNifBoneObjects[object.name]
					#see if the parent is also a bone, and if so, transfer the parent index
					if skelObject.parentIndex >= 0:
						skelParentObject = skelNif.objects[skelObject.parentIndex]
						if skelParentObject.isBone and skelParentObject.name in nifBoneObjectIndicesByName:
							#for now, we only transfer transforms for non-root objects. otherwise, we'd need to transform up the hierarchy before grabbing,
							#in case there are parents in the skeleton nif not reflected in the nif we're mapping to.
							object.matrix = skelObject.matrix
							object.scale = skelObject.scale
							object.parentIndex = nifBoneObjectIndicesByName[skelParentObject.name]
							

def nifConstructModelFromNif(nif):
	noeMatList = []
	noeTexList = []
	for texObject in nif.nifTextures:
		if texObject.externalTex is True:
			continue

		#run through and convert texture data
		pixObject = nif.objects[texObject.pixLinkID]
		noeFmt = noesis.NOESISTEX_UNKNOWN
		pixelFormatObj = noeSafeGet(pixObject, "pixelFormat")
		if pixelFormatObj is None:
			print("WARNING: Object", texObject.pixLinkID, "type", pixObject.typeName, "should have contained a pixel format, but didn't.")
			continue
		pixelFormat = pixelFormatObj.format
		imageData = pixObject.imageData
		
		pixelImageInfo = [pixObject.numFaces, pixObject.mipLevels, pixObject.mipsTotalSize, pixObject.mipInfo]
		
		if pixelFormat == NIFTEX_RGB:
			noeFmt = noesis.NOESISTEX_RGBA32
			imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageDecodeRaw, "r8g8b8")
		elif pixelFormat == NIFTEX_RGBA:
			noeFmt = noesis.NOESISTEX_RGBA32
			if pixObject.platform == NIF_PLATFORM_PS3: #alpha first on ps3 (or so we not always correctly assume)
				imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageDecodeRaw, "a8r8g8b8")
			elif pixObject.platform == NIF_PLATFORM_XBOX360: #another potentially-faulty assumption - bgra for 360
				imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageDecodeRaw, "b8g8r8a8")
		elif pixelFormat == NIFTEX_DXT1:
			noeFmt = noesis.NOESISTEX_DXT1
		elif pixelFormat == NIFTEX_DXT3:
			noeFmt = noesis.NOESISTEX_DXT3
		elif pixelFormat == NIFTEX_DXT5:
			noeFmt = noesis.NOESISTEX_DXT5
		elif pixelFormat == NIFTEX_MONO:
			#expand out to rgba32
			noeFmt = noesis.NOESISTEX_RGBA32
			imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageDecodeRaw, "r8")
			imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageKernelProcess, 4, nifImageExpandMonoColorKernel)
		else:
			print("WARNING: Unsupported texture format", pixelFormat)

		if noeFmt != noesis.NOESISTEX_UNKNOWN:
			if pixelFormatObj.tiling != 0:
				#lots of games seem to have bad mip offsets when using tiling/swizzling modes,
				#which don't take into account necessary platform-specific padding. so, sadly,
				#we'll have to skip the mips.
				pixelImageInfo[1] = 1
			
			if pixelFormatObj.tiling == 1:
				#360 untile
				if noeFmt == noesis.NOESISTEX_RGBA32:
					imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageUntile360Raw, 4)
				else: #dxt
					imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageUntile360DXT, 8 if noeFmt == noesis.NOESISTEX_DXT1 else 16)
			elif pixelFormatObj.tiling == 3:
				#morton untile
				if noeFmt == noesis.NOESISTEX_RGBA32:
					imageData = noeProcessImage(imageData, pixelImageInfo, rapi.imageFromMortonOrder, 4, 2 if pixObject.platform == NIF_PLATFORM_VITA else 0)
				else: #dxt
					dxtBlockBytes = 4 if noeFmt == noesis.NOESISTEX_DXT1 else 8
					imageData = rapi.imageFromMortonOrder(imageData, pixObject.width>>1, pixObject.height>>2, dxtBlockBytes)
					#possible todo - support untiling dxt blocks with multiple mips/faces
					pixelImageInfo[0] = 1
					pixelImageInfo[1] = 1
					
			#name isn't guaranteed to be unique, so make a unique name instead
			texName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName())) + "_niftex_" + repr(len(noeTexList)) #texObject.texFileName
			noeTex = NoeTexture(texName, pixObject.width, pixObject.height, imageData, noeFmt)
			if pixelImageInfo[0] > 1: #if more than 1 face, set the cubemap flag
				noeTex.setFlags(noesis.NTEXFLAG_CUBEMAP)
			if pixelImageInfo[1] > 1: #set mip count
				noeTex.setMipCount(pixelImageInfo[1])
			texObject.noeTexIndex = len(noeTexList)
			noeTexList.append(noeTex)

	if noesis.optWasInvoked("-nifloadskel"):
		skelFile = noesis.optGetArg("-nifloadskel")
		if os.path.exists(skelFile):
			skelData = rapi.loadIntoByteArray(skelFile)
		else:
			relName = rapi.getDirForFilePath(rapi.getLastCheckedName()) + skelFile
			if os.path.exists(relName):
				skelData = rapi.loadIntoByteArray(relName)
			else:
				skelData = None
		if skelData is not None:
			skelNif = NifFile(NoeBitStream(skelData))
			if skelNif.loadAll() != 0:
				nif.mapObjectsFromSkeletonNif(skelNif)
			
	#find bone objects
	boneObjects = []
	for object in nif.objects:
		if object.isBone is True:
			boneObjects.append(object)

	#there's a skeleton consisting of 1 or more nodes
	noeBones = None
	if len(boneObjects) > 0:
		noeBones = []
		for object in boneObjects:
			boneMat = object.matrix if object.matrix is not None else NoeMat43()
			boneIndex = len(noeBones)
			noeBone = NoeBone(boneIndex, object.name, boneMat, None, -1)
			if len(noeBone.name) >= 128: #truncate names as necessary
				noeBone.name = "__renamed_bone_%08i"%len(noeBones)
			object.noeBoneIndex = boneIndex
			noeBones.append(noeBone)
		#set parents now that bones have been mapped out for all bone objects
		for object in boneObjects:
			if object.parentIndex >= 0:
				noeBones[object.noeBoneIndex].parentIndex = nif.objects[object.parentIndex].noeBoneIndex
		#put bones in model space instead of local space
		noeBones = rapi.multiplyBones(noeBones)

	ctx = rapi.rpgCreateContext()
	if nif.isLittleEndian is not True:
		rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
	
	bindCorrectionBones = None
	if noeBones is not None:
		#build a list of bones that will be used to transform the geometry into bone space
		bindCorrectionBones = []
		for bone in noeBones:
			newBone = NoeBone(bone.index, bone.name, NoeMat43(), None, bone.parentIndex)
			bindCorrectionBones.append(newBone)
	
	#commit triangle geometry
	nif.rpgCommitTriangleGeometry(noeBones, bindCorrectionBones, noeMatList, noeTexList)
	
	#commit meshes
	nif.rpgCommitMeshes(noeBones, bindCorrectionBones, noeMatList, noeTexList)
	
	#commit bs shapes
	nif.rpgCommitBsShapes(noeBones, bindCorrectionBones, noeMatList, noeTexList)

	mdlMats = NoeModelMaterials(noeTexList, noeMatList)

	try:
		#some models may need special tangent/bitangent treatment (which also means we can't use the fast construct path)
		if nif.nifHack == NIF_HACK_SPLATTERHOUSE:
			rapi.rpgSmoothTangents()
			rapi.rpgUnifyBinormals(1)
		elif nif.nifHack == NIF_HACK_FO4:
			rapi.rpgSetOption(noesis.RPGOPT_TANMATROTATE, 1)
			mdl = rapi.rpgConstructModel()
		else:
			mdl = rapi.rpgConstructModelSlim()
	except:
		mdl = None

	if mdl is None:
		if noeBones is not None or len(noeTexList) > 0:
			#if there was no model, create one if we still have anything worth putting in it
			mdl = NoeModel()

	if mdl is not None:
		#if there was a model created at any point, associated textures/materials with it
		mdl.setModelMaterials(mdlMats)
		#and set bones
		if noeBones is not None:
			mdl.setBones(noeBones)

		if nif.nifHack == NIF_HACK_OBLIVION or nif.nifHack == NIF_HACK_SKYRIM or nif.nifHack == NIF_HACK_FO4:
			rapi.setPreviewOption("setAngOfs", "0 90 0")
			if nif.nifHack == NIF_HACK_FO4:
				rapi.setPreviewOption("ddsAti2NoNorm", "1")
		elif nif.nifHack == NIF_HACK_SPLATTERHOUSE:
			rapi.setPreviewOption("setAngOfs", "0 180 0")
		else:
			rapi.setPreviewOption("setAngOfs", "0 270 0")
		rapi.setPreviewOption("autoLoadNonDiffuse", "1")
		
	return mdl


def nifCheckType(data):
	nif = NifFile(NoeBitStream(data))
	if nif.loadHeader() == 0:
		return 0
	return 1


def nifLoadModel(data, mdlList):
	nif = NifFile(NoeBitStream(data))
	if nif.loadAll() == 0:
		return 0
	mdl = nifConstructModelFromNif(nif)
	if mdl is not None:
		mdlList.append(mdl)
		return 1
	return 0


def kfLoadModel(data, mdlList):
	nif = NifFile(NoeBitStream(data))
	if nif.loadAll() == 0:
		return 0
	if len(nif.nifSequences) == 0:
		print("No sequences found in KF.")
		return 0

	otherNifData = rapi.loadPairedFile("Gamebryo NIF Model", ".nif")
	otherNif = NifFile(NoeBitStream(otherNifData))
	if otherNif.loadAll() == 0:
		print("Not a valid NIF.")
		return 0

	mdl = nifConstructModelFromNif(otherNif)
	if mdl is None:
		return 0

	if mdl.bones is None or len(mdl.bones) == 0:
		print("WARNING: No bones on NIF to animate.")
	else:
		seqNif = nif
		objNif = otherNif
		
		kfAnims = []
		sampleRate = 30.0
		for seq in seqNif.nifSequences:
			kfBones = []
			for evalID in seq.seqEvalIDList:
				evalObj = seqNif.objects[evalID]
				if noeSafeGet(evalObj, "evalConstData") is None:
					#probably an unhandled sequence node type
					continue
				#find the object that will be animated by this evaluator
				objToEval = None
				for object in objNif.objects:
					objName = noeSafeGet(object, "name")
					if objName == evalObj.evalName and noeSafeGet(object, "noeBoneIndex") is not None:
						objToEval = object
						break
				if objToEval is None:
					print("WARNING: Could not find bone object", evalObj.evalName)
				else:
					noeBoneIndex = noeSafeGet(objToEval, "noeBoneIndex")
					if evalObj.evalConstData is True:
						#constant evaluator, no data
						kfBone = NoeKeyFramedBone(noeBoneIndex)
						kfBone.setRotation([NoeKeyFramedValue(0.0, evalObj.evalRotate)])
						kfBone.setTranslation([NoeKeyFramedValue(0.0, evalObj.evalTranslate)])
						kfBone.setScale([NoeKeyFramedValue(0.0, evalObj.evalScale)])
						kfBones.append(kfBone)
					elif evalObj.evalDataID != NIF_INVALID_LINK_ID:
						#use data reference to get keys
						evalDataObj = seqNif.objects[evalObj.evalDataID]
						kfBone = NoeKeyFramedBone(noeBoneIndex)
						kfBone.setRotation(evalDataObj.rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, evalDataObj.rotKeyType)
						kfBone.setTranslation(evalDataObj.trnKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, evalDataObj.trnKeyType)
						kfBone.setScale(evalDataObj.sclKeys, noesis.NOEKF_SCALE_SCALAR_1, evalDataObj.sclKeyType)
						kfBones.append(kfBone)
			kfAnims.append(NoeKeyFramedAnim(seq.seqName, mdl.bones, kfBones, sampleRate))
		mdl.setAnims(kfAnims)

	mdlList.append(mdl)
	return 1
