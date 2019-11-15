from inc_noesis import *
import sys
import math
import time

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("Quake II BSP", ".bsp")
	noesis.setHandlerTypeCheck(handle, bspCheckType)
	noesis.setHandlerLoadModel(handle, bspLoadModel)
	return 1

Q2LUMP_ENTS		= 0
Q2LUMP_PLANES		= 1
Q2LUMP_VERTS		= 2
Q2LUMP_VIS		= 3
Q2LUMP_NODES		= 4
Q2LUMP_TEXINFO		= 5
Q2LUMP_FACES		= 6
Q2LUMP_LIGHTMAPS	= 7
Q2LUMP_LEAVES		= 8
Q2LUMP_LEAFFACES	= 9
Q2LUMP_LEAFBRUSHES	= 10
Q2LUMP_EDGES		= 11
Q2LUMP_SURFEDGES	= 12
Q2LUMP_MODELS		= 13
Q2LUMP_BRUSHES		= 14
Q2LUMP_BSIDES		= 15
Q2LUMP_POP		= 16
Q2LUMP_AREAS		= 17
Q2LUMP_AREAPORTALS	= 18
Q2LUMP_NUM		= 19
Q2LM_WIDTH		= 256	#lightmap dimensions can actually be whatever you want, the pages are constructed in this script
Q2LM_HEIGHT		= 256
Q2LM_BPP		= 3	#bytes per pixel

class BspDrawVert:
	def __init__(self, pos, uv, lmuv):
		self.pos = pos
		self.uv = uv
		self.lmuv = lmuv

class BspDrawTri:
	def __init__(self, idxList):
		self.idxList = idxList

class BspLMPage:
	def __init__(self, index, defaultLum = [0]):
		self.index = index
		self.pageUse = [0]*Q2LM_WIDTH
		self.data = bytearray(defaultLum*Q2LM_WIDTH*Q2LM_HEIGHT*Q2LM_BPP)

	#returns a tuple of lightmap coordinates, or None if the surface won't fit
	def fitSurface(self, lmW, lmH):
		lmCoord = None
		b1 = Q2LM_HEIGHT
		for i in range(0, Q2LM_WIDTH-lmW):
			b2 = 0
			lcol = 0
			for j in range(0, lmW):
				if self.pageUse[i+j] >= b1:
					lcol = 1
					break
				if self.pageUse[i+j] > b2:
					b2 = self.pageUse[i+j]
			if lcol == 0:
				b1 = b2
				lmCoord = (i, b1)
		if b1+lmH > Q2LM_HEIGHT:
			return None

		for i in range(0, lmW):
			self.pageUse[lmCoord[0]+i] = b1+lmH

		return lmCoord

	#draws a surface into the lightmap page
	def drawSurface(self, surf, lmW, lmH, bsp):
		lmDataSize = lmW*lmH*Q2LM_BPP
		lmSrc = bsp.lmData[surf.lightOfs:surf.lightOfs+lmDataSize]
		dstBase = (surf.lmCoord[1]*Q2LM_WIDTH + surf.lmCoord[0])*Q2LM_BPP
		rowSize = lmW*Q2LM_BPP
		for y in range(0, lmH):
			srcOfs = y*lmW*Q2LM_BPP
			dstOfs = dstBase + y*Q2LM_WIDTH*Q2LM_BPP
			self.data[dstOfs:dstOfs+rowSize] = lmSrc[srcOfs:srcOfs+rowSize]

	def toTexture(self):
		return NoeTexture("__lightmap"+repr(self.index), Q2LM_WIDTH, Q2LM_HEIGHT, self.data, noesis.NOESISTEX_RGB24)

class BspTexInfo:
	def __init__(self, data, bsp):
		self.texAx = (NoeVec3.fromBytes(data[0:12]), NoeVec3.fromBytes(data[16:28]))
		self.texOfs = (noeUnpackFrom("<f", data, 12)[0], noeUnpackFrom("<f", data, 28)[0])
		self.flags = noeUnpackFrom("<i", data, 32)
		self.value = noeUnpackFrom("<i", data, 36)
		self.texName = noeStrFromBytes(data[40:72])
		self.nextInfo = noeUnpackFrom("<i", data, 72)
		mtTup = bsp.addTexture(self.texName, self)
		self.texture = mtTup[0]
		self.material = mtTup[1]
		if self.texture is not None:
			self.width = self.texture.width
			self.height = self.texture.height
		else:
			print("WARNING: Could not load " + self.texName)
			self.width = 128
			self.height = 128

class BspSurface:
	def __init__(self, bsp, data):
		self.drawVerts = []
		self.drawTris = []
		faceData = noeUnpackFrom("<hhihhBBBBi", data, 0)
		self.planeNum = faceData[0]
		self.side = faceData[1]
		self.firstEdge = faceData[2]
		self.numEdges = faceData[3]
		self.texInfo = bsp.texInfo[faceData[4]]
		self.lightStyles = faceData[5:9]
		self.lightOfs = faceData[9]
		#calculate texture coordinate extents
		self.tcMins = [0, 0]
		self.tcExtents = [0, 0]
		self.edgeVerts = []
		wtcMins = [sys.float_info.max, sys.float_info.max]
		wtcMaxs = [-sys.float_info.max, -sys.float_info.max]
		for i in range(0, self.numEdges):
			edgeIdx = noeUnpackFrom("<i", bsp.surfEdges, (self.firstEdge+i)*4)[0]
			vertOfs = bsp.edges[edgeIdx][0]*12 if edgeIdx >= 0 else bsp.edges[-edgeIdx][1]*12
			vpos = NoeVec3.fromBytes(bsp.verts[vertOfs:vertOfs+12])
			tu = vpos.dot(self.texInfo.texAx[0]) + self.texInfo.texOfs[0]
			tv = vpos.dot(self.texInfo.texAx[1]) + self.texInfo.texOfs[1]
			edgeVert = (vpos, tu, tv)
			self.edgeVerts.append(edgeVert)
			for j in range(0, 2):
				f = edgeVert[1+j]
				if f < wtcMins[j]:
					wtcMins[j] = f
				if f > wtcMaxs[j]:
					wtcMaxs[j] = f
		for i in range(0, 2):
			exMin = math.floor(wtcMins[i]/16.0)
			exMax = math.ceil(wtcMaxs[i]/16)
			self.tcMins[i] = int(math.fmod(exMin*16, 32767.0))
			self.tcExtents[i] = int(math.fmod((exMax-exMin)*16, 32767.0))
		self.putInLightmap(bsp)
		self.calculateDrawData(bsp)

	def putInLightmap(self, bsp):
		lmW = (self.tcExtents[0]>>4)+1
		lmH = (self.tcExtents[1]>>4)+1
		self.lmPage = None
		self.lmCoord = None
		if self.lightOfs > 0 or self.lightStyles[0] != 0 or self.lightStyles[1] != 0 or self.lightStyles[2] != 0 or self.lightStyles[3] != 0:
			if len(bsp.lmPages) > 0:
				lmPage = bsp.lmPages[-1]
				self.lmCoord = lmPage.fitSurface(lmW, lmH)
				if self.lmCoord is not None:
					self.lmPage = lmPage

			if self.lmCoord is None: #need to create a new page if there was no room in any existing page
				defaultLum = [255] if bsp.lmData is None else [0]
				newPage = BspLMPage(len(bsp.lmPages), defaultLum)
				self.lmCoord = newPage.fitSurface(lmW, lmH)
				if self.lmCoord is None:
					noesis.doException("Surface is too big for lightmap page!")
				self.lmPage = newPage
				bsp.lmPages.append(newPage)
			if bsp.lmData is not None:
				self.lmPage.drawSurface(self, lmW, lmH, bsp)

	def calculateDrawData(self, bsp):
		numVerts = self.numEdges
		numTris = numVerts-2
		for edgeVert in self.edgeVerts:
			vpos = edgeVert[0]
			tu = edgeVert[1]
			tv = edgeVert[2]
			if self.lmCoord is not None:
				lmu = (tu - self.tcMins[0]) + self.lmCoord[0]*16.0 + 8.0
				lmv = (tv - self.tcMins[1]) + self.lmCoord[1]*16.0 + 8.0
			else:
				lmu = lmv = 0.0
			self.drawVerts.append( BspDrawVert( vpos.getStorage(), (tu/self.texInfo.width, tv/self.texInfo.height), (lmu/(Q2LM_WIDTH*16.0), lmv/(Q2LM_HEIGHT*16.0)) ) )
		self.drawTris.append(BspDrawTri((2, 1, 0)))
		for i in range(0, numTris-1):
			self.drawTris.append(BspDrawTri((3+i-1, 0, 3+i)))

class BspFile:
	def __init__(self, bs):
		self.bs = bs
		self.textures = []
		self.materials = []
		self.lmPages = []
		self.matDict = {}

	def loadLumps(self):
		bs = self.bs
		if bs.dataSize <= 8 + 8*Q2LUMP_NUM:
			return 0
		id = noeStrFromBytes(bs.readBytes(4))
		if id != "IBSP":
			return 0
		ver = bs.readInt()
		if ver != 38:
			return 0
		self.lumps = []
		for i in range(0, Q2LUMP_NUM):
			lump = (bs.readInt(), bs.readInt())
			if lump[0] < 0 or lump[1] < 0 or lump[0]+lump[1] > bs.dataSize:
				return 0
			self.lumps.append(lump)
		return 1

	def loadVerts(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_VERTS]
		self.numVerts = lump[1] // 12
		bs.seek(lump[0], NOESEEK_ABS)
		self.verts = bs.readBytes(lump[1])

	def loadEdges(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_EDGES]
		numEdges = lump[1] // 4
		bs.seek(lump[0], NOESEEK_ABS)
		edges = bs.readBytes(lump[1])
		self.edges = []
		for i in range(0, numEdges):
			self.edges.append(noeUnpackFrom("<HH", edges, 4*i))

	def loadSurfEdges(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_SURFEDGES]
		self.numSurfEdges = lump[1] // 4
		bs.seek(lump[0], NOESEEK_ABS)
		self.surfEdges = bs.readBytes(lump[1])

	def loadTexInfo(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_TEXINFO]
		numTexInfo = lump[1] // 76
		bs.seek(lump[0], NOESEEK_ABS)
		self.texInfo = []
		startTime = time.time()
		for i in range(0, numTexInfo):
			texInfo = BspTexInfo(bs.readBytes(76), self)
			self.texInfo.append(texInfo)
		timeTaken = time.time() - startTime
		print("Loaded texture dependencies in", timeTaken, "seconds.")

	def loadLightmaps(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_LIGHTMAPS]
		if lump[1] <= 0:
			self.lmData = None
		else:
			bs.seek(lump[0], NOESEEK_ABS)
			self.lmData = bs.readBytes(lump[1])

	def loadSurfaces(self):
		bs = self.bs
		lump = self.lumps[Q2LUMP_FACES]
		numFaces = lump[1] // 20
		bs.seek(lump[0], NOESEEK_ABS)
		self.surfs = []
		startTime = time.time()
		for i in range(0, numFaces):
			self.surfs.append(BspSurface(self, bs.readBytes(20)))
		timeTaken = time.time() - startTime
		print("Calculated surface geometry and generated lightmap pages in", timeTaken, "seconds.")

	def loadData(self):
		self.loadVerts()
		self.loadEdges()
		self.loadSurfEdges()
		self.loadTexInfo()
		self.loadLightmaps()
		self.loadSurfaces()
		self.lmMatBase = len(self.materials)
		for lmPage in self.lmPages:
			tex = lmPage.toTexture()
			self.textures.append(tex)
			mat = NoeMaterial(tex.name, tex.name)
			self.materials.append(mat)

	#returns a tuple containing texture and material for the given texture
	def addTexture(self, texName, texInfo):
		if texName in self.matDict:
			return self.matDict[texName]

		texture = rapi.loadExternalTex(texName)
		if texture is None:
			texture = rapi.loadExternalTex("../textures/" + texName) #may need to go up and over in standard q2 path layout
		if texture is not None:
			self.textures.append(texture)
			material = NoeMaterial(texName, texture.name)
			material.setFlags(0, 1)
			if texName.find("/trigger") != -1 or texName.find("/sky") != -1: #the right way to deal with this is by paying attention to entities and bmodels
				material.setSkipRender(1)
			self.materials.append(material)
		else:
			material = None
		mtTup = (texture, material)
		self.matDict[texName] = mtTup
		return mtTup

def bspCheckType(data):
	bsp = BspFile(NoeBitStream(data))
	if bsp.loadLumps() == 0:
		return 0
	return 1

def bspLoadModel(data, mdlList):
	startTime = time.time()
	bsp = BspFile(NoeBitStream(data))
	if bsp.loadLumps() == 0:
		return 0

	bsp.loadData()

	ctx = rapi.rpgCreateContext()

	for surf in bsp.surfs:
		#set diffuse material
		if surf.texInfo.material is not None:
			rapi.rpgSetMaterial(surf.texInfo.material.name)
		else:
			rapi.rpgSetMaterial("")

		#set lightmap material
		if surf.lmPage is not None:
			lmMat = bsp.materials[bsp.lmMatBase + surf.lmPage.index]
			rapi.rpgSetLightmap(lmMat.name)
		else:
			rapi.rpgSetLightmap("")

		rapi.immBegin(noesis.RPGEO_TRIANGLE)
		for tri in surf.drawTris:
			for idx in tri.idxList:
				dv = surf.drawVerts[idx]
				rapi.immUV2(dv.uv)
				rapi.immLMUV2(dv.lmuv)
				rapi.immVertex3(dv.pos)
		rapi.immEnd()

	constructModelStart = time.time()
	rapi.rpgOptimize() #calling optimize would be bad if you wanted to preserve leaf surface batching
	mdl = rapi.rpgConstructModelSlim()
	timeTaken = time.time() - constructModelStart
	print("Constructed procedural model in", timeTaken, "seconds.")
	mdl.setModelMaterials(NoeModelMaterials(bsp.textures, bsp.materials))
	mdlList.append(mdl)

	timeTaken = time.time() - startTime
	print("Total load time:", timeTaken, "seconds.")

	rapi.setPreviewOption("setAngOfs", "0 180 0")
	return 1
