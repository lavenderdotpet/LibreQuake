#this started as a pretty bare-bones script, but has evolved to support a good range of UE4 versions. thanks to gildor for some of the initial (<4.15)
#ObjectVersion checking. this script is primarily intended to deal with cooked data. limited support is provided for editor-only packages, mainly for
#tools/analysis purposes, but many code paths for editor-only data remain unimplemented.

from inc_noesis import *
import os
import math
import noewin
from noewin import user32, gdi32, kernel32

UE4_ENABLE_TOOLS = False
UE4_VERSION_TOOL_SAVE_OPTIONS = True
UE4_VERSION_TOOL_SAVE_VERSION = 1

UE4_BGRA_SWIZZLE = True

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("UE4 Archive", ".pak")
	noesis.setHandlerExtractArc(handle, ue4ExtractArc)
	
	handle = noesis.register("UE4 Asset", ".uasset;.umap")
	noesis.setHandlerTypeCheck(handle, ue4CheckType)
	noesis.setHandlerLoadModel(handle, ue4LoadModel)
	noesis.addOption(handle, "-ue4serialver", "force serialization version to <arg>. see UE4_SERIALVER_*.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-ue4gamehack", "force gamehack to <arg>. see UE4_GAMEHACK_*.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-ue4tex1dthin", "force texture untiling. (ps4)", 0)
	noesis.addOption(handle, "-ue4texgob", "force texture untiling. (switch)", 0)
	noesis.addOption(handle, "-ue4texgobpad", "apply padding for blgob-tiled textures. (switch)", 0)
	noesis.addOption(handle, "-ue4texalign", "align textures to <arg>.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-ue4defaultmtl", "force default material names.", 0)
	noesis.addOption(handle, "-ue4nosecname", "don't name meshes by section.", 0)
	noesis.addOption(handle, "-ue4sanity", "sanity-check list counts.", 0)
	noesis.addOption(handle, "-ue4bidx", "name bones by index.", 0) #apparently ue4 allows identically-named bones
	noesis.addOption(handle, "-ue4anims", "attempt to load animations.", 0)
	noesis.addOption(handle, "-ue4animref", "specifies skinned mesh for anim reference.", noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-ue4datapath", "scan <arg> recursively for export data.", noesis.OPTFLAG_WANTARG)

	if UE4_ENABLE_TOOLS:
		toolHandle = noesis.registerTool("UE4 Version Tool", ue4VersionToolMethod, "Select ObjectVersion, game hacks, etc.")
		toolHandle = noesis.registerTool("UE4 Diff Tool", ue4DiffToolMethod, "Performs diff analysis with package.diff.")
		noesis.setToolFlags(toolHandle, noesis.NTOOLFLAG_CONTEXTITEM)
		noesis.setToolVisibleCallback(toolHandle, ue4PackageContextVisible)
		toolHandle = noesis.registerTool("UE4 Property Lister", ue4PropToolMethod, "Loads all exports and lists object properties.")
		noesis.setToolFlags(toolHandle, noesis.NTOOLFLAG_CONTEXTITEM)
		noesis.setToolVisibleCallback(toolHandle, ue4PackageContextVisible)
		toolHandle = noesis.registerTool("UE4 ASTC PSNR Tool", ue4AstcToolMethod, "Scan for texture assets and encode as ASTC in various block modes.")
		toolHandle = noesis.registerTool("UE4 Object Finder", ue4ObjFindToolMethod, "Scan every asset in a given hierarchy to locate matching exports.")
	
	return 1
		

UE4_GAMEHACK_NONE = 0
UE4_GAMEHACK_T7 = 1
UE4_GAMEHACK_F13 = 2

UE4_SERIALVER_PREREL_ASSET_REGISTRY_TAGS = 112
UE4_SERIALVER_PREREL_ADD_SKELMESH_MESHTOIMPORTVERTEXMAP = 152
UE4_SERIALVER_PREREL_REMOVE_ARCHETYPE_INDEX_FROM_LINKER_TABLES = 163
UE4_SERIALVER_PREREL_REMOVE_NET_INDEX = 196
UE4_SERIALVER_PREREL_SUMMARY_HAS_BULKDATA_OFFSET = 212
UE4_SERIALVER_PREREL_APEX_CLOTH = 254
UE4_SERIALVER_PREREL_STATIC_SKELETAL_MESH_SERIALIZATION_FIX = 269
UE4_SERIALVER_PREREL_APEX_CLOTH_LOD = 280
UE4_SERIALVER_PREREL_KEEP_SKEL_MESH_INDEX_DATA = 283
UE4_SERIALVER_PREREL_MOVE_SKELETALMESH_SHADOWCASTING = 302
UE4_SERIALVER_PREREL_REFERENCE_SKELETON_REFACTOR = 310
UE4_SERIALVER_PREREL_FIXUP_ROOTBONE_PARENT = 312
UE4_SERIALVER_PREREL_SUPPORT_8_BONE_INFLUENCES_SKELETAL_MESHES = 332
UE4_SERIALVER_PREREL_SUPPORT_GPUSKINNING_8_BONE_INFLUENCES = 334
UE4_SERIALVER_PREREL_ENGINE_VERSION_OBJECT = 336
UE4_SERIALVER_PREREL_SKELETON_GUID_SERIALIZATION = 338
UE4_SERIALVER_400 = 342
UE4_SERIALVER_401 = 352
UE4_SERIALVER_402 = 363
UE4_SERIALVER_402_LOAD_FOR_EDITOR_GAME = 365
UE4_SERIALVER_402_FTEXT_HISTORY = 368
UE4_SERIALVER_402_STORE_BONE_EXPORT_NAMES = 370
UE4_SERIALVER_403 = 382
UE4_SERIALVER_403_ADD_STRING_ASSET_REFERENCES_MAP = 384
UE4_SERIALVER_404 = 385
UE4_SERIALVER_404_RENAME_CROUCHMOVESCHARACTERDOWN = 394
UE4_SERIALVER_404_DEPRECATE_UMG_STYLE_ASSETS = 397
UE4_SERIALVER_405 = 401
UE4_SERIALVER_406 = 413
UE4_SERIALVER_406_RENAME_WIDGET_VISIBILITY = 416
UE4_SERIALVER_407 = 434
UE4_SERIALVER_407_STRUCT_GUID_IN_PROPERTY_TAG = 441
UE4_SERIALVER_407_PACKAGE_SUMMARY_HAS_COMPATIBLE_ENGINE_VERSION = 444
UE4_SERIALVER_408 = 451
UE4_SERIALVER_408_SERIALIZE_TEXT_IN_PACKAGES = 459
UE4_SERIALVER_409 = 482
UE4_SERIALVER_410 = 482
UE4_SERIALVER_410_COOKED_ASSETS_IN_EDITOR_SUPPORT = 485
UE4_SERIALVER_410_SOUND_CONCURRENCY_PACKAGE = 489
UE4_SERIALVER_411 = 498
UE4_SERIALVER_411_INNER_ARRAY_TAG_INFO = 500
UE4_SERIALVER_411_PROPERTY_GUID_IN_PROPERTY_TAG = 503
UE4_SERIALVER_412 = 504
UE4_SERIALVER_413 = 505
UE4_SERIALVER_413_PRELOAD_DEPENDENCIES_IN_COOKED_EXPORTS = 507
UE4_SERIALVER_414 = 508
UE4_SERIALVER_414_PROPERTY_TAG_SET_MAP_SUPPORT = 509
UE4_SERIALVER_415 = 510
UE4_SERIALVER_415_64BIT_EXPORTMAP_SERIALSIZES = 511
UE4_SERIALVER_416 = 513
UE4_SERIALVER_417 = 513
UE4_SERIALVER_418 = 514
UE4_SERIALVER_419 = 516
UE4_SERIALVER_419_ADDED_DISABLED_TO_RENDERSECTION = 516 #seems to have been added in interim 4.19 dev, could be some 4.19 data out there without this field
UE4_SERIALVER_420 = 517 #this is currently a lie, ObjectVersion hasn't been updated!
UE4_SERIALVER_421 = 518 #also a lie
UE4_SERIALVER_422 = 519 #and another lie
UE4_SERIALVER_LATEST = UE4_SERIALVER_422

UE4_MAX_SANE_LIST_COUNT = 1 * 1024 * 1024

class UE4Asset:
	def __init__(self, bs, fullPath, loadData):
		self.bs = bs
		self.fullPath = fullPath
		self.loadData = loadData
		
	def getSuggestedSerialVersion(self):
		serialVersion = self.verB & 0xFFFF
		if serialVersion == 0:
			if self.version < -7:
				serialVersion = UE4_SERIALVER_LATEST
			elif self.version == -6:
				serialVersion = UE4_SERIALVER_411
			elif self.version == -5 or self.version == -4:
				serialVersion = UE4_SERIALVER_407
			else:
				serialVersion = UE4_SERIALVER_414
		return serialVersion
		
	def determineVersion(self):
		self.isUnversioned = self.verB == 0
		
		if ue4VersionToolOptions.gameHack < 0 and ue4VersionToolOptions.version < 0 and not noesis.optWasInvoked("-ue4gamehack") and not noesis.optWasInvoked("-ue4serialver"):
			#someone is blindly reading a file without specifying a version, which will usually end in disaster.
			#so let's go ahead and prompt for them to select a version now.
			ue4VersionToolInternal(self.getSuggestedSerialVersion(), -1)
			if ue4VersionToolOptions.gameHack < 0 and ue4VersionToolOptions.version < 0:
				#they didn't bother selecting anything. let's get out of here.
				return False
		
		if ue4VersionToolOptions.gameHack >= 0:
			self.gameHack = ue4VersionToolOptions.gameHack
		else:
			self.gameHack = UE4_GAMEHACK_NONE
			if noesis.optWasInvoked("-ue4gamehack"):
				self.gameHack = int(noesis.optGetArg("-ue4gamehack"))
			
		if ue4VersionToolOptions.version >= 0:
			self.serialVersion = ue4VersionToolOptions.version
		else:
			if self.gameHack == UE4_GAMEHACK_T7 or self.gameHack == UE4_GAMEHACK_F13:
				self.serialVersion = UE4_SERIALVER_414
			elif noesis.optWasInvoked("-ue4serialver"):
				self.serialVersion = int(noesis.optGetArg("-ue4serialver"))
			else:
				self.serialVersion = self.getSuggestedSerialVersion()
		return True
		
	def parse(self):
		try:
			bs = self.bs
			id = bs.readUInt()
			if id != 0x9E2A83C1:
				if id == 0xC1832A9E:
					bs.setEndian(NOE_BIGENDIAN)
				else:
					return -1
			self.version = bs.readInt()
			#this support/script is pretty half-assed (not a complete implementation, just here to update as needed in order to get at select data), so i'm not supporting a whitelist.
			#at the time of this writing, i'm loading version -7, 0, 0, 0 files.
			if self.version >= 0:
				return -1
			self.verA = bs.readInt()
			self.verB = bs.readInt()
			self.verLic = bs.readInt()
			self.versionList = ue4ReadList(self, UE4VersionType)

			if not self.determineVersion():
				return -1

			self.headersSize = bs.readInt()

			self.packageGroup = ue4ReadString(self)
			self.packageFlags = bs.readInt()

			self.namesCount = bs.readInt()
			self.namesOffset = bs.readInt()
			
			if self.serialVersion >= UE4_SERIALVER_419 and self.containsEditorData():
				ue4ReadString(self)
			
			if self.serialVersion >= UE4_SERIALVER_408_SERIALIZE_TEXT_IN_PACKAGES:
				self.gatherableTextDataCount = bs.readInt()
				self.gatherableTextDataOffset = bs.readInt()

			self.exportCount = bs.readInt()
			self.exportOffset = bs.readInt()
			self.importCount = bs.readInt()
			self.importOffset = bs.readInt()
			self.dependsOffset = bs.readInt()
			
			ue4SanityCheckListSize(self.namesCount)
			ue4SanityCheckListSize(self.exportCount)
			ue4SanityCheckListSize(self.importCount)

			if self.serialVersion >= UE4_SERIALVER_403_ADD_STRING_ASSET_REFERENCES_MAP:
				self.assetStringRefCount = bs.readInt()
				self.assetStringRefOffset = bs.readInt()
			if self.serialVersion >= UE4_SERIALVER_415:
				bs.readInt() #searchableNamesOffset

			self.thumbnailTableOffset = bs.readInt()

			self.guid = UE4Guid(self)
			
			self.generations = ue4ReadList(self, UE4GenerationInfo)
			if self.serialVersion >= UE4_SERIALVER_PREREL_ENGINE_VERSION_OBJECT:
				self.engineVersion = UE4EngineVersion(self)
			if self.serialVersion >= UE4_SERIALVER_407_PACKAGE_SUMMARY_HAS_COMPATIBLE_ENGINE_VERSION:
				self.compatVersion = UE4EngineVersion(self)
			
			self.compressionFlags = bs.readInt()
			self.compressionChunks = ue4ReadList(self, UE4CompressedChunk)
			
			self.pkgSource = bs.readInt()
			self.cookPackages = ue4ReadList(self, UE4String)
			
			if self.serialVersion < UE4_SERIALVER_414:
				bs.readInt() #numTextureAllocations
			
			if self.serialVersion >= UE4_SERIALVER_PREREL_ASSET_REGISTRY_TAGS:
				self.assetRegistryOffset = bs.readInt()
			if self.serialVersion >= UE4_SERIALVER_PREREL_SUMMARY_HAS_BULKDATA_OFFSET:
				self.bulkDataOffset = bs.readInt()
			else:
				self.bulkDataOffset = 0
		except:
			return -1
		
		return 0
		
	def getName(self, index):
		if index >= 0 and index < len(self.names):
			name, flags = self.names[index]
			return name
		return None
		
	def getImportExport(self, index):
		if index < 0:
			index = -index
			if index > 0 and index <= len(self.imports):
				return self.imports[index - 1]
		elif index > 0:
			if index > 0 and index <= len(self.exports):
				return self.exports[index - 1]
		return None
		
	def getImportExportName(self, index):
		importExport = self.getImportExport(index)
		return repr(importExport.objectName) if importExport else "None"
		
	def containsEditorData(self):
		if self.isUnversioned:
			return False
		if self.packageFlags & 0x80000000:
			return False
		return True
		
	def getVersionByGuid(self, guid):
		for version in self.versionList:
			if version.key == guid:
				return version.version
		return -1
		
	def getRenderingObjectVersion(self):
		guid = UE4Guid.fromValue(0x12F88B9F, 0x88754AFC, 0xA67CD90C, 0x383ABD29)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_412:
				return 0
			elif self.serialVersion <= UE4_SERIALVER_412:
				return 2
			elif self.serialVersion <= UE4_SERIALVER_413:
				return 4
			elif self.gameHack == UE4_GAMEHACK_T7 or self.gameHack == UE4_GAMEHACK_F13:
				return 9
			elif self.serialVersion <= UE4_SERIALVER_415:
				return 12
			elif self.serialVersion <= UE4_SERIALVER_416:
				return 15
			elif self.serialVersion <= UE4_SERIALVER_417:
				return 19
			elif self.serialVersion <= UE4_SERIALVER_418:
				return 20
			elif self.serialVersion <= UE4_SERIALVER_419:
				return 25
			elif self.serialVersion <= UE4_SERIALVER_420:
				return 26
			elif self.serialVersion <= UE4_SERIALVER_421:
				return 27
			return 27
		return ver

	def getEditorObjectVersion(self):
		guid = UE4Guid.fromValue(0xE4B068ED, 0xF49442E9, 0xA231DA0B, 0x2E46BB41)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_412:
				return 0
			elif self.serialVersion <= UE4_SERIALVER_412:
				return 2
			elif self.serialVersion <= UE4_SERIALVER_413:
				return 6
			elif self.gameHack == UE4_GAMEHACK_F13:
				return 7
			elif self.serialVersion <= UE4_SERIALVER_414:
				return 8
			elif self.serialVersion <= UE4_SERIALVER_415:
				return 14
			elif self.serialVersion <= UE4_SERIALVER_416:
				return 17
			elif self.serialVersion <= UE4_SERIALVER_418:
				return 20
			elif self.serialVersion <= UE4_SERIALVER_419:
				return 23
			elif self.serialVersion <= UE4_SERIALVER_420:
				return 24
			elif self.serialVersion <= UE4_SERIALVER_421:
				return 26
			return 26
		return ver			
			
	def getSkeletalMeshVersion(self):
		guid = UE4Guid.fromValue(0xD78A4A00, 0xE8584697, 0xBAA819B5, 0x487D46B4)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_413:
				return 0
			elif self.serialVersion <= UE4_SERIALVER_413:
				return 4
			elif self.serialVersion <= UE4_SERIALVER_414:
				return 5
			elif self.serialVersion <= UE4_SERIALVER_415:
				return 7
			elif self.serialVersion <= UE4_SERIALVER_417:
				return 9
			elif self.serialVersion <= UE4_SERIALVER_418:
				return 10
			elif self.serialVersion <= UE4_SERIALVER_419:
				return 15
			elif self.serialVersion <= UE4_SERIALVER_421:
				return 16
			return 16
		return ver

	def getReleaseObjectVersion(self):
		guid = UE4Guid.fromValue(0x9C54D522, 0xA8264FBE, 0x94210746, 0x61B482D0)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_411:
				return 0
			elif self.serialVersion <= UE4_SERIALVER_412:
				return 1
			elif self.serialVersion <= UE4_SERIALVER_413:
				return 3
			elif self.serialVersion <= UE4_SERIALVER_414:
				return 4
			elif self.serialVersion <= UE4_SERIALVER_415:
				return 7
			elif self.serialVersion <= UE4_SERIALVER_416:
				return 9
			elif self.serialVersion <= UE4_SERIALVER_418:
				return 10
			elif self.serialVersion <= UE4_SERIALVER_419:
				return 12
			elif self.serialVersion <= UE4_SERIALVER_420:
				return 17
			elif self.serialVersion <= UE4_SERIALVER_421:
				return 20
			return 20
		return ver
			
	def getRecomputeTangentVersion(self):
		guid = UE4Guid.fromValue(0x5579F886, 0x933A4C1F, 0x83BA087B, 0x6361B92F)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_412:
				return 0
			return 1
		return ver

	def getOverlappinngVerticesVersion(self):
		guid = UE4Guid.fromValue(0x612FBE52, 0xDA53400B, 0x910D4F91, 0x9FB1857C)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_419:
				return 0
			return 1
		return ver

	def getFrameworkObjectVersion(self):
		guid = UE4Guid.fromValue(0xCFFC743F, 0x43B04480, 0x939114DF, 0x171D2073)
		ver = self.getVersionByGuid(guid)
		if ver < 0:
			if self.serialVersion < UE4_SERIALVER_411:
				return 0
			elif self.serialVersion <= UE4_SERIALVER_412:
				return 6
			elif self.serialVersion <= UE4_SERIALVER_413:
				return 12
			elif self.serialVersion <= UE4_SERIALVER_414:
				return 17
			elif self.serialVersion <= UE4_SERIALVER_415:
				return 22
			elif self.serialVersion <= UE4_SERIALVER_416:
				return 23
			elif self.serialVersion <= UE4_SERIALVER_417:
				return 28
			elif self.serialVersion <= UE4_SERIALVER_418:
				return 30
			elif self.serialVersion <= UE4_SERIALVER_420:
				return 33
			elif self.serialVersion <= UE4_SERIALVER_422:
				return 34
			return 34
		return ver
		
	def getExportableObjectByName(self, exportName):
		for object in self.serializedObjects:
			export = noeSafeGet(object, "exportEntry")
			if export and repr(export.objectName) == exportName:
				return object
		return None
						
	def loadTables(self):
		self.exportDataOffset = -1
		self.externalBulkDataOffset = -1
		self.secondaryExternalBulkDataOffset = -1
		if self.loadData:
			uexpName = rapi.getExtensionlessName(self.fullPath) + ".uexp"
			ubulkName = rapi.getExtensionlessName(self.fullPath) + ".ubulk"
			uptnlName = rapi.getExtensionlessName(self.fullPath) + ".uptnl"
			if os.path.exists(uexpName):
				self.exportDataOffset = len(self.bs.getBuffer())
				self.bs = NoeBitStream(self.bs.getBuffer() + ue4LoadBinaryChunk(uexpName))
			if os.path.exists(ubulkName):
				self.externalBulkDataOffset = len(self.bs.getBuffer())
				self.bs = NoeBitStream(self.bs.getBuffer() + ue4LoadBinaryChunk(ubulkName))
			if os.path.exists(uptnlName):
				self.secondaryExternalBulkDataOffset = len(self.bs.getBuffer())
				self.bs = NoeBitStream(self.bs.getBuffer() + ue4LoadBinaryChunk(uptnlName))

		bs = self.bs
		self.names = []
		self.imports = []
		self.exports = []
		if self.namesCount > 0:
			bs.seek(self.namesOffset, NOESEEK_ABS)
			for nameIndex in range(0, self.namesCount):
				name = ue4ReadString(self)
				flags = bs.readInt() if self.serialVersion >= UE4_SERIALVER_412 else 0
				self.names.append((name, flags))
		if self.importCount > 0:
			bs.seek(self.importOffset, NOESEEK_ABS)
			for importIndex in range(0, self.importCount):
				self.imports.append(UE4ImportObject(self))
		if self.exportCount > 0:
			bs.seek(self.exportOffset, NOESEEK_ABS)
			for exportIndex in range(0, self.exportCount):
				self.exports.append(UE4ExportObject(self))

	def loadAssetData(self):
		#todo - support compression? would usually be pointless in practice to compress cooked uassets (package-level or native platform compression), so might not be common
		bs = self.bs
		self.textures = []
		self.meshes = []
		self.serializedObjects = []
		for export in self.exports:
			className = self.getImportExportName(export.classIndex)
			print("Examining export", className, "-", export.objectName)
			if className in ue4LoaderDict:
				bs.seek(export.serialOffset, NOESEEK_ABS)
				newObject = ue4LoaderDict[className](self)
				newObject.load(export)
				self.serializedObjects.append(newObject)
		for object in self.serializedObjects:
			object.postLoad()
					
	def transferTextures(self, noeTextures):
		if len(self.textures) > 0:
			for uTexture in self.textures:
				if uTexture.texture:
					uTexture.noeTextureIndex = len(noeTextures)
					noeTextures.append(uTexture.texture)	

					
#=================================================================
# UObject implementations
#=================================================================
		
class UE4Object:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
	def load(self, export):
		bs = self.asset.bs
		self.exportEntry = export
		ue4LoadObjectProperties(self)
		if self.asset.serialVersion < UE4_SERIALVER_PREREL_REMOVE_NET_INDEX:
			bs.readInt()
		if ue4ReadBool(bs):
			self.objectGuid = UE4Guid(self.asset)
	def postLoad(self):
		pass
	def findPropertyTagByName(self, tagName):
		lTagName = tagName.lower()
		if lTagName in self.propTags:
			return self.propTags[lTagName]
		return None
	def getName(self):
		return repr(self.exportEntry.objectName) if self.exportEntry else "None"

class UE4StaticMesh(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		asset = self.asset
		bs = asset.bs

		stripFlags = UE4StripFlags(asset)
		isCooked = ue4ReadBool(bs)

		if not stripFlags.isEditorDataStripped():
			print("Unstripped StaticMesh is unimplemented.")
			return
		elif not isCooked:
			print("Uncooked StaticMesh is unimplemented.")
			return
		
		self.refSkeleton = None
		
		self.bodySetupRef = UE4ObjectRef(asset)
		if asset.gameHack != UE4_GAMEHACK_T7:
			self.navCollisionRef = UE4ObjectRef(asset)
		
		#if not stripFlags.isEditorDataStripped():
		#	UE4String(asset)
		#	bs.readUInt()
			
		self.lightingGuid = UE4Guid(asset)
		self.sockets = ue4ReadList(asset, UE4ObjectRef)

		self.lods = ue4ReadList(asset, UE4StaticModelLOD)
		
		if asset.serialVersion >= UE4_SERIALVER_404_RENAME_CROUCHMOVESCHARACTERDOWN:
			stripVolumeData = False
			if asset.serialVersion >= UE4_SERIALVER_406_RENAME_WIDGET_VISIBILITY:
				stripFlags = UE4StripFlags(asset)
				stripVolumeData = stripFlags.isRenderDataStripped()
			if not stripVolumeData:
				for lodIndex in range(0, len(self.lods)):
					if ue4ReadBool(bs):
						UE4DistanceFieldVolumeData(asset)

		self.bounds = UE4BoxSphereBounds(asset)
		
		if asset.serialVersion < UE4_SERIALVER_415 or asset.serialVersion >= UE4_SERIALVER_416:
			ue4ReadBool(bs) #LODsShareStaticLighting
		
		if asset.serialVersion < UE4_SERIALVER_414:
			bs.readInt() #simplygon flag
			
		renderVer = asset.getRenderingObjectVersion()
		if renderVer < 10:
			#streaming texture factors
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
			bs.readFloat()
		
		maxLods = 8 if asset.serialVersion >= UE4_SERIALVER_409 else 4
		for lodIndex in range(0, maxLods):
			bs.readFloat()
			
		self.materials = []
		
		hasStaticMaterials = False
		if asset.serialVersion >= UE4_SERIALVER_414:
			hasSpeedTreeData = ue4ReadBool(bs)
			if hasSpeedTreeData:
				print("Warning: SpeedTree parsing unimplemented.")
			else:
				if asset.getEditorObjectVersion() >= 8:
					self.materials = ue4ReadList(asset, UE4StaticMaterial)
					hasStaticMaterials = len(self.materials) > 0
					
		if not hasStaticMaterials:
			#if necessary, yank them out of properties
			if len(self.materials) == 0:
				materialArrayProp = self.findPropertyTagByName("Materials")
				if materialArrayProp:
					matInstNameList = materialArrayProp.readProperty()
					for matName in matInstNameList:
						self.materials.append(UE4LegacyMaterial(asset, matName))
		
		asset.meshes.append(self)
			
class UE4SkeletalMesh(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		asset = self.asset
		stripFlags = UE4StripFlags(asset)
		self.bounds = UE4BoxSphereBounds(asset)
		self.materials = ue4ReadList(asset, UE4SkeletalMaterial)
		self.refSkeleton = UE4RefSkeleton(asset)
		if not stripFlags.isEditorDataStripped():
			self.lods = ue4ReadList(asset, UE4SkeletalModelLOD.asEditorData, self)
			if asset.getSkeletalMeshVersion() >= 12:
				UE4Guid(asset) #don't care about guid
				ue4ReadBool(asset.bs) #whether guid is hash

		isCooked = True
		if asset.getSkeletalMeshVersion() >= 12:
			isCooked = ue4ReadBool(asset.bs)
			
		if isCooked:
			self.lods = ue4ReadList(asset, UE4SkeletalModelLOD, self)
		else:
			#possible todo - use soft verts instead or convert them to a UE4SkeletalMeshVertexBuffer. (kind of a pain, want to avoid per-vertex ops in python)
			print("Warning: Uncooked skeletal mesh contains no cooked geometry, ignoring.")
		self.asset.meshes.append(self)
			
class UE4Texture(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		stripFlags = UE4StripFlags(self.asset)
		self.sourceArt = None
		if not stripFlags.isEditorDataStripped():
			self.sourceArt = UE4ByteBulkData(self.asset)
			
		self.texture = None
		self.noeTextureIndex = -1
		self.asset.textures.append(self)
		
class UE4Texture2D(UE4Texture):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		bs = self.asset.bs
		
		UE4StripFlags(self.asset)
		isCooked = ue4ReadBool(bs)
		if isCooked:
			pixelFormat = repr(UE4Name(self.asset))
			while pixelFormat.lower() != "none":
				dataSize = bs.readInt64() if self.asset.serialVersion >= UE4_SERIALVER_420 else bs.readInt()
				if self.texture is None:
					width = bs.readInt()
					height = bs.readInt()
					depth = bs.readInt()
					imagePixelFormat = repr(UE4String(self.asset))
					firstMip = bs.readInt()
					mips = ue4ReadList(self.asset, UE4Texture2DMip)
					if len(mips) > 0:
						#textureData = bytearray()
						#for mip in mips:
						#	textureData += mip.bulkData.readData()
						#for now, just take mip 0. although generally we could just do the above for windows, other platforms will have a variety of alignment/packing rules.
						textureData = mips[firstMip].bulkData.readData()
						if textureData:
							mipWidth = mips[firstMip].width
							mipHeight = mips[firstMip].height
							if noesis.optWasInvoked("-ue4texalign"):
								#possible todo - pad appropriately for platform format+tiling, support cropping pad off when it's applied
								alignTo = int(noesis.optGetArg("-ue4texalign"))
								if alignTo < 0:
									mipWidth = noesis.nextPow2(mipWidth)
								else:
									m = mipWidth % alignTo
									if m != 0:
										mipWidth += (alignTo - m)
							textureData, noeFormat = ue4ConvertTextureData(self.asset, mipWidth, mipHeight, textureData, imagePixelFormat)
							if textureData:
								self.texture = NoeTexture(repr(export.objectName) if export else "ue4tex", mipWidth, mipHeight, textureData, noeFormat)
								self.texture.uTexture = self
				else:
					if dataSize <= 0:
						break
					bs.seek(dataSize, NOESEEK_REL)
				pixelFormat = repr(UE4Name(self.asset))
		else:
			sourceProps = self.findPropertyTagByName("Source")
			if self.sourceArt and sourceProps:
				sourcePropList = sourceProps.readProperty()
				width = 0
				height = 0
				format = None
				sliceCount = 1
				mipCount = 1
				pngCompressed = False
				for sourcePropEntry in sourcePropList:
					if sourcePropEntry.name == "SizeX":
						width = sourcePropEntry.readProperty()
					elif sourcePropEntry.name == "SizeY":
						height = sourcePropEntry.readProperty()
					elif sourcePropEntry.name == "NumSlices":
						sliceCount = sourcePropEntry.readProperty()
					elif sourcePropEntry.name == "NumMips":
						mipCount = sourcePropEntry.readProperty()
					elif sourcePropEntry.name == "Format":
						format = repr(sourcePropEntry.readProperty())
					elif sourcePropEntry.name == "bPNGCompressed":
						pngCompressed = sourcePropEntry.readProperty()
				if width <= 0 or height <= 0 or not format:
					print("Warning: Could not find expected struct properties for source art.")
				else:
					sourceData = self.sourceArt.readData()
					if pngCompressed:
						decompTex = rapi.loadTexByHandler(sourceData, ".png")
						sourceData = decompTex.pixelData if decompTex else None

					if sourceData:
						noeFormat = None
						if format == "TSF_BGRA8":
							sourceData = rapi.imageDecodeRaw(sourceData, width, height, "b8g8r8a8")
							noeFormat = noesis.NOESISTEX_RGBA32
						elif format == "TSF_RGBA8":
							noeFormat = noesis.NOESISTEX_RGBA32

						if noeFormat:
							self.texture = NoeTexture(repr(export.objectName) if export else "ue4tex", width, height, sourceData, noeFormat)
							self.texture.uTexture = self
						else:
							print("Warning: Unsupported source art format:", format)
					else:
						print("Warning: Could not read source art data.")
			else:
				print("Warning: Uncooked texture data with no source art.")
		
#currently, this is used generically for all material instance objects. we only care about digging props out.
class UE4MaterialInstance(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		self.parentObject = None
		self.parentInstance = None
		parentTag = self.findPropertyTagByName("Parent")
		if parentTag:
			self.parentInstance = parentTag.readProperty()
			
		self.albedoTex = None
		self.normalTex = None
		self.roughnessTex = None
		self.compositeTex = None
		self.compositeType = None
		self.metalnessTex = None
			
		paramVals = self.findPropertyTagByName("TextureParameterValues")
		if paramVals:
			listsOfParamProps = paramVals.readProperty()
			for propList in listsOfParamProps:
				nameProp = ue4FindPropertyTagLinear("ParameterName", propList)
				valueProp = ue4FindPropertyTagLinear("ParameterValue", propList)
				if not nameProp: #pull the name out of the ParameterInfo if necessary
					infoProp = ue4FindPropertyTagLinear("ParameterInfo", propList)
					infoPropData = infoProp.readProperty()
					if infoPropData:
						nameProp = infoPropData[0]
				
				if nameProp and valueProp:
					ue4SetTextureOverride(self, nameProp.readProperty(), valueProp.readProperty())
					
	def loadDependencies(self, loadedDeps):
		if self.parentInstance:
			self.parentObject = ue4ImportDependency(self.parentInstance, loadedDeps)
			if self.parentObject:
				self.parentObject.loadDependencies(loadedDeps)
			else:
				print("Warning: Failed to load material instance parent:", self.parentInstance)
		self.albedoObject = ue4ImportDependency(self.albedoTex, loadedDeps)
		self.normalObject = ue4ImportDependency(self.normalTex, loadedDeps)
		self.roughnessObject = ue4ImportDependency(self.roughnessTex, loadedDeps)
		self.compositeObject = ue4ImportDependency(self.compositeTex, loadedDeps)
		self.metalnessObject = ue4ImportDependency(self.metalnessTex, loadedDeps)
		return True
		
	def getAlbedo(self):
		if self.albedoTex:
			return self.albedoTex
		if self.parentObject:
			return self.parentObject.getAlbedo()
		return ""
	def getNormal(self):
		if self.normalTex:
			return self.normalTex
		if self.parentObject:
			return self.parentObject.getNormal()
		return ""
	def getRoughness(self):
		if self.roughnessTex:
			return self.roughnessTex
		if self.parentObject:
			return self.parentObject.getRoughness()
		return ""
	def getComposite(self):
		if self.compositeTex:
			return self.compositeTex
		if self.parentObject:
			return self.parentObject.getComposite()
		return ""
	def getCompositeType(self):
		if self.compositeType:
			return self.compositeType
		if self.parentObject:
			return self.parentObject.getCompositeType()
		return ""
	def getMetalness(self):
		if self.metalnessTex:
			return self.metalnessTex
		if self.parentObject:
			return self.parentObject.getMetalness()
		return ""
				
class UE4Material(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		self.parentInstance = None
		self.albedoTex = None
		self.normalTex = None
		self.roughnessTex = None
		self.compositeTex = None
		self.compositeType = None
		self.metalnessTex = None
		#could potentially parse out all of the expression objects to try to dig through and find reasonable inputs to trace back through to get
		#better default texture assignments. currently not nearly enough shits are given.
		#baseColorProp = self.findPropertyTagByName("BaseColor")
		#normalProp = self.findPropertyTagByName("Normal")
		#roughnessProp = self.findPropertyTagByName("Roughness")
		#metalnessProp = self.findPropertyTagByName("Metallic")
		
	def loadDependencies(self, loadedDeps):
		self.albedoObject = ue4ImportDependency(self.albedoTex, loadedDeps)
		self.normalObject = ue4ImportDependency(self.normalTex, loadedDeps)
		self.roughnessObject = ue4ImportDependency(self.roughnessTex, loadedDeps)
		self.compositeObject = ue4ImportDependency(self.compositeTex, loadedDeps)
		self.metalnessObject = ue4ImportDependency(self.metalnessTex, loadedDeps)
		return True
		
	def getAlbedo(self):
		return self.albedoTex if self.albedoTex else ""
	def getNormal(self):
		return self.normalTex if self.normalTex else ""
	def getRoughness(self):
		return self.roughnessTex if self.roughnessTex else ""
	def getComposite(self):
		return self.compositeTex if self.compositeTex else ""
	def getCompositeType(self):
		return self.compositeType if self.compositeType else ""
	def getMetalness(self):
		return self.metalnessTex if self.metalnessTex else ""
		
class UE4MaterialExpressionTexture(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		self.paramName = self.findPropertyTagByName("ParameterName")
		self.materialName = self.findPropertyTagByName("Material")
		self.textureName = self.findPropertyTagByName("Texture")
	def postLoad(self):
		super().postLoad()
		if self.paramName and self.materialName and self.textureName:
			materialName = self.materialName.readProperty()
			foundMaterial = self.asset.getExportableObjectByName(materialName)
			if foundMaterial:
				ue4SetTextureOverride(foundMaterial, self.paramName.readProperty(), self.textureName.readProperty())

class UE4Skeleton(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		if noesis.optWasInvoked("-ue4anims") and self.asset.serialVersion >= UE4_SERIALVER_PREREL_REFERENCE_SKELETON_REFACTOR:
			super().load(export)
			self.refSkeleton = UE4RefSkeleton(self.asset)
			#don't care about anything below here, for now

class UE4AnimationAsset(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		super().load(export)
		if self.asset.serialVersion >= UE4_SERIALVER_PREREL_SKELETON_GUID_SERIALIZATION:
			UE4Guid(self.asset)

class UE4AnimSequenceBase(UE4AnimationAsset):
	def __init__(self, asset):
		super().__init__(asset)
	#no serialization needed currently, just fall through to parent

class UE4AnimSequence(UE4AnimSequenceBase):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		if noesis.optWasInvoked("-ue4anims"):
			super().load(export)
			asset = self.asset
			self.skeleton = None
			self.skeletonReference = None
			seqLenProp = self.findPropertyTagByName("SequenceLength")
			skeletonProp = self.findPropertyTagByName("Skeleton")
			numFramesProp = self.findPropertyTagByName("NumFrames")
			rateScaleProp = self.findPropertyTagByName("RateScale")
			if not seqLenProp or not skeletonProp or not numFramesProp:
				print("Warning: Missing expected properties on AnimSequence. Ignoring.")
			else:
				self.sequenceLength = seqLenProp.readProperty()
				self.skeletonReference = skeletonProp.readProperty()
				self.numFrames = numFramesProp.readProperty()
				self.rateScale = rateScaleProp.readProperty() if rateScaleProp else 1.0
				self.frameRate = self.numFrames / self.sequenceLength * self.rateScale

				stripFlags = UE4StripFlags(asset)
				if not stripFlags.isEditorDataStripped():
					print("Warning: AnimSequence with editor data is not currently supported.")
				else:
					if asset.getFrameworkObjectVersion() < 5:
						self.compressedData = ue4ReadListAsRawData(asset, 1)
						keyEncProp = self.findPropertyTagByName("KeyEncodingFormat")
						transCompProp = self.findPropertyTagByName("TranslationCompressionFormat")
						rotCompProp = self.findPropertyTagByName("RotationCompressionFormat")
						scaleCompProp = self.findPropertyTagByName("ScaleCompressionFormat")
						compTrackOffsetsProp = self.findPropertyTagByName("CompressedTrackOffsets")
						compScaleOffsetsProp = self.findPropertyTagByName("CompressedScaleOffsets")
						trackToSkelProp = self.findPropertyTagByName("TrackToSkeletonMapTable")
						if compTrackOffsetsProp and trackToSkelProp:
							keyEncString = repr(keyEncProp.readProperty()) if keyEncProp else "AKF_ConstantKeyLerp"
							if keyEncString in ue4AnimKeyFormatStringDict:
								self.keyEncodingFormat = ue4AnimKeyFormatStringDict[keyEncString]
								transCompString = repr(transCompProp.readProperty()) if transCompProp else "ACF_None"
								rotCompString = repr(rotCompProp.readProperty()) if rotCompProp else "ACF_None"
								scaleCompString = repr(scaleCompProp.readProperty()) if scaleCompProp else "ACF_None"
								if transCompString in ue4AnimCompFormatStringDict and rotCompString in ue4AnimCompFormatStringDict and scaleCompString in ue4AnimCompFormatStringDict:
									self.transCompFormat = ue4AnimCompFormatStringDict[transCompString]
									self.rotCompFormat = ue4AnimCompFormatStringDict[rotCompString]
									self.scaleCompFormat = ue4AnimCompFormatStringDict[scaleCompString]
									self.compTrackOffsets = ue4ConvertListEntriesToObjectData(asset, compTrackOffsetsProp.readProperty())
									if compScaleOffsetsProp:
										scaleOffsetsProps = compScaleOffsetsProp.readProperty()
										self.compScaleOffsets = UE4CompScaleOffsetsPropStruct(asset, scaleOffsetsProps)
									else:
										self.compScaleOffsets = UE4CompScaleOffsetsPropStruct(asset, [])
										
									self.trackToSkeletonMap = []
									trackSkelEntries = trackToSkelProp.readProperty()
									for trackSkelEntryProps in trackSkelEntries:
										mapEntry = UE4TrackToSkeletonMapPropStruct(asset, trackSkelEntryProps)
										self.trackToSkeletonMap.append(mapEntry)
									self.validAnimation = True
								else:
									print("Warning: Unhandled anim sequence compression:", transCompString, rotCompString, scaleCompString)
							else:
								print("Warning: Unhandled anim sequence encoding:", keyEncString)
					else:
						bs = asset.bs
						hasCompressedData = ue4ReadBool(bs)
						if hasCompressedData:
							self.validAnimation = True
							self.keyEncodingFormat = ue4GetVersionedAnimKeyFormat(asset, bs.readByte())
							self.transCompFormat = ue4GetVersionedAnimCompFormat(asset, bs.readByte())
							self.rotCompFormat = ue4GetVersionedAnimCompFormat(asset, bs.readByte())
							self.scaleCompFormat = ue4GetVersionedAnimCompFormat(asset, bs.readByte())
							self.compTrackOffsets = ue4ReadList(asset, UE4RawType.typeInt)
							self.compScaleOffsets = UE4CompScaleOffsets(asset)
							if asset.serialVersion >= UE4_SERIALVER_421:
								self.compressedSegments = ue4ReadList(asset, UE4CompressedSegment)
							self.trackToSkeletonMap = ue4ReadList(asset, UE4TrackToSkeletonMap)
							self.curveData = UE4RawCurveTracks(asset)
							if asset.serialVersion >= UE4_SERIALVER_417:
								self.compressedRawSize = bs.readInt()
								if asset.serialVersion >= UE4_SERIALVER_422:
									self.compressedNumFrames = bs.readInt()
							self.compressedData = ue4ReadListAsRawData(asset, 1)
							#for now, don't care about the rest
						else:
							print("Warning: AnimSequence contains no compressed data.")
	def loadDependencies(self, loadedDeps):
		if not self.skeleton and self.skeletonReference:
			self.skeleton = ue4ImportDependency(self.skeletonReference, loadedDeps)
			if not self.skeleton:
				print("Warning: Failed to load skeleton", self.skeletonReference)
		return self.skeleton is not None
	def generateKeyframedAnim(self, kfAnims, slotName, animRefMesh, animBoneList):
		if self.skeleton:
			noeBones = self.skeleton.refSkeleton.generateNoesisBones(animRefMesh, True)
			if not animBoneList:
				animBoneList = noeBones

			if len(animBoneList) != len(noeBones):
				print("Warning: Bone count mismatch across multiple animations in the same package.")
			else:
				animBoneInfo = self.skeleton.refSkeleton.boneInfo
				boneToTrackIndex = [-1] * len(animBoneInfo)
				for trackIndex in range(0, len(self.trackToSkeletonMap)):
					trackMapping = self.trackToSkeletonMap[trackIndex]
					if trackMapping.boneTreeIndex < 0 or trackMapping.boneTreeIndex >= len(animBoneInfo):
						print("Warning: Out of range track to bone mapping.")
					else:
						boneToTrackIndex[trackMapping.boneTreeIndex] = trackIndex
				
				if self.keyEncodingFormat == UE4_ANIM_KEYFORMAT_PERTRACKCOMP:
					if self.transCompFormat != UE4_ANIM_COMPFORMAT_IDENTITY or self.rotCompFormat != UE4_ANIM_COMPFORMAT_IDENTITY:
						#doesn't really matter since compression formats are inline, but warn about it as it could be indicative of some unhandled mode
						print("Warning: Unexpected compression formats for PerTrackCompression:", self.transCompFormat, self.rotCompFormat)
						
					if not self.perTrackCompressionFixup():
						print("Warning: Could not fix up per-track compression offsets.")
					else:
						compBs = NoeBitStream(self.compressedData)
						
						elemsPerTrack = self.getElemsPerTrack()
						
						if len(self.trackToSkeletonMap) * elemsPerTrack != len(self.compTrackOffsets):
							#also don't consider this a real error, but it means elemsPerTrack is probably wrong
							print("Warning: Unexpected number of track offset entries.")
						
						kfBones = []
						for boneIndex in range(0, len(animBoneInfo)):
							boneInfo = animBoneInfo[boneIndex]
							if boneInfo.noeIndex < 0:
								continue #not associated with a generated noesis bone, which means we have a mesh ref skeleton and want to skip this bone
							trackIndex = boneToTrackIndex[boneIndex]
							if trackIndex < 0:
								continue
							offsetsIndex = trackIndex * elemsPerTrack
							rotOffset = self.compTrackOffsets[offsetsIndex + 1].data
							transOffset = self.compTrackOffsets[offsetsIndex].data
							#possible todo - handle scale. currently don't care.
							
							kfBone = NoeKeyFramedBone(boneInfo.noeIndex)
							kfRot = []
							kfTrans = []
							if rotOffset >= 0:
								compBs.seek(rotOffset, NOESEEK_ABS)
								header = UE4PerTrackCompHeader(compBs, self.asset)
								self.readKeys(header, compBs, kfRot, True)
							else:
								kfRot.append(NoeKeyFramedValue(0.0, NoeQuat([0.0, 0.0, 0.0, 1.0])))

							if transOffset >= 0:
								compBs.seek(transOffset, NOESEEK_ABS)
								header = UE4PerTrackCompHeader(compBs, self.asset)
								self.readKeys(header, compBs, kfTrans, False)
							else:
								kfTrans.append(NoeKeyFramedValue(0.0, NoeVec3([0.0, 0.0, 0.0])))
								
							kfBone.setRotation(kfRot)
							kfBone.setTranslation(kfTrans)
							kfBones.append(kfBone)
							
						kfAnim = NoeKeyFramedAnim(self.getName(), animBoneList, kfBones, self.frameRate)
						kfAnims.append(kfAnim)
				elif self.keyEncodingFormat == UE4_ANIM_KEYFORMAT_CONSTANTKEYLERP or self.keyEncodingFormat == UE4_ANIM_KEYFORMAT_VARIABLEKEYLERP:
					compBs = NoeBitStream(self.compressedData)						
					elemsPerTrack = self.getElemsPerTrack()
					kfBones = []
					for boneIndex in range(0, len(animBoneList)):
						boneInfo = animBoneInfo[boneIndex]
						if boneInfo.noeIndex < 0:
							continue #not associated with a generated noesis bone, which means we have a mesh ref skeleton and want to skip this bone
						trackIndex = boneToTrackIndex[boneIndex]
						if trackIndex < 0:
							continue
						offsetsIndex = trackIndex * elemsPerTrack
						rotOffset = self.compTrackOffsets[offsetsIndex + 2].data
						rotCount = self.compTrackOffsets[offsetsIndex + 3].data
						transOffset = self.compTrackOffsets[offsetsIndex].data
						transCount = self.compTrackOffsets[offsetsIndex + 1].data

						kfBone = NoeKeyFramedBone(boneInfo.noeIndex)
						kfRot = []
						kfTrans = []

						if rotCount > 0:
							if self.rotCompFormat in ue4AnimCompFormatDict:
								compBs.seek(rotOffset, NOESEEK_ABS)
								header = UE4ExplicitKeyHeader(compBs, self.asset, self.keyEncodingFormat, self.rotCompFormat, rotCount)
								self.readKeys(header, compBs, kfRot, True)
						else:
							kfRot.append(NoeKeyFramedValue(0.0, NoeQuat([0.0, 0.0, 0.0, 1.0])))
						
						if transCount > 0:
							if self.transCompFormat in ue4AnimCompFormatDict:
								compBs.seek(transOffset, NOESEEK_ABS)
								header = UE4ExplicitKeyHeader(compBs, self.asset, self.keyEncodingFormat, self.transCompFormat, transCount)
								self.readKeys(header, compBs, kfTrans, False)
						else:
							kfTrans.append(NoeKeyFramedValue(0.0, NoeVec3([0.0, 0.0, 0.0])))								

						kfBone.setRotation(kfRot)
						kfBone.setTranslation(kfTrans)
						kfBones.append(kfBone)

					kfAnim = NoeKeyFramedAnim(self.getName(), animBoneList, kfBones, self.frameRate)
					kfAnims.append(kfAnim)
				else:
					print("Warning: Unsupported keyEncodingFormat:", self.keyEncodingFormat)
		return animBoneList
	def frameToTime(self, frameIndex):
		return frameIndex / self.numFrames * self.sequenceLength
	def readKeyTable(self, compBs, header, startIndex, noeKeys):
		compBs.seek((compBs.tell() + 3) & ~3, NOESEEK_ABS)
		#go back and override key times with frametable entries
		for keyIndex in range(0, header.keyCount):
			frameIndex = compBs.readByte() if self.numFrames <= 255 else compBs.readUShort()
			noeKeys[startIndex + keyIndex].time = self.frameToTime(frameIndex)
	def readKeys(self, header, compBs, kfDest, isRotation):
		header.readTrackData()
		keyType = ue4AnimCompFormatDict[header.keyFormat]
		
		startIndex = len(kfDest)
		for keyIndex in range(0, header.keyCount):
			keyObject = keyType(compBs, header, self.asset)
			keyVal = keyObject.toQuat() if isRotation else keyObject.toVec()
			kfDest.append(NoeKeyFramedValue(self.frameToTime(keyIndex), keyVal))
		if header.reallyNeedsFrameTable:
			self.readKeyTable(compBs, header, startIndex, kfDest)		
	def getElemsPerTrack(self):
		return 2 if self.keyEncodingFormat == UE4_ANIM_KEYFORMAT_PERTRACKCOMP else 4
	def getOffsetForTrackAndTransformElement(self, trackIndex, transformElemIndex):
		if transformElemIndex > 1:
			if len(self.compScaleOffsets.offsets) == 0: #these are allowed to be absent
				return -1
			return self.compScaleOffsets.offsets[trackIndex].data
		else:
			elemsPerTrack = self.getElemsPerTrack()
			return self.compTrackOffsets[trackIndex * elemsPerTrack + transformElemIndex].data
	def setOffsetForTrackAndTransformElement(self, trackIndex, transformElemIndex, offset):
		if transformElemIndex > 1:
			if len(self.compScaleOffsets.offsets) > 0:
				self.compScaleOffsets.offsets[trackIndex].data = offset
		else:
			elemsPerTrack = self.getElemsPerTrack()
			self.compTrackOffsets[trackIndex * elemsPerTrack + transformElemIndex].data = offset
	def perTrackCompressionFixup(self):
		#pretty awful, offsets are no longer correct for this type and UE4 corrects it at load time
		#by copying memory around. there's no way to get around this without parsing through the
		#compressed data, but we'll at least do one better and just correct the offsets.
		trackCount = len(self.trackToSkeletonMap)
		compBs = NoeBitStream(self.compressedData)
		elemsPerTrack = self.getElemsPerTrack()
		transformElemCount = 3 #0=translation, 1=rotation, 2=scale
		for trackIndex in range(0, trackCount):
			for transformElemIndex in range(0, transformElemCount):
				offset = self.getOffsetForTrackAndTransformElement(trackIndex, transformElemIndex)
				if offset >= 0: #we'll never use this offset otherwise, but we're employing it to see if the data's present
					startOffset = compBs.tell()
					header = UE4PerTrackCompHeader(compBs, self.asset)
					if header.keyFormat not in ue4AnimCompFormatDict:
						print("Warning: Can't fix up offsets due to unhandled key format:", header.keyFormat)
						return False

					keyType = ue4AnimCompFormatDict[header.keyFormat]
					compBs.seek(keyType.getTrackSize(header), NOESEEK_REL)
					
					compBs.seek((compBs.tell() + 3) & ~3, NOESEEK_ABS)
	
					if header.reallyNeedsFrameTable:
						frameTableEntrySize = 1 if self.numFrames <= 255 else 2
						compBs.seek(frameTableEntrySize * header.keyCount, NOESEEK_REL)
						#align again after frametable
						compBs.seek((compBs.tell() + 3) & ~3, NOESEEK_ABS)
											
					self.setOffsetForTrackAndTransformElement(trackIndex, transformElemIndex, startOffset)
		return True

class UE4AnimMontage(UE4Object):
	def __init__(self, asset):
		super().__init__(asset)
	def load(self, export):
		if noesis.optWasInvoked("-ue4anims"):
			super().load(export)
			self.slotAnimTracks = []
			slotAnimTracksProp = self.findPropertyTagByName("SlotAnimTracks")
			if not slotAnimTracksProp:
				print("Warning: AnimMontage with no anim tracks. Ignoring.")
			else:
				slotAnimTracks = slotAnimTracksProp.readProperty()
				#run through the track property array to dig out the sub-properties we (currently) care about
				for slotAnimTrack in slotAnimTracks:
					slotNameProp = ue4FindPropertyTagLinear("SlotName", slotAnimTrack)
					animTrackProp = ue4FindPropertyTagLinear("AnimTrack", slotAnimTrack)
					if slotNameProp and animTrackProp:
						self.slotAnimTracks.append(UE4SlotAnimTrack(self, slotNameProp.readProperty(), animTrackProp.readProperty()))
				if len(self.slotAnimTracks) > 0:
					self.validMontage = True
				else:
					print("Warning: AnimMontage without any slot anim tracks. Ignoring.")
	def loadDependencies(self, loadedDeps):
		try:
			for slotAnimTrack in self.slotAnimTracks:
				animTrack = slotAnimTrack.animTrack
				for animSegment in animTrack.animSegments:
					if not animSegment.loadDependencies(loadedDeps):
						return False
		except:
			return False
		return True
				

#=================================================================
# Data implementations
#=================================================================

class UE4PerTrackCompHeader:
	def __init__(self, compBs, asset):
		ue4BaseObjectSetup(self, asset)
		self.compBs = compBs
		data = compBs.readUInt()
		self.keyCount = data & 16777215
		self.keyFlags = (data >> 24) & 7
		self.reallyNeedsFrameTable = (data >> 27) & 1
		self.keyFormat = ue4GetVersionedAnimCompFormat(asset, data >> 28)
		self.trackData = None
	def getUsedElemCount(self):
		usedCount = 0
		if self.keyFlags & 1: usedCount += 1
		if self.keyFlags & 2: usedCount += 1
		if self.keyFlags & 4: usedCount += 1
		return usedCount
	def readTrackData(self):
		#currently special cased just for the IntervalFixed32NoW type, which uses a scale & bias
		if self.keyFormat == UE4_ANIM_COMPFORMAT_INTERVALFIXED32NOW:
			compBs = self.compBs
			mins = NoeVec3((0.0, 0.0, 0.0))
			ranges = NoeVec3((0.0, 0.0, 0.0))
			if self.keyFlags & 1:
				mins[0] = compBs.readFloat()
				ranges[0] = compBs.readFloat()
			if self.keyFlags & 2:
				mins[1] = compBs.readFloat()
				ranges[1] = compBs.readFloat()
			if self.keyFlags & 4:
				mins[2] = compBs.readFloat()
				ranges[2] = compBs.readFloat()
			self.trackData = mins, ranges

class UE4ExplicitKeyHeader(UE4PerTrackCompHeader):
	def __init__(self, compBs, asset, keyEncoding, keyFormat, keyCount):
		ue4BaseObjectSetup(self, asset)
		self.compBs = compBs	
		self.keyCount = keyCount
		self.keyFlags = 7
		self.reallyNeedsFrameTable = keyEncoding == UE4_ANIM_KEYFORMAT_VARIABLEKEYLERP
		self.keyFormat = keyFormat
		self.trackData = None
			
class UE4AnimCompBaseType:
	def __init__(self, compBs, header, asset):
		ue4BaseObjectSetup(self, asset)
		self.header = header
		
class UE4AnimCompFloat96NoW(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.x = compBs.readFloat() if (header.keyFlags & 1) else 0.0
		self.y = compBs.readFloat() if (header.keyFlags & 2) else 0.0
		self.z = compBs.readFloat() if (header.keyFlags & 4) else 0.0
	@classmethod
	def getTrackSize(classObject, header):
		return 4 * header.getUsedElemCount() * header.keyCount
	def toVec(self):
		return NoeVec3((self.x, self.y, self.z))
	def toQuat(self):
		return ue4VecToNoeQuat(self.toVec())

class UE4AnimCompFixed48NoW(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.x = compBs.readUShort() if (header.keyFlags & 1) else UE4_QUANTIZE_16BIT_OFFS
		self.y = compBs.readUShort() if (header.keyFlags & 2) else UE4_QUANTIZE_16BIT_OFFS
		self.z = compBs.readUShort() if (header.keyFlags & 4) else UE4_QUANTIZE_16BIT_OFFS
	@classmethod
	def getTrackSize(classObject, header):
		return 2 * header.getUsedElemCount() * header.keyCount
	def toVec(self):
		x = (self.x - UE4_QUANTIZE_16BIT_OFFS) / UE4_QUANTIZE_16BIT_DIV
		y = (self.y - UE4_QUANTIZE_16BIT_OFFS) / UE4_QUANTIZE_16BIT_DIV
		z = (self.z - UE4_QUANTIZE_16BIT_OFFS) / UE4_QUANTIZE_16BIT_DIV
		return NoeVec3((x, y, z)) * 128.0
	def toQuat(self):
		return ue4VecToNoeQuat(self.toVec() / 128.0)

class UE4AnimCompIntervalFixed32NoW(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.data = compBs.readUInt()
	@classmethod
	def getTrackSize(classObject, header):
		return 8 * header.getUsedElemCount() + 4 * header.keyCount
	def toVec(self):
		unpackedX = (self.data & 0x000003FF)
		unpackedY = (self.data & 0x001FFC00) >> 10
		unpackedZ = self.data >> 21
		mins, ranges = self.header.trackData
		x = ((unpackedX - UE4_QUANTIZE_10BIT_OFFS) / UE4_QUANTIZE_10BIT_DIV) * ranges[0] + mins[0]
		y = ((unpackedX - UE4_QUANTIZE_11BIT_OFFS) / UE4_QUANTIZE_11BIT_DIV) * ranges[1] + mins[1]
		z = ((unpackedX - UE4_QUANTIZE_11BIT_OFFS) / UE4_QUANTIZE_11BIT_DIV) * ranges[2] + mins[2]
		return NoeVec3((x, y, z))
	def toQuat(self):
		return ue4VecToNoeQuat(self.toVec())

class UE4AnimCompFixed32NoW(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.data = compBs.readUInt()
	@classmethod
	def getTrackSize(classObject, header):
		return 4 * header.keyCount
	def toVec(self):
		unpackedX = self.data >> 21
		unpackedY = (self.data & 0x001FFC00) >> 10
		unpackedZ = (self.data & 0x000003FF)
		x = (unpackedX - UE4_QUANTIZE_11BIT_OFFS) / UE4_QUANTIZE_11BIT_DIV;
		y = (unpackedY - UE4_QUANTIZE_11BIT_OFFS) / UE4_QUANTIZE_11BIT_DIV;
		z = (unpackedZ - UE4_QUANTIZE_10BIT_OFFS) / UE4_QUANTIZE_10BIT_DIV;
		return NoeVec3((x, y, z))
	def toQuat(self):
		return ue4VecToNoeQuat(self.toVec())

class UE4AnimCompFloat32NoW(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.data = compBs.readUInt()
	@classmethod
	def getTrackSize(classObject, header):
		return 4 * header.keyCount
	def getVec(self):
		unpackedX = self.data >> 21;
		unpackedY = (self.data & 0x001FFC00) >> 10;
		unpackedZ = (self.data & 0x000003FF)
		x = noesis.getArbitraryFloat(unpackedX, 7, 3, 1)
		y = noesis.getArbitraryFloat(unpackedY, 7, 3, 1)
		z = noesis.getArbitraryFloat(unpackedZ, 6, 3, 1)
		return NoeVec3((x, y, z))
	def toQuat(self):
		return ue4VecToNoeQuat(self.toVec())

class UE4AnimCompIdentity(UE4AnimCompBaseType):
	def __init__(self, compBs, header, asset):
		super().__init__(compBs, header, asset)
		self.elemSize = 0
	@classmethod
	def getTrackSize(classObject, header):
		return 0
	def toVec(self):
		return NoeVec3((0.0, 0.0, 0.0))
	def toQuat(self):
		return NoeQuat((0.0, 0.0, 0.0, 1.0))
		
class UE4CompScaleOffsets:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.offsets = ue4ReadList(asset, UE4RawType.typeInt)
		self.stripSize = bs.readInt()

class UE4CompScaleOffsetsPropStruct:
	def __init__(self, asset, propList):
		ue4BaseObjectSetup(self, asset)
		self.offsets = []
		self.stripSize = 2
		for prop in propList:
			if prop.name == "OffsetData":
				self.offsets = prop.readProperty()
			elif prop.name == "StripSize":
				self.stripSize = prop.readProperty()
		self.offsets = ue4ConvertListEntriesToObjectData(asset, self.offsets)

class UE4TrackToSkeletonMap:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		self.boneTreeIndex = asset.bs.readInt()

class UE4CompressedSegment:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.startFrame = bs.readInt()
		self.numFrames = bs.readInt()
		self.byteStreamOffset = bs.readInt()
		self.transFormat = bs.readByte()
		self.rotFormat = bs.readByte()
		self.scaleFormat = bs.readByte()
		
class UE4TrackToSkeletonMapPropStruct:
	def __init__(self, asset, propList):
		ue4BaseObjectSetup(self, asset)
		self.boneTreeIndex = -1
		for prop in propList:
			if prop.name == "BoneTreeIndex":
				self.boneTreeIndex = prop.readProperty()
		
class UE4RawCurveTracks:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		ue4LoadObjectProperties(self)
		floatCurvesName = "FloatCurves"
		if floatCurvesName.lower() not in self.propTags:
			print("Warning: UE4RawCurveTracks without FloatCurves property.")
		else:
			curvesProp = self.propTags[floatCurvesName.lower()]
			self.floatCurves = curvesProp.readProperty()

class UE4SlotAnimTrack:
	def __init__(self, montage, slotName, animTrack):
		ue4BaseObjectSetup(self, montage.asset)
		self.montage = montage
		self.slotName = slotName
		self.animTrack = UE4AnimTrack(self, animTrack)
		
class UE4AnimTrack:
	def __init__(self, slotAnimTrack, animTrack):
		ue4BaseObjectSetup(self, slotAnimTrack.asset)
		self.slotAnimTrack = slotAnimTrack
		self.animSegments = []
		animSegmentsProp = ue4FindPropertyTagLinear("AnimSegments", animTrack)
		if not animSegmentsProp:
			print("Warning: AnimTrack is missing AnimSegments.")
		else:
			animSegments = animSegmentsProp.readProperty()
			for animSegment in animSegments:
				self.animSegments.append(UE4AnimSegment(self, animSegment))
				
class UE4AnimSegment:
	def __init__(self, animTrack, animSegment):
		ue4BaseObjectSetup(self, animTrack.asset)
		self.animTrack = animTrack
		self.animRefObject = None
		self.animReference = None
		animReferenceProp = ue4FindPropertyTagLinear("AnimReference", animSegment)
		if animReferenceProp:
			self.animReference = animReferenceProp.readProperty()
	def loadDependencies(self, loadedDeps):
		if self.animReference and not self.animRefObject:
			self.animRefObject = ue4ImportDependency(self.animReference, loadedDeps)
			if not self.animRefObject:
				print("Warning: Failed to load animation", self.animReference)			
		return self.animRefObject is not None

class UE4StaticMaterial:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.materialInterfaceRef = bs.readInt()
		self.materialName = asset.getImportExportName(self.materialInterfaceRef)
		self.materialSlotName = UE4Name(asset)
		if asset.getRenderingObjectVersion() >= 10:
			self.uvChannelInfo = UE4MeshUVChannelInfo(asset)
			
class UE4SkeletalMaterial:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.materialInterfaceRef = bs.readInt()
		self.materialName = asset.getImportExportName(self.materialInterfaceRef)
		if asset.getEditorObjectVersion() >= 8:
			self.materialSlotName = UE4Name(asset)
			if asset.containsEditorData():
				UE4Name(asset) #imported material slot name
		else:
			if asset.serialVersion >= UE4_SERIALVER_PREREL_MOVE_SKELETALMESH_SHADOWCASTING:
				ue4ReadBool(bs) #enableShadowCasting
			if asset.getRecomputeTangentVersion() > 0:
				self.recomputeTangent = ue4ReadBool(bs)
		if asset.getRenderingObjectVersion() >= 10:
			self.uvChannelInfo = UE4MeshUVChannelInfo(asset)
			
class UE4LegacyMaterial:
	def __init__(self, asset, materialName):
		ue4BaseObjectSetup(self, asset)
		self.materialName = materialName
	
class UE4MeshUVChannelInfo:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.initialized = ue4ReadBool(bs)
		self.overrideDensities = ue4ReadBool(bs)
		for channelIndex in range(0, 4):
			bs.readFloat() #uv densities
		
class UE4RefSkeleton:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		self.boneInfo = ue4ReadList(asset, UE4MeshBoneInfo)
		self.bindPose = ue4ReadList(asset, UE4Transform)				
		if asset.serialVersion >= UE4_SERIALVER_PREREL_REFERENCE_SKELETON_REFACTOR:
			#currently just assuming mats and info are 1:1
			self.nameToIndex = ue4ReadPairList(asset, UE4Name, UE4RawType.typeInt)
		if asset.serialVersion < UE4_SERIALVER_PREREL_FIXUP_ROOTBONE_PARENT and len(self.boneInfo) > 0:
			#how revolting, maybe an actorx exporter remnant
			self.boneInfo[0].parentIndex = -1
	def generateNoesisBones(self, refMesh, inModelSpace):
		boneCount = len(self.boneInfo)
		#run through and mark bones that are referenced by the skinned mesh skeleton
		if refMesh:
			meshSkel = refMesh.refSkeleton
			boneCount = len(meshSkel.boneInfo)
			infoDict = {}
			for boneInfo in self.boneInfo:
				infoDict[repr(boneInfo.name)] = boneInfo
			for boneIndex in range(0, len(meshSkel.boneInfo)):
				boneInfo = meshSkel.boneInfo[boneIndex]
				boneName = repr(boneInfo.name)
				if boneName in infoDict:
					otherInfo = infoDict[boneName]
					otherInfo.skinReferenced = True
					otherInfo.refMeshBoneIndex = boneIndex
		
		noeBones = [NoeBone(0, "", NoeMat43(), None, -1)] * boneCount
		for boneIndex in range(0, len(self.boneInfo)):
			boneInfo = self.boneInfo[boneIndex]
			if refMesh and not boneInfo.skinReferenced:
				continue #if we have a reference mesh skeleton and this bone doesn't reference it, skip it
			bindTransform = self.bindPose[boneIndex]
			boneName = repr(boneInfo.name)
			boneInfo.noeIndex = boneInfo.refMeshBoneIndex if refMesh else boneIndex
			if noesis.optWasInvoked("-ue4bidx"):
				boneName = "%04i_"%boneInfo.noeIndex + boneName
			noeBone = NoeBone(boneInfo.noeIndex, boneName, bindTransform.toNoeMat43(), None, boneInfo.parentIndex)
			#noeBone.ue4Index = boneIndex
			noeBones[boneInfo.noeIndex] = noeBone
			
		if refMesh:
			#run through and remap parents
			for boneIndex in range(0, len(noeBones)):
				noeBone = noeBones[boneIndex]
				if noeBone.parentIndex >= 0:
					if self.boneInfo[noeBone.parentIndex].skinReferenced:
						noeBone.parentIndex = self.boneInfo[noeBone.parentIndex].refMeshBoneIndex
					else:
						print("Warning: Lost bone in reference hierarchy:", self.boneInfo[noeBone.parentIndex].name)
						noeBone.parentIndex = -1
			
		if inModelSpace:
			noeBones = rapi.multiplyBones(noeBones)
		return noeBones
	
class UE4MeshBoneInfo:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.name = UE4Name(asset)
		self.parentIndex = bs.readInt()
		self.skinReferenced = False
		self.noeIndex = -1
		if asset.serialVersion < UE4_SERIALVER_PREREL_REFERENCE_SKELETON_REFACTOR:
			self.color = UE4Color(asset)
		if asset.containsEditorData() and asset.serialVersion >= UE4_SERIALVER_402_STORE_BONE_EXPORT_NAMES:
			UE4String(asset)

class UE4SkeletalMeshSection:
	def __init__(self, asset, objectOwner, parseObject = True):
		ue4BaseObjectSetup(self, asset, objectOwner)
		if parseObject:
			self.parseObject(objectOwner, True)
		
	@classmethod
	def asEditorData(classObject, asset, objectOwner):
		inst = classObject(asset, objectOwner, False)
		inst.parseObject(objectOwner, False)
		return inst
		
	def parseObject(self, objectOwner, asRenderData):
		asset = self.asset
		bs = asset.bs
		
		stripFlags = UE4StripFlags(asset)
		self.materialIndex = bs.readShort()
		
		self.softVerts = None
		
		#the majority of this is unnecessary, but we have to parse to completion as these things are back-to-back in storage
		skelMeshVer = asset.getSkeletalMeshVersion()
		if skelMeshVer >= 12 and asRenderData: #FSkelMeshRenderSection (might need some game hacks to circumvent this path at some point)
			self.firstIndex = bs.readInt()
			self.triangleCount = bs.readInt()
			self.recomputeTangent = ue4ReadBool(bs)
			self.castShadow = ue4ReadBool(bs)
			self.baseVertexIndex = bs.readInt()
			clothSize = len(ue4ReadList(asset, UE4ApexClothPhysToRenderVertData))
			if clothSize > 0:
				objectOwner.hasCloth = True
			self.boneMap = ue4ReadList(asset, UE4RawType.typeShort)
			self.vertCount = bs.readInt()
			self.maxBoneInfluences = bs.readInt()			
			bs.readShort() #cloth asset index
			UE4ClothingSectionData(asset)
			ue4ReadList(asset, UE4RawType.typeInt)
			ue4ReadList(asset, UE4RawType.typeInt64)
			if asset.serialVersion >= UE4_SERIALVER_419_ADDED_DISABLED_TO_RENDERSECTION:
				ue4ReadBool(bs) #disabled
		else:
			if skelMeshVer < 1:
				bs.readShort() #chunkIndex

			if stripFlags.isRenderDataStripped():
				self.firstIndex = 0
				self.triangleCount = 0
			else:
				self.firstIndex = bs.readInt()
				self.triangleCount = bs.readInt()
			
			if skelMeshVer < 13:
				self.triangleSorting = bs.readByte()
			if asset.serialVersion >= UE4_SERIALVER_PREREL_APEX_CLOTH:
				if skelMeshVer < 15:
					self.disabled = ue4ReadBool(bs)
				if skelMeshVer < 14:
					self.clothIndex = bs.readShort()
				if asset.serialVersion >= UE4_SERIALVER_PREREL_APEX_CLOTH_LOD:
					bs.readByte() #enableClothLOD
			else:
				self.disabled = False
				
			if asset.getRecomputeTangentVersion() > 0:
				self.recomputeTangent = ue4ReadBool(bs)
			if asset.getEditorObjectVersion() >= 8 and asset.gameHack != UE4_GAMEHACK_T7:
				self.castShadow = ue4ReadBool(bs)
				
			if skelMeshVer >= 1:
				if not stripFlags.isRenderDataStripped():
					self.baseVertexIndex = bs.readInt()
				if not stripFlags.isEditorDataStripped():
					if skelMeshVer < 2:
						ue4ReadList(asset, UE4RigidVertex)
					self.softVerts = ue4ReadList(asset, UE4SoftVertex)
				
				self.boneMap = ue4ReadList(asset, UE4RawType.typeShort)
				if skelMeshVer >= 4:
					self.vertCount = bs.readInt()
				if skelMeshVer < 2:
					bs.readInt() #numRigidVerts
					bs.readInt() #numSoftVerts
				self.maxBoneInfluences = bs.readInt()
				
				#cloth stuff, don't care
				clothSize = len(ue4ReadList(asset, UE4ApexClothPhysToRenderVertData))
				if clothSize > 0:
					objectOwner.hasCloth = True
				if skelMeshVer < 14:
					ue4ReadList(asset, UE4Vector)
					ue4ReadList(asset, UE4Vector)
				bs.readShort() #cloth asset index
				if skelMeshVer < 8:
					bs.readShort() #submesh index
				else:
					UE4ClothingSectionData(asset)
					
				if asset.getOverlappinngVerticesVersion() >= 1:
					ue4ReadPairList(asset, UE4RawType.typeInt, UE4RawType.typeIntList)
				if asset.getReleaseObjectVersion() >= 17:
					ue4ReadBool(bs) #disabled bool
				if skelMeshVer >= 16:
					bs.readInt() #generate up to lod index, we don't care about this
			
class UE4StaticMeshSection:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.materialIndex = bs.readInt()
		self.firstIndex = bs.readInt()
		self.triangleCount = bs.readInt()
		self.minVertIndex = bs.readInt()
		self.maxVertIndex = bs.readInt()
		self.enableCollision = ue4ReadBool(bs)
		self.castShadow = ue4ReadBool(bs)
			
class UE4VertexPositions:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.stride = bs.readInt()
		self.count = bs.readInt()
		arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
		self.data = arrayData
		
class UE4VertexColors:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.stride = bs.readInt()
		self.count = bs.readInt()
		stripFlags = UE4StripFlags(asset)
		if not stripFlags.isRenderDataStripped() and self.count > 0:
			arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
			self.data = arrayData #rgba32
		else:
			self.data = None

class UE4VertexColorsLegacy:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		strippedColor = False
		if asset.serialVersion >= UE4_SERIALVER_PREREL_STATIC_SKELETAL_MESH_SERIALIZATION_FIX:
			stripFlags = UE4StripFlags(asset)
			strippedColor = stripFlags.isRenderDataStripped()
		if not strippedColor:
			arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
			self.data = arrayData #rgba32
			self.stride = arrayStride
			self.count = arrayCount
		else:
			self.data = None
			
class UE4VertexInterleaved:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		UE4StripFlags(asset)
		self.uvSetCount = bs.readInt()
		if asset.serialVersion < UE4_SERIALVER_419:
			self.stride = bs.readInt()
		self.vertCount = bs.readInt()
		self.fullPrecisionUV = ue4ReadBool(bs)
		self.fullPrecisionTangent = False
		if asset.serialVersion >= UE4_SERIALVER_412:
			self.fullPrecisionTangent = ue4ReadBool(bs)
			
		self.normTanOffset = 0
		self.uvsOffset = 16 if self.fullPrecisionTangent else 8
		self.uvSetSize = 8 if self.fullPrecisionUV else 4
			
		if asset.serialVersion < UE4_SERIALVER_419:
			interleavedStride, interleavedCount, interleavedData = ue4ReadBulkArray(asset)
			self.interleavedData = interleavedData
		else:
			self.stride = self.uvsOffset + self.uvSetSize * self.uvSetCount
			self.interleavedData = bytearray(self.stride * self.vertCount)
			tanSize = bs.readInt()
			tanCount = bs.readInt()
			for tanIndex in range(0, self.vertCount):
				tanData = bs.readBytes(tanSize)
				if tanIndex < self.vertCount:
					ilvOffset = self.stride * tanIndex + self.normTanOffset
					self.interleavedData[ilvOffset : ilvOffset + tanSize] = tanData
			uvSize = bs.readInt()
			uvSize = self.uvSetSize * self.uvSetCount #force the size here
			uvCount = bs.readInt()
			for uvIndex in range(0, self.vertCount):
				uvData = bs.readBytes(uvSize)
				if uvIndex < self.vertCount:
					ilvOffset = self.stride * uvIndex + self.uvsOffset
					self.interleavedData[ilvOffset : ilvOffset + uvSize] = uvData
					
class UE4VertexSkinWeights:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		stripFlags = UE4StripFlags(asset)
		self.extraBoneWeights = ue4ReadBool(bs)
		self.vertCount = bs.readInt()
		self.weightsPerVert = 8 if self.extraBoneWeights else 4		
		self.stride = self.weightsPerVert * 2
		arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
		self.data = arrayData
					
class UE4SkeletalMeshVertexBuffer:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		UE4StripFlags(asset)
		self.uvSetCount = bs.readInt()
		self.fullPrecisionUV = ue4ReadBool(bs)
		self.extraBoneWeights = False
		skelMeshVer = asset.getSkeletalMeshVersion()
		if asset.serialVersion >= UE4_SERIALVER_PREREL_SUPPORT_GPUSKINNING_8_BONE_INFLUENCES and skelMeshVer < 7:
			self.extraBoneWeights = ue4ReadBool(bs)
		self.meshExtent = UE4Vector(asset)
		self.meshOrigin = UE4Vector(asset)
		
		skelMeshVer = asset.getSkeletalMeshVersion()
		#position should really come first here, and for that matter be packed next to the weights. but, you know, ue4.
		self.normTanOffset = 0
		self.weightsOffset = -1
		self.weightsPerVert = 8 if self.extraBoneWeights else 4
		postNormalsOffset = self.normTanOffset + 8
		if skelMeshVer < 7:
			self.weightsOffset = postNormalsOffset
			postNormalsOffset += 2 * self.weightsPerVert
		self.posOffset = postNormalsOffset
		self.uvsOffset = self.posOffset + 12
		self.uvSetSize = 8 if self.fullPrecisionUV else 4
		self.stride = self.uvsOffset + self.uvSetCount * self.uvSetSize
		#we don't serialize each vert
		arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
		self.data = arrayData
			
class UE4RawIndices:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.indexSize = 4 if ue4ReadBool(bs) else 2
		arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
		self.indexCount = (arrayStride * arrayCount) // self.indexSize
		self.data = arrayData

class UE4MultiSizeIndices:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		if asset.serialVersion < UE4_SERIALVER_PREREL_KEEP_SKEL_MESH_INDEX_DATA:
			ue4ReadBool(bs) #needsCPUAccess
		self.indexSize = bs.readByte()
		if self.indexSize <= 0:
			self.indexSize = 4
		arrayStride, arrayCount, arrayData = ue4ReadBulkArray(asset)
		self.indexCount = (arrayStride * arrayCount) // self.indexSize
		self.data = arrayData

class UE4FixedSizeIndices:
	def __init__(self, asset, indexSize):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.indexSize = indexSize
		self.indexCount = bs.readUInt()
		self.data = bs.readBytes(self.indexSize * self.indexCount)
		
class UE4WeightedRandomSampler:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		self.prob = ue4ReadList(asset, UE4RawType.typeFloat)
		self.alias = ue4ReadList(asset, UE4RawType.typeInt)
		self.totalWeight = asset.bs.readFloat()
		
class UE4SkeletalModelLOD:	
	def __init__(self, asset, objectOwner, parseObject = True):
		ue4BaseObjectSetup(self, asset, objectOwner)
		if parseObject:
			self.parseObject(objectOwner, True)
			
	@classmethod
	def asEditorData(classObject, asset, objectOwner):
		inst = classObject(asset, objectOwner, False)
		inst.parseObject(objectOwner, False)
		return inst
		
	def parseObject(self, objectOwner, asRenderData):
		asset = self.asset
		bs = asset.bs
		stripFlags = UE4StripFlags(asset)
		
		self.hasCloth = False
		self.chunks = []
		sectionGenerator = UE4SkeletalMeshSection if asRenderData else UE4SkeletalMeshSection.asEditorData
		self.sections = ue4ReadList(asset, sectionGenerator, self)
			
		skelMeshVer = asset.getSkeletalMeshVersion()
				
		if skelMeshVer >= 12 and asRenderData: #FSkeletalMeshLODRenderData (might need some game hacks to circumvent this path at some point)
			self.indices = UE4MultiSizeIndices(asset)
			self.activeBoneIndices = ue4ReadList(asset, UE4RawType.typeShort)
			self.requiredBones = ue4ReadList(asset, UE4RawType.typeShort)
			self.vertSkinnable = None
			
			if stripFlags.isRenderDataStripped():
				self.uvSetCount = 0
				self.vertPositions = self.vertInterleaved = self.vertSkinWeights = None
			else:
				self.vertPositions = UE4VertexPositions(asset)
				self.vertInterleaved = UE4VertexInterleaved(asset)
				self.vertSkinWeights = UE4VertexSkinWeights(asset)
				vertexColorProp = objectOwner.findPropertyTagByName("bHasVertexColors")
				if vertexColorProp and noeSafeGet(vertexColorProp, "boolValue") is True:
					self.vertColors = UE4VertexColors(asset)
				if (stripFlags.classStripFlags & 1) == 0:
					UE4MultiSizeIndices(asset) #adjacency index buffer
				if self.hasCloth:
					clothStripFlags = UE4StripFlags(asset)
					if not stripFlags.isRenderDataStripped():
						ue4ReadBulkArray(asset)
						ue4ReadList(asset, UE4RawType.typeInt64)
		else:
			if asRenderData:
				self.indices = UE4MultiSizeIndices(asset)
			else:
				self.indices = UE4FixedSizeIndices(asset, 4)
			self.activeBoneIndices = ue4ReadList(asset, UE4RawType.typeShort)
			if skelMeshVer < 1:
				self.chunks = ue4ReadList(asset, UE4SkelMeshChunk, self)
			self.size = bs.readInt()
			if stripFlags.isRenderDataStripped():
				self.vertCount = 0
			else:
				self.vertCount = bs.readInt()
			self.requiredBones = ue4ReadList(asset, UE4RawType.typeShort)
			
			if not stripFlags.isEditorDataStripped():
				UE4ByteBulkData(asset)
			
			if asset.serialVersion >= UE4_SERIALVER_PREREL_ADD_SKELMESH_MESHTOIMPORTVERTEXMAP:
				#self.meshToImportVertexMap = ue4ReadList(asset, UE4RawType.typeInt)
				ue4ReadListAsRawData(asset, 4) #don't need this, so don't waste time serializing each element
				self.maxImportVertex = bs.readInt()
				
			if stripFlags.isRenderDataStripped():
				self.uvSetCount = 0
				self.vertSkinnable = None
			else:
				self.uvSetCount = bs.readInt()
				if skelMeshVer >= 12: #editor-only path, no cooked geometry present
					self.vertSkinnable = None
				else:
					self.vertSkinnable = UE4SkeletalMeshVertexBuffer(asset)
					if skelMeshVer >= 7: #bsn - may not be accurate, not present in some v510
						#weight data may be stored in a separate array, not interleaved with the vertSkinnable data
						self.vertSkinWeights = UE4VertexSkinWeights(asset)
							
					vertexColorProp = objectOwner.findPropertyTagByName("bHasVertexColors")
					if vertexColorProp and noeSafeGet(vertexColorProp, "boolValue") is True:
						if skelMeshVer < 7: #bsn - may not be accurate, legacy present in some v510
							self.vertColors = UE4VertexColorsLegacy(asset)
						else:
							self.vertColors = UE4VertexColors(asset)
					if (stripFlags.classStripFlags & 1) == 0:
						UE4MultiSizeIndices(asset) #adjacency index buffer
					if self.hasCloth:
						clothStripFlags = UE4StripFlags(asset)
						if not stripFlags.isRenderDataStripped():
							ue4ReadBulkArray(asset)
							if skelMeshVer >= 10:
								ue4ReadList(asset, UE4RawType.typeInt64)
	
class UE4StaticModelLOD:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		stripFlags = UE4StripFlags(asset)
		self.chunks = []
		self.sections = ue4ReadList(asset, UE4StaticMeshSection)
		self.maxDeviation = bs.readFloat()
		self.vertSkinnable = None
		self.vertPositions = None
		if not stripFlags.isRenderDataStripped():
			self.vertPositions = UE4VertexPositions(asset)
			self.vertInterleaved = UE4VertexInterleaved(asset)
			self.vertColors = UE4VertexColors(asset)
			
			self.indices = UE4RawIndices(asset)
			#so many turds
			if asset.serialVersion >= UE4_SERIALVER_410_SOUND_CONCURRENCY_PACKAGE:
				UE4RawIndices(asset) #reversed indices
			UE4RawIndices(asset) #depth-only indices
			if asset.serialVersion >= UE4_SERIALVER_410_SOUND_CONCURRENCY_PACKAGE:
				UE4RawIndices(asset) #reversed depth-only indices
				
			if asset.serialVersion >= UE4_SERIALVER_402_FTEXT_HISTORY and asset.serialVersion < UE4_SERIALVER_404_RENAME_CROUCHMOVESCHARACTERDOWN:
				UE4DistanceFieldVolumeData(self.asset)		
				
			if not stripFlags.isEditorDataStripped():
				UE4RawIndices(asset) #wireframe index buffer
			if (stripFlags.classStripFlags & 1) == 0:
				UE4RawIndices(asset) #adjacency index buffer
				
			if asset.serialVersion >= UE4_SERIALVER_416:
				for sectionIndex in range(0, len(self.sections)):
					UE4WeightedRandomSampler(asset)
				UE4WeightedRandomSampler(asset)
		
class UE4Texture2DMip:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		isCooked = ue4ReadBool(bs)
		self.bulkData = UE4ByteBulkData(asset)
		self.width = bs.readInt()
		self.height = bs.readInt()
		if asset.serialVersion >= UE4_SERIALVER_420:
			self.depth = bs.readInt()
		if not isCooked:
			UE4String(asset)
			
class UE4PropertyTag:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.name = repr(UE4Name(asset))
		if self.name.lower() != "none":
			self.propType = repr(UE4Name(asset))
			self.dataSize = bs.readInt()
			self.arrayIndex = bs.readInt()
			if self.propType == "StructProperty":
				self.structName = repr(UE4Name(asset))
				if asset.serialVersion >= UE4_SERIALVER_407_STRUCT_GUID_IN_PROPERTY_TAG:
					self.structGuid = UE4Guid(asset)
			elif self.propType == "BoolProperty":
				self.boolValue = bs.readUByte() > 0
			elif self.propType == "ByteProperty":
				self.enumName = repr(UE4Name(asset))
			elif self.propType == "ArrayProperty":
				self.innerTypeName = repr(UE4Name(asset))
				
			if asset.serialVersion >= UE4_SERIALVER_414_PROPERTY_TAG_SET_MAP_SUPPORT:
				if self.propType == "SetProperty":
					self.innerTypeName = repr(UE4Name(asset))
				elif self.propType == "MapProperty_UE4":
					self.innerTypeName = repr(UE4Name(asset))
					self.valueTypeName = repr(UE4Name(asset))
					
			if asset.serialVersion >= UE4_SERIALVER_411_PROPERTY_GUID_IN_PROPERTY_TAG:
				if bs.readUByte() > 0:
					UE4Guid(asset)
			self.dataOffset = bs.tell() #can be parsed later on demand, if needed
			bs.seek(self.dataSize, NOESEEK_REL)
	def readProperty(self):
		asset = self.asset
		bs = asset.bs
		prevOffset = bs.tell()
		bs.seek(self.dataOffset, NOESEEK_ABS)
		
		#limited support, only implementing what i need as i need it
		r = None
		if self.propType == "NameProperty":
			r = repr(UE4Name(asset))
		elif self.propType == "StructProperty":
			#return self.structName + " " + repr(self.dataSize) + " " + repr(bs.tell())
			entryTag = UE4PropertyTag(asset)
			r = []
			while entryTag.name.lower() != "none":
				r.append(entryTag)
				entryTag = UE4PropertyTag(asset)
		elif self.propType == "ObjectProperty":
			objectRef = bs.readInt()
			r = asset.getImportExportName(objectRef)
		elif self.propType == "ArrayProperty":
			r = []
			dataCount = bs.readInt()
			if self.innerTypeName == "StructProperty":
				if asset.serialVersion >= UE4_SERIALVER_411_INNER_ARRAY_TAG_INFO:
					innerTag = UE4PropertyTag(asset)
					bs.seek(innerTag.dataOffset, NOESEEK_ABS)
			
				for dataIndex in range(0, dataCount):
					entryTag = UE4PropertyTag(asset)
					tagList = []
					while entryTag.name.lower() != "none":
						tagList.append(entryTag)
						entryTag = UE4PropertyTag(asset)
					r.append(tagList)
			elif self.innerTypeName == "ObjectProperty":
				for dataIndex in range(0, dataCount):
					objectRef = bs.readInt()
					objectName = asset.getImportExportName(objectRef)
					r.append(objectName)
			elif self.innerTypeName == "IntProperty":
				for dataIndex in range(0, dataCount):
					r.append(bs.readInt())
			elif self.innerTypeName == "FloatProperty":
				for dataIndex in range(0, dataCount):
					r.append(bs.readFloat())
			#possible todo - needs a bit of refactoring to avoid dumbness and duplication
		elif self.propType == "IntProperty":
			r = bs.readInt()
		elif self.propType == "FloatProperty":
			r = bs.readFloat()
		elif self.propType == "BoolProperty":
			r = ue4ReadBool(bs)
		elif self.propType == "ByteProperty":
			r = UE4Name(asset)
			
		bs.seek(prevOffset, NOESEEK_ABS)
		return r
	def readPropertyRaw(self):
		asset = self.asset
		bs = asset.bs
		prevOffset = bs.tell()
		bs.seek(self.dataOffset, NOESEEK_ABS)
		r = bs.readBytes(self.dataSize)
		bs.seek(prevOffset, NOESEEK_ABS)
		return r
			
class UE4ByteBulkData:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.dataFlags = bs.readInt()
		self.elementCount = bs.readInt()
		self.dataSize = bs.readInt()
		self.dataOffset = bs.readInt64()
		self.endOfHeader = bs.tell()
		if self.dataFlags & 64:
			bs.seek(self.dataSize, NOESEEK_REL)
	def readData(self):
		bs = self.asset.bs
		prevOffset = bs.tell()
		
		#print("bulk read:", self.dataFlags, self.dataSize, self.endOfHeader, self.dataOffset, self.asset.bulkDataOffset)
		data = None
		if self.dataFlags & 2048 and self.asset.secondaryExternalBulkDataOffset > 0:
			bs.seek(self.asset.secondaryExternalBulkDataOffset + self.asset.bulkDataOffset + self.dataOffset, NOESEEK_ABS)
		elif self.dataFlags & 256:
			if self.asset.externalBulkDataOffset > 0:
				bs.seek(self.asset.externalBulkDataOffset + self.asset.bulkDataOffset + self.dataOffset, NOESEEK_ABS)
			else:
				return None
		elif self.dataFlags & 1: #elsewhere in file
			bs.seek(self.asset.bulkDataOffset + self.dataOffset, NOESEEK_ABS)
		else: #assume inline, not really correct
			bs.seek(self.endOfHeader, NOESEEK_ABS)

		if self.dataFlags & 2: #compressed
			data = None
			tagChunk = UE4CompressedChunk(self.asset)
			if tagChunk.compSize != 0x9E2A83C1:
				print("Warning: Compressed bulk data without expected tag.")
			else:
				summary = UE4CompressedChunk(self.asset)
				chunks = []
				totalCompSize = 0
				totalDecompSize = 0
				while totalCompSize < summary.compSize and totalDecompSize < summary.compSize:
					chunk = UE4CompressedChunk(self.asset)
					totalCompSize += chunk.compSize
					totalDecompSize += chunk.decompSize
					chunks.append(chunk)
				if totalCompSize != summary.compSize or totalDecompSize != summary.decompSize:
					print("Warning: Unexpected bulk data compression chunk size total:", totalCompSize, summary.compSize, totalDecompSize, summary.decompSize)
				else:
					data = bytearray()
					for chunk in chunks:
						compData = bs.readBytes(chunk.compSize)
						data += rapi.decompInflate(compData, chunk.decompSize)
		else:
			data = bs.readBytes(self.dataSize)			
		
		bs.seek(prevOffset, NOESEEK_ABS)
		return data
		
class UE4DistanceFieldVolumeData:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		distanceFieldElemSize = 2 if asset.serialVersion < UE4_SERIALVER_416 else 1
		self.data = ue4ReadListAsRawData(asset, distanceFieldElemSize)
		self.size = UE4IntVector(asset)
		self.box = UE4Box(asset)
		self.meshWasClosed = ue4ReadBool(bs)
		if asset.serialVersion >= UE4_SERIALVER_404_RENAME_CROUCHMOVESCHARACTERDOWN:
			ue4ReadBool(bs) #builtAsIfTwoSided
			if asset.serialVersion >= UE4_SERIALVER_404_DEPRECATE_UMG_STYLE_ASSETS:
				ue4ReadBool(bs) #meshWasPlane

class UE4ApexClothPhysToRenderVertData:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.positionBaryCoordsAndDist = UE4Vector4(asset)
		self.normalBaryCoordsAndDist = UE4Vector4(asset)
		self.tangentBaryCoordsAndDist = UE4Vector4(asset)
		self.simMeshVertInidices = (bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort())
		bs.readInt() #pad
		bs.readInt() #pad
		
class UE4ClothingSectionData:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.guid = UE4Guid(asset)
		self.assetLodIndex = bs.readInt()

class UE4SkelMeshChunk:
	def __init__(self, asset, objectOwner):
		ue4BaseObjectSetup(self, asset, objectOwner)
		bs = asset.bs
		stripFlags = UE4StripFlags(asset)
		if stripFlags.isRenderDataStripped():
			noesis.doException("Stripped SkelMeshChunk data is not supported.")

		self.baseVertexIndex = bs.readInt()
		if not stripFlags.isEditorDataStripped():
			ue4ReadList(asset, UE4RigidVertex)
			ue4ReadList(asset, UE4SoftVertex)
		self.boneMap = ue4ReadList(asset, UE4RawType.typeShort)
		bs.readInt() #numRigidVerts
		bs.readInt() #numSoftVerts
		self.maxBoneInfluences = bs.readInt()

		if asset.serialVersion >= UE4_SERIALVER_PREREL_APEX_CLOTH:
			clothSize = len(ue4ReadList(asset, UE4ApexClothPhysToRenderVertData))
			if clothSize > 0:
				objectOwner.hasCloth = True
			ue4ReadList(asset, UE4Vector)
			ue4ReadList(asset, UE4Vector)
			bs.readShort()
			bs.readShort()
		
class UE4RigidVertex:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.pos = UE4Vector(asset)
		self.normals = (UE4PackedNormal(asset), UE4PackedNormal(asset), UE4PackedNormal(asset))
		self.uvs = []
		for uvSetIndex in range(0, 4):
			self.uvs.append(UE4UVFloat(asset))
		self.boneIndex = bs.readUByte()
		self.color = UE4Color(asset)

class UE4SoftVertex:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.pos = UE4Vector(asset)
		self.normals = (UE4PackedNormal(asset), UE4PackedNormal(asset), UE4PackedNormal(asset))
		self.uvs = []
		for uvSetIndex in range(0, 4):
			self.uvs.append(UE4UVFloat(asset))
		self.color = UE4Color(asset)
		self.boneIndices = []
		self.boneWeights = []
		weightsPerVert = 8 if asset.serialVersion >= UE4_SERIALVER_PREREL_SUPPORT_8_BONE_INFLUENCES_SKELETAL_MESHES else 4
		for weightIndex in range(0, weightsPerVert):
			self.boneIndices.append(bs.readUByte())
		for weightIndex in range(0, weightsPerVert):
			self.boneWeights.append(bs.readUByte())
		
class UE4Box:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.mins = UE4Vector(asset)
		self.maxs = UE4Vector(asset)
		self.isValid = bs.readByte() != 0
		
class UE4BoxSphereBounds:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.origin = UE4Vector(asset)
		self.extent = UE4Vector(asset)
		self.radius = bs.readFloat()
		
class UE4Vector:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.v = (bs.readFloat(), bs.readFloat(), bs.readFloat())
	def __repr__(self):
		return repr(self.v)
		
class UE4Vector4:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.v = (bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())
	def __repr__(self):
		return repr(self.v)
		
class UE4IntVector:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.v = (bs.readInt(), bs.readInt(), bs.readInt())
	def __repr__(self):
		return repr(self.v)

class UE4Quat:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.q = (bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())
	def __repr__(self):
		return repr(self.q)
		
class UE4Transform:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		self.rotation = UE4Quat(asset)
		self.translation = UE4Vector(asset)
		self.scale = UE4Vector(asset)
	def __repr__(self):
		return "(" + repr(self.rotation) + ", " + repr(self.translation) + ", " + repr(self.scale) + ")"
	def toNoeMat43(self):
		t = NoeVec3(self.translation.v)
		r = NoeQuat(self.rotation.q)
		s = NoeVec3(self.scale.v)
		noeMat = r.toMat43(1)
		noeMat = noeMat.transpose()
		noeMat[0] *= s[0] #note - untested, pretty sure scaling transform needs to be transposed
		noeMat[1] *= s[1]
		noeMat[2] *= s[2]
		noeMat = noeMat.transpose()
		noeMat[3] = t
		return noeMat
	
class UE4UVFloat:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.uv = (bs.readFloat(), bs.readFloat())
	
class UE4PackedNormal:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.data = bs.readUInt()
	
class UE4Color:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		bs.r = bs.readUByte()
		bs.g = bs.readUByte()
		bs.b = bs.readUByte()
		bs.a = bs.readUByte()
		
class UE4StripFlags:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.globalStripFlags = bs.readUByte()
		self.classStripFlags = bs.readUByte()
	def isEditorDataStripped(self):
		return (self.globalStripFlags & 1) != 0
	def isRenderDataStripped(self):
		return (self.globalStripFlags & 2) != 0
		
class UE4VersionType:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.key = UE4Guid(asset)
		self.version = bs.readInt()

class UE4EngineVersion:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.verMajor = bs.readUShort()
		self.verMinor = bs.readUShort()
		self.verPatch = bs.readUShort()
		self.clNumber = bs.readUInt()
		self.branch = ue4ReadString(asset)
				
class UE4ObjectRef:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.refIndex = bs.readInt()
		
class UE4Guid:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		if asset:
			bs = asset.bs
			self.A = bs.readUInt()
			self.B = bs.readUInt()
			self.C = bs.readUInt()
			self.D = bs.readUInt()
	@classmethod
	def fromValue(classObject, a, b, c, d):
		inst = classObject(None)
		inst.A = a
		inst.B = b
		inst.C = c
		inst.D = d
		return inst
	def __eq__(self, other):
		return self.A == other.A and self.B == other.B and self.C == other.C and self.D == other.D
	def __ne__(self, other):
		return self.A != other.A or self.B != other.B or self.C != other.C or self.D != other.D
		
class UE4GenerationInfo:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.exportCount = bs.readInt()
		self.nameCount = bs.readInt()
		
class UE4CompressedChunk:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.compSize = bs.readInt64()
		self.decompSize = bs.readInt64()

class UE4String:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		self.data = ue4ReadString(asset)
	def __repr__(self):
		return self.data
		
class UE4Name:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.index = bs.readInt()
		self.extraIndex = bs.readInt()
		self.data = asset.getName(self.index)
		if self.data is None:
			self.data = "None"
	def __repr__(self):
		return self.data
		
class UE4ImportObject:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.classPackage = UE4Name(asset)
		self.className = UE4Name(asset)
		self.packageIndex = bs.readInt()
		self.objectName = UE4Name(asset)
		
class UE4ExportObject:
	def __init__(self, asset):
		ue4BaseObjectSetup(self, asset)
		bs = asset.bs
		self.classIndex = bs.readInt()
		self.superIndex = bs.readInt()
		self.templateIndex = bs.readInt() if asset.serialVersion >= UE4_SERIALVER_414 else 0
		self.packageIndex = bs.readInt()
		self.objectName = UE4Name(asset)
		if asset.serialVersion < UE4_SERIALVER_PREREL_REMOVE_ARCHETYPE_INDEX_FROM_LINKER_TABLES:
			bs.readInt()
		self.objectFlags = bs.readInt()

		if asset.serialVersion >= UE4_SERIALVER_415_64BIT_EXPORTMAP_SERIALSIZES:
			self.serialSize = bs.readInt64()
			self.serialOffset = bs.readInt64()
		else:
			self.serialSize = bs.readInt()
			self.serialOffset = bs.readInt()
			
		ue4ReadBool(bs) #forced export
		ue4ReadBool(bs) #not for client
		ue4ReadBool(bs) #not for server
		
		if asset.serialVersion < UE4_SERIALVER_PREREL_REMOVE_NET_INDEX:
			bs.readInt()
		
		self.guid = UE4Guid(asset)
		self.packageFlags = bs.readInt()
		
		if asset.serialVersion >= UE4_SERIALVER_402_LOAD_FOR_EDITOR_GAME:
			ue4ReadBool(bs) #not for editor
		if asset.serialVersion >= UE4_SERIALVER_410_COOKED_ASSETS_IN_EDITOR_SUPPORT:
			self.isAsset = ue4ReadBool(bs)
		if asset.serialVersion >= UE4_SERIALVER_413_PRELOAD_DEPENDENCIES_IN_COOKED_EXPORTS:
			#preload dependencies
			bs.readInt()
			bs.readInt()
			bs.readInt()
			bs.readInt()
			bs.readInt()

class UE4RawType:
	def __init__(self, asset, data):
		ue4BaseObjectSetup(self, asset)
		self.data = data
	def __repr__(self):
		return repr(self.data)
	@classmethod
	def typeInt(classObject, asset):
		bs = asset.bs
		data = bs.readInt()
		return classObject(asset, data)
	@classmethod
	def typeIntList(classObject, asset):
		bs = asset.bs
		data = ue4ReadList(asset, UE4RawType.typeInt)
		return classObject(asset, data)
	@classmethod
	def typeInt64(classObject, asset):
		bs = asset.bs
		data = bs.readInt64()
		return classObject(asset, data)
	@classmethod
	def typeShort(classObject, asset):
		bs = asset.bs
		data = bs.readShort()
		return classObject(asset, data)
	@classmethod
	def typeUByte(classObject, asset):
		bs = asset.bs
		data = bs.readByte()
		return classObject(asset, data)
	@classmethod
	def typeFloat(classObject, asset):
		bs = asset.bs
		data = bs.readFloat()
		return classObject(asset, data)
		
class UE4ImportableObject:
	def __init__(self, export, fullPath):
		self.export = export
		self.filePath = fullPath
		
class UE4VersionToolOptions:
	def __init__(self):
		self.version = -1
		self.gameHack = -1
		if UE4_ENABLE_TOOLS and UE4_VERSION_TOOL_SAVE_OPTIONS:
			if os.path.exists(self.getSaveOptionPath()):
				with open(self.getSaveOptionPath(), "r") as f:
					for line in f:
						if line.startswith("CONFIGVERSION="):
							configVer = int(line.split("=", 1)[1])
							if configVer != UE4_VERSION_TOOL_SAVE_VERSION:
								break
						if line.startswith("VERSION="):
							self.version = int(line.split("=", 1)[1])
						elif line.startswith("GAMEHACK="):
							self.gameHack = int(line.split("=", 1)[1])
	def getSaveOptionPath(self):
		return noesis.getScenesPath() + "ue4_version_tool.cfg"
	def setFromToolWindow(self, noeWnd):
		verList = noeWnd.getControlByIndex(noeWnd.verListIndex)
		hackList = noeWnd.getControlByIndex(noeWnd.hackListIndex)
		verSelIndex = verList.getSelectionIndex()
		hackSelIndex = hackList.getSelectionIndex()
		if verSelIndex >= 0 and verSelIndex < len(noeWnd.ue4Versions):
			self.version = noeWnd.ue4Versions[verSelIndex][1]
		else:
			self.version = -1
		if hackSelIndex >= 0 and hackSelIndex < len(noeWnd.ue4Hacks):
			self.gameHack = noeWnd.ue4Hacks[hackSelIndex][1]
		else:
			self.gameHack = -1
		if UE4_ENABLE_TOOLS and UE4_VERSION_TOOL_SAVE_OPTIONS:
			with open(self.getSaveOptionPath(), "w") as f:
				f.write("CONFIGVERSION=" + repr(UE4_VERSION_TOOL_SAVE_VERSION) + "\n")
				f.write("VERSION=" + repr(self.version) + "\n")
				f.write("GAMEHACK=" + repr(self.gameHack) + "\n")
			
ue4VersionToolOptions = UE4VersionToolOptions()
		

#=================================================================
# Utility implementations
#=================================================================

ue4LoaderDict = {
	"Texture2D" : UE4Texture2D,
	"StaticMesh" : UE4StaticMesh,
	"SkeletalMesh" : UE4SkeletalMesh,
	"Material" : UE4Material,
	"MaterialInstance" : UE4MaterialInstance,
	"MaterialInstanceConstant" : UE4MaterialInstance,
	"MaterialExpressionTextureSample" : UE4MaterialExpressionTexture,
	"MaterialExpressionTextureSampleParameter2D" : UE4MaterialExpressionTexture,
	"Skeleton" : UE4Skeleton,
	"AnimSequence" : UE4AnimSequence,
	"AnimMontage" : UE4AnimMontage
}

def ue4ReadList(asset, listType, objectOwner = None):
	bs = asset.bs
	count = bs.readUInt()
	ue4SanityCheckListSize(count)
	list = []
	for index in range(0, count):
		if objectOwner is None:
			list.append(listType(asset))
		else:
			list.append(listType(asset, objectOwner))
	return list

def ue4ReadListAsRawData(asset, elemSize):
	bs = asset.bs
	count = bs.readUInt()
	ue4SanityCheckListSize(count)
	return bs.readBytes(elemSize * count)
	
def ue4ReadPairList(asset, firstType, secondType):
	bs = asset.bs
	count = bs.readUInt()
	ue4SanityCheckListSize(count)
	list = []
	for index in range(0, count):
		list.append((firstType(asset), secondType(asset)))
	return list
	
def ue4ConvertListEntriesToObjectData(asset, list):
	dataList = []
	for listEntry in list:
		dataList.append(UE4RawType(asset, listEntry))
	return dataList
	
def ue4ReadBulkArray(asset):
	bs = asset.bs
	stride = bs.readInt()
	count = bs.readInt()
	data = bs.readBytes(stride * count)
	return stride, count, data
	
def ue4ReadString(asset):
	return ue4StreamReadString(asset.bs)

def ue4StreamReadString(bs):
	stringLength = bs.readInt()
	if stringLength >= 0:
		return noeStrFromBytes(bs.readBytes(stringLength), "UTF-8")
	else:
		return noeStrFromBytes(bs.readBytes(-stringLength * 2), "UTF-16")	
		
def ue4ReadBool(bs):
	return bs.readInt() != 0
	
def ue4VecToNoeQuat(v):
	w = 1.0 - v[0] * v[0] - v[1] * v[1] - v[2] * v[2]
	w = math.sqrt(w) if w > 0.0 else 0.0
	return NoeQuat((-v[0], -v[1], -v[2], w))

def ue4BaseObjectSetup(object, asset, objectOwner = None):
	object.asset = asset
	object.objectOwner = objectOwner
	object.exportEntry = None

def ue4LoadObjectProperties(object):	
	object.propTags = {}
	bs = object.asset.bs
	while not bs.checkEOF():
		propTag = UE4PropertyTag(object.asset)
		if propTag.name.lower() == "none":
			break
		object.propTags[propTag.name.lower()] = propTag

def ue4FindPropertyTagLinear(name, propList):
	for prop in propList:
		if prop.name == name:
			return prop
	return None
	
def ue4SanityCheckListSize(count, maxCount = UE4_MAX_SANE_LIST_COUNT):
	if not noesis.optWasInvoked("-ue4sanity"):
		return
	if count > maxCount:
		noesis.doException("Hit unreasonable list count, you probably need to select a different UE4 object version.")

def ue4SetTextureOverride(material, paramName, textureName):
	namePropVal = paramName.lower()
	#here's some hacked up bullshit, for now
	if namePropVal.startswith("base") or namePropVal.startswith("bace") or namePropVal.startswith("diffuse") or namePropVal.startswith("albedo"):
		material.albedoTex = textureName
	elif namePropVal.startswith("normal") or namePropVal.startswith("nomal"):
		material.normalTex = textureName
	elif namePropVal.startswith("rough"):
		material.roughnessTex = textureName
	elif namePropVal.startswith("metal"):
		material.metalnessTex = textureName
	elif namePropVal.startswith("srma"):
		material.compositeTex = textureName
		material.compositeType = "srma"
	elif material.asset.gameHack == UE4_GAMEHACK_T7 and (namePropVal.startswith("specluar") or namePropVal.startswith("specular")):
		material.compositeTex = textureName
		material.compositeType = "rnasmul"
	elif material.asset.gameHack == UE4_GAMEHACK_T7 and namePropVal.startswith("color"):
		material.albedoTex = textureName
	#else:
	#	print("Discard texture property:", namePropVal, textureName)

def ue4UntileTexture(asset, width, height, blockWidth, blockHeight, blockSize, textureData, bitsPerTexel):
	if noesis.optWasInvoked("-ue4tex1dthin"):
		bcFlag = 1 if blockWidth > 1 or blockHeight > 1 else 0
		textureData = rapi.callExtensionMethod("untile_1dthin", textureData, width, height, bitsPerTexel, bcFlag)
	elif noesis.optWasInvoked("-ue4texgob"):
		widthInBlocks = (width + (blockWidth - 1)) // blockWidth
		heightInBlocks = (height + (blockHeight - 1)) // blockHeight
		#in the data i'm looking at, the max block height seems to be 8 (1 << 3) across the board.
		#and now i've found some uncompressed tiled textures, which appear to use a max block height of 16.
		#it also looks like we're meant to snap to the closest power of 2 here, which is a little bizarre, as hardware always rounds up.
		#umodel reportedly gets this wrong. (until gildor sees this) for a broken umodel case, see OT's UiTX_Title_CharaSelect_DoropShadow_CharaDs.uasset.
		if heightInBlocks < 16:
			maxBlockHeight = 1
		elif heightInBlocks < 24:
			maxBlockHeight = 2
		elif heightInBlocks < 48:
			maxBlockHeight = 4
		else:
			maxBlockHeight = 16 if blockWidth == 1 and blockHeight == 1 and heightInBlocks >= 96 else 8
		
		paddedWidth = width
		if noesis.optWasInvoked("-ue4texgobpad"):
			#umodel also needs this (can just enable it always on switch, keeping the options flexible for other tegra x1 data here)
			if height > 128:
				widthInBlocks = (widthInBlocks + 127) & ~127
				paddedWidth = widthInBlocks * blockWidth
		#possible todo - any other padding criteria? don't have a lot of ue4 switch texture variety to test.
			
		textureData = rapi.callExtensionMethod("untile_blocklineargob", textureData, widthInBlocks, heightInBlocks, blockSize, maxBlockHeight)
		if paddedWidth > width:
			#unpad the data
			rowSize = widthInBlocks * blockSize
			unpaddedWidthInBlocks = (width + (blockWidth - 1)) // blockWidth
			unpaddedRowSize = unpaddedWidthInBlocks * blockSize
			croppedData = bytearray()
			for rowIndex in range(0, heightInBlocks):
				rowOffset = rowIndex * rowSize
				croppedData += textureData[rowOffset : rowOffset + unpaddedRowSize]
			textureData = croppedData
	return textureData

def ue4ConvertTextureData(asset, width, height, textureData, pixelFormat):
	noeFormat = noesis.NOESISTEX_RGBA32
	if pixelFormat == "PF_BC5":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 16, textureData, 8)
		textureData = rapi.imageDecodeDXT(textureData, width, height, noesis.FOURCC_ATI2)
		noeFormat = noesis.NOESISTEX_RGBA32
	elif pixelFormat == "PF_BC4":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 16, textureData, 4)
		textureData = rapi.imageDecodeDXT(textureData, width, height, noesis.FOURCC_ATI1)
		noeFormat = noesis.NOESISTEX_RGBA32
	elif pixelFormat == "PF_B8G8R8A8":
		textureData = ue4UntileTexture(asset, width, height, 1, 1, 4, textureData, 32)
		if UE4_BGRA_SWIZZLE:
			textureData = rapi.imageDecodeRaw(textureData, width, height, "b8g8r8a8")		
		noeFormat = noesis.NOESISTEX_RGBA32
	elif pixelFormat == "PF_DXT1":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 8, textureData, 4)
		noeFormat = noesis.NOESISTEX_DXT1
	elif pixelFormat == "PF_DXT3":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 16, textureData, 8)
		noeFormat = noesis.NOESISTEX_DXT3
	elif pixelFormat == "PF_DXT5":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 16, textureData, 8)
		noeFormat = noesis.NOESISTEX_DXT5
	elif pixelFormat == "PF_FloatRGBA":
		textureData = ue4UntileTexture(asset, width, height, 1, 1, 16, textureData, 64)
		textureData = rapi.imageDecodeRaw(textureData, width, height, "r#f16g#f16b#f16a#f16")
		noeFormat = noesis.NOESISTEX_RGBA32
	elif pixelFormat == "PF_ASTC_8x8":
		textureData = ue4UntileTexture(asset, width, height, 8, 8, 16, textureData, 2)
		textureData = rapi.callExtensionMethod("astc_decoderaw32", textureData, 8, 8, 1, width, height, 1)
		noeFormat = noesis.NOESISTEX_RGBA32
	elif pixelFormat == "PF_ASTC_4x4":
		textureData = ue4UntileTexture(asset, width, height, 4, 4, 16, textureData, 8)
		textureData = rapi.callExtensionMethod("astc_decoderaw32", textureData, 4, 4, 1, width, height, 1)
		noeFormat = noesis.NOESISTEX_RGBA32
	#could easily support PVRTC and ASTC as decoders are already exposed to python, but don't have any test data at the moment.
	#ue4 doesn't look to even support PVRTC2, although noesis supports that too. (PF_PVRTC2 == PVRTC 2bpp, not PVRTC2)
	else:
		print("Unhandled pixel format:", pixelFormat)
		textureData = None
	return textureData, noeFormat

ue4LastScanPath = None
ue4AssetDatabase = {}

def ue4ImportDependency(objectName, loadedDeps):
	global ue4AssetDatabase
	if objectName is None:
		return None
	if objectName in ue4AssetDatabase: #alright, someone has it
		importableObject = ue4AssetDatabase[objectName]
		#see if it's already been loaded
		depAsset = None
		if importableObject.filePath in loadedDeps:
			depAsset = loadedDeps[importableObject.filePath]
		else:
		#attempt to load it
			print("Loading dependency:", importableObject.filePath)
			with open(importableObject.filePath, "rb") as f:
				data = f.read()
				bs = NoeBitStream(data)
				testAsset = UE4Asset(bs, importableObject.filePath, True)
				if testAsset.parse() == 0:
					depAsset = testAsset
					loadedDeps[importableObject.filePath] = depAsset
					depAsset.loadTables()
					depAsset.loadAssetData()
		if depAsset:
			importedObject = depAsset.getExportableObjectByName(objectName)
			if not importedObject:
				print("Warning: Object", objectName, "not found in expected package.")
			return importedObject
	return None

#a poor man's asset registry. this is a little terrible and only considers object names when constructing the dictionary.
#typically works well enough for small asset groupings.
def ue4ScanAssetData(scanDataPath):
	global ue4LastScanPath
	global ue4AssetDatabase
	
	ue4LastScanPath = scanDataPath
	ue4AssetDatabase = {}
	if not ue4LastScanPath:
		return
	for root, dirs, files in os.walk(scanDataPath):
		for fileName in files:
			lowerName = fileName.lower()
			if lowerName.endswith(".uasset"):
				fullPath = os.path.join(root, fileName)
				print("Attempting to scan:", fullPath)
				with open(fullPath, "rb") as f:
					bs = NoeFileStream(f)
					asset = UE4Asset(bs, fullPath, False)
					if asset.parse() == 0:
						asset.loadTables()
						for export in asset.exports:
							ue4AssetDatabase[repr(export.objectName)] = UE4ImportableObject(export, fullPath)

def ue4LoadBinaryChunk(fullPath):
	with open(fullPath, "rb") as f:
		return f.read()

UE4_ANIM_KEYFORMAT_CONSTANTKEYLERP = 0
UE4_ANIM_KEYFORMAT_VARIABLEKEYLERP = 1
UE4_ANIM_KEYFORMAT_PERTRACKCOMP = 2

UE4_ANIM_COMPFORMAT_NONE = 0
UE4_ANIM_COMPFORMAT_FLOAT96NOW = 1
UE4_ANIM_COMPFORMAT_FIXED48NOW = 2
UE4_ANIM_COMPFORMAT_INTERVALFIXED32NOW = 3
UE4_ANIM_COMPFORMAT_FIXED32NOW = 4
UE4_ANIM_COMPFORMAT_FLOAT32NOW = 5
UE4_ANIM_COMPFORMAT_IDENTITY = 6

UE4_QUANTIZE_16BIT_OFFS = 32767.0
UE4_QUANTIZE_16BIT_DIV = 32767.0
UE4_QUANTIZE_11BIT_OFFS = 1023.0
UE4_QUANTIZE_11BIT_DIV = 1023.0
UE4_QUANTIZE_10BIT_OFFS = 511.0
UE4_QUANTIZE_10BIT_DIV = 511.0

ue4AnimCompFormatDict = {
	UE4_ANIM_COMPFORMAT_FLOAT96NOW : UE4AnimCompFloat96NoW,
	UE4_ANIM_COMPFORMAT_FIXED48NOW : UE4AnimCompFixed48NoW,
	UE4_ANIM_COMPFORMAT_INTERVALFIXED32NOW : UE4AnimCompIntervalFixed32NoW,
	UE4_ANIM_COMPFORMAT_FIXED32NOW : UE4AnimCompFixed32NoW,
	UE4_ANIM_COMPFORMAT_FLOAT32NOW : UE4AnimCompFloat32NoW,
	UE4_ANIM_COMPFORMAT_IDENTITY : UE4AnimCompIdentity
}

ue4AnimKeyFormatStringDict = {
	"AKF_ConstantKeyLerp" : UE4_ANIM_KEYFORMAT_CONSTANTKEYLERP,
	"AKF_VariableKeyLerp" : UE4_ANIM_KEYFORMAT_VARIABLEKEYLERP,
	"AKF_PerTrackCompression" : UE4_ANIM_KEYFORMAT_PERTRACKCOMP
}

ue4AnimCompFormatStringDict = {
	"ACF_None" : UE4_ANIM_COMPFORMAT_NONE,
	"ACF_Float96NoW" : UE4_ANIM_COMPFORMAT_FLOAT96NOW,
	"ACF_Fixed48NoW" : UE4_ANIM_COMPFORMAT_FIXED48NOW,
	"ACF_IntervalFixed32NoW" : UE4_ANIM_COMPFORMAT_INTERVALFIXED32NOW,
	"ACF_Fixed32NoW" : UE4_ANIM_COMPFORMAT_FIXED32NOW,
	"ACF_Float32NoW" : UE4_ANIM_COMPFORMAT_FLOAT32NOW,
	"ACF_Identity" : UE4_ANIM_COMPFORMAT_IDENTITY
}

#just here for future maintenance in case we end up needing to translate based on version
def ue4GetVersionedAnimKeyFormat(asset, keyFormat):
	return keyFormat

def ue4GetVersionedAnimCompFormat(asset, compFormat):
	return compFormat


#=================================================================
# Noesis implementations
#=================================================================
		
def ue4CheckType(data):
	asset = UE4Asset(NoeBitStream(data), rapi.getLastCheckedName(), False)
	if asset.parse() != 0:
		return 0
	return 1
	
def ue4LoadModel(data, mdlList):
	asset = UE4Asset(NoeBitStream(data), rapi.getLastCheckedName(), True)
	if asset.parse() != 0:
		return 0
		
	print("UE4 version info:", asset.version, asset.serialVersion, asset.verA, asset.verB, asset.verLic)

	asset.loadTables()
	
	scanDataPath = None
	if noesis.optWasInvoked("-ue4datapath"):
		scanDataPath = noesis.optGetArg("-ue4datapath")
	global ue4LastScanPath
	if scanDataPath != ue4LastScanPath:
		ue4ScanAssetData(scanDataPath)
	
	asset.loadAssetData()

	noeTextures = []
	noeMaterials = []
	
	loadedDeps = {}
	
	#run through loaded exports looking for animation data
	if noesis.optWasInvoked("-ue4anims"):
		kfAnims = []
		animBoneList = None
		animRefMesh = None
		if noesis.optWasInvoked("-ue4animref"):
			importMeshName = noesis.optGetArg("-ue4animref")
			importMesh = ue4ImportDependency(importMeshName, loadedDeps)
			if importMesh and noeSafeGet(importMesh, "refSkeleton"):
				animRefMesh = importMesh
			else:
				print("Warning: Failed to import anim reference mesh:", importMeshName)
				
		for object in asset.serializedObjects:
			if noeSafeGet(object, "validAnimation"):
				if not object.loadDependencies(loadedDeps):
					print("Warning: Failed to load animation dependencies for", object.getName())
					continue
				animBoneList = object.generateKeyframedAnim(kfAnims, None, animRefMesh, animBoneList)
			elif noeSafeGet(object, "validMontage"):
				if not object.loadDependencies(loadedDeps):
					print("Warning: Failed to load montage dependencies for", object.getName())
					continue
				for slotAnimTrack in object.slotAnimTracks:
					animTrack = slotAnimTrack.animTrack
					for animSegment in animTrack.animSegments:
						animObject = animSegment.animRefObject
						if not animObject.loadDependencies(loadedDeps):
							print("Warning: Failed to load montage animation dependencies for", animObject.getName())
							continue
						#possible todo - evaluate/generate anim data using the montage. for now, just splat the whole thing in here.
						animBoneList = animObject.generateKeyframedAnim(kfAnims, slotAnimTrack.slotName, animRefMesh, animBoneList)
		if animBoneList:
			animModel = NoeModel([], [] if len(kfAnims) > 0 else animBoneList, kfAnims)
			mdlList.append(animModel)
	
	#check the database for material dependencies
	for mesh in asset.meshes:
		for lod in mesh.lods:
			for section in lod.sections:
				if section.materialIndex >= 0 and section.materialIndex < len(mesh.materials) and not noesis.optWasInvoked("-ue4defaultmtl"):
					materialName = mesh.materials[section.materialIndex].materialName
					foundMaterial = False
					for noeMat in noeMaterials:
						if noeMat.name == materialName:
							foundMaterial = True
							break
					if not foundMaterial:
						noeMat = NoeMaterial(materialName, "")
						noeMat.setMetal(0.0, 0.0)
					
						materialObject = ue4ImportDependency(materialName, loadedDeps)
						albedoTex = ""
						normalTex = ""
						roughnessTex = ""
						compositeTex = ""
						compositeType = ""
						if materialObject:
							try:
								materialObject.loadDependencies(loadedDeps)
								albedoTex = materialObject.getAlbedo()
								normalTex = materialObject.getNormal()
								roughnessTex = materialObject.getRoughness()
								compositeTex = materialObject.getComposite()
								compositeType = materialObject.getCompositeType()
							except:
								print("Warning: Failed to load material dependencies for", materialName)
						if compositeTex == "" and roughnessTex == "":
							roughnessTex = noesis.getScenesPath() + "sample_pbr_o.png"
							noeMat.setMetal(0.0, 0.0)
							noeMat.setRoughness(0.0, 0.75)
						if albedoTex == "":
							albedoTex = noesis.getScenesPath() + "sample_pbr_o.png"
							noeMat.setMetal(0.0, 1.0)
							noeMat.setRoughness(0.0, 0.25)
						hadNormalTex = (normalTex != "")
						if normalTex == "":
							normalTex = noesis.getScenesPath() + "sample_pbr_n.png"

						noeMat.setTexture(albedoTex)
						noeMat.setNormalTexture(normalTex)
						if compositeTex != "":
							noeMat.setSpecularTexture(compositeTex)
							if compositeType == "srma":
								noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_SPEC_IR_RG
								noeMat.setMetal(1.0, 0.0)
								noeMat.setSpecularSwizzle( NoeMat44([[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]) )
							if compositeType == "rnasmul":
								#flag it as metal and just eliminate metal contribution. spec map is often shared with albedo and
								#doesn't look good as a scalar.
								noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_ROUGHNESS_NRMALPHA
								noeMat.setMetal(0.0, 0.0)
							else:
								noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_SPEC_IR_RG
								print("Warning: Unhandled composite type", compositeType)
						else:
							if hadNormalTex and asset.gameHack == UE4_GAMEHACK_T7:
								noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_ROUGHNESS_NRMALPHA
								noeMat.setMetal(0.0, 0.0)
								noeMat.setRoughness(1.0, 0.0)
								
							noeMat.setSpecularTexture(roughnessTex)
							noeMat.flags |= noesis.NMATFLAG_PBR_METAL | noesis.NMATFLAG_PBR_SPEC_IR_RG
						noeMat.setEnvTexture(noesis.getScenesPath() + "sample_pbr_e4.dds")
						noeMat.uMaterial = materialObject
						noeMaterials.append(noeMat)

	#transfer all loaded textures into the noesis list
	asset.transferTextures(noeTextures)
	for depAsset in loadedDeps.values():
		depAsset.transferTextures(noeTextures)

	mdlMats = NoeModelMaterials(noeTextures, noeMaterials) if len(noeTextures) > 0 or len(noeMaterials) > 0 else None
	
	normalDataType = noesis.RPGEODATA_BYTE if asset.serialVersion >= UE4_SERIALVER_420 else noesis.RPGEODATA_UBYTE
	normalDataTypeHigh = noesis.RPGEODATA_SHORT if asset.serialVersion >= UE4_SERIALVER_420 else noesis.RPGEODATA_USHORT
		
	for meshIndex in range(0, len(asset.meshes)):
		ctx = rapi.rpgCreateContext()
		rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
		#possible todo - if asset is big-endian, set rpg mode, since we keep all rendering data in the native endian.
		#however, don't have any UE4 big-endian data to test with.

		mesh = asset.meshes[meshIndex]
		if len(mesh.lods) == 0:
			continue
		lod = mesh.lods[0] #for now, just always pick the first lod.
		
		if mesh.exportEntry:
			rapi.rpgSetName(mesh.getName())

		if lod.vertSkinnable: #skeletal mesh path
			ilv = lod.vertSkinnable
			rapi.rpgBindPositionBufferOfs(ilv.data, noesis.RPGEODATA_FLOAT, ilv.stride, ilv.posOffset)
			rapi.rpgBindTangentBufferOfs(ilv.data, normalDataType, ilv.stride, ilv.normTanOffset)
			rapi.rpgBindNormalBufferOfs(ilv.data, normalDataType, ilv.stride, ilv.normTanOffset + 4)
			if ilv.uvSetCount > 0:
				uvFormat = noesis.RPGEODATA_FLOAT if ilv.fullPrecisionUV else noesis.RPGEODATA_HALFFLOAT
				rapi.rpgBindUV1BufferOfs(ilv.data, uvFormat, ilv.stride, ilv.uvsOffset)
				if ilv.uvSetCount > 1:
					rapi.rpgBindUV2BufferOfs(ilv.data, uvFormat, ilv.stride, ilv.uvsOffset + ilv.uvSetSize)
			if ilv.weightsOffset >= 0:
				rapi.rpgBindBoneIndexBufferOfs(ilv.data, noesis.RPGEODATA_UBYTE, ilv.stride, ilv.weightsOffset, ilv.weightsPerVert)
				rapi.rpgBindBoneWeightBufferOfs(ilv.data, noesis.RPGEODATA_UBYTE, ilv.stride, ilv.weightsOffset + ilv.weightsPerVert, ilv.weightsPerVert)
			else:
				skinWeights = noeSafeGet(lod, "vertSkinWeights")
				if skinWeights and skinWeights.vertCount == lod.vertCount:
					rapi.rpgBindBoneIndexBufferOfs(skinWeights.data, noesis.RPGEODATA_UBYTE, skinWeights.stride, 0, skinWeights.weightsPerVert)
					rapi.rpgBindBoneWeightBufferOfs(skinWeights.data, noesis.RPGEODATA_UBYTE, skinWeights.stride, skinWeights.weightsPerVert, skinWeights.weightsPerVert)			
		else: #static mesh path (as well as skinned with newer/unified renderdata)
			pos = noeSafeGet(lod, "vertPositions")
			if pos is None:
				continue
			rapi.rpgBindPositionBufferOfs(pos.data, noesis.RPGEODATA_FLOAT, pos.stride, 0)
			ilv = lod.vertInterleaved
			if ilv.vertCount == pos.count:
				normTanFormat = normalDataTypeHigh if ilv.fullPrecisionTangent else normalDataType
				normalOffset = 8 if ilv.fullPrecisionTangent else 4
				rapi.rpgBindTangentBufferOfs(ilv.interleavedData, normTanFormat, ilv.stride, ilv.normTanOffset)
				rapi.rpgBindNormalBufferOfs(ilv.interleavedData, normTanFormat, ilv.stride, ilv.normTanOffset + normalOffset)
				if ilv.uvSetCount > 0:
					uvFormat = noesis.RPGEODATA_FLOAT if ilv.fullPrecisionUV else noesis.RPGEODATA_HALFFLOAT
					rapi.rpgBindUV1BufferOfs(ilv.interleavedData, uvFormat, ilv.stride, ilv.uvsOffset)
					if ilv.uvSetCount > 1:
						rapi.rpgBindUV2BufferOfs(ilv.interleavedData, uvFormat, ilv.stride, ilv.uvsOffset + ilv.uvSetSize)
			#static mesh and skeletal mesh datasets are unified in 4.19+, so check to see if this thing has weights too
			skinWeights = noeSafeGet(lod, "vertSkinWeights")
			if skinWeights and skinWeights.vertCount == pos.count:
				rapi.rpgBindBoneIndexBufferOfs(skinWeights.data, noesis.RPGEODATA_UBYTE, skinWeights.stride, 0, skinWeights.weightsPerVert)
				rapi.rpgBindBoneWeightBufferOfs(skinWeights.data, noesis.RPGEODATA_UBYTE, skinWeights.stride, skinWeights.weightsPerVert, skinWeights.weightsPerVert)
			
		indexType = noesis.RPGEODATA_USHORT if lod.indices.indexSize == 2 else noesis.RPGEODATA_INT
		
		if len(lod.sections) > 0:
			for sectionIndex in range(0, len(lod.sections)):
				section = lod.sections[sectionIndex]
			
				if len(lod.chunks) == len(lod.sections): #if chunks are still around, pull the bonemap out of the corresponding chunk
					boneMap = lod.chunks[sectionIndex].boneMap
				else: #otherwise assume it's part of the section data
					boneMap = noeSafeGet(section, "boneMap")
			
				if boneMap:
					translatedBoneMap = []
					for boneMapData in boneMap:
						translatedBoneMap.append(int(boneMapData.data))
					rapi.rpgSetBoneMap(translatedBoneMap)
			
				if section.materialIndex >= 0 and section.materialIndex < len(mesh.materials) and not noesis.optWasInvoked("-ue4defaultmtl"):
					materialName = mesh.materials[section.materialIndex].materialName
				else:
					materialName = "ue4_material_%03i"%section.materialIndex
					
				if not noesis.optWasInvoked("-ue4nosecname"):
					if mesh.exportEntry:
						rapi.rpgSetName(mesh.getName() + "_section%03i"%sectionIndex)
					else:
						rapi.rpgSetName("mesh%03i_section%03i"%(meshIndex, sectionIndex))
					
				rapi.rpgSetMaterial(materialName)
				rapi.rpgCommitTriangles(lod.indices.data[section.firstIndex * lod.indices.indexSize:], indexType, section.triangleCount * 3, noesis.RPGEO_TRIANGLE, 1)
				rapi.rpgSetBoneMap(None)
		else:
			rapi.rpgCommitTriangles(lod.indices.data, indexType, lod.indices.indexCount, noesis.RPGEO_TRIANGLE, 1)
		
		rapi.rpgClearBufferBinds()
		
		mdl = rapi.rpgConstructModel()
		if mdl:
			if mesh.refSkeleton:
				#convert the bones for this skeleton
				noeBones = mesh.refSkeleton.generateNoesisBones(None, True)
				mdl.setBones(noeBones)
			mdlList.append(mdl)

	if mdlMats:
		#if no model exists, create a container for the texture(s)
		if len(mdlList) == 0:
			mdlList.append(NoeModel())
		#associate shared textures + materials with all models
		for mdl in mdlList:
			mdl.setModelMaterials(mdlMats)
		
	if len(mdlList) != 0:
		rapi.setPreviewOption("setAngOfs", "0 90 0")
		rapi.setPreviewOption("autoLoadNonDiffuse", "1")
	else:
		print("Found nothing of interest in the package.")
		
	return 1
		

#=================================================================
# Archive handling
#=================================================================
		
class UE4ArcEntry:
	def __init__(self, name, offset, compSize, decompSize, compType, encrypted, chunkList, chunkSize, entryOffset, entrySize):
		self.name = name
		self.offset = offset
		self.compSize = compSize
		self.decompSize = decompSize
		self.compType = compType
		self.encrypted = encrypted
		self.chunkList = chunkList
		self.chunkSize = chunkSize
		self.entryOffset = entryOffset
		self.entrySize = entrySize
		
def ue4DecryptData(data, key):
	if key is None or len(data) == 0:
		return data
	data = rapi.decryptAES(data, key)
	return data
	
def getDecryptionKey():
	decryptKey = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Enter Key", "Some entries in this archive are encrypted. Please enter a decryption key.", "", None)
	if decryptKey is None:
		print("Warning: No key provided. Proceeding to extract data without decryption. Results may be invalid.")
	else:
		if decryptKey.startswith("noesis_hexkey:"):
			decryptKey = bytearray.fromhex(decryptKey[14:])
		else:
			decryptKey = noePaddedByteArray(bytearray(decryptKey, "ASCII"), 32)
	return decryptKey
		
#see if the file in question is a valid pak file
def ue4ExtractArc(fileName, fileLen, justChecking):
	if fileLen <= 44:
		return 0
	with open(fileName, "rb") as f:
		try:
			f.seek(fileLen - 44, os.SEEK_SET)
			endian = "<"
			id = noeUnpack(endian + "I", f.read(4))[0]
			if id == 0xE1126F5A:
				endian = ">"
			elif id != 0x5A6F12E1:
				return 0
				
			ver, entriesOffset, entriesSize = noeUnpack(endian + "IQI", f.read(4 + 8 + 4))
			if ver < 3 or entriesOffset <= 0 or entriesSize <= 0:
				return 0
		except:
			return 0

		if justChecking: #it's valid
			return 1
		
		f.seek(entriesOffset, os.SEEK_SET)
		entriesData = f.read(entriesSize)
		decryptKey = None
		if ver >= 3: #decrypt the file entries if necessary
			f.seek(fileLen - 45, os.SEEK_SET)
			entriesEncrypted = f.read(1)[0]
			if entriesEncrypted > 0:
				decryptKey = getDecryptionKey()
				if decryptKey:
					entriesData = ue4DecryptData(entriesData, decryptKey)

		bs = NoeBitStream(entriesData)
		if endian == ">":
			bs.setEndian(NOE_BIGENDIAN)

		basePath = ue4StreamReadString(bs)
		entryCount = bs.readUInt()
		
		print("Extracting", entryCount, "files.")
				
		anyEncryption = False
		entries = []
		for entryIndex in range(0, entryCount):
			name = ue4StreamReadString(bs)
			entryOffset = bs.tell()
			offset, compSize, decompSize, compType = noeUnpack(endian + "QQQI", bs.readBytes(8 + 8 + 8 + 4))
			bs.seek(20, NOESEEK_REL) #unused
			chunkList = []
			if compType != 0:
				chunkCount = bs.readUInt()
				for chunkIndex in range(0, chunkCount):
					chunkOffset, nextChunkOffset = noeUnpack(endian + "QQ", bs.readBytes(8 + 8))
					if ver >= 5:
						#apparently changed to be relative to the entry offset, despite already being 64-bit offsets.
						#that should really come in handy for pak files that include the entirety of human knowledge. with shitty zlib compression, of course.
						chunkOffset += offset
						nextChunkOffset += offset
					chunkList.append((chunkOffset, nextChunkOffset))
			encrypted, chunkSize = noeUnpack(endian + "BI", bs.readBytes(1 + 4))
			entrySize = bs.tell() - entryOffset
			encrypted &= 1 #this was turned into flags where 1 == encrypted and 2 == deleted. & 1 still works for backward-compatible encyrption flag test. currently don't care about deleted records.
			if encrypted > 0:
				anyEncryption = True
			entries.append(UE4ArcEntry(name, offset, compSize, decompSize, compType, encrypted, chunkList, chunkSize, entryOffset, entrySize))
	
		if anyEncryption:
			if not decryptKey:
				decryptKey = getDecryptionKey()
	
		for entry in entries:
			print("Writing", entry.name)
			if len(entry.chunkList) > 0:
				data = bytearray()
				for chunkOffset, nextChunkOffset in entry.chunkList:
					f.seek(chunkOffset, os.SEEK_SET)
					chunkReadSize = nextChunkOffset - chunkOffset
					if entry.encrypted > 0: #needs to be padded out to aes block size
						chunkReadSize = (chunkReadSize + 15) & ~15
						
					chunkData = f.read(chunkReadSize)
					if entry.encrypted > 0:
						chunkData = ue4DecryptData(chunkData, decryptKey)
					if entry.compType > 0:
						chunkData = rapi.decompInflate(chunkData, entry.chunkSize)
					data += chunkData
			else:
				f.seek(entry.offset + entry.entrySize, os.SEEK_SET)
				readSize = entry.compSize
				if entry.encrypted > 0: #needs to be padded out to aes block size
					readSize = (readSize + 15) & ~15
				
				data = f.read(readSize)
				if entry.encrypted > 0:
					data = ue4DecryptData(data, decryptKey)
				if entry.compType > 0:
					data = rapi.decompInflate(fileData, entry.decompSize)

			if len(data) > entry.decompSize:
				#encryption or compression might've resulted in padding off the end, so be lazy and just truncate at the end before writing.
				data = data[:entry.decompSize]
			rapi.exportArchiveFile(entry.name, data)
			
	return 1


#=================================================================
# Tools
#=================================================================

def ue4FindExportsMatchingExport(asset, otherAsset, otherExport):
	exports = []
	otherExportClassName = otherAsset.getImportExportName(otherExport.classIndex)
	otherExportSuperName = otherAsset.getImportExportName(otherExport.superIndex)
	for export in asset.exports:
		exportClassName = asset.getImportExportName(export.classIndex)
		exportSuperName = asset.getImportExportName(export.superIndex)
		if otherExportClassName == exportClassName and otherExport.objectName.data == export.objectName.data and otherExportSuperName == exportSuperName and otherExport.packageIndex == export.packageIndex and otherExport.objectFlags == export.objectFlags and otherExport.packageFlags == export.packageFlags:
			exports.append(export)
	return exports
	
def ue4ListExportProps(asset, baseExport, listName):
	asset.bs.seek(baseExport.serialOffset, NOESEEK_ABS)
	baseObj = UE4Object(asset)
	baseObj.load(baseExport)
	for prop in baseObj.propTags.values():
		readProp = prop.readProperty()
		print(" " + listName + " prop:", prop.name, readProp)

def ue4CompareExports(baseExport, diffExports, asset, diffAsset, reportDiffs):
	foundMatch = False
	baseClassName = asset.getImportExportName(baseExport.classIndex)
	for diffExport in diffExports:
		if baseExport.serialSize != diffExport.serialSize:
			if reportDiffs:
				print("Export size mismatch:", baseClassName, "-", baseExport.objectName, "-", baseExport.serialSize, "vs", diffExport.serialSize)
			continue
		else:
			baseBs = asset.bs
			diffBs = diffAsset.bs
			baseBs.seek(baseExport.serialOffset, NOESEEK_ABS)
			diffBs.seek(diffExport.serialOffset, NOESEEK_ABS)
			baseData = baseBs.readBytes(baseExport.serialSize)
			diffData = diffBs.readBytes(diffExport.serialSize)
			mismatchOffsets = []
			for offset in range(0, baseExport.serialSize):
				if baseData[offset] != diffData[offset]:
					mismatchOffsets.append(offset)
			if len(mismatchOffsets) > 0:
				if reportDiffs:
					print("Export data mismatch:", baseClassName, "-", baseExport.objectName, "-", mismatchOffsets)
				continue
			else:
				foundMatch = True
				break

	if not foundMatch and reportDiffs:
		try:
			ue4ListExportProps(asset, baseExport, "base")
		except:
			print(" Error serializing base as uobject.")
			
		for diffExport in diffExports:
			try:
				ue4ListExportProps(diffAsset, diffExport, "diff")
			except:
				print(" Error serializing diff as uobject.")
	
	return foundMatch
	
def ue4PackageContextVisible(toolIndex, selectedFile):
	if selectedFile is None:
		return 0
	fileExt = os.path.splitext(selectedFile)[1].lower()
	if fileExt != ".uasset" and fileExt != ".umap":
		return 0
	return 1
	
def ue4VersionButtonOk(noeWnd, controlId, wParam, lParam):
	global ue4VersionToolOptions
	ue4VersionToolOptions.setFromToolWindow(noeWnd)
	noeWnd.closeWindow()
	return True

def ue4VersionButtonReset(noeWnd, controlId, wParam, lParam):
	verList = noeWnd.getControlByIndex(noeWnd.verListIndex)
	hackList = noeWnd.getControlByIndex(noeWnd.hackListIndex)
	verList.selectString("Default")
	hackList.selectString("None")
	return True

def ue4VersionTupleCompare(a, b):
	return a[1] - b[1]

def ue4VersionToolInternal(suggestedSerialVersion, suggestedGameHack):
	noeWnd = noewin.NoeUserWindow("UE4 Version Tool", "UE4VTWindowClass", 644, 300)
	#offset a bit into the noesis window
	noeWindowRect = noewin.getNoesisWindowRect()
	if noeWindowRect:
		windowMargin = 64
		noeWnd.x = noeWindowRect[0] + windowMargin
		noeWnd.y = noeWindowRect[1] + windowMargin
	if noeWnd.createWindow():
		noeWnd.setFont("Arial", 14)
		
		noeWnd.createStatic("Version", 16, 16, 80, 20)
		listIndex = noeWnd.createListBox(16, 36, 500, 140, None, 0)
		noeWnd.verListIndex = listIndex

		noeWnd.createStatic("Game Hack", 16, 192, 80, 20)
		listIndex = noeWnd.createListBox(16, 212, 500, 40, None, 0)
		noeWnd.hackListIndex = listIndex
		
		globalVars = globals()
		verList = noeWnd.getControlByIndex(noeWnd.verListIndex)
		hackList = noeWnd.getControlByIndex(noeWnd.hackListIndex)
		
		noeWnd.createButton("OK", 528, 16, 96, 32, ue4VersionButtonOk)
		noeWnd.createButton("Reset", 528, 52, 96, 32, ue4VersionButtonReset)

		selectedVer = None
		selectedHack = None
		noeWnd.ue4Versions = []
		noeWnd.ue4Versions.append(("Default", -1))
		noeWnd.ue4Hacks = []
		noeWnd.ue4Hacks.append(("None", -1))
		
		selectedSerialVersion = ue4VersionToolOptions.version if ue4VersionToolOptions.version >= 0 else suggestedSerialVersion
		selectedGameHack = ue4VersionToolOptions.gameHack if ue4VersionToolOptions.gameHack >= 0 else suggestedGameHack
		
		for ue4Var in globalVars.keys():
			if ue4Var.startswith("UE4_SERIALVER_"):
				noeWnd.ue4Versions.append((ue4Var, globalVars[ue4Var]))
				if selectedSerialVersion >= 0 and globalVars[ue4Var] == selectedSerialVersion:
					selectedVer = ue4Var					
			elif ue4Var.startswith("UE4_GAMEHACK_") and ue4Var != "UE4_GAMEHACK_NONE":
				noeWnd.ue4Hacks.append((ue4Var, globalVars[ue4Var]))
				if selectedGameHack >= 0 and globalVars[ue4Var] == selectedGameHack:
					selectedHack = ue4Var				

		noeWnd.ue4Versions = sorted(noeWnd.ue4Versions, key=noeCmpToKey(ue4VersionTupleCompare))
		noeWnd.ue4Hacks = sorted(noeWnd.ue4Hacks, key=noeCmpToKey(ue4VersionTupleCompare))
					
		for varName, varVal in noeWnd.ue4Versions:
			verList.addString(varName)
		for varName, varVal in noeWnd.ue4Hacks:
			hackList.addString(varName)
		
		ue4VersionButtonReset(noeWnd, 0, 0, 0)
		if selectedVer:
			verList.selectString(selectedVer)
		if selectedHack:
			hackList.selectString(selectedHack)
		
		noeWnd.doModal()

	return 0
	
def ue4VersionToolMethod(toolIndex):
	return ue4VersionToolInternal(-1, -1)

def ue4DiffToolMethod(toolIndex):
	srcPath = noesis.getSelectedFile()
	if srcPath is None or os.path.exists(srcPath) is not True:
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0

	splitName = os.path.splitext(srcPath)
	diffPath = splitName[0] + ".diff" + splitName[1]
	if not os.path.exists(diffPath):
		noesis.messagePrompt("Cannot find diff file.")
		return 0
				
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	noesis.logPopup()
	
	with open(srcPath, "rb") as fBase, open(diffPath, "rb") as fDiff:
		data = fBase.read()
		diffData = fDiff.read()

		matchCount = 0
		mismatchCount = 0
		asset = UE4Asset(NoeBitStream(data), srcPath, True)
		diffAsset = UE4Asset(NoeBitStream(diffData), diffPath, True)
		if asset.parse() == 0 and diffAsset.parse() == 0:
			asset.loadTables()
			diffAsset.loadTables()
			
			exportsMatch = True
			if len(asset.exports) != len(diffAsset.exports):
				print("Export count mismatch:", len(asset.exports), "vs", len(diffAsset.exports))
				exportsMatch = False
			else:
				for exportIndex in range(0, len(asset.exports)):
					baseExport = asset.exports[exportIndex]
					diffExport = diffAsset.exports[exportIndex]
					baseClassName = asset.getImportExportName(baseExport.classIndex)
					diffClassName = asset.getImportExportName(diffExport.classIndex)
					if baseClassName != diffClassName or baseExport.objectName.data != diffExport.objectName.data:
						print("1:1 export mismatch at", exportIndex, "-", baseClassName, diffClassName, baseExport.objectName, diffExport.objectName)
						exportsMatch = False
				
			for exportIndex in range(0, len(asset.exports)):
				baseExport = asset.exports[exportIndex]
				baseClassName = asset.getImportExportName(baseExport.classIndex)
				diffExports = [diffAsset.exports[exportIndex]] if exportsMatch else ue4FindExportsMatchingExport(diffAsset, asset, baseExport)
				if len(diffExports) == 0:
					print("Missing export in diff:", baseClassName, "-", baseExport.objectName)
					mismatchCount += 1
				else:
					foundMatch = ue4CompareExports(baseExport, diffExports, asset, diffAsset, exportsMatch)
					if not foundMatch:
						print("  No matching export:", baseClassName, "-", baseExport.objectName)
						mismatchCount += 1
					else:
						matchCount += 1
					
			#now see if anything exists in the diff that doesn't exist in the base
			if not exportsMatch:
				for exportIndex in range(0, len(diffAsset.exports)):
					diffExport = diffAsset.exports[exportIndex]
					diffClassName = asset.getImportExportName(diffExport.classIndex)
					baseExports = [asset.exports[exportIndex]] if exportsMatch else ue4FindExportsMatchingExport(asset, diffAsset, diffExport)
					if len(baseExports) == 0:
						print("Missing export in base:", diffClassName, "-", diffExport.objectName)
						mismatchCount += 1
					else:
						foundMatch = ue4CompareExports(diffExport, baseExports, diffAsset, asset, exportsMatch)
						if not foundMatch:
							print("  No matching base export:", diffClassName, "-", diffExport.objectName)
							mismatchCount += 1
						else:
							matchCount += 1

		print("Matches:", matchCount, "Mismatches:", mismatchCount)
					
	noesis.freeModule(noeMod)
		
	return 0
	
def ue4PropToolMethod(toolIndex):
	srcPath = noesis.getSelectedFile()
	if srcPath is None or os.path.exists(srcPath) is not True:
		noesis.messagePrompt("Selected file isn't readable through the standard filesystem.")
		return 0
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	noesis.logPopup()
	
	print("Listing object properties for", srcPath)
	with open(srcPath, "rb") as f:
		data = f.read()
		asset = UE4Asset(NoeBitStream(data), srcPath, True)
		if asset.parse() == 0:
			asset.loadTables()
			for export in asset.exports:
				className = asset.getImportExportName(export.classIndex)
				print(export.objectName, "-", className)
				try:
					ue4ListExportProps(asset, export, "Object")
				except:
					print(" Error serializing export as uobject.")
			
	noesis.freeModule(noeMod)

	return 0

def ue4FilterPsnr(psnrValue):
	#arbitrarily cut off at 100 to avoid massive numbers in filenames
	return min(psnrValue, 100.0)

def ue4ValidateInputDirectory(inVal):
	if os.path.isdir(inVal) is not True:
		return "'" + inVal + "' is not a valid directory."
	return None

def ue4AstcToolMethod(toolIndex):
	noesis.logPopup()

	baseDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select a folder to scan.", noesis.getSelectedDirectory(), ue4ValidateInputDirectory)
	if baseDir is None:
		return 0
	
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	
	goodPsnrList = []
	minGoodPsnr = 40.0
		
	textureAssets = []
	print("Scanning for texture assets in:", baseDir)
	for root, dirs, files in os.walk(baseDir):
		for fileName in files:
			lowerName = fileName.lower()
			if lowerName.endswith(".uasset"):
				fullPath = os.path.join(root, fileName)
				with open(fullPath, "rb") as f:
					bs = NoeFileStream(f)
					asset = UE4Asset(bs, fullPath, False)
					if asset.parse() == 0:
						asset.loadTables()
						foundTexture = False
						for export in asset.exports:
							className = asset.getImportExportName(export.classIndex)
							if className == "Texture2D":
								#make sure it's not just a thumbnail
								if repr(export.objectName) != "ThumbnailTexture":
									foundTexture = True
									break
						#if we found a texture object in there, load the whole thing up
						if foundTexture:
							textureAssets.append(fullPath)

	print("Found", len(textureAssets), "assets containing texture objects.")
							
	for assetIndex in range(0, len(textureAssets)):
		fullPath = textureAssets[assetIndex]
		print("Loading asset (%i/%i):"%(assetIndex + 1, len(textureAssets)), fullPath)
		noesis.pumpModalStatus("(File %i/%i) Loading asset: "%(assetIndex + 1, len(textureAssets)) + fullPath, 3.0)
		with open(fullPath, "rb") as f:
			bs = NoeFileStream(f)
			asset = UE4Asset(bs, fullPath, False)
			if asset.parse() == 0:
				asset.loadTables()
				asset.loadAssetData()
				baseName = os.path.splitext(fullPath)[0]
				textureCount = 0
				for object in asset.serializedObjects:
					texture = noeSafeGet(object, "texture")
					if texture:
						rgba = rapi.imageGetTexRGBA(texture)
						texBaseName = baseName + "_noesisenc_%03i_"%textureCount

						rawTexName = texBaseName + "raw.png"
						noesis.saveImageRGBA(rawTexName, NoeTexture(rawTexName, texture.width, texture.height, rgba, noesis.NOESISTEX_RGBA32))
						
						#encode as dxt5 for reference (same quality as dxt1 either way, don't care about wasted alpha)
						encoded = rapi.imageEncodeDXT(rgba, 4, texture.width, texture.height, noesis.NOE_ENCODEDXT_BC3)
						encoded = rapi.imageDecodeDXT(encoded, texture.width, texture.height, noesis.FOURCC_DXT5)
						dxtPsnrColor, psnrAlpha = rapi.callExtensionMethod("calculate_psnr", rgba, encoded, texture.width, texture.height, 0)
						encTexName = texBaseName + "dxt5_%.02f_%.02f.png"%(ue4FilterPsnr(dxtPsnrColor), ue4FilterPsnr(psnrAlpha))
						noesis.saveImageRGBA(encTexName, NoeTexture(encTexName, texture.width, texture.height, encoded, noesis.NOESISTEX_RGBA32))
						
						goodPsnr = None
						blockSizes = (8, 10, 12)
						for blockSize in blockSizes:
							noesis.pumpModalStatus("(File %i/%i) Encoding ASTC with a block size of %ix%i..."%(assetIndex + 1, len(textureAssets), blockSize, blockSize), 3.0)
							encoded = rapi.callExtensionMethod("astc_encoderaw32", rgba, blockSize, blockSize, 1, texture.width, texture.height, 1, 2)
							encoded = rapi.callExtensionMethod("astc_decoderaw32", encoded, blockSize, blockSize, 1, texture.width, texture.height, 1)
							psnrColor, psnrAlpha = rapi.callExtensionMethod("calculate_psnr", rgba, encoded, texture.width, texture.height, 0)
							if blockSize > 8 and (psnrColor >= dxtPsnrColor or psnrColor >= minGoodPsnr):
								goodPsnr = psnrColor
							encTexName = texBaseName + "%ix%i_%.02f_%.02f.png"%(blockSize, blockSize, ue4FilterPsnr(psnrColor), ue4FilterPsnr(psnrAlpha))
							noesis.saveImageRGBA(encTexName, NoeTexture(encTexName, texture.width, texture.height, encoded, noesis.NOESISTEX_RGBA32))
						
						if goodPsnr:
							print("Good PSNR:", goodPsnr)
							goodPsnrList.append(rawTexName)
						
						textureCount += 1
			
	noesis.clearModalStatus()
	if len(goodPsnrList) > 0:
		print("Good texture list:", len(goodPsnrList))
		for fileName in goodPsnrList:
			print("  " + fileName)

	noesis.freeModule(noeMod)

	return 0

def ue4ObjFindToolMethod(toolIndex):
	noesis.logPopup()

	baseDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select a folder to scan.", noesis.getSelectedDirectory(), ue4ValidateInputDirectory)
	if baseDir is None:
		return 0

	objName = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Object Name", "Enter the name of the object to find.", "", None)
	if objName is None:
		return 0

	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)

	print("Scanning for", objName, " in:", baseDir)
	foundFiles = []
	checkCount = 0
	for root, dirs, files in os.walk(baseDir):
		for fileName in files:
			lowerName = fileName.lower()
			if lowerName.endswith(".uasset"):
				fullPath = os.path.join(root, fileName)
				with open(fullPath, "rb") as f:
					print("Checking:", fullPath)
					checkCount += 1
					bs = NoeFileStream(f)
					asset = UE4Asset(bs, fullPath, False)
					if asset.parse() == 0:
						asset.loadTables()
						for export in asset.exports:
							if repr(export.objectName) == objName:
								print("Found a match!")
								foundFiles.append(fullPath)

	if len(foundFiles) == 0:
		print("Checked", checkCount, "files, and found no matches.")
	else:
		print("Checked", checkCount, "files, and found matches in the following", len(foundFiles), "file(s):")
		for foundFile in foundFiles:
			print(" ", foundFile)

	noesis.freeModule(noeMod)
	return 0
