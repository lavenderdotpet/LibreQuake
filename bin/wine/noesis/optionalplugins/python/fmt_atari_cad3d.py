from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("CAD-3D Model", ".3d")
	noesis.setHandlerTypeCheck(handle, c3d1CheckType)
	noesis.setHandlerLoadModel(handle, c3d1LoadModel)

	handle = noesis.register("CAD-3D V2 Model", ".3d2")
	noesis.setHandlerTypeCheck(handle, c3d2CheckType)
	noesis.setHandlerLoadModel(handle, c3d2LoadModel)
	
	handle = noesis.register("CAD-3D Animation", ".3da")
	noesis.setHandlerTypeCheck(handle, caniCheckType)
	noesis.setHandlerLoadModel(handle, caniLoadModel)
	
	return 1
		

class CadObject:
	def __init__(self, bs, owner):
		self.name = noeAsciiFromBytes(bs.readBytes(9).split(b"\0",1)[0])
		self.vertCount = bs.readUShort()
		if (self.vertCount & 0x8000):
			#unknown, encountered a sample file like this
			bs.readUShort()
			self.vertCount = 0
			return
		self.positionsX = []
		self.positionsY = []
		self.positionsZ = []
		if owner.id == 0x3D02:
			for posIndex in range(0, self.vertCount):
				self.positionsX.append(bs.readShort() / 100.0)
				self.positionsY.append(bs.readShort() / 100.0)
				self.positionsZ.append(bs.readShort() / 100.0)
		else:
			for posIndex in range(0, self.vertCount):
				self.positionsX.append(noesis.getMFFP(bs.readUInt()))
			for posIndex in range(0, self.vertCount):
				self.positionsY.append(noesis.getMFFP(bs.readUInt()))
			for posIndex in range(0, self.vertCount):
				self.positionsZ.append(noesis.getMFFP(bs.readUInt()))
		self.faceCount = bs.readUShort()
		self.faceIndices = []
		self.faceColors = []
		for faceIndex in range(0, self.faceCount):
			self.faceIndices.append(bs.readUShort())
			self.faceIndices.append(bs.readUShort())
			self.faceIndices.append(bs.readUShort())
			self.faceColors.append(bs.readUShort())

class CadModel:
	def __init__(self, data):
		self.bs = NoeBitStream(data, NOE_BIGENDIAN)
		self.defaultMaterialName = "cadmaterial"
			
	def parse(self, id):
		bs = self.bs
		self.id = bs.readUShort()
		if self.id != id:
			return -1
		self.objectCount = bs.readUShort()
		if self.objectCount == 0:
			return -1
		self.lightsEnabled = (bs.readUShort(), bs.readUShort(), bs.readUShort())
		self.lightsBrightness = (bs.readUShort(), bs.readUShort(), bs.readUShort())
		if self.id == 0x3D02:
			self.lightAmbient = bs.readUShort()
		self.lightPositionsX = (bs.readUShort(), bs.readUShort(), bs.readUShort())
		self.lightPositionsY = (bs.readUShort(), bs.readUShort(), bs.readUShort())
		self.lightPositionsZ = (bs.readUShort(), bs.readUShort(), bs.readUShort())
		self.objectsOffset = bs.tell()
		return 0
			
	def load(self):
		bs = self.bs
		bs.seek(self.objectsOffset, NOESEEK_ABS)
		self.objects = []
		for objectIndex in range(0, self.objectCount):
			object = CadObject(bs, self)
			if object.vertCount > 0:
				self.objects.append(object)
			
	def createDefaultMaterialData(self):
		noeMat = NoeMaterial(self.defaultMaterialName, "")
		noeMat.setTexture(noesis.getScenesPath() + "sample_pbr_o.png")
		noeMat.setNormalTexture(noesis.getScenesPath() + "sample_pbr_n.png")
		noeMat.setSpecularTexture(noesis.getScenesPath() + "sample_pbr_o.png")
		noeMat.setEnvTexture(noesis.getScenesPath() + "sample_pbr_e4.dds")
		noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_SPEC_IR_RG
		noeMat.setMetal(0.0, 1.0)
		noeMat.setRoughness(0.0, 0.5)
		noeMat.setDefaultBlend(0)
		return NoeModelMaterials([], [noeMat])
			
class CadV1Model(CadModel):
	def __init__(self, data):
		super().__init__(data)
	
	def parse(self):
		return super().parse(0x3D3D)
	
	def createModel(self):
		ctx = rapi.rpgCreateContext()
		color0 = NoeVec4((1.0, 0.0, 0.0, 1.0))
		color1 = NoeVec4((0.0, 0.0, 1.0, 1.0))
		rapi.rpgSetMaterial(self.defaultMaterialName)
		for object in self.objects:
			rapi.rpgSetName(object.name)
			for faceIndex in range(0, object.faceCount):
				vertIndices = object.faceIndices[faceIndex * 3 : faceIndex * 3 + 3]
				colorBits = object.faceColors[faceIndex]
				rapi.immBegin(noesis.RPGEO_TRIANGLE)
				colorLow = colorBits & 15
				if colorLow == 0 or colorLow >= 15:
					rapi.immColor4((1.0, 1.0, 1.0, 1.0))
				elif colorLow <= 7:
					shade = (colorLow - 1) / 6.0
					rapi.immColor4((color0 * NoeVec4((shade, shade, shade, 1.0))).vec4)
				else:
					shade = (colorLow - 8) / 6.0
					rapi.immColor4((color1 * NoeVec4((shade, shade, shade, 1.0))).vec4)
					
				for vertIndex in vertIndices:
					pos = (object.positionsX[vertIndex], object.positionsY[vertIndex], object.positionsZ[vertIndex])
					rapi.immVertex3(pos)
				rapi.immEnd()
		rapi.rpgFlatNormals()
		rapi.rpgCreatePlaneSpaceUVs()
		return rapi.rpgConstructModel()

		
class CadV2Model(CadModel):
	def __init__(self, data):
		super().__init__(data)
	
	def parse(self):
		if super().parse(0x3D02) != 0:
			return -1

		bs = self.bs
		paletteData = rapi.swapEndianArray(bs.readBytes(16 * 2), 2)
		self.decodedPalette = rapi.imageDecodeRaw(paletteData, 16, 1, "b3p1g3p1r3p5")
		self.colorBases = noeUnpack("H" * 16, rapi.swapEndianArray(bs.readBytes(16 * 2), 2))
		self.palType = bs.readUShort()
		self.wireframeColor = bs.readUShort()
		self.outlineColor = bs.readUShort()
		bs.seek(150, NOESEEK_REL)
	
		self.objectsOffset = bs.tell() #update the offset accounting for v2 data
		return 0
		
	def createModel(self):
		ctx = rapi.rpgCreateContext()
		rapi.rpgSetMaterial(self.defaultMaterialName)
		for object in self.objects:
			rapi.rpgSetName(object.name)
			for faceIndex in range(0, object.faceCount):
				vertIndices = object.faceIndices[faceIndex * 3 : faceIndex * 3 + 3]
				colorBits = object.faceColors[faceIndex]
				rapi.immBegin(noesis.RPGEO_TRIANGLE)
				
				colorLow = colorBits & 15
				fColor = [float(clr) / 255.0 for clr in noeUnpack("BBBB", self.decodedPalette[colorLow * 4 : colorLow * 4 + 4])]
				rapi.immColor4(fColor)
					
				for vertIndex in vertIndices:
					pos = (object.positionsX[vertIndex], object.positionsY[vertIndex], object.positionsZ[vertIndex])
					rapi.immVertex3(pos)
				rapi.immEnd()
		rapi.rpgFlatNormals()
		rapi.rpgCreatePlaneSpaceUVs()
		return rapi.rpgConstructModel()

		
def cadCheckType(data, modelClass):
	cad = modelClass(data)
	if cad.parse() != 0:
		return 0
	return 1
	
def cadLoadModel(data, mdlList, modelClass):
	cad = modelClass(data)
	if cad.parse() != 0:
		return 0
	cad.load()
	mdl = cad.createModel()
	if mdl:
		materialData = cad.createDefaultMaterialData()
		if materialData:
			mdl.setModelMaterials(materialData)
		mdlList.append(mdl)
		rapi.setPreviewOption("setAngOfs", "0 270 0")
		rapi.setPreviewOption("autoLoadNonDiffuse", "1")
	return 1

def c3d1CheckType(data):
	return cadCheckType(data, CadV1Model)
def c3d1LoadModel(data, mdlList):
	return cadLoadModel(data, mdlList, CadV1Model)
def c3d2CheckType(data):
	return cadCheckType(data, CadV2Model)
def c3d2LoadModel(data, mdlList):
	return cadLoadModel(data, mdlList, CadV2Model)

def caniCheckType(data):
	if len(data) <= 37 or data[36] != 0 or data[37] != 3:
		return 0
	animRes, animMode = noeUnpack(">HH", data[:4])
	if animRes > 2 or animMode > 3:
		return 0
	#not exactly great verification
	return 1
	
class CadAnimFramePoly:
	def __init__(self, bs, animRes, animMode, decodedPalette, vertCount, zCurrent):
		self.vertCount = vertCount
		colorBits = bs.readUByte()
		if animMode > 0:
			#min/max unused
			bs.readUShort()
			bs.readUShort()
		
		colorLow = colorBits & 15
		if animRes == 0:
			self.color = [float(clr) / 255.0 for clr in noeUnpack("BBBB", decodedPalette[colorLow * 4 : colorLow * 4 + 4])]
		else:
			shade = colorLow / 15.0
			self.color = [shade, shade, shade, 1.0]
		
		self.verts = []
		for vertIndex in range(0, vertCount):
			vertPos = (float(bs.readShort()), float(bs.readShort()), float(zCurrent))
			self.verts.append(vertPos)
		#last edge unused
		bs.readUShort()
		bs.readUShort()
	
def caniLoadModel(data, mdlList):
	bs = NoeBitStream(data, NOE_BIGENDIAN)
	animRes = bs.readUShort()
	animMode = bs.readUShort()
	paletteData = rapi.swapEndianArray(bs.readBytes(16 * 2), 2)
	decodedPalette = rapi.imageDecodeRaw(paletteData, 16, 1, "b3p1g3p1r3p5")
	
	allFrames = []
	
	zIncrement = 0.001
	zCurrent = 0.0
	framePolys = []
	while not bs.checkEOF():
		vertCount = bs.readUByte()
		if vertCount == 0x00 or vertCount == 0xFF:
			if len(framePolys) > 0:
				allFrames.append(framePolys)
			framePolys = []
			if vertCount == 0x00:
				#new frame
				vertCount = bs.readUByte()
				zCurrent = 0.0
			else:
				break
			
		framePolys.append(CadAnimFramePoly(bs, animRes, animMode, decodedPalette, vertCount, zCurrent))
		zCurrent += zIncrement

	ctx = rapi.rpgCreateContext()
	
	#since these things aren't guaranteed to share geometry between frames, just create every frame as a separate model
	for framePolys in allFrames:
		rapi.rpgReset()
		for poly in framePolys:
			rapi.immBegin(noesis.RPGEO_POLYGON)
			rapi.immColor4(poly.color)
			for vert in poly.verts:
				rapi.immVertex3(vert)
			rapi.immEnd()
		rapi.rpgFlatNormals()
		rapi.rpgCreatePlaneSpaceUVs()
		mdl = rapi.rpgConstructModel()
		if mdl:
			mdlList.append(mdl)
	if len(mdlList) > 0:
		rapi.setPreviewOption("setAngOfs", "0 90 90")
		
	return 1
