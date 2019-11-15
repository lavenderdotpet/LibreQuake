from inc_noesis import *
import random

def registerNoesisTypes():
	handle = noesis.registerTool("&Text maker", tmToolMethod, "Make a mesh of text")
	return 1

def tmValidateInput(inVal):
	if len(inVal) <= 0:
		return "You must enter a non-blank string."
	elif len(inVal) > 32:
		return "The string you've entered is too long."
	return None
	
def tmExportFile():
	saveDefault = noesis.getSelectedDirectory() + "\\textmodel.fbx"
	savePath = noesis.userPrompt(noesis.NOEUSERVAL_SAVEFILEPATH, "Save Model", "Select destination for text model.", saveDefault, None)
	if savePath is None:
		return None
	if rapi.toolExportGData(savePath, "") is not True:
		noesis.messagePrompt("Failed to write file.")
		return None
	return savePath

def tmMakeTextures():		
	texList = []
	
	#make a simple solid-color diffuse
	texWidth = 4
	texHeight = 4
	clr = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
	texData = bytearray(clr*texWidth*texHeight)
	texList.append(NoeTexture("textmodel_d.dds", texWidth, texHeight, texData))
	
	#make some random bumps
	texWidth = 256
	texHeight = 256
	texData = bytearray()
	for i in range(0, texWidth*texHeight):
		r = random.randint(20, 255)
		texData += bytearray((r, r, r, 255))
	texData = rapi.imageGaussianBlur(texData, texWidth, texHeight, 2.0)
	texData = rapi.imageScaleRGBA32(texData, (3, 3, 3, 1), texWidth, texHeight, 2)
	texData = rapi.imageScaleRGBA32(texData, (3, 3, 3, 1), texWidth, texHeight, 0)
	#double the height scale to make the the contrast more subtle
	texData = rapi.imageNormalMapFromHeightMap(texData, texWidth, texHeight, 2.0, 1.0)
	texList.append(NoeTexture("textmodel_n.dds", texWidth, texHeight, texData))
	
	envTexPath = noesis.getScenesPath() + "sample_texa.png"
	tex1 = rapi.loadExternalTex(envTexPath)
	envTexPath = noesis.getScenesPath() + "sample_puppy.png"
	tex2 = rapi.loadExternalTex(envTexPath)
	#build a cubemap using these textures for each face
	if tex1 is not None:
		#if the other image couldn't be loaded for any reason, replace it
		if tex2 is None or tex2.width != tex1.width or tex2.height != tex1.height:
			tex2 = tex1
		cubeData = bytearray()
		cubeData += tex2.pixelData*2
		cubeData += tex1.pixelData*2
		cubeData += tex2.pixelData*2
		cubeTex = NoeTexture("textmodel_env.dds", tex1.width, tex1.height, cubeData)
		cubeTex.setFlags(noesis.NTEXFLAG_CUBEMAP)
		texList.append(cubeTex)
		
	return texList

def tmToolMethod(toolIndex):
	text = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Enter Text", "Enter a string to generate a text model.", "Some text.", tmValidateInput)
	if text is None:
		return 0
		
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	
	ctx = rapi.rpgCreateContext()
	rapi.rpgSetName("textmodel")
	rapi.rpgSetMaterial("textmodel")
	matList = []
	texList = tmMakeTextures()
	mat = NoeMaterial("textmodel", "textmodel_d")
	mat.setNormalTexture("textmodel_n")
	mat.setEnvTexture("textmodel_env")
	matList.append(mat)

	tmat = NoeMat43()
	tmat[1] = (0.0, -1.0, 0.0)
	for s in text:
		ss = noesis.getCharSplineSet(ord(s))
		#draw from the center of the splineset on x
		tmat = tmat.translate( ((ss.maxs[0]-ss.mins[0])*0.5, 0.0, 0.0) )
		for spline in ss.splines:
			#reverse the winding because we're inverting the vertices in our transform
			meshData = rapi.splineToMeshBuffers(spline, tmat, 1, 0.05, 3.0, 2)
			if meshData is not None:
				vertData = meshData[0]
				idxData = meshData[1]
				numVerts = len(vertData) // 32
				numIdx = len(idxData) // 4
				rapi.rpgBindPositionBufferOfs(vertData, noesis.RPGEODATA_FLOAT, 32, 0)
				rapi.rpgBindNormalBufferOfs(vertData, noesis.RPGEODATA_FLOAT, 32, 12)
				rapi.rpgBindUV1BufferOfs(vertData, noesis.RPGEODATA_FLOAT, 32, 24)
				rapi.rpgCommitTriangles(idxData, noesis.RPGEODATA_INT, numIdx, noesis.RPGEO_TRIANGLE, 1)
		#skip past the other half, and add 6.0 for character spacing
		tmat = tmat.translate( ((ss.maxs[0]-ss.mins[0])*0.5 + 6.0, 0.0, 0.0) )

	mdl = rapi.rpgConstructModel()
	mdl.setModelMaterials(NoeModelMaterials(texList, matList))
	
	rapi.toolSetGData([mdl])
	saveName = tmExportFile()
	
	rapi.toolFreeGData()
	noesis.freeModule(noeMod)
	
	if saveName is not None:
		noesis.openFile(saveName)
	
	return 0
