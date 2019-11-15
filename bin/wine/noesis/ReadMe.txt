This is Noesis version 4.406.
Written by Rich Whitehouse
Follow @DickWhitehouse on Twitter for news and various magical things.

Noesis converts and previews many data formats. You can get an idea of which ones by looking at the file type mask droplist on the face of the application.

A NOTE ABOUT PLUGINS:
Noesis plugins run as native binary on your machine. This means that they can contain harmful and malicious code! Before you place any DLL file in your Noesis\Plugins folder, make sure you know who the author of the DLL is, and that you trust them completely!

A NOTE ABOUT BEING A DECENT HUMAN BEING:
Don't distribute content that you don't own unless you have explicit permission from the content owner(s). Adhere to proper attribution.

RUNTIME SUPPORT:
Some components and plugins for Noesis may require MSVC++ 2010 runtimes to be installed. These runtimes can currently be downloaded from:

https://www.microsoft.com/en-us/download/details.aspx?id=5555

Older native binary plugins, which will still function with current versions of Noesis, may require 2005 runtimes. 2005 runtimes can currently be downloaded here:

https://www.microsoft.com/en-us/download/details.aspx?id=3387

USAGE:
For basic usage and information, see "Basic Controls" and the subsequent sections, located near the bottom of this document.

TROUBLESHOOTING:
See the "Trouble!" section near the bottom of this document.

==========
What's New
==========
Version 4.406:
 - New inc_imgtools Python module, contains implementations to assist in mounting/reading various image types. Additional filesystem support will probably be coming in the near future.
 - New scripts to extract files from .cue and .gdi images are provided under optionalplugins - fmt_cue.py and fmt_gdi.py.
 - New tile renderers for Game Boy, NES, and SNES.
 - Support for an arbitrary number of UV channels in the rpg interface. The preview renderer only uses UV0/UV1, but additional channels can be viewed in the data viewer and are passed through to exporters. I've only updated the FBX (2019) and glTF exporters to support additional channels.
 - UV scale/bias function now takes an optional parameter to affect a specific UV channel.
 - Bumped NOESIS_PLUGINAPI_VERSION again.

Version 4.405:
 - Merged FBX updates from the dev branch. Now on FBX SDK 2019.2. Old 2017.1 plugin is now located in optionalplugins as "autodesk_fbx_2017.dll".
 - FBX module saves/loads occlusion texture properties on materials.
 - FBX module has changed -fbxtexabs to -fbxtexrel, as using non-relative texture paths is now the default. (because the latest FBX SDK does horrific things when providing relative paths)
 - FBX now supports UV set association on materials to preserve _UV1 flags.
 - Fixed a problem introduced with the last FBX SDK upgrade which was breaking non-orthogonal transforms.
 - FBX module has changed -fbxmanualprop to -fbxoldprop, with a new property iteration method to work around Yet Another FBX SDK Bug which can result in material properties not being correctly picked up with older FBX files.

Version 4.404:
 - More minor bug fixes, and exposed material "flags 2" property in data viewer.

Version 4.403:
 - Finally updated NOESIS_PLUGINAPI_VERSION, since some third party plugins are depending on fixes from recent versions.
 - Occlusion maps are now used on the non-PBR path, when "render occlusion maps" option is enabled.
 - Various NIF updates. (mostly related to materials) A new -niflmindex option has also been added to specify a lightmap texture index, as some >= 20.6 files in the wild are in contradiction. -niflmindex 2 will work for most cases.

Version 4.402:
 - Fixed a bug in 1dthin tiling, which was affecting the GNF loader.
 - Fixed a shader typo which broke the _UV1 flags on the non-PBR preview rendering path.
 - Support for loading NiSortAdjustNode and NiBillboardNode in the NIF script. (just passes straight through to the NiNode loader)
 - Added some more built-in VDP palette options.
 - Included newer version of DickTools in optionalplugins.
 - The "duplicate bone names" case now just adds prefix strings instead of stomping bone names altogether.
 - Still just bug-fixing out of the release branch, sorry guy who's been overly hostile in demanding x64 builds!

Version 4.401:
 - Added NMSHAREDFL_MULTIMATS and a couple of other shared model flags, for exporters to use in targeting formats with multi-material mesh support.
 - Added -fbxmeshmerge, which combines meshes (usually generating multi-material meshes) based on source name. Will still combine meshes with mismatched vertex components if source names match, so use with caution.
 - Removed -fbxnewexport, added -fbxoldexport. You'll need to explicitly use -fbxoldexport if you still want to export FBX files that are compatible with software from 2009.
 - Fixed an old bug with -fbxcollapsecp which could occur when collapsing control points for weighted models.

Version 4.4:
 - Generic 8x8 system font rendering exposed to Python.
 - VDP rendering interface exposed to Python.
 - Added various color ramp options to VDP renderer.
 - Added RPGOPT_SANITIZEWEIGHTS.
 - Exposed RPGOPT_SWAPHANDEDNESS and RPGOPT_SANITIZEWEIGHTS to the commandline.
 - Various bug fixes.

Version 4.399:
 - Quake II PSX character and map model support.
 - Quake II PSX prototype editor model support.
 - Fixed the same textures being exported repeatedly when multiple models reference the same shared material and texture data.
 - Fixed SMD importer referencing node 0 for nodes with no transforms.

Version 4.398:
 - More bug fixes.
 - Removed old png transparency masking options and replaced with -paltransindex and -paltranscolor. These work for all formats which export using the generic paletted data interface.

Version 4.397:
 - Several minor bug fixes.

Version 4.396:
 - Added support for importing Sega Digitizer System III files. (this is a quick build out of the release branch mainly for this purpose, sorry if you've been waiting on other in-development features!)
 - Added support for 16bpp to the TGA loader.
 - Support for exporting to DeluxePaint Animation format.
 - Support for carrying palette data across import/export for some image formats. Added -pngpal to prefer exporting to paletted png files.
 - Fixed a bug where the optional fat12 script could hang due to FAT entries not ending on an aligned byte.

Version 4.395:
 - UE4 Block Linear GoB (-ue4texgob) untiling now uses a max block height of 16 for uncompressed textures, in certain situations. Only tested on Octopath Traveler.
 - Added a -ue4texalign option, to specify per-platform alignment. Will vary for different platforms, formats, and tiling modes.
 - UE4 script now prompts the user to specify a version by default, because the default version is usually wrong.
 - Hacked apart MFC shell views to allow SHOWSELALWAYS flags. This is the new default - there's an option in the data viewer to revert to old behavior.

Version 4.394:
 - Added a glTF export option, -gltfmeshgroup, to re-group meshes on export. The new default setting is 1, which re-groups by source name to take advantage of the new property added in 4.392.
 - More random bug fixes.

Version 4.393:
 - The FF15 animation importer now supports scale. Additionally, it no longer requires user distinction between motion types (-ff15rootmo has been removed), and attempts to do the right thing automatically. However, a couple of options are still required for certain clips. -ff15addanim should be used for additive animations, and -ff15trnonsphere should be used to confine translations to a sphere.
 - A couple of minor FF15 material additions.

Version 4.392:
 - Added "rpgSetSourceName" and accompanying data structures. Ties a mesh to a given source name, so that exporters can choose to re-group meshes using this identifier.
 - More random bug fixes.

Version 4.391:
 - Added explicit material support for occlusion maps, rather than relying on passthroughs. Additonally, there's an option under the data viewer to enable occlusion in the preview render. ("Render occlusion")
 - Lots of other less notable material options/changes, see the headers for more information.
 - Added a new option to convert both material-based lightmaps and legacy importer (e.g. Quake, Quake 3) lightmaps to multi-pass materials. Note that this option generates new materials for each unique surface-material-lightmap combination, which can cause performance issues for engines which do not efficiently re-batch.
 - The glTF exporter now grabs multi-pass material lightmaps and assigns them as occlusion maps, with a Noesis-specific material extension to specify that the occlusion map was originally a lightmap. (this typically means it will look more correct to apply directly to diffuse rather than using purely to mask irradiance contribution)
 - Added limited support for parsing FF15 materials, which can be enabled via -ff15materials. -ff15occlmap may also be used in conjunction with this option.
 - Fixed another bug in the FF15 animation importer, pertaining to the few files which had channel runs exceeding 256.
 - Added two new options for DICOM: -dicomapplywindow and -dicomsetwindow. The former applies the window provided in the file, if any. The latter applies a custom window.
 - Added a new plugin extension method, getDicomSeriesInDirectory. This hands back a list of DICOM files in a given directory, along with relevant transform data for each. A script demonstrating its use has been included in optionalplugins, tool_dicomseries.py.
 - Added support for recognizing more DICOM properties in implicit VR files.
 - Fixed a typo in the RichVecH3 implementation, which was breaking normalization.
 - New native plugin interface function to get a list of files in a given directory.

Version 4.39:
 - Added glTF import (1.0 and 2.0) and export (2.0) support.
 - There's a new optional Model Server script, tool_modelserver.py. Once again, see my web site for information on what this is and how to use it.
 - Added some new material and texture flags, and exposed them to Python.
 - Materials without normal/spec/etc. maps can now elect to take the various shading paths that previously required those maps.
 - Added Noesis_GetPreviewAngleTransform. This transform can optionally be applied on export, and is saved in a custom extension when targeting glTF so that the inverse can be applied if/when desired.
 - Fixed a bug that was causing the material energy conservation flag to do terrible things.
 - Fixed some console-only run options hanging onto the system mutex handle and preventing GUI instances from running in parallel without ?multinstance.

Version 4.382:
 - Another couple of fixes/additions to the UE4 script, including Block Linear GOB support.

Version 4.381:
 - Fixed a bug in the FF15 animation loader which was sometimes causing translation scale/bias to be applied incorrectly.

Version 4.38:
 - Various bug fixes, chipping away at various new under-the-hood features.

Version 4.37:
 - Went back and rewrote the Sub-Culture DFF loader, giving it a new home in noesis_misc. Now handles materials correctly, and thanks to Steve, supports BSP files. There's also a new option to generate bones from transforms, for the clumps which make use of them.
 - Some UE4 script updates.

Version 4.36:
 - Minor DOOMBA additions. There are now options to place exit switches instead of exit sectors, and place teleporters when islands are detected. This allows you to merge Roomba runs from completely different locations into the same map.

Version 4.35:
 - New Roomba script in optionalplugins: tools_roomba.py. Contains a Roomba tracker and DOOMBA, which is a tool to turn your Roomba tracking data into a DOOM map. Check my web site for an article on what this is and how to use it.
 - Python's ssl module is now implemented.
 - Added some Sub-Culture DFF loader fixes (and added -dff1trans to apply transforms where applicable), although the importer is still in need of an overhaul and proper material support.

Version 4.34:
 - Another minor bugfix update. Anim-only SMD files now convey more bone data to the exporter, and fixed a bug on the "pure anim export" path that's employed when bone data isn't available.

Version 4.33:
Special update!
 - Various JPEG-2000 loader additions, including an option to preserve HDR data.
 - Added a GeometryScale option for .noevmarch files.
 - Added Noesis_FeedOptions and Noesis_LoadTexByHandlerMulti to the native plugin API.
 - Added "DickTools - TxV Dump", which appears under the right-click context menu for .exe files when using the DickTools plugin.
My wife had some dental scans done, and they gave us the data in the form of an awful Treatment Studio Viewer ("TxSTUDIOVIEWER") executable. This software is used in association with i-CAT devices, and it's horrible. The software silently refuses to run under a wide range of OS configurations. Even worse, though, the TxSTUDIOVIEWER executable with embedded resources is generated by the client software that sits on a random Windows machine, and represents a massive security hole due to the way most practioners seem to be managing said machine/software. So I reverse-engineered the resource data and added a feature to DickTools which dumps image data from the executable container. This means you can retrieve your data in raw(ish) form, and you never have to run the awful viewer software. Noesis can view the resulting slices, and you can construct a .dcmvolset file to generate mesh data from the slices. An example .dcmvolset file that worked well with my wife's data:
	NOE_DICOM_VOLUME_SET_VER	"1"
	marchConfig			"WR_20180925.noevmarch"
	mipDown				"2" #adjust accordingly based on how much resolution and geometric complexity you want in the final mesh
	showProgress			"1" #optional, just provides message pumps to inform you of loading progress
	setAngleOffset			"0" "270" "0" #depends on coordinate system used in scan
	loadOptions			"-j2kbias 1000 -j2knoshift -j2kchansplit -j2khdr -j2kchanskip 2" #slices are stored in single images across channels
Followed by dicomData entries pointing to each slice in .j2k format. You can find an example .noevmarch file in scenes/dicom, but the IsoLevel should probably be something like 0.002 given the range of densities present in this scan data.

Version 4.31 & 4.32:
 - Minor bug fixes.

Version 4.3:
 - Added basic FF15 animation support. Requires all assets to be extracted from .earc files in their original structure, in order to successfully locate asset dependencies. The batch extraction feature can help you with this, by allowing you to extract all .earc files to a central path. Animation data is supported for Windows and PS4. Xbox One probably works too, but hasn't been tested. If you bug me with questions about this, there's a 99.8% chance you'll be ignored.
 - Added support for FF15 Windows edition textures and archives. (models, skeletons, etc. are already identical to PS4)
 - UE4 animations are now supported. Use -ue4anims, and -ue4datapath to make sure all dependencies (e.g. skeleton) are available. -ue4animref can also be used to map animations to a given skeletal mesh's skeleton. (useful for games like SF5 where the common skeleton is massive)
 - UE4 script now has support all the way up through 4.20.
 - Various new UE4 tools. To enable them, set UE4_ENABLE_TOOLS to True in fmt_ue4.py. This includes a version picker interface which persists between runs and plugin reloads. There are also some diagnostic tools specifically for UE4 development, which were used to diagnose some cooking issues on a major UE4 title.
 - Added ASTC support to the UE4 script, as well as support for secondary bulk data.
 - Added support for source art data to the UE4 script. (editor-only packages generally aren't supported, but this path was required specifically for the ASTC PSNR tool)
 - Added support for compressed bulk data to the UE4 script.
 - Added the ability to specify a full device path to the image ripper interface.
 - New optional Python script to mount/extract NTFS images.
 - New optional Python script to extract PS2 Aligned Partition Allocation images.
 - Added support for Build v8/v9 maps.
 - New optional Python script to extract character frames from MK/MK2/UMK3 ROM images.
 - Added a modal status pump function, available from Python. This displays the provided status to the user and pumps an update - can be useful to avoid locking the application during long operations.
 - Exposed a new function to Python to get the absolute path of an archive-export file. Allows archive scripts to perform their own file handling.
 - The ASTC encoder is now exposed to Python.
 - Exposed getArbitraryFloat/encodeArbitraryFloat to Python.
 - Added FAT32 with LFN support to the FAT script. (previously only supported FAT12/16)
 - Added FAT32 option to detect non-contiguous files. (for diagnostics, used to debug an issue with an EverDrive)
 - Added "write SRAM" option to F2A script.
 - Python imageDecodeRaw/imageEncodeRaw functions now use the underlying engine versions, which adds support for some extra string formatting. (including half-float support)
Top items from the current todo list:
 - Refine FF15 animation implementation. I've documented 3 additional channel types, as well as 3 additional data formats. However, I haven't bothered adding support for most of this to the implementation yet.
 - Wrap up x64 support and include x64 builds in the main distribution.
 - Go back and revisit support for games that I really half-assed by only spending a few hours, never bothering to look at animations and such. (this includes Death by Degrees, Bayonetta/Vanquish/etc., DMC4/RE5/etc., Crisis Core, The Bouncer, Bullet Witch, and a few others)
 - Nicer support for physics/cloth simulation in preview, and for baking into exported animations. (also need to document/expose IK/physics interfaces for user plugins)
 - Go through the laundry list of other games I'd like to support.
With that said, I'm dropping Noesis for a while. I just had a baby, and unrelated to that, I'm set to have life-threatening surgery near the end of the year. If you never see another Noesis release, I probably ended up dead, so go to my web site and donate to my PayPal to help my fatherless family.

Version 4.297:
 - Provided an optional Python script which implements a basic Flash2Advance (GBA flash cart and linker cable) interface. See the accompanying text file for more info.
 - Exposed a new USB device interface to Python.
 - Basic support for Philips proprietary volume data in the DICOM loader, specifically to use on scans of my daughter! (she's due in June, baby gifts are welcome)
 - Support for non-DICOM images referenced by .dcmvolset files.
 - Haven't merged my development branch over to release, so various things (FF15 anim support, lots of bug fixes, various major overhauls) still aren't present in this release. I'll get it wrapped up one of these days. Maybe.

Version 4.296:
 - Added support for Chasm: The Rift models and maps. Use -chasmloadmodels to load maps up with all of the static models. Also note that CSM.BIN must be extracted with Noesis, in order to extract map resources with the naming conventions that Noesis expects. Thanks to Panzerscrek for many of the file specs that were used for this support - source code for the importer is also available on my web site.
 - Added native support for Build Engine v4, v5, and v6 map files. (previously only supported v7) Also added special handling for TekWar.
 - Support for MT .pak and .atlas files.
 - Support for alpha encoding when expanding paletted PNG files with transparency by index.

Version 4.295:
 - Added DNF animation import support.
 - Added an option to flip DNF materials into PBR mode.
 - Fixed a bug that could cause bad reads and crashes in the DNF importer.

Version 4.294:
 - Exposed Block Linear GOB tiling to Python via "untile_blocklineargob" and "tile_blocklineargob" extension methods. The last argument for each is optional, and is used as the block height. If the block height is negative, it's treated as mip0's log2(maxBlockHeight) and used to auto-calculate the block height. If the argument is not provided, block height is auto-calculated by auto-fitting with the assumption that the maximum block height is 16.
 - Fixed a bug in the TGA loader which was causing idLength to be ignored.

Version 4.293:
 - Implemented support for nVidia's Block Linear GoB tiling (used by the Tegra X1, among others), exposed through some new extension methods: Noesis_UntileBlockLinearGOBs, Noesis_TileBlockLinearGOBs, Noesis_TileCalculateBlockLinearGOBBlockHeight.
 - Basic BNTX import support. Loads everything other than PVRTC/ETC/EAC formats, as I haven't seen any of those in the wild.
 - Fixed a potential crash when attempting to enable bloom without the necessary hardware caps.

Version 4.292:
 - Added a "?compat_nomemmod" commandline option. This disables memory modules and generates DLL files on the temp path where dynamic code execution is used. I noticed a mysterious crash in a memory module's entrypoint function in a crash log. If Noesis crashes for you on startup, try this. But also scan your system for viruses - the person who had this crash had a trojan module in his process space!
 - Fixed a crash that could occur when attempting to export a model/animation with multiple childless roots to PSK/PSA.
 - Various documentation updates. It'd been a long time.

Version 4.291:
 - Fixed a bug in the MD3 exporter that was causing bad transforms to be applied to skeletally animated verts. The bug was introduced back in 4.205 or so. Thanks to Edison for reporting this!

Version 4.29:
 - Added import support for Sega Genesis/Mega Drive data exported by Virgin's Chopper tool.
 - Included a new optionalplugins script to dig Chopper data out of Sega Genesis/Mega Drive ROM images, and export it back into higher-level M68K table and tile formats.
 - Added DeluxePaint ILBM import and export support. Supports a wide variety of variations and types, including ACBM and HAM. Finding test data in all of these variants is a real pain, so if you have a file that works in another viewer and doesn't work in Noesis, send the file over and tell me which viewer it works in.
 - Added DeluxePaint Animation (MS-DOS) import support. Includes options to crop by single-pixel rectangle and adjust opaque palette ranges, for Chopper-friendliness.
 - Added a whitespace callback to the ancient generic parser exposed through the native API, to allow custom comments/delimiters.
 - Brought in a GIFLIB patch to address various GIF loading issues, and fixed a bug where some files would result in accumulating bad background values.
 - Exposed decompRNC (Robert Northen Compression) to Python. (this is based on some 8086 assembly, and has had limited testing)
 - Exposed compressHuffmanCanonical and decompHuffmanCanonical to Python. (this is my own implementation and encoding, and assumes 8-bit code words, so probably won't work out of the box with any given game)
 - Exposed an option to dictate the default preview texture animation playback rate in the data viewer.
 - Added a commandline option to crop from image origin.
 - Fixed a bug causing some ISO images to not be recognized. (legacy internal archive handler was doing bad things with the file position)
 - Numerous crash fixes.

Version 4.2 - 4.282:
 -4.282 - Exposed decompLZMA to Python.
 -4.281 - Reworked FBX cluster transform logic - use "-fbxlegacycluster" if you want old behavior.
 -4.281 - FBX importer now defaults to using relative texture filenames - use "-fbxtexabs" to use absolute paths.
 -4.281 - Added an option to disable vertex colors on FBX import - "-fbxnovcolor".
 -4.281 - Added an option in the data viewer to force preview texture filenames to apply only to relative path - "Only relative preview textures".
 -4.281 - Added persistent options for preview UV flip and model wireframe layer under the data viewer. These act identically to the existing per-model options, but apply globally and are maintained between loads.
 -4.28 - Default to "UV.v = -UV.v + 1.0" for FBX import/export instead of just "UV.v = -UV.v". Use -fbxnoflipuv to disable flipping behavior in the FBX module.
 -4.279 - Fixed geometry transform not being applied to static/unskinned geometry in the FBX importer. Thanks to Ken Miller for spotting this and providing test data so I could fix it!
 -4.278 - More UE4 changes.
 -4.277 - Small UE4 script adjustment.
 -4.276 - Tekken 7 material hack.
 -4.275 - Default preview commands are now applied to the common module on startup and plugin reload. This ensures arguments also also passed through to affect validation functions.
 -4.275 - Added "-ue4gamehack" in order to support games that don't conform to stock version serialization.
 -4.274 - Reverted default behavior change for Python exporters to use NMSHAREDFL_BONEPALETTE, which remaps per-vertex bone indices using the palette. Got complaints of old scripts breaking.
 -4.273 - Exposed a variety of DFT & DCT reference implementation functions to the native plugin API.
 -4.273 - Added "-msiahanimfilter" option, which acts as a prefix mask to attach any given animation(s) to a Messiah model.
 -4.273 - Added PLY2 import & export support. This is PLY2 as specified by Shin Yoshizawa, as opposed to one of the many revolting PLY derivatives floating around.
 -4.273 - Exposed rpgCalculateGenus to native API.
 -4.272 - Fixed "-msiahfrcact" always using "prost1", forgot to remove some debug code.
 -4.271 - Fix for Messiah texture export names.
 -4.27 - Added support for Messiah models and animations. See related commands "-msiahfrcact" and "-msiahtblack".
 -4.27 - Added checkbox support to the Python "noewin" module.
 -4.267 - New optional plugin script: fmt_atari_cad3d.py. Adds support for CAD-3D .3d (v1), .3d2 (v2), and .3da (animation, which goes by many extensions) files.
 -4.267 - New optional plugin script: tool_neopick.py. This is a custom GUI tool which is designed to re-align and trim NEOchrome images. Although it's unlikely anyone will ever have a use for this tool, it's a good template for a tool that uses a custom window proc.
 -4.267 - Exposed encoding and decoding methods for Motorola Fast Floating Point values to Python: noesis.getMFFP and noesis.encodeMFFP.
 -4.267 - New Python utility function: rpgCreatePlaneSpaceUVs. Auto-generates UV's for each triangle using the triangle plane.
 -4.267 - New Python utility function: rpgFlatNormals. Auto-generates flat normals using triangle planes.
 -4.267 - Added option to decode DXT blocks as signed to the DXT decoder parameter struct. Made this automatically happen for FourCC-DX10 BC4/BC5 SNORM files.
 -4.266 - Allow 0-length files to be written via the standard archive export calls.
 -4.266 - Added MSA support to fmt_atari_st.py.
 -4.266 - Various FAT12/FAT16 fixes.
 -4.266 - Various STX fixes.
 -4.266 - Added support for additional UV channels in FF15 importer.
 -4.265 - New optional plugin script: fmt_atari_st.py. Features NEOchrome .neo import + export, NEOchrome .ani import, and STX image conversion.
 -4.265 - New optional plugin script: fmt_fs_fat1216.py. Handles extraction of FAT12/FAT16 disk images.
 -4.265 - XDVDFS detection will now search from a base of 0, in addition to the usual suspects. (works for Xbox classic images)
 -4.264 - Fixed bitstream output not being written for non-deferred Python animation exporters. Thanks to chrrox for putting this path to the test.
 -4.263 - Fix for Python exception when trying to decrypt 0-length files in UE4 script.
 -4.262 - Various UE4 compatibility fixes.
 -4.261 - Fixed a couple of issues with preserving additional UV channels on FBX import/export.
 -4.261 - Allow the data viewer to show additional UV sets, even if those sets don't have any materials associated with them.
 -4.261 - Added "-fbxexportver" option to specify a particular version to write on FBX export. Since the FBX SDK seems to be broken when it comes to queerying valid strings, a few are: "FBX201300", "FBX201400", "FBX201600"
 -4.26 - Basic UE4 import support. Hasn't really been tested.
 -4.26 - Various bug/crash fixes.
 -4.251 - Exposed ASTC decoder to Python, added .astc file support via Python script.
 -4.251 - Added PSNR comparison features to the optional DickTools plugin.
 -4.251 - Fixed file size getting truncated to 32 bits for Python-based archive stream handlers.
 -4.251 - Fixed crash when calling NPAPI_GetFormatExtensionFlags without a valid module instance.
 -4.25 - Added supersampling to "DickTools - Sphere2Cube".
 -4.25 - New sample scene cubemaps. These cubemaps were generated using "DickTools - Sphere2Cube" (included in optionalplugins), from photo sources licensed under CC 4.0: https://creativecommons.org/licenses/by/4.0/ (author unspecified)
 -4.25 - Don't start up per-module job systems by default.
 -4.25 - Fixed a JPEG loader bug which could occur with exceptionally large files.
 -4.25 - If BRDF clamping is used, the same clamp is now also applied to the HDR environment background.
 -4.25 - More crash fixes.
 -4.24 - Updated FBX plugin to FBX SDK 2017.1. The old 2014-based plugin is included in "optionalplugins" as autodesk_fbx_2014.dll, in case of compatibility issues.
 -4.235 - Added a custom specular texture swizzle transform. Can be specified in Python via NoeMaterial.setSpecularSwizzle.
 -4.234 - Added FF15 import support. Big thanks to flatz, chrrox, and Angela for their parts in making this happen.
 -4.234 - Added a material flag to enable self-sorting for transparency.
 -4.234 - Tweaked mousewheel image zoom, added a display in the upper-left of images to show the current zoomed dimensions.
 -4.234 - Fixed an issue with PBR-generated textures when being combined with embedded model textures.
 -4.234 - Fixed a potential crash from specifying a file that doesn't exist on the commandline.
 -4.233 - Added a bunch of optional plugin scripts: fmt_catherine_pac, fmt_lovehinasa_image, tool_dicomheadermaker, tool_dxtencode, tool_makenx_pac_split, tool_textmaker.
 -4.233 - Updated physics DLL to fix an issue where a shared bone structure had gotten out of sync.
 -4.232 - Exposed bone palettes for Python model exporters. (see NoeMesh.setBoneMap)
 -4.232 - Various crash fixes. Started going through the last 4 or so months of Noesis crash reports.
 -4.232 - To whoever managed to get Noesis to crash on "Exotic Hume Female Dancer - Legs [Unshaven].DAT": Congratulations! You now own the crown of Classiest Noesis User of All Time!
 -4.232 - When importing FBX files, grab material emissive if it's available and use it to create an additive "nextPass" material.
 -4.231 - Addressed an issue with console mode not recognizing when output is piped to an existing handle, and fixed up return codes to reflect an error (< 0) value in a couple of extra edge failure cases.
 -4.23 - Added -forcedeppath and -forcedeppathrel in order to force additional dependencies (like textures and animations) to be written on a given path.
 -4.23 - Changed rpgMatsAndInfoFromAnim to hand back a duplicate bone buffer instead of a pointer to the existing bone buffer, as some animation plugins were abusing this to mutilate bone transforms, resulting in bad transform data by the time it got to the model exporter.
 -4.23 - Having duplicate texture names no longer results in all textures being renamed.
 -4.23 - Fixed embedded FBX textures sometimes being unnecessarily loaded multiple times.
 -4.23 - SMD animation export now normalizes transforms in modelspace before converting back to local space, preserving joint placement for animations that use scaling.
 -4.22 - Added KVX file export support.
 -4.22 - Added VOX file import + export support.
 -4.22 - Voxelization parameters now exposed through text-based .noevox files. An example file is located in the "scenes" directory.
 -4.22 - New option to add additional skins to Quake MDL files when exporting. (-mdladdskin, may be used multiple times for additional skins)
 -4.22 - New option to preserve framegroups when exporting Quake MDL files. (-mdlexportfg)
 -4.22 - New option to preserve IQM animation sequences on import and export. (-iqmpreserveseq)
 -4.214 - Added material flags NMATFLAG_NORMAL_UV1 and NMATFLAG_SPEC_UV1.
 -4.214 - Another optimization to shader permutation data to shrink it down even more.
 -4.213 - Added noesis.deinterleaveBytes for faster data deinterleaving in Python.
 -4.213 - Added GNF import support.
 -4.213 - Some voxelizer fixes. (sorry, voxelizer still isn't exposed to the public API, hoping to get around to finishing this by the next release)
 -4.212 - Fixed diffuse and specular color material expressions not being parsed correctly when provided via a Python importer. Thanks to chrrox for catching this, by being the first person to try using it.
 -4.212 - Added Blood RFF archive support.
 -4.212 - Added Blood map support, which includes support for the expanded shading table range.
 -4.211 - Fixed a bug that was introduced in 4.205 which was causing vertex normals to be ignored on FBX import.
 -4.21 - Respect origin bit for TGA import.
 -4.209 - Added a function to adjust overlapping collinear segments - fixes problems with a few Duke3D sectors.
 -4.208 - Build-related bug fixes.
 -4.207 - Started a new geometry library, and reworked Doom map support to make use of it. Default behavior is now to generate new convex polygons for sectors instead of trying to salvage existing not-necessarily-convex subsector data.
 -4.207 - New Build Engine (Duke Nukem 3D, Shadow Warrior, etc.) support. Your mileage will vary, due to overlapping sectors and such. There are numerous commandline options for this module to work around various issues and hit varying levels of visual authenticity.
 -4.207 - Added a new oriented sprite material flag. The Noesis renderer will obey this new flag if "Obey sprite facing flags" is enabled through the view preferences in the data viewer.
 -4.207 - New option (-wadloadspr) to load sprites for Doom WAD files.
 -4.207 - New option (-wadopensec) to attempt to auto-close open sectors. Recommend using this for Hexen, where lots of sectors are a complete mess. Otherwise you'll end up with a good number of holes in maps.
 -4.207 - New option (-wadmapindex) to specify a given map to load in a Doom WAD, instead of loading them all as individual models. Use -1 to only load textures/sprites/etc.
 -4.207 - DXT encoder and box resample methods exposed to Python.
 -4.207 - Various bug fixes.
 -4.206 - Added Ninja Gaiden 2 .ng2 extraction support, auto-loads filenames from the game's .xex file.
 -4.206 - Changed Stainless MDL loader to accept version 0x603 files.
 -4.206 - Added limited support for P4G Vita .amd files.
 -4.205 - Added support for import and export of FBX blendshapes.
 -4.205 - Internal merging logic now applies transforms to morph frame data, if applicable, when transforming geometry for certain skeletal merging modes.
 -4.205 - Allow vertex morph and skeletal animations to stack in preview playback.
 -4.205 - Fixed a crash when attempting to load Python modules with invalid module names. (such that creating the object fails due to encoding)
 -4.205 - Fixed a rare-timing shutdown crash.
 -4.204 - Fixed crashes when using -vertbones. Sorry about that, whoever was trying to use that on ogre.mdl.
 -4.204 - Prevent GXT crashes on some of the garbage data floating around from bad extraction/conversion tools.
 -4.204 - Sanity check DDS mip counts, for files which claim to provide a mip count via header flag, but actually have garbage in them.
 -4.203 - SMD is now a supported animation export target. (writes a sequence-only SMD)
 -4.203 - Revisited Bujingai - added full animation support, as well as correct material associations and full transform and instancing support for maps. If you have previously extracted .bjp files, you will need to re-extract them with this version of Noesis, due to material/transform/etc. dependencies on data that lives within the ELF.
 -4.203 - Import support for Space Channel 5 Dreamcast DMDM animations.
 -4.203 - New R5900 core emulator, with an optional interface that adds support for PS2-like memory mapping and some VU0 instructions.
 -4.203 - Reworked lighting setup, added support for populating scene lights from importer plugins and the ability to specify scene lights in the .noesis file.
 -4.203 - Fixed a crash in vertex morph animation playback.
 -4.203 - Support for multiple light attenuation models.
 -4.203 - Added a PBR fresnel intensity material property.
 -4.203 - Added an option to allow preview-loaded textures to be exported along with a given model/animation.
 -4.203 - Added a "load preview textures" data path for pure export operations, to facilitate gathering up textures to batch out with an export job.
 -4.203 - Added VMT parsing to Source MDL loader, also support UV projection for iris materials, and a PBR-enabled mode.
 -4.203 - HFS extraction support.
 -4.203 - Added an option to preserve all FBX material/mesh/node properties and pass them through the Noesis model as "custom data".
 -4.203 - Reworked ancient 3DS importer a little bit, and added proper material support.
 -4.203 - Re-implemented the image creator to eliminate old ASPI32 dependencies.
 -4.203 - Automatically load paired PVM files for Ninja models.
 -4.203 - Added an "optionalplugins" directory. These plugins/scripts are not loaded by default, and generally consist of useful tools or one-off/specialized game-oriented loaders and tasks.
 -4.202 - Various Source MDL fixes. (also added LOD support)
 -4.202 - Fixed single-frame sequence SMD's not being recognized as sequences on import.
 -4.202 - Added VPK extraction support.
 -4.202 - Fixed GXT importer not writing mips out at the correct stride for decoded block-compressed formats.
 -4.202 - Fixed AFS extraction not recognizing the 0-directory case.
 -4.201 - Fixed a crash when re-enabling shell views.
 -4.2 - New "Universal Debugger" client built into Noesis. Uses a generic protocol to support disassembly, memory viewing/modification, and a variety of general debugging features under virtually any architecture and addressing mode. Debugger protocol specifies that either the client or the host may implement necessary functionality to support disassembly and other debugging interfaces.
 -4.2 - New PBR material shading options. Default implementation uses something close to Disney's BRDF, with D=GTR (default exponent 2), G=Smith-GGX, F=Schlick approximation. Lambert diffuse is used by default instead of the Disney diffuse term. To avoid runtime importance sampling and maintain lighting parity with IBL (which uses diffuse irradiance and pre-convolved cubemaps), both direct light and IBL paths implement anisotropy by projecting the halfangle vector along the geometric bitangent. I wasn't sure this was going to be useful to anyone when pulling this approach out of my ass, but have since learned that at least Far Cry 4 is doing something similar. On the whole, the default models should be adjustable to fit most games using "PBR" content with reasonable accuracy, although fitting more specialized shaders for things like cloth or skin might get ugly.
 -4.2 - Various new post effect options, with linear output, bloom, and an assortment of color-adjustment and environment map tweak/override parameters. Generally geared toward being able to test and validate correct handling of PBR data.
 -4.2 - New HDR color picker, which allows mouse picking of 16-bit HDR color values from the framebuffer. Also useful for analyzing/validating HDR content and ensuring correct material parameters.
 -4.2 - Internally, everything has finally been switched over from ARBfp1.0/ARBvp1.0 to GLSL. All shaders have been written to be compatible with 1.20 or later of the GLSL spec, and should run even newer shading models on fairly ancient hardware without issue. The old GL fixed function path still exists as a worst-case fallback.
 -4.2 - Better compression of pre-compiled shader permutations.
 -4.2 - Noesis core module handling has been reworked to allow for faster load times.
 -4.2 - Reliance on the Windows Temp directory has been eliminated in the core module. (still required for FBX handling)
 -4.2 - Basic Carmageddon: Reincarnation support.
 -4.2 - Added GXT import support.
 -4.2 - Various additions to the DX10 DDS path, with preservation of HDR data formats.
 -4.2 - Various new tools and routines, including support routines for handling Spherical Harmonic data and a variety of image projection spaces, and derivative/integral functions which have been tested for BRDF debugging and approximation.
 -4.2 - Changed file types/lists in export dialog to be alphabetically sorted.
 -4.2 - Fixed a bug in 16-bit PNG support.
 -4.2 - Fixed a bug in Doom/Heretic/etc. PWAD support.
 -4.2 - Basic compute shader support. Some operations, such as specular convolution for baking IBL, may be accelerated by enabling compute shaders through the data viewer.
 -4.2 - Fixed an interface bug that could create duplicate folders in the shell tree view when expanding a folder.
 -4.2 - Added an option to completely remove shell views. Best used with Explorer file associations and/or drag-n-drop.
 -4.2 - Added a "swap handedness" preview option, available through the data viewer. Swaps handedness of the rendered scene without modifying any associated model data.
 -4.2 - Fixed up Fallout 4 support slightly, and added a commandline option to apply PBR materials to loaded NIF's when possible. (mostly for testing and novelty, NIF PBR material assignments currently assume everything is metal)
 -4.2 - Added NOEKF_SCALE_VECTOR_3 and NOEKF_SCALE_TRANSPOSED_VECTOR_3 keyframe data types.
 -4.2 - Added animation sequence flags - NSEQFLAG_NONLOOPING and NSEQFLAG_REVERSE.
 -4.2 - Added an "always use anim framerate" option, available in the data viewer. (by default, the preview framerate override is used - this forces the animation/sequence framerate to be used for playback instead)
 -4.2 - New ".noefbxmulti" format. Facilitates splitting animation sequences into multiple FBX files, as well as combining multiple FBX files into a single set of sequences.
 -4.2 - Added "-fbxsortnodes" option, which sorts FBX nodes alphabetically to ensure bone/mesh order on import. Can be useful in conjunction with .noefbxmulti files to ensure ordering dependent on node name instead of file or hierarchy order.
 -4.2 - Added a "force no anim lerp" option, available in the data viewer.
 -4.2 - Added a "force texture point filtering" option, available in the data viewer.
 -4.2 - Added a "global angle offset" option, available in the data viewer.
 -4.2 - Added a "disable cursor locking" option, available in the data viewer. This can be useful for tablets and other input devices that don't play nicely with having the cursor position reset.
 -4.2 - "m" is now a valid format string character for the imageEncodeRaw function. This indicates the maximum value should be stored at the given location. For example, the following would split the alpha channel out of a RGBA32 source, spreading it across a 32-bit RGBA destination's RGB channels and setting alpha to 255: rapi.imageEncodeRaw(rgbaSrc, w, h, "a8a8a8m8")
 -4.2 - Fixed a crash in the GMO loader with models containing over 1024 bones.
 -4.2 - Fixed a crash when activating certain tool context menu items without any files selected.

Version 4.1 - 4.177:
 -4.177 - Added a monochrome option for Anaglyph 3D rendering.
 -4.177 - Modified disgusting MFC tree controls on the face of the GUI to prevent large load delays, and fixed a couple stock bugs. Old behavior for these controls is available through the "Full shellview tree expansion" option in the data viewer.
 -4.177 - A couple performance fixes relating to shader hashing.
 -4.177 - Updated R3000A, now includes hooks to a universal debugger interface. Universal debugger client will probably be forthcoming.
 -4.177 - Setting an explicit strip ender now overrides default treatment of 0xFFFF with 16-bit indices.
 -4.177 - Some new native API functions.
 -4.176 - Added PWAD support to the Doom/Heretic/Hexen/etc. map loader.
 -4.175 - New R3000A emulator.
 -4.174 - Added import support for Battlezone VDF, SDF, GEO, and ZFS formats. Texture MAP files are also supported as part of the model loading, and will be searched for on relative "..\bzsw_files" and "..\odysw_files" paths. (so if you extract the texture ZFS's with Noesis on the same path as the main ZFS, textures will be successfully located) Special thanks to Ken Miller and his undying love for the Battlezone community, and thanks to Mike A. for giving the go-ahead to flip these formats on in the public Noesis branch.
 -4.173 - Added support for DICOM .dcmvolset format, a sample set of data is included in scenes/dicom.
 -4.173 - Added support for Quake-format .map files in the .map loader, this must be forced with -mapquake.
 -4.173 - Added -mapbnames, which preserves brushes by mesh name in the .map loader.
 -4.172 - Added a -ddsati2nonorm command which prevents Noesis from deriving z and renormalizing for ATI2/BC5. In the case of games that aren't using explicitly splayed normals (like FO4), adding this to your default command list will work just fine. Noesis already derives Z and renormalizes in its default lighting shaders when sampling normal maps.
 -4.171 - DDS files with FOURCC DX10 are now supported, including new BC6H and BC7 block compression formats.
 -4.171 - Added FO4 archive and NIF support.
 -4.17 - More work on the software renderer. The software renderer is now exposed in the native plugin API, see NoeSRShared.h.
 -4.169 - Fixed some software rendering bugs, and an issue with UV wrapping when sampling textures via the API.
 -4.168 - Added a new -ff11blendhack option. This uses the Noesis software renderer to render all FF11 map geometry triangles in UV space, and determine how many of each mesh's triangles are only touching zero-alpha pixels in the texture. -ff11blendhack 0.99 is typically a good value to use. This completely demented solution is not foolproof, but catches the vast majority of broken blending cases.
 -4.168 - Added support for FF11 SQLE models, including both types of animation.
 -4.167 - Added socket and unicodedata libs to Python implementation.
 -4.166 - Added FF11 import (characters, animations, textures, and maps) support.
 -4.166 - Added a new "noewin" module, which exposes some basic windowing functionality.
 -4.166 - Included ctypes in the Python implementation.
 -4.166 - Modified the UO multi loader script to cache off tile textures.
 -4.166 - Chopped out some useless cruft that had been accumulating and bloating image size.
 -4.166 - Added some code to prevent a crash when loading GIM files with bad palette offsets.
 -4.166 - Fixed a crash in the MVC3 loader.
 -4.166 - Added the ability to disable existing format modules by name, so that plugins/scripts can elect to replace existing implementations entirely.
 -4.165 - Fixed the Quake .map importer not using the correct material names if it couldn't find a texture WAD.
 -4.164 - Finished up an old Ultima Online classic client script. Supports UOP with hash-based indexing, animations, gumps, textures, tiles, multis, statics, maps, sounds, and raw mul dumps. All 6 maps (as of the current UO build) are supported.
 -4.164 - Added an alpha blending flag to imageBlit32. (interpolates using source alpha)
 -4.164 - Added an option to allow negative zoom when viewing images.
 -4.164 - Added a "mousewheel arrows" option, so arrows can be used to emulate mousewheel functionality.
 -4.164 - Exposed a RIFF WAVE header generation function through the Python API.
 -4.163 - Fixed a bug where .noesis scene mergeTo wasn't preserving animations with the same bone count pre-merge and post-merge. Thanks to LUBDAR for coming across this problem, and for continuing to be a supporter for so many years.
 -4.162 - More PVRTC fixes. PVRTexTool has incorrect implicit alpha bit handling for 4bpp PVRTCII, so behavior has been changed to match hardware. (verified pixel perfect against the SGX543)
 -4.161 - Included a context tool for doing simple reordering (Morton versus linear) of PVRTC1/2 blocks. It can be enabled by setting ENABLE_PVR_REORDERING_TOOL to True in fmt_pvrtc_pvr.py.
 -4.16 - More PVRTC fixes. PVRTCII is now fully implemented, and a couple of bugs with 2bpp mode were fixed. The following PVRTC decoding flags are now available: PVRTC_DECODE_PVRTC2 (takes the PVRTCII path), PVRTC_DECODE_LINEARORDER (expects blocks in linear order instead of Morton order), PVRTC_DECODE_BICUBIC (performs bicubic sampling of low frequency signals), PVRTC_DECODE_PVRTC2_ROTATE_BLOCK_PAL (rotates block palette layout for PVRTCII), and PVRTC_DECODE_PVRTC2_NO_OR_WITH_0_ALPHA. (does not perform |1 with C1 alpha if alpha is otherwise zero - seems to be the behavior for some decoders, but only for 4bpp)
 -4.159 - PVRTC fixes.
 -4.158 - Added support for PVRTCII. Handling of new block bits still needs work.
 -4.157 - Added -rpgforcesort. Forces triangle material/name/etc. bucket sorting in the RPG interface, regardless of the importer's preference. This will reduce mesh count for importers which don't elect to sort and which don't provide triangles in material order.
 -4.156 - Implemented -bsppatchsub for JA/SoF2/etc. Q3BSP. Functions the same as it does on the standard Q3BSP path. Set to 0 to disable patch subdivision.
 -4.155 - More Saturn Quake fixes.
 -4.154 - Fixed a Saturn Quake bug where vertices could be welded to non-existent edges between quads.
 -4.154 - Added -qsatenabletexfilter.
 -4.153 - Added import support for Saturn Quake LEV and PIC files.
 -4.153 - Added an "Enabled ViewPos Key" option under "Persistent settings->View" in the data viewer. When enabled, this allows the viewport orientation to be copied to the clipboard via Enter, or set via Shift + Enter. (when the viewport is selected)
 -4.153 - Added NDSNIF recognition to the Gamebryo script.
 -4.153 - Changed dbdinfo behavior to not import embedded skeletons on explicitly hidden objects.
 -4.152 - A few fixes to the PNG importer.
 -4.151 - Added -fbxreducekeys, removes redundant animation keyframes during FBX export.
 -4.151 - Added -fbxcollapsecp, welds controlpoints and uses separate indices for UV/normal/etc. during FBX export.
 -4.151 - Added -fbxtritopoly, uses n-sided polygons instead of triangles where possible during FBX export, with a specified tri/poly normal threshold.
 -4.151 - Added -fbxtritopolyconctol, specifies concavity tolerance for generating polygons from triangles.
 -4.151 - Bumped character limit on batch exporter command text control.
 -4.151 - Various bug fixes.
 -4.15 - Added a new FBX option to export animation sequences as multiple takes. This mode also respects per-sequence framerates.
 -4.15 - Various bug fixes.
 -4.149 - Added some new FBX export options, including one to derive mesh transforms from bone transforms, and apply bone animations to mesh nodes instead of bone nodes.
 -4.149 - Various Death by Degrees fixes.
 -4.148 - Added import support for Death by Degrees.
 -4.148 - Updated the VIF-related native API to support full unpacking.
 -4.147 - Added DICOM export support.
 -4.147 - Added support for DICOM's JPEG-LS and JPEG 2000 transfer syntaxes.
 -4.147 - Various new DICOM commandline/processing options.
 -4.147 - Added JPEG 2000 import and export support.
 -4.146 - Added DICOM support. Initial support includes a decent variety of transfer syntaxes.
 -4.146 - Implemented runtime variable data precision in libjpeg, exposed a new RAPI function to decode a JPEG stream at an arbitrary data precision.
 -4.146 - Applied Ken Murchison's libjpeg patch for lossless JPEG support.
 -4.146 - Added an option to convert NIfTI-1 and Analyze 7.5 data into a series of 2D texture slices.
 -4.146 - HDR texture data is now displayed for textures in the data viewer.
 -4.146 - Added a Luminance F32 HDR texture format type.
 -4.146 - Fixed some Analyze format parameters being incorrectly registered under the KVX format.
 -4.145 - Fixed a bug in one of the RichMat44 constructors.
 -4.144 - Import and export support for Radiance HDR images.
 -4.144 - So many exciting new math functions! Math_ExtractFractionAndExponent, Math_CalculateExponentBits, Math_CalculateFractionBits, Math_GammaToLinear, Math_LinearToGamma, Math_Log2, Math_Log. See header comments for documentation.
 -4.144 - Added HDR texture support in the native API, along with Image_GetTexRGBAFloat. (converts from any fixed or dynamic range format without modifying source data) HDR texture formats are piled on top of existing textures instead of being integrated as native formats, because I'm lazy and hate the codebase.
 -4.143 - Added Math_EncodeFloatBitsFromBits and Math_DecodeFloatFromBits. Math_DecodeFloatFromBits will decode to a 32-bit float given arbitrary mantissa, exponent, and sign bits. Math_EncodeFloatBitsFromBits will encode between any floating point formats given arbitrary source and destination mantissa, exponent, and sign bits. It doesn't necessarily obey IEEE standards, but assumes an exponent bias in keeping with IEEE standards and will globally treat zeroed exponent bits as a zero value.
 -4.143 - Exposed Noesis_DecodeNormals32 through native plugin API.
 -4.142 - User vertex components are now correctly preserved for pure point meshes.
 -4.141 - Even more dev stuff.
 -4.14 - More dev stuff.
 -4.13 - All behind-the-scenes dev stuff.
 -4.12 - Added -fbxpreservecp.
 -4.11 - Reworked some crash report stuff.
 -4.1 - Added morphFrame .noesis scene file option. Allows constructing vertex morph animations from a variety of meshes/models.
 -4.1 - Added -fbxnooptimize to allow disabling fast geometry optimization pass on FBX import.
 -4.1 - When exporting to MDR without -mdrvertlocal, if a bone is specified as a tag using -mdrbtag, that bone will be kept in model space instead of pose space. If vertices are weighted to that bone, they will be transformed into bone-local space (with weights respected) to compensate even though -mdrvertlocal is not invoked.
 -4.1 - Added -mdrforcebonemspace to force a bone to be in modelspace regardless of tag status.

Version 4.0 - 4.0999:
 -4.0999 - Added a -bakeanimscale option. Takes frame 0 of animation, bakes into geometry, and removes scale from skeleton/animation.
 -4.0998 - Instead of transforming verts into bone-local space, MDR export now puts matrices in bind-local space. Revert to old behavior if desired with -mdrvertlocal.
 -4.0997 - When using -g2exforceskeleton 1, will force all GLM verts to be weighted to root.
 -4.0996 - Fixed -md3tbone only working when exporting with animation data. Now works for exporting static geometry with a skeleton as well.
 -4.0995 - Fixed a typo in the GLM importer which could result in duplicated materials with the same name, causing problems for some exporters.
 -4.0994 - Added -g2extrivertshift and -g2extagtrivertshift. Allows shifting triangle indices for tag/non-tag GLM surfaces.
 -4.0993 - Fixed parent/child indices not being correctly remapped when using -g2exorderbonesfromgla on GLA export.
 -4.0992 - Added -g2exorderbonesfromgla and -g2exforceskeleton for GLM/GLA exporters.
 -4.0991 - Various fixes.
 -4.099 - Option to cycle multiple models on a timer.
 -4.099 - Various fixes for Analyze 7.5 and NIfTI-1.
 -4.0989 - Import support for NIfTI-1 and Analyze 7.5 MRI data formats.
 -4.0988 - An assortment of new development features that no one knows about.
 -4.0987 - Added KVX import support.
 -4.0987 - Fixed a crash in the GHOUL2 export path when unweighted geometry was exported. Also added a warning message for meshes with no bones, but it is allowed.
 -4.0987 - Fixed a potential crash from a stale pointer on shared model data.
 -4.0986 - Added -maxverts and -maxtris which enable splitting meshes up when a given vert/tri count is exceeded. Automatically invoked for GLM export by default.
 -4.0986 - GHOUL2 skin file parsing support.
 -4.0986 - Added a "Force texture path" option under Persistent settings->Other in the data viewer. This is a semicolon-delimited lists of additional global texture paths.
 -4.0986 - Various other new GHOUL2 export options.
 -4.0986 - Added a commandline override to disable format-specific commandline options.
 -4.0986 - Fixed a resource hashing bug in the noesis_misc module which could affect various import modules.
 -4.0986 - Fixed MD3 surface naming.
 -4.0985 - Added NMSHAREDFL_NOEMPTYMESHES.
 -4.0984 - Various bug fixes.
 -4.0983 - Fixed transform modifiers not modifying bones before animation export is performed.
 -4.0982 - GHOUL2 GLA export support.
 -4.0981 - GHOUL2 GLM export support.
 -4.098 - Converted Bayonetta project to VS2010, which auto-remedied AVG thinking its DLL was a virus due to some haphazard binary signature match.
 -4.098 - Rewrote GHOUL2 import support and moved it out into the noesis_misc module, and added animconfig support. Prep work for export support.
 -4.098 - Noesis FBX sidecar now supports animation sequences and user sequence data.
 -4.098 - Fixed the Python module crashing if Noesis is run on a path containing non-mbcs characters.
 -4.098 - Added a native ADPCM block decompression function.
 -4.098 - New ADPCM Python utility module with methods for decoding various forms of PSX ADPCM data.
 -4.098 - Added Noesis_GetExportingModelSetCount/Noesis_GetExportingModel, to allow export modules to grab other non-targeted models if desired.
 -4.0979 - Basic SotN zone import support, based on nyxo's specs. -sotnseplayers to break individual layers up on export.
 -4.0978 - New mode to allow running console/tool mode even when there's no parent console to attach to.
 -4.0977 - Fixed DDS export not setting DDSF_MIPMAP in ddsCaps when exporting DDS files with mipmaps.
 -4.0977 - Tokyo Jungle.
 -4.0976 - Various development support features.
 -4.0975 - Added Hexen support, and glbsp support. Noesis will use glbsp lumps instead of trying to generate convex polygons from subsectors using bsp partition lines (which tends to break down on anything after Doom 1 due presumably to some unfortunate node builder optimizations), if said lumps exist in the wad or if there's a .gwa file of the same name for it to pull from.
 -4.0975 - Added a WASD zoom control option. When enabled, allows you to move with WASD when camera is zoomed all the way in.
 -4.09742 - More Doom map fixes. Yeah, I know no one cares.
 -4.09741 - Doom map fixes.
 -4.0974 - Doom map support. Noesis will load every map in a wad as multiple models. Generally looks good to me on the first Doom wad, but there are likely to be some issues here. It turns out generating convex polygons for Doom map subsectors from node planes and subsector segments is a less trivial problem than one might expect.
 -4.0974 - Fixed a bug where Python PVRTC decode function wasn't correctly range-checking negative bit values.
 -4.0974 - Added "flags" member to native text parser, and a few new flags.
 -4.0974 - Various SMD parsing fixes.
 -4.09731 - More info on "vertex bone index out of range for bone map" warning for chrrox.
 -4.0973 - Support parsing PVR textures out of NJ streams.
 -4.0972 - Hacked in support in the IQM exporter for exporting non-skeletal/unskinned models.
 -4.0971 - Fixed a crash in Half-Life map handling when LM block size exceeds standard format limits.
 -4.097 - Added "-smduseactualmatname", which causes Noesis to use the actual material names when exporting to SMD instead of the diffuse texture names. This is not the default because it would probably cause a lot of people who don't know what they're doing to send me messages complaining about "no textures" on the SMD's in preview mode.
 -4.097 - Added "-smdoldtexexportnaming" and changed default behavior to strip path and extension from SMD material names, at the request of shadowmoy.
 -4.0969 - Added rapi.processCommands.
 -4.0969 - Added 4bpp support to rapi.imageTwiddlePS2.
 -4.0969 - Added -texnorepfn.
 -4.0968 - Added noesis.isPreviewModuleRAPIValid and noesis.setPreviewModuleRAPI.
 -4.0968 - Added rapi.simulateDragAndDrop.
 -4.0968 - Fix for Duke3D GRP script throwing exceptions for invalid data when checking its validity.
 -4.0967 - Garbage DDS header crash fix. Apparently some PhotoShop DDS plugins can spit out horribly mangled headers when trying to spit out non-block-aligned DXT data.
 -4.0966 - Various fixes for dealing with bad triangle indices.
 -4.0965 - Added named user vertex streams. Named streams can specify raw data as per-vertex or per-mesh/instance, and can be provided to the RPGeo interface using rpgBindUserDataBuffer, or immUserData in immediate mode. To specify that a stream is per-instance, simply provide a data stride of 0. User data streams will not be modified or processed in any way, and will be passed along the export path as-is. Attaching per-instance streams to draws can also be useful as it allows you to pass through your own custom arbitrary data structures. I recommend giving your user streams reasonably unique names. For example, instead of naming something "verts" where another script might have created a like-named user stream to hold differently-formatted data, name it something like "yourscriptname_custom_vert_data".
 -4.0965 - Added -fbxnoesidecar. This enables reading/writing of .noefbx files when importing/exporting FBX. A .noefbx file will be generated if the model being exported contains custom user stream data, so that the data can be preserved across export/import of the resulting FBX.
 -4.0965 - Added readDouble, readInt64, readUInt64, writeDouble, writeInt64, and writeUInt64 functions to NoeBitStream.
 -4.0965 - Better handling for when someone decides it's a good idea to turn a high-detail skeletally animated model into a 4GB Quake MDL.
 -4.0964 - Fixed various buffer overflows which could occur in legacy print functions.
 -4.0963 - Fixed a z precision issue in BC5 decoding.
 -4.0963 - Fixed a bug in calculating BC4 size that caused recent DXT safeguards to refuse to decode data.
 -4.0963 - Added a "Force software DXT decode" option in the data viewer.
 -4.0962 - Added Noesis_ConvertDXTEx, and failsafed more of the DXT code scattered throughout Noesis.
 -4.0962 - MvC3 vertex weighting fix.
 -4.0962 - Added NPAPI_SelectDataViewerBone.
 -4.0961 - Fixed a possible crash when untiling unaligned DXT data.
 -4.096 - Added a new "Default tool plugins" option. This is a semicolon-delimited list of tools that you want to be automatically invoked when you start Noesis or reload plugins.
 -4.096 - Added NPAPI_SelectDataViewerMeshMaterial. Does the same thing as NPAPI_SelectDataViewerMesh, but goes directly to the mesh's material instead of the mesh.
 -4.096 - Added NOESISBUTTON_ALT for tool input callbacks.
 -4.096 - Fixed a problem with Noesis_CopyInternalTransforms failing when not every mesh in the model has a transform buffer.
 -4.096 - Added Noesis_GetMeshInternalProperties.
 -4.0959 - Added options for "Disable anisotropic filtering" and "Disable hardware mipmaps".
 -4.0958 - Added noeProcessImage. This is a utility function that lives in inc_noesis, and is very useful for automating the task of invoking image processing calls on multi-face/multi-mip images. See the example usage in the NIF script.
 -4.0958 - Cubemaps and mipmaps are now used for NIF files.
 -4.0958 - Added rapi.imageKernelProcess. Allows you to specify a Python "kernel" method to do per-pixel data processing on image data. Performing logic in the kernel is typically around 2-4 times faster than doing the same thing by looping through bytearrays yourself in Python.
 -4.0958 - Added NPAPI_SelectDataViewerMesh to the native API. This is used by the latest triangle picker plugin (Rich/native_bin/example_visualize02.dll in the Noesis plugins repository), and allows you to go directly to meshes in the data viewer by ctrl+clicking any of their triangles.
 -4.0958 - Fixed a formatting bug in Python error text.
 -4.0958 - Added a "skip render" flag for models in the data viewer, mainly for convenience when using the "draw all models" option.
 -4.0957 - Ctrl-C now works to copy the current selection in the data viewer. You can also use the "Copy data only" option to have Ctrl-C only grab the data string instead of the full entry text.
 -4.0956 - Added a search option in the data viewer. You can search by value name or in the actual data. Convenient for finding meshes/materials in the model by name.
 -4.0955 - rapi.imageNormalSwizzle may now have 2 passed for "derive z" parameter to do normalize from z=1. Some games use this instead of the default method.
 -4.0955 - Changed default derive z method for normal swizzling to be more precise.
 -4.0954 - Added NMATFLAG_GAMMACORRECT, flags the material for gamma-correct lighting.
 -4.0954 - Reduced memory footprint of program permutation data to permit for yet more permutations without considerable overhead.
 -4.0954 - Added -ff13mgamma, enables gamma-correct lighting on all FF13 materials.
 -4.0953 - Small update to se_lzfastest_decomp implementation.
 -4.0953 - Various speedups and fixes.
 -4.0952 - Added "se_lzfastest_decomp" extension method.
 -4.0951 - Support for YMO version used in Ys Origin.
 -4.095 - Added skeleton, skinning, and animation support for Ys: The Oath in Felghanna YMO files.
 -4.094 - Fix for Ys Origin AIA files.
 -4.093 - Python script for importing Ys AIA files is now included.
 -4.093 - Added rapi.imageBlit32.
 -4.093 - Added rapi.callExtensionMethod. Exposes various extension methods to Python.
 -4.092 - Various bug fixes.
 -4.092 - Support for large address space on 64-bit operating systems.
 -4.091 - Various FF13 fixes/updates.
 -4.09 - More FF13-2 and LR:FF13 fixes. Also added support for new LR:FF13 animation channel types.
 -4.0899 - Various fixes for LR:FF13.
 -4.0898 - Added mapAnimFrom, mapAnimDiff, and replaceBone properties for Noesis scene file objects.
 -4.0897 - Added rpgGetMorphBase and rpgSetMorphBase, made rpgClearBufferBinds automatically invalidate current morph base.
 -4.0896 - Added RPGOPT_MORPH_RELATIVEPOSITIONS and RPGOPT_MORPH_RELATIVENORMALS.
 -4.0896 - Various morph target fixes.
 -4.0895 - Changed the way morph target positions/normals are handled internally. RPG interface now copies off the data at CommitMorphFrame time (so you can free it immediately after commit), and performs all standard transform/scale/bias operations on it.
 -4.0894 - Fixed NoeAngles.fromBytes handing back a NoeVec3 instead of a NoeAngles.
 -4.0893 - Added toMat43_ArbConv, toRadians, and toDegrees to NoeAngles.
 -4.0893 - Fixed a number of Noesis Python constants being truncated to longs. Oops!
 -4.0892 - Some small UI fixes.
 -4.0891 - Added -ff12animadd, automatically applies base pose to additive animations instead of leaving them as-is. (additive animations otherwise appear with the model all balled up, because channels are all in pose-relative space)
 -4.0891 - Minor FF12 animation fixes.
 -4.089 - Finally went back and figured out the rest of FF12's animation format.
 -4.088 - Fixed an issue with manually pairing FF13 models to animations.
 -4.0879 - Fixed materials with normal maps having their noLighting flag ignored.
 -4.0878 - Fixed a scale issue with FF13 animations, and added -ff13ascale because, as with FF8, non-uniform scales may cause issues with some exporters/tools.
 -4.0877 - FF13 animation support. Thanks to nohbdy for the format info.
 -4.0877 - Added NOEKF_TRANSLATION_SINGLE and NOEKF_SCALE_SINGLE keyframed anim types.
 -4.0877 - Various bug fixes.
 -4.0876 - More small NIF fixes.
 -4.0875 - Changed NIF script to do bonespace transforms for each mesh, because different skins/modifiers may specify different bind poses for the same bone.
 -4.0875 - Added rpgGetVertexCount and rpgGetTriangleCount.
 -4.0875 - Added optional parameters to rpgSkinPreconstructedVertsToBones.
 -4.0874 - Fixed rotations for constant evaluators in KF files not being transposed correctly.
 -4.0873 - More NIF fixes. Thanks to chrrox for helping test and providing lots of test data.
 -4.0872 - Added support for 360 texture untiling in NIF files.
 -4.0872 - Added Splatterhouse NIF hack mode.
 -4.0872 - Added a -nifnoversionhacks option.
 -4.0872 - The auto-updater now automatically clears out your old pycache directory.
 -4.0871 - Fixed a possible crash when merging a model with bad material indices into another model.
 -4.087 - Added NIF support, using http://niftools.sourceforge.net/doc/nif/ as a reference. Supports Skyrim and a bunch of other games. Kind of supports Oblivion, may die on files that contain unrecognized objects. (Oblivion uses an earlier version of the format that doesn't contain object sizes, so there's no way to skip over unknown object types)
 -4.087 - Added Image_MortonOrderEx.
 -4.087 - Fixed bad parameter checks in rapi.dataToIntList/rapi.dataToFloatList.
 -4.087 - Don't use mip filtering on textures without a complete mip set - fixes some DDS images showing up white in preview.
 -4.0869 - Added "modelIndex" parameter for .noesis file objects, to specify a particular model to use in the file being loaded if it has multiple models.
 -4.0869 - When merging objects in Noesis files, animations were only used if they contained enough bones for the merged skeleton. Now they're also used if they only contain enough bones for the destination skeleton in the event that all bones in the source skeleton are collapsed.
 -4.0869 - Fixed memory leaks from models containing multiple models being loaded by .noesis files and having unused models discarded.
 -4.0869 - Unified mesh, bone, and material display in data viewer.
 -4.0868 - Added rapi.mergeKeyFramedFloats. It will take a list of keyframed data lists, and convert it into a multi-element keyframe data list. Useful if you want to do something like take 3 separate X/Y/Z keyframe tracks and convert them into a single XYZ track.
 -4.0868 - Fixed a typo in NoeKeyFramedValue.
 -4.0868 - Fixed a crash when running out of memory on TGA export.
 -4.0867 - Fixed a timing issue in Noesis_AnimFromBonesAndKeyFramedAnim.
 -4.0866 - Added NoeKeyFramedAnim, NoeKeyFramedBone, and NoeKeyFramedValue. You can attach NoeKeyFramedAnim lists to a model the same way you would attach NoeAnim lists. Keyframed animations support a variety of data types and interpolation modes.
 -4.0866 - Fixed a crash when committing vertex weight indices without weight values.
 -4.0866 - Fixed a bug that would cause Python-created animations to have an internal framerate of 20 regardless of the framerate specified on the NoeAnim. (wasn't immediately obvious, because Noesis doesn't use that value to determine playback rate)
 -4.0865 - Added rapi.dataToIntList and rapi.dataToFloatList for raw data conversion using the RPGEODATA types.
 -4.0865 - If the number of vertex bone weights fed to the RPG interface is equal to the number of bone indices minus 1, the last weight is now automatically determined as 1-sum.
 -4.0864 - Fixed a case-sensitivity bug in noesis.getFormatExtensionFlags.
 -4.0863 - Added rapi.imageFromMortonOrder and rapi.imageToMortonOrder.
 -4.0862 - Wine hack - Currently Wine's implementation of SHGetPathFromIDList is broken, so Noesis will display all files in the shell list when "All Files" is selected even if this function fails.
 -4.0862 - Wine hack - Currently Wine screws something up with the CRT when the Noesis preview module is reloaded. This doesn't happen when the CRT is dynamically linked, but switching from static linking just because Wine is broken would be a bad idea. To work around the Wine bug, browse to your file in the shell view using the above-mentioned hack and use the standard export option instead. Thanks to Riker191 for sending me the Wine crash reports that allowed me to track this crap down.
 -4.0862 - Updated Noesis core module to new VC runtimes.
 -4.0861 - Changed behavior of export dialog so that it stays open and allows re-exporting without closing.
 -4.086 - Added a new preference in the data viewer, "Persistent settings->Other->Default preview commands". Adding stuff to this string will cause it to be executed on model preview import, so that you can enable non-default options or perform actual processing by default in the model preview. So if you wanted to, for example, see FF8's animation scales in the preview, you'd set that string to "-ff8animscale".
 -4.086 - Added support for scale data in FF8 animations. It's disabled by default, because it requires non-uniform scales which will upset a bunch of things. Including the FBX SDK. Use -ff8animscale to enable.
 -4.086 - Added big-endian byte order for bit reads/writes to the bitstream interface. Exposed in Python via NoeBitStream's setByteEndianForBits.
 -4.086 - Various fixes for the bitstream reader/writer. Now supports > 64-bit reads/writes.
 -4.086 - Prevent GetAttributesOf from being called on large zip files in the terrible MFC shell view, because it sometimes decides to spend minutes trying to determine if said zip files have any "subfolders".
 -4.086 - Various minor interface bug fixes.
 -4.086 - Someone managed to get a memory alloc failure and subsequent crash while trying to load an insanely large JPEG image, so that case is handled gracefully now.
 -4.085 - Modified crunch to handle reverse-ordered mipmaps and header-relative data offsets.
 -4.085 - Made DDS import module handle badly-formatted DDS files that don't specify dimension/format flags. You'll get a warning about them.
 -4.0849 - Added import/export of crunch texture compression library (v1.04) .crn files. Thanks to Rich Geldreich for writing the crunch library.
 -4.0849 - Added -fbxsmoothgroups to compute smoothing groups from vertex normals when exporting to FBX.
 -4.0849 - Fixed a crash when loading TPL image lists with bad offsets.
 -4.0849 - Fixed a crash when loading HL MDL's that specify no movement on a given axis of the motion bone while providing an invalid motion bone index.
 -4.0848 - Fixed GMO crash on bad bone and reference indices.
 -4.0848 - Fixed some FPK extraction crashes.
 -4.0848 - Fixed COLLADA importer crashing if bone names were too long.
 -4.0848 - Fixed FBX crash when file has an obscene number of bones and animation frames, causing an actual memory allocation failure.
 -4.0847 - Fixed Noesis crashing when you give it vertex morphs but don't supply normals for the morphs.
 -4.0846 - Fixed default light positions being off-center. (they'd been stuck in the wrong transform space for a while now)
 -4.0846 - Fixed multi-model animation having issues when all models were set to render, caused by a recent stereoscopic rendering fix.
 -4.0846 - Added "animateAllModels" option, settable by rapi.setPreviewOption.
 -4.0845 - Fixed FF13 DXT data not having its dimensions padded out correctly, which could result in crashes on models that used DXT textures not aligned to block size.
 -4.0845 - Made generic DDS DXT writer check for unpadded source data.
 -4.0844 - Fixed a GMO skinning bug with multiple models in a single file that was introduced about a month ago.
 -4.0844 - Attempted fix for a random crash someone got while trying to resample bad image data to upload it on hardware without NPoT texture support.
 -4.0844 - Support for BSBM Mk2 BND archives.
 -4.0844 - Added rapi.noesisIsExporting. This allows import scripts to see if they're being invoked with the intent of exporting to a specified target.
 -4.0844 - Added an "Export" option to the file view right-click context menu.
 -4.0843 - Added rapi.rpgSkinPreconstructedVertsToBones. This function takes a list of bones and transforms all pre-constructed (but post-committed) vertices in the RPG context using the bone matrices. Useful for formats that store vertices in bone-local space.
 -4.0842 - Cleaned up GL extension management in GL renderer module, added a "Force disable PPL" option in the data viewer under View.
 -4.0841 - Fixed a bug causing pixel picker and some help text not to display correctly.
 -4.084 - New right-click context menu in file view. Default items include functionality to open the file, browse to the file in Explorer, and copy the file's full path to the Clipboard.
 -4.084 - Tools can now be members of the right-click context menu, using noesis.NTOOLFLAG_CONTEXTITEM. In combination with the visibility callback, it's possible to create format-aware context menu items.
 -4.084 - Added noesis.setToolFlags/noesis.getToolFlags/noesis.setToolVisibleCallback. See __NPReadMe.txt for usage.
 -4.084 - Added noesis.openAndRemoveTempFile. See __NPReadMe.txt for usage.
 -4.084 - Added noesis.getFormatExtensionFlags. See __NPReadMe.txt for usage.
 -4.084 - Added ?runtool, which functions like ?cmode but allows you to run tool plugins/scripts from the command line. If the tool uses a mainframe GUI feature, it may not work or it may explode horribly. Use at your own risk.
 -4.0839 - Added Decomp_Inflate2, Compress_Deflate2, and Noesis_GetInflatedSize2. Allows you to specify window bits. In Python, this is exposed as an optional argument at the end of decompInflate/compressDeflate/getInflatedSize.
 -4.0838 - Added a rimBias material property.
 -4.0838 - Fixed a crash when extracting MGZ files with unexpected content headers.
 -4.0838 - Fixed a crash when trying to preview really large files that aren't actually recognized as anything.
 -4.0837 - Added rim lighting material properties. See setRimLighting on the NoeMaterial.
 -4.0837 - Exposed envmap color and ambient color material properties to Python. See setEnvColor and setAmbientColor.
 -4.0836 - Automatic loading of external texture bundles as needed for FF13 models. This works for both zones and some of the characters/monsters with external dependencies.
 -4.0836 - HDR colors are used for FF13. Added -ff13cscale and -ff13cclamp to determine how/if HDR values are crunched into non-HDR range.
 -4.0836 - Tangent vectors for FF13 models are now loaded from file instead of being auto-generated.
 -4.0836 - Automatic assignment of normal maps and skin/hair material flags for FF13. (material assignment still isn't perfect, because I can't be assed to chart down the sampler mappings for every base shader type)
 -4.0836 - Python now validates RPG context state for all relevant RPG calls. (turns crashes into Python exceptions)
 -4.0836 - Added rpgActiveContextIsValid.
 -4.0836 - Added source endian option for index decompression.
 -4.0836 - Added a material sort flag.
 -4.0836 - Per pixel lighting path uses vertex colors if available.
 -4.0835 - Embedded textures are now loaded from FBX files, and Noesis cleans them up. Because the FBX SDK enjoys quietly shitting them all over the Windows temporary directory.
 -4.0835 - FBX files on unicode paths should work now. Unless they break their widechar-UTF8 conversion in the SDK again.
 -4.0835 - Display internal texture names in the data viewer.
 -4.0835 - TIM2's loaded from GMO's now have a consistent naming scheme.
 -4.0835 - Fixed a recently-introduced bug that caused the preview module to not be freed correctly.
 -4.0834 - Added -gmokeeptexnames. This is not enabled by default because lots of GMO's tend to have useless/garbage texture names.
 -4.0834 - Assign material names from external TTD references when auto-loading a TTD for a GMO. (fixes recently introduced material mapping issues with Fate/Unlimited)
 -4.0834 - When loading GMO's without stored textures, prefer to use external texture names for material texture references.
 -4.0834 - Fixed memory leak from loading a GMO without any model/anim/texture data in it.
 -4.0834 - Fixed memory leak from loading a GMO which specifies bone references without any surfaces.
 -4.0833 - Reworked GMO loader to use the RPGeo interface. Loads much faster and automatically removes degenerate triangles.
 -4.0833 - Fixed handling of GMO material diffuse colors, didn't know the same chunk could come in ubyte form.
 -4.0833 - Fixed GMO normals getting corrupted. (uninitialized heap memory, oops)
 -4.0833 - rpgOptimize now checks for degenerate faces after combining vertices, which removes degenerate faces that aren't index-degenerate.
 -4.0832 - Added -fbxcanimtime to get FBX animation times out of curve keys instead of using clamped evaluator times. May produce more accurate animation sampling if the FBX file is screwed up or has animation curves on unused nodes.
 -4.0832 - Added -fbxzup to specify Z-up orientation on FBX export.
 -4.0832 - Obey Z-up orientation when loading FBX files for preview. (this only affects preview mode, it does not do any transforms on the actual geometry)
 -4.0832 - Fixed 3D grid being drawn when previewing textures out of the data viewer.
 -4.0831 - Various GMO animation fixes, support for animated bones with inverted scales.
 -4.083 - Fixed a bug in PSP untwiddling on non-tile-aligned images.
 -4.083 - Added support for another data type for GMO skeletons.
 -4.083 - Sped up GMO loader.
 -4.083 - HL MDL loader no longer uses sequence group data offsets by default, because apparently there are a lot of HL MDL's out there with garbage sequence group data. Use -hlmdluseseqgroups to force it.
 -4.083 - Fixed a Q1/HL BSP crash from vis data on the last leaf overflowing.
 -4.0829 - Fixed various potential shutdown and GL-related crashes.
 -4.0828 - Upgraded FBX plugin to FBX SDK 2014.1.
 -4.0828 - Added rpgUnifyBinormals. Unifies binormal vectors, since FBX tends to have screwed up binormals for mirrored UV's.
 -4.0827 - Tangent and binormal vectors are preserved with FBX import and export. (-fbxrottan and -fbxnotan options are also provided, to rotate and ignore tangent matrices)
 -4.0826 - Added NMATFLAG_KAJIYAKAY, which enables Kajiya-Kay specular lighting, using the alpha channel from the spec map to determine the scale of the surface normal to offset the tangent vector. This technique is commonly used for things like hair and scratched metal.
 -4.0826 - Added NMATFLAG_BLENDEDNORMALS, which does a per-color-channel blend between geometric normals and normal mapped normals using the values provided in blendedNormalFracs. This technique is commonly used to fake subsurface scattering.
 -4.0826 - Recentering the view no longer resets the axis of rotation.
 -4.0825 - Specular halfangle is now non-biased by default. (biased method can be used by setting Data viewer->Persistent settings->Other->Biased specular halfangle)
 -4.0825 - Default material exponent is now 32 instead of 1.
 -4.0824 - Added Math_CatmullRomTangent, Math_CatmullRomLerp3D, Math_CatmullRomTangent3D, Math_CreateProjectionMatrix.
 -4.0823 - Size validation on GIM files to prevent crashes on bad data.
 -4.0822 - Noesis_TextureAlloc won't return NULL if you feed it bad dimensions, it'll just fix your parameters. This was crashing some old plugins that fed Noesis bad texture sizes.
 -4.0821 - The last argument of rapi.rpgCommitTriangles (usePlotMap) is now optional. (defaults to 1)
 -4.082 - Added rapi.decodePSPVert.
 -4.082 - Did away with the concept of reserved texture indices, which was causing crashes under extremely shitty OpenGL implementations.
 -4.082 - Exit gracefully with an extremely helpful, informative, friendly message when running out of memory in a dynamic array.
 -4.081 - Added NoeSplineSet, NoeSpline, and NoeSplineKnot.
 -4.081 - Added rapi.splineToMeshBuffers.
 -4.081 - Added noesis.getCharSplineSet.
 -4.081 - Added noesis.cubicBezier3D.
 -4.081 - Changed the way light vectors are calculated in order to reduce error from interpolation.
 -4.081 - Added NGL_GetEye.
 -4.081 - Added Noesis_GetFrameTime.
 -4.081 - Added rapi.imageNormalMapFromHeightMap. This uses a technique that I pulled out of my ass to generate normals from a height map using sub-texel tangents. It usually looks pretty good. You can use a negative height scale to invert the height. The texel scale affects the sub-texel sampling radius.
 -4.081 - Made NoeMat43/NoeMat44 swapHandedness return the swapped matrix to be consistent with the rest of the matrix operations.
 -4.081 - Added mipmap and cubemap import for non-DXT DDS.
 -4.081 - Added DDS export. Preserves RGBA/DXT1-5 as well as mipmaps and cubemaps.
 -4.081 - Boosted precision on DDS color decoding.
 -4.081 - Prevent crash if GL fails to (re)initialize, and stop GL unnecessarily reinitializing when plugins are reloaded.
 -4.081 - Fix for some corrupt DDS files crashing Noesis.
 -4.081 - Fixed a bug that could prevent auto-generated smoothed tangent matrices from being used in the final model.
 -4.08 - Figured out a problem with NJCM weight handling, Maken X models now look correct.
 -4.08 - Corrected some timing issues that could cause the eyes to unsync when using stereo view.
 -4.0799 - Added support for CCS (and probably other) NJCM models.
 -4.0799 - NMDM (.njm) files are now loadable directly, and will prompt for the corresponding .nj file. If you choose the wrong model for the animation, terrible things will probably happen, so don't do that.
 -4.0799 - Added a Hermite interpolation function. (math.hermiteLerp in Python)
 -4.0799 - Exposed cubic interpolation to Python. (math.cubicLerp)
 -4.0799 - Added 3D Bezier curve evaluation. (math.bezier3D in Python)
 -4.0799 - Added clamp/wrap int functions to native API.
 -4.0798 - Exposed material flags in the data viewer.
 -4.0797 - Fixed a sporadic Python texture loading crash that was introduced in 4.079 by forgetting to increment a reference count. This is why we can't have nice things, Richard.
 -4.0797 - Various nested handler fixes for Python.
 -4.0797 - FBX import now auto-loads normal/spec/etc. maps for preview by default.
 -4.0797 - Fixed a couple memory leaks.
 -4.0797 - Various array class fixes, one of which fixed a possible GL shutdown crash.
 -4.0796 - Added noesis.NMATFLAG_USELMUVS.
 -4.0795 - Exposed envmap color and Fresnel factor for materials in the data viewer.
 -4.0795 - Beautiful Soup (BS4) is now included in the core Python distribution.
 -4.0794 - Fixed a bug introduced in 4.079 that was causing textures to use the wrong wrap mode.
 -4.0794 - Added a preview option called "autoLoadNonDiffuse", allowing format modules to override user preferences for auto-loading normal/spec/env/etc. maps.
 -4.0793 - Made envmapping work on crappier hardware.
 -4.0792 - Fixed per pixel lights having the wrong transform when changing the model axis space.
 -4.0792 - Added "lightAxis" option for setPreviewOption, determines the default axis for light offsets. (should be 0-2)
 -4.0792 - Crash fix for loadExternalTex.
 -4.0791 - Cubemap DDS files are now recognized as cubemaps. (but only used as cubemaps if they contain all 6 sides)
 -4.0791 - Fixed a bug with NoeBones having themselves set as their own parent, thanks to TheDude for reporting the bug.
 -4.0791 - Fixed more const inconsistencies.
 -4.079 - Exposed mipmap count and cubemap flag on NoeTexture.
 -4.079 - Cubemaps are now supported in texture preview mode. Pan values are used to generate 3D texture coordinates so that you can look around the cubemap.
 -4.079 - Environment maps are now a material property. They're preserved in FBX as reflection maps, and are displayed with per-pixel (using the tangentspace normal) reflections with Fresnel term in preview mode.
 -4.079 - Mipmaps are now uploaded (if provided) for all natively-supported Noesis texture formats in preview mode.
 -4.079 - Redid the way preview textures work behind the scenes, no more special-case treatment. Textures auto-loaded for preview are also now viewable in the data viewer.
 -4.079 - Opening archive types now just opens the export dialog, instead of asking you if you want to export.
 -4.079 - Fixed GMO's with bad/no geometry crashing Noesis.
 -4.079 - Added -gmobasepose. Exports untransformed GMO geometry, and stomps over base pose matrices with skinning matrices where necessary.
 -4.079 - Fixed FBX files with bad cluster/bone indices crashing Noesis.
 -4.079 - Running out of memory while writing to a stream container provides the user with a semi-helpful messagebox instead of mysteriously exploding.
 -4.079 - Made default image format output replace .dds extension when auto-decompressing on export, instead of appending the new extension after the .dds.
 -4.079 - Fixed a crash when using rapi.loadTexByHandler to load a Python-handled format within an instanced module's rapi context.
 -4.0785 - Allow models with weights but no skeleton again.
 -4.0785 - Renormalize normals and tangents from lower-precision data types after conversion in the rpg system.
 -4.0783 - Bounds checking for bone index maps.
 -4.0783 - Extra validation of mesh indices and weights when passing mesh data directly back to Noesis in Python.
 -4.0783 - Various changes to Python math classes.
 -4.0782 - Fixed ISO extraction choking on massive files.
 -4.0781 - Added rapi.imageDXTRemoveFlatFractionBlocks. I've been experimenting with getting better visual results from DXT compression on hardware that uses shitty color coefficients.
 -4.078 - Pixel picker displays DXT color samples in addition to block information.
 -4.078 - Fixes/tweaks to pixel picker.
 -4.078 - Fixed a leak when selecting View->Reset all.
 -4.078 - Added optional offset and stride parameters to rapi.swapEndianArray.
 -4.077 - Added a pixel picker, enabled in the data viewer under Persistent settings->View. When viewing textures, it shows information for the pixel the mouse cursor is over. For DXT images, it shows the block and its alpha/color data. This is useful for diagnosing problems with DXT compression.
 -4.076 - Size validation now pads dimensions to block sizes for DXT data.
 -4.075 - Added size validation for textures in Python.
 -4.074 - Added "bump" texture types to materials. Bump textures are preserved across FBX files and native/Python interfaces.
 -4.074 - Fixed a RAPI module instantiation crash.
 -4.074 - Added the "noeSafeGet" Python convenience method.
 -4.073 - Changed -smdnorm to -smdnonorm.
 -4.071 - Fixed a bug in SMD animation parsing.
 -4.071 - Made SMD geometry loading less stupid. (now takes 10% of the time, fixed various bugs)
 -4.07 - Added support for 1bpp PNG images.
 -4.07 - Fixed handling of 4bpp PNG images in certain dimensions.
 -4.07 - Fixed handling of non-3bpp/4bpp JPEG images.
 -4.069 - Fixed a crash in Python vertex color handling.
 -4.068 - Fixed possible overwrite issues with the auto-updater.
 -4.067 - Fix for a problem introduced with the DNF plugin by the last release.
 -4.066 - Significant restructuring of native plugin code. Old plugin binaries will still work fine, but to compile old plugins against the new SDK, you'll have to make some changes.
 -4.066 - Made removal of temp files check for failure cases.
 -4.066 - Fixed a crash in the MFC splitter caused by broken IntelliMouse scroll handling, because I actually found this crash in my report list.
 -4.065 - Running Noesis with "?multinstance" on the commandline will allow multiple instances.
 -4.065 - Fixed a potential crash in the ISO extractor.
 -4.065 - Fixed pixel order being incorrect for 4bpp PNG images.
 -4.065 - Fixed log windows being limited to 30000 characters by default.
 -4.065 - Fixed some JK:MotS levels not being recognized as MotS format. (thereby causing Noesis to crash)
 -4.065 - Fixed TIM2's sometimes being incorrectly swizzled. This was breaking Saint Seiya.
 -4.065 - Fixed a bug in the SMD parser which was causing bad results on vertices with 0 weights. Thanks to Badcrc for reporting this bug.
 -4.064 - Fixed a potential crash in the GMO loader.
 -4.064 - Fixed a crash when loading invalid NJCM data.
 -4.063 - Made rpgCommitTriangles even more bulletproof.
 -4.063 - Fixed possible crash when feeding None for the index buffer to rpgCommitTriangles.
 -4.062 - Updated to FBX SDK 2013.3. The FBX plugin now exports to FBX 6.0 by default for compatibility. Use -fbxnewexport to export the most current version.
 -4.061 - Added noesis.getSelectedDirectory.
 -4.061 - Browse in the user prompt for directory selection now auto-browses to the last selected directory.
 -4.061 - Made the debug log suck less.
 -4.061 - Also made the export log suck less.
 -4.061 - Unsupported archives no longer show up in the shell view.
 -4.061 - Fixed shell view sometimes leaking items, sped up filtered views.
 -4.06 - Added Safe versions of all the rpgBind* functions to the native API. Python now uses safe functions by default, which do bounds checking against buffers using triangle indices upon commit to prevent crashes from scripts feeding bad data. noesis.RPGOPT_UNSAFE can be used to override this behavior, however.
 -4.055 - If a TIM2 image type is > 5, Noesis subtracts 5 and auto-untwiddles. This seems to handle some new types provided by brienj.
 -4.055 - TIM3 files are only untwiddled if dimensions are > 64.
 -4.055 - Added rapi.compressInflate to Python API. See the official Noesis plugins repository for an example script that deflates and inflates.
 -4.055 - Fixed a potential crash in the TPR/GMD loader.
 -4.055 - Made ASE importer use the material name correctly.
 -4.055 - Added support for 32bpp BMP's.
 -4.054 - Added new "Always use vertex colors" option in persistent settings. Vertex colors will not be previewed by default if every vertex color is identical. (that functionality was accidentally disabled for quite a few builds)
 -4.054 - Fixed a bug with Noesis filtering the file view by Explorer display name instead of actual file names.
 -4.053 - TSPR format now supports loading images in any supported image format.
 -4.053 - Added "cropWidth" and "cropHeight" properties to TSPR entries.
 -4.053 - Fixed a typo that could result in a crash when doing a clamped bilinear resample on images.
 -4.052 - Now renormalizing quaternions for NMDM animation.
 -4.051 - Corrected -fbxframerate breaking when using a framerate below 20.
 -4.051 - Added -fbxframecount to force a frame count for FBX animation sampling.
 -4.051 - Added -fbxnoextraframe to disable single frame insertion for FBX animation sampling. (this is done by default because of inconsistent behavior across FBX exporters)
 -4.05 - Added support for NMDM animations.
 -4.05 - Overhauled the NJCM loader. Now supports multiple vertex weights.
 -4.05 - Added support for NJCM vertex index overrides. (fixes a number of models, particularly ones from IllBleed)
 -4.05 - Point-only models use vertex colors (if available) in preview mode.
 -4.05 - Changed IQM output to write number of elements in vertex array structure, instead of the vertex buffer size. Thanks to taniwha for discovering this issue.
 -4.05 - Added import support for Sonic Shuffle (Dreamcast) models/anims.
 -4.05 - Record of Lodoss War (Dreamcast) models will automatically load animations as well, if they're present in the same directory.
 -4.041 - Color fix for RGBA4444 Dreamcast PVR textures.
 -4.04 - Added import support for Space Channel 5 (Dreamcast) models.
 -4.04 - Added noesis.getPluginsPath / NPAPI_GetPluginsPath.
 -4.04 - Added noesis.getOpenPreviewFile / NPAPI_GetOpenPreviewFile.
 -4.04 - If a model fails to reload after an automatic plugin reload, the file is loaded again automatically after the next auto-reload unless another file is opened before then. (so that when you mess up a Python script and it prevents your model from reloading, you don't have to manually load it again after fixing your script)
 -4.04 - Python errors from automatic plugin reloads will not MessageBox, and will pop the debug log up to print them if it isn't already open.
 -4.04 - Fixed a potential bug reading ISO directory records.
 -4.04 - Fixed a bug where models could be incorrectly scaled in viewer or not draw triangle data if there was a geometryless model in the middle of a model list.
 -4.03 - Added rapi.unpackPS2VIF to the Python API. This method takes raw VIFcode bytes and returns a list of unpacked components.
 -4.03 - Fixed a bug in the FF13 extraction support, made it more robust so that it also handles FF7:DoC archives.
 -4.03 - Added -arcnooverwrite option, to prevent overwriting when extracting archive files. This only functions with newer (or non-internal) archive handlers, since some of the old ones haven't been updated and still do their own I/O handling.
 -4.03 - Contents of ISO 9660 images are now extracted, even if the image does not contain any special filesystem.
 -4.02 - Partial FF12 animation support. (still don't have channel deltas working correctly, so you only get sequence base frames)
 -4.02 - Added rapi.decompPRS and rapi.getPRSSize, to handle PRS compression which is used in a variety of Sega games.
 -4.02 - Added an "Auto-reload scripts" option under Persistent settings->Other. Plugins must be reloaded for changes to the setting to take effect. If enabled, Python scripts are automatically reloaded when any .py file is changed under the plugins\python directory. Other scripting plugins may also choose to implement this setting.
 -4.02 - Corrected an issue with animation hierarchies sometimes not being preserved when fed without models from plugins.
 -4.02 - When script load errors occur, if the debug log is open and script auto-reloading is enabled, the error will not pop up as a messagebox and will instead only print to the debug log.
 -4.01 - Fixed some FF12 models missing surfaces from incorrect draw list handling.
 -4.01 - Fixed incorrect texture-CLUT combinations being used in some FF12 models.
 -Added FF12 model import support. Thanks to revelation for providing me with his notes on this format!
 -Added FF12 ISO filesystem and decompression support.
 -New material expression system, which allows script/plugin writers to do things like vertex deforms, texture animations, and more using simple expressions.
 -Fixed VIFcode processor not re-aligning to 32-bits after unpack operations.
 -Fixed a bug in 4bpp PS2 texture untwiddling.

Version 3.9 - 3.997:
 -3.997 - Added Noesis_CopyInternalTransforms, to allow grabbing transform buffers directly from the internal model.
 -3.997 - Fixed a GL state error when using a pre-render visualizer callback.
 -3.996 - Added "Visualizers". Plugins can now register visualizers to hook into preview rendering. See example_visualizer01 (effect rendering) and example_visualizer02 (allows you to select and export triangles) in my folder on the plugins repository.
 -3.996 - New shared Noesis GL interface for native plugins to perform API-agnostic rendering.
 -3.996 - Tool menu items can now be checked/unchecked, using noesis.checkToolMenuItem.
 -3.996 - New optional parameter at the end of registerTool allows tools to specify their help text. (which is displayed in the Noesis status bar when the user mouseovers the tool menu item)
 -3.996 - New math functions: Math_WorldToScreenSpace, Math_ScreenToWorldSpace, Math_PointRelativeToPlane, Math_LineIntersectTri.
 -3.996 - Added Noesis_RegisterUserButton, which allows native plugins to register new model control buttons.
 -3.996 - Fixed a Python print-related crash. Thanks to demonsangel for reporting the crash.
 -3.996 - More interface cleanup. Anim slider moves above buttons if window is too small for it to fit next to buttons.
 -3.995 - Small interface cleanup.
 -3.994 - Added import support for Stainless MDL/CNT files.
 -3.994 - Added import support for Stainless TDX files.
 -3.994 - Added extraction support for Stainless WAD files.
 -3.994 - Added rapi.createBoneMap. See example_bonemaps.py in the Noesis scripts repository for usage. Also keep in mind that you can use -maxbones # when exporting models to have Noesis automatically split meshes to keep bone reference counts under #.
 -3.994 - Added noesis.setTypeExportOptions, to specify default export options for a type. Also see example_bonemaps.py for usage.
 -3.994 - Static chrome UV's are now used for HL1 MDL chrome surfaces.
 -3.994 - Corrected a bug with HL1 MDL normals. Also added -hlmdlnonrm to discard HL1 MDL normals.
 -3.994 - Fixed a typo that was making setFlags unusable in the NoeTexture class. Thanks to demonsangel for spotting it.
 -3.994 - Now recognizing 0 and NaN cases in the half-float decode function. Thanks to demonsangel for pointing out that this was not happening.
 -3.994 - Fixed another typo in the NoeBitStream class. Thanks to demonsangel for spotting this one too.
 -3.994 - Added Noesis_InputReadFile/Noesis_InputReadFileW, which read files into memory relative to the path of the input file.
 -3.994 - Added RPGOPT_SWAPHANDEDNESS.
 -3.994 - Added swapHandedness methods to NoeMat43 and NoeMat44.
 -3.993 - Bug fixes.
 -3.992 - The animation slider is now next to the control buttons instead of above them by default. Old behavior can be restored with the new "Long anim slider" option under persistent settings in the data viewer.
 -3.992 - Auto-play anims is now the default behavior.
 -3.992 - Fixed shortcut keys not being registered sometimes when the preview window pane is selected.
 -3.991 - Added a new animation slider for quickly skipping through animations. The slider will only appear after animations have been initially started in the preview.
 -3.991 - Added an optional argument for rapi.createTriStrip, which allows the user to specify a strip break value. (if provided, the generated strip will use this value to reset strips instead of inserting degenerate faces)
 -3.991 - Added an "Auto-play anims" option to the persistent settings under "Other". This will automatically start playing animations in a loaded model, even if its loader module does not default to auto-play.
 -3.991 - A few small documentation and bug fixes.
 -3.99 - Added a "nextPass" field to NoeMaterials. This can reference a material that is inside or outside of the main material list, and allows you to perform n-pass rendering. Note that if the nextPass material is not in the main material list, it will not be included in exported material lists to other formats, unless the exporter in question has special handling for nextPass materials.
 -3.99 - Added rapi.decompressEdgeIndices.
 -3.99 - Added MvC3 PS3 index support.
 -3.99 - Added Noesis_PS2_ProcessVIFCodes to native RAPI interface.
 -3.99 - Added Noesis_PS2_RPGCommitLists, Noesis_PS2_GetComponentIndex, and Noesis_PS2_RPGHandleChunk for automatically handling and committing PS2-standard geometry chunk types.
 -3.99 - Various bug fixes.
 -3.98 - Added Silent Hill: Homecoming model/texture import and archive extraction support.
 -3.98 - Specular maps are now used by default (if present) in render preview.
 -3.98 - Corrected a bug causing W component of tan4's to be incorrectly preserved when binding buffers in the RPG interface.
 -3.98 - Specular color material property is no longer readonly.
 -3.98 - Fixed a new COLLADA export bug which was introduced in 3.97.
 -3.98 - Added RPGOPT_DERIVEBONEORIS, which will automatically generate bone orientations from vertex weights when using the RPG interface.
 -3.98 - Added RPGOPT_FILLINWEIGHTS, which will automatically fill in vertex weights from bone orientations when using the RPG interface. Only applies to meshes which have no vertex weights.
 -3.98 - Added rpgConvertTangents, to generate tan4 components from full tangent matrices.
 -3.971 - Added rapi.imageGaussianBlur.
 -3.971 - Various bug and leak fixes.
 -3.97 - Added rapi.toolLoadGData, rapi.toolFreeGData, rapi.toolSetGData, rapi.toolExportGData, rapi.toolGetLoadedModelCount, and rapi.toolGetLoadedModel. These functions are intended for tool scripts, and allow loading/saving/manipulating any kind of supported (models, textures, etc.) data.
 -3.97 - Added noesis.instantiateModule, noesis.freeModule, and noesis.setModuleRAPI. These functions allow you to insantiate modules and set the active rapi module context, and are intended for use with tool scripts.
 -3.97 - Added noesis.getSelectedFile to get the path of the currently selected file in the Noesis browser.
 -3.97 - Added noesis.loadImageRGBA and noesis.saveImageRGBA. These are mainly for convenience, as the same functionality can be achieved with the new module instantiation and tool methods.
 -3.97 - Added a "Use memory mapping" persistent setting. This may result in a barely-detectable performance penalty in some situations, but will utilize 64-bit address space for some of the Noesis interfaces in order to circumvent some 32-bit memory limits.
 -3.96 - Added HL1 MDL import support.
 -3.96 - Added a "Snapshot" button to the Kinect dialog.
 -3.96 - Fixed multiple memory leaks in JK support.
 -3.96 - Fixed a possible crash when reporting memory leaks.
 -3.96 - Improved memory management for MD3 export, also capping import frame count when necessary.
 -3.96 - Added NOEUSERVAL_SAVEFILEPATH to compliment NOEUSERVAL_FILEPATH.
 -3.95 - Added support for bone-only NMD files.
 -3.95 - Fixed a potential crash on export with no geometry.
 -3.95 - Added Castlevania Dracula X Chronicles .res extraction support.
 -3.95 - GMO's which do not contain internal textures now use the correct external material reference names.
 -3.94 - Added a fullscreen preview option. (View->Fullscreen in the menu)
 -3.94 - Added extraction support for Jedi Knight/Mysteries of the Sith GOB/GOO files.
 -3.94 - Added import support for JK/MotS MAT textures.
 -3.94 - Added import support for JK/MotS 3DO models.
 -3.94 - Added import support for JK/MotS KEY animations.
 -3.94 - Added import support for JK/MotS JKL models.
 -3.93 - Added NPAPI_UserSettingWrite/NPAPI_UserSettingRead, which allows native plugins to write/read settings in the Noesis registry section.
 -3.93 - Added NPAPI_Threads_DoJob and NPAPI_Threads_JobDone, so that plugins can offload tasks to the multi-threaded Noesis job system.
 -3.92 - Extended "mergeBones" option again. If it is set to 3, functionality for 2 performed, and geometry is also transformed with new bone matrices.
 -3.92 - Added a "renameBone" option for the .noesis scene files.
 -3.92 - Fixed a possible memory leak caused by the merging of textures between 2 different models.
 -3.91 - Extended "mergeBones" option. If it is set to 2, relative bone transforms are re-applied after the bone collapse.
 -Added "mergeTo" and "mergeBones" options for .noesis scene files, which allow models (and their skeletons/animations/materials) to be merged into a single model.
 -Exposed new noesis.getScenesPath method.
 -Exposed new noesis.openFile method.

Version 3.8 - 3.89:
 -3.89 - Added a generic input prompt method, noesis.userPrompt.
 -3.89 - Added a new method for scripts to regiser tools, noesis.registerTool. New tools will be listed under the Noesis "Tools" menu once they're registered.
 -3.89 - Added anaglyphic stereoscopic rendering, which can be enabled through the data viewer. (Persistent settings->View->Anaglyph 3D) Anaglyphic rendering obeys all of the same stereo settings as quadbuffered stereo rendering. (quadbuffering is only functional, to my knowledge, on nVidia Quadro cards)
 -3.89 - Fixed matrix translation being uninitialized memory when converting a quaternion to a 4x3 matrix in Python.
 -3.89 - User preference version value has been changed, so your preferences will be reset when you run this version.
 -3.89 - Other assorted fixes and additions that I've lost track of.
 -3.881 - Now grabbing proper texture names from PVM files.
 -3.88 - Updated OpenNI implementation to 1.5.
 -3.88 - Added an "Append" record option in the Kinect interface. This will append new frames to the end of the existing framelist, instead of overwriting.
 -3.88 - Added Dreamcast PVM file support.
 -3.872 - Optimized the rpg vertex structure to lower memory usage very significantly.
 -3.871 - Defaulting to flat shading for STL import.
 -3.87 - Added import+export support for Standard Tessellation Language (STL) models.
 -3.87 - Added prevention for recursive exceptions in the exception handler, in the event that things are somehow so broken that the exception handler itself crashes. (and/or a crash occurs in the messagepump for the report dialog)
 -3.866 - Passing a negative bit value into the PVRTC decoder will force bilinear lookups. The results can be visually inferior, but are more authentic. (in line with official PVR hardware and viewers)
 -3.866 - Added CRC validation to the auto-updater.
 -3.866 - Corrected a bug that was causing non-default blend modes on lightmap materials to not be obeyed.
 -3.866 - Made the outpath path for the batch exporter scriptable. Do not abuse this.
 -3.866 - Random bug/crash fixes.
 -3.865 - Yet more timing/messagepump bug fixes. (I just had the chance to try Noesis on a horribly underpowered machine, it's flushing this stuff out of the woodwork)
 -3.864 - When message throttling is enabled, paints are also aborted if other messages are in the queue. This prevents Noesis from flooding the queue on systems with incredibly bad rendering performance.
 -3.864 - Exposed interval of regular update timer in the system settings. (mostly for diagnostic use)
 -3.863 - Fixed a rather nasty bug in the data viewer that could result in a crash when texture/animation counts happened to be just right.
 -3.862 - Exposed noesis.morton2D in Python.
 -3.861 - Small fix for Python immediate-mode drawing.
 -3.86 - Added -imgbicubic, to force bicubic sampling. (instead of bilinear)
 -3.86 - Added -imgcrop.
 -3.86 - All image operations are now correctly stacked and performed in the order that the arguments are provided.
 -3.86 - Added noesis.NTEXFLAG_FILTER_NEAREST and noesis.NTEXFLAG_WRAP_CLAMP so that scripts can provide texture mode hints.
 -3.86 - If a texture is being previewed and using nearest filtering, it will be snapped to the nearest fixed point offset, as well as round to the nearest fixed point zoom level with a 0.1 threshold. (in order to allow easier examination of uniform pixels)
 -3.86 - Fixed a crash when passing NULL vertex components in with immediate-mode rendering. (this is valid behavior for removing active components)
 -3.86 - Moved COLLADA from the Noesis core into an external plugin module. I fixed some material/texture issues with it while I was at it.
 -3.858 - Added support for 1bpp, 4bpp, and 16bpp BMP files, as well as RLE compression modes.
 -3.857 - Exposed external texture material name strings in the data viewer.
 -3.857 - Added support for 8bpp BMP files. (note: BMP support is still half-assed)
 -3.856 - Added ability to reset XMem LZX streams every n frames (in addition to specifying the use of frame reset/size data) by providing negative frame intervals.
 -3.856 - Fixed some output naming/extension bugs.
 -3.856 - Fixed subsequent images not being written out in the selected image format for data sourced from an image (as opposed to model) import.
 -3.855 - More various bug/crash fixes, and corrected a bug that could cause Model_LoadNoesisTexturesForModel to incorrectly grab duplicate textures.
 -3.854 - Various bug/crash fixes.
 -3.853 - Added support for extracting Desert Strike archives, and import support for its picture/sprite graphics.
 -3.852 - Added a high-precision PVRTC decoder function to native and Python API's. Also included a simple script to parse PVRTC-compressed .pvr files in V2 and V3 form.
 -3.852 - Fixed a bug in the "load TIM2" plugin extension which was causing returned texture data to always be untwiddled.
 -3.851 - Quick fix to make UV viewer work on meshes without textures. (a red default background is used)
 -3.85 - Added a "UV flip" property for meshes in the data viewer, as well as a "Global UV flip" under the model. If the global UV flip is set, it will override any per-mesh preferences.
 -3.849 - More GMO fixes. Discovered a couple of places where the GMO loader was crapping all over the stack. Fixed those instances and moved some arrays to the heap with write boundaries. Be on the lookout for new crashes! (and submit them if they come up)
 -3.849 - Exposed a "Culling flag" property for meshes in the data viewer. 0 = default culling mode, 1 = no culling, 2 = reverse culling.
 -3.848 - Added a bunch of new immediate-mode drawing functions to the Python interface.
 -3.848 - Added recognition of reset state command to LZX decompressor.
 -3.848 - Fixed another GIF import bug where row offset wasn't being correctly applied for non-interlaced images.
 -3.848 - Fixed a crash in the GMO loader, and fixed several triangle indexing bugs.
 -3.848 - Added rapi.loadMdlTextures to the Python API, see __NPReadMe.txt for usage.
 -3.847 - I really need to stop jumping the gun on new releases. More GIF fixes, cumulative transparency is now handled correctly, and the GCE flush flag is now obeyed. Also exposed additional texture info in the data viewer.
 -3.845 - Added automatic texture animation to preview mode. When a file is loaded which has an array of textures but no model, the textures will automatically begin cycling. You can also pause the cycling and jump back and forth with the arrow buttons.
 -3.845 - Made image framerate preserve for GIF export if it exists. This also preserves framerate across GIF-GIF conversions. If -gifdelay is used, that value still overrides existing per-frame timings.
 -3.844 - Added -gifnoalpha, which eliminates alpha masking on GIF import and allows Noesis to preserve cumulative screenbuffer effects.
 -3.842 - Small adjustment to color reduction for GIF files.
 -3.841 - Quick fix to pluginshare.h.
 -3.84 - Added Decomp_XMemLZX (native API) and decompXMemLZX (Python API) for decompressing XMemCompress (or other MS LZX) streams.
 -3.84 - Added import support for Grandia 2 models. Thanks to Mat for his work in figuring out the compression used in this game.
 -3.84 - Added import support for Love Hina: Smile Again models.
 -3.84 - Added import/export support for GIF images. For animated images, additional frames can be viewed under "Textures" in the data viewer. When exporting to the GIF format, a batch writer is used which grabs all textures/images being exported and writes them to a single animated GIF file.
 -3.84 - Added a maximum length for the export log buffer, can be changed under System in the data viewer.
 -3.84 - Enabled support for extracting MVC3 360 .arc files.
 -3.84 - Improved color precision and contrast of the median cut algorithm.
 -3.84 - Added NPAPI_SetTypeHandler_WriteRGBABatch for image formats that want to export from all texture sources in a given export process.
 -3.84 - Added Image_GetTexRGBA to get raw RGBA32 data from a Noesis texture regardless of its internal format.
 -3.84 - Fixed a crash where Noesis could mistake unrelated data for being a Quake BSP file.
 -3.84 - Fixed a potential crash in validation of .ico files.
 -3.84 - Fixed a bug where outputting to a batched image format (like .spr) was not working in conjunction with model export.
 -3.84 - Fixed a potential conflict when exporting to a format with the same file extension as another different format.
 -3.832 - Quick fix for Python bitstream class.
 -3.831 - Added crude support for NS:UNS2 models. No skeleton (seems to be in a different file), material assignments are usually off, some meshes are offset, and some meshes just have screwed up verts. Seems like a vertex format or offset issue, haven't looked into it.
 -3.83 - Added a viewing mode for UV coordinates. (select "UV view"/"LMUV view" under the desired mesh in the data viewer)
 -3.83 - NMD files from SC5 are now loadable.
 -3.83 - Fixed a bug preventing materials from being assigned for Python export scripts.
 -3.83 - Fixed a bug where Noesis could overflow its message pump by spamming too many paint messages, causing the program to sometimes become unresponsive. The new behavior can still be reverted by enabling the "Disable message throttle" System setting, but this is not recommended.
 -3.83 - Fixed a COLLADA import crash, when a controller node instance does not reference a valid entity.
 -3.83 - Fixed an OBJ import crash when the file has out-of-range indices.
 -3.83 - Fixed a crash when attempting to load TEX files with bad mip offsets.
 -3.83 - A couple of fixes to the device image creator. It will now skip over unreadable sectors and fill them out in the image file instead of aborting when it hits them.
 -3.82 - Quick fix for XPR files being incorrectly recognized as NG2/DOAX2 models.
 -3.81 - Fixed a potential FBX crash, where the FBX gives control point indices that are out of range.
 -3.81 - Fixed several potential crashes in the md5mesh loader.
 -Fixed a potential crash when extracting FFX disc images.
 -Fixed a potential crash when loading unsupported Source MDL files.
 -Various other small additions and fixes.

Version 3.7 - 3.79:
 -Now applying an unroll filter before exporting FBX animation rotation curves, which typically fixes bad linear interpolations when playing animations back from other FBX viewers/importers. Special thanks to Viviane Rochon for informing me of this solution.
 -Lots of under-the-hood changes. Things may explode. I'm interested in crash reports, so send them in, and try to make them useful. (e.g. provide sample files, and ideally provide process module base addresses with instruction pointer offsets for each thread)
 -3.71 - Upped the bone name limit in the Python plugin to reflect the new limit in the bone structure.
 -3.71 - Made UMvC3 models load.
 -3.72 - Added Zegapain XOR support to Bullet Witch Python script.
 -3.72 - Optimized vertex structure and memory use for the procedural geometry interface, and removed the 16 weights per vertex limit.
 -3.72 - Added decompLZHMelt/Decomp_LZHMelt to the Python/C++ API's.
 -3.73 - Added rpgSetStripEnder/rpgGetStripEnder to specify (or get) the value which ends/resets triangle strips mid-buffer. For most console games this should be set to 0xFFFF, but it can differ per title.
 -3.73 - rapi.createProceduralAnim is now available in Python, with a new NoeProceduralAnim object for specifying procedural animation parts. See the commented out example in the Bullet Witch script.
 -3.73 - Added a readline method to the NoeBitStream at the request of chrrox.
 -3.73 - Exposed and tested loadTexByHandler in Python. Example use:
	def proxyLoadRGBA(data, texList):
		f = open("c:\\other\\somefile.jpg", "rb")
		tex = rapi.loadTexByHandler(f.read(), ".jpg")
		f.close()
		if tex is not None:
			texList.append(tex)
			return 1
		return 0
 -3.73 - Now resetting the bit pointer in the stream container when doing a byte-level seek.
 -3.73 - Updated BVH plugin to use the new bone name string limit.
 -3.73 - Fixed a bug causing validateListType to sometimes raise its exception in the wrong place.
 -3.73 - Added support for ATI1 (BC4) DXT compression. ATI2/BC5 has already been supported for a while.
 -3.73 - Added support for Dead Rising 1 360 .tex files.
 -3.73 - Fixed MVC3 360 spec maps not being handled correctly.
 -3.73 - Added support for 360 DMC4/RE5/LP .tex files. PS3 files are not supported.
 -3.73 - Added support for 360 DMC/RE5 .mod files. PS3 files are untested and probably don't work.
 -3.73 - Added support for 360 LP/DR1 .mod files. Not well-tested, but works on the files I've tried.
 -3.73 - Fixed certain material properties not being obeyed in the preview render with externally-loaded textures.
 -3.73 - Fixed a potential crash when loading external textures without extensions on a wide-character path.
 -3.74 - Special thanks again to LUBDAR for another donation!
 -3.74 - Added FFXIII-2 support.
 -3.74 - Made normal/spec/etc. texture index properties in data viewer modifiable.
 -3.74 - Now looking for XDVDFS markers at 0x2080000 as well for ISO extraction. (this handles FFXIII-2 for 360)
 -3.741 - Quick bugfix for FFXIII-2.
 -3.742 - Another quick fix for loading PS3 FFXIII-2 models. If the image bundle extension is .ps3.imgb (which means the model's extension must be .ps3.trb), then the texture data will not be untiled.
 -3.75 - Another thanks to dear old brother Bradford for an uneven-penny'd donation, and a congratulations for another set of academic milestones met. :)
 -3.75 - Added a custom exception handler which can send off crash logs to my web site. Please say yes when it asks you if you want to send the log.
 -3.75 - Noesis is now capable of auto-updating itself. There is an option to check for updates in the Tools menu, as well as a persistent option (accessible from the data viewer) to tell it to automatically check for updates on startup.
 -3.75 - Added support for .RZL+.RZP archives, used in Lord of Apocalypse and possibly other games.
 -3.75 - Removed link dependency on psapi.dll.
 -3.751 - Made the debug log window resizable.
 -3.752 - Changed default HTTP transfer timeout.
 -3.76 - Kinect support (with OpenNI/NITE) is working again.
 -3.77 - Removed all OpenGL dependencies and integrated a new graphics API standard into all of the Noesis modules. A new graphics module that uses OpenGL is now provided. (Direct3D and/or software renderers will probably be coming in the future)
 -3.77 - Fixed another bug in the Kinect module.
 -3.77 - Added RPGEO_QUAD_ABC_BCD, RPGEO_QUAD_ABC_ACD, RPGEO_QUAD_ABC_DCA to cover other common quad index order conventions. (RPGEO_QUAD is ABC_DCB, as now denoted by the comment in pluginshare.h)
 -3.77 - Fixed a crash in the SMD loader.
 -3.77 - When you select a bone in the data viewer, shift+clicking will auto-enable the bone's transform offset and allow you to rotate the bone with your mouse. (left and right buttons control which axes you're rotating)
 -3.77 - Fixed a bug that occurred when parsing OBJ files with blank usemtl entries.
 -3.771 - Fixed another crash in the SMD loader, and a bug in the SMD exporter with textures that have spaces in their names.
 -3.772 - Various fixes for the new rendering system.
 -3.774 - Dependency fix for the ODE physics module.
 -3.775 - Fixed a "reload plugins" crash that was introduced by the new renderer changes.
 -3.78 - Copied animations will now be exported with secondary models as well as the primary. (GMO files with multiple models and animations shared between models were only getting animations exported with the first model in the file)
 -3.78 - Added "sharedAnims" option for .noesis files.
 -3.79 - Fixed a crash when loading COLLADA files and encountering NULL child node or scene root pointers.
 -3.79 - Fixed a crash when trying to generate vertex normals for a mesh with no vertices or out-of-range triangle indices.
 -3.79 - Added more post-load sanity/safety-checking logic for triangle/weight/etc. values.
 -3.79 - Weapon models for Zell and Kiros are now loadable with the FF8 module. The skeleton is stored externally for those weapons, so you'll be required to select a Zell/Kiros character model when you load the weapon model in order to import the skeleton.
 -3.79 - Fixed a bug introduced by the recent renderer changes that was causing Noesis to upload resize some non-power-of-2 textures even on hardware with NPoT texture support.
 -3.79 - Noesis will now obey the reported maximum texture size from hardware and resize textures appropriately before uploading.
 -3.79 - Fixed a possible crash when loading non-power-of-2 DXT data on hardware without NPoT texture support.

Version 3.6 - 3.69:
 -Added support for DOTA2 (and maybe others) Source MDL files. Special thanks to Quest and chrrox for providing test files.
 -Fixed a possible reference count error when exporting animations from Python.
 -Changed geometry lists provided by the Python implementation to default to tuples instead of lists, since they usually aren't modified after being handed back.
 -Added .mtl import/export. To export .mtl with .obj, -objmtl must be used.
 -3.61 - This build is hereby dedicated to Bradford, for sending me another 10 dollars via PayPal to spend on booze.
 -3.61 - Added import/export of FBX files. Don't bug me about issues related to scaling, rotation/orientation, UV flipping, or vertex normals. Max tends to screw normals up when importing with skin modifiers. (if you want normals intact you can uncheck deformers in the FBX import options) Seems like a bug in the FBX SDK and/or Max importer.
 -3.61 - Fixed handling of weights for Source MDL dx90 vertices.
 -3.61 - Improved validation of FF Type-0 models to eliminate false positives. (only tested on Japanese demo)
 -3.62 - Thanks to firsak for another PayPal donation! I think I've spent enough on booze though. I guess I'll order a pizza.
 -3.62 - Fixed filetype filter being case-sensitive for formats with capital letters in their extensions. Thanks to revelation for discovering this one.
 -3.63 - Fix for crash on load of some FF Type-0 models.
 -3.64 - Fixed a bug where the checked file extension was not correctly reset at times. (as far as I know, this only caused bugs with identifying file types in the status bar)
 -3.65 - Added a scene scale setting, in the data viewer under persistent settings. Acts as a multiplier for the preview scene scale. (which mainly affects movement speed and clipping planes)
 -3.65 - Added a "recenter on meshes" option in the data viewer under persistent settings. When enabled, this will cause the preview view to recenter on meshes when you select them in the data viewer. Useful for extremely complex scenes.
 -3.65 - Added more under the hood error-checking for incoming bone and animation data.
 -3.65 - Fixed an issue with FBX import where initial mesh matrix was not accounted for on skinned meshes.
 -3.66 - Now handling multiple animation stacks in FBX scenes.
 -3.66 - New double-precision modes and functions in the API.
 -3.66 - Switched FBX plugin over to double-precision for everything, and added re-normalization of weights if any error is present at all instead of an error of more than 0.0001. (I ran into some extremely large scenes where weighting precision was causing vertices to drift over long distances)
 -3.67 - Fixed a possible crash with bone name length in the IQM plugin.
 -3.67 - Fixed a bug which was preventing Noesis from sleeping between frames, and exposed standard and background frame intervals in the persistent settings in the data viewer.
 -3.67 - Added -fbxscalehack for the FBX plugin. The current FBX SDK is failing to correctly incorporate scale into local and global transforms, this is a hack workaround for that.
 -3.68 - Fixed a possible crash in skin handling for Quake MDL files.
 -3.69 - Added automatic filtering of output image names, added Noesis_FilterFileName and Noesis_FilterFileNameW to the API so that plugins can use the same filename filtering methods that Noesis uses internally.
 -3.69 - Enforced correct struct alignment for structures in pluginshare.h.

Version 3.5 - 3.59:
 -Added the ability to feed tangent vectors into the RPG interface.
 -Optimized allocation scheme for the generic "get unique elements" function exposed in the C/C++ plugin API.
 -Added rpgSetOption/rpgGetOption. rpgSetOption has eliminated the need for rpgSetEndian and rpgSetTriWinding.
 -Various other mostly-behind-the-scenes fixes and optimizations.
 -3.51 - Added rapi.imageDecodeRawPal.
 -3.52 - Added Quake II .wal import+export support via Python script.
 -3.52 - Added Quake II .bsp import support via Python script.
 -3.52 - Added Noesis_LoadExternalTex/rapi.loadExternalTex.
 -3.52 - Added rpgSetLightmap, allows lightmap and/or second-pass rendering to take place with named material references.
 -3.53 - Changed Quake II lightmap packing. (traded off better packing for better load time and batching)
 -3.53 - Added lightmap material property to meshes in the data viewer.
 -3.54 - Added rapi.getInflatedSize for chrrox.
 -3.55 - Added rapi.loadTexByHandle, various other changes/fixes.
 -3.56 - Unified the animation preview functionality between models with anims and anims without models.
 -3.56 - Added mouseover status bar help tips for the model control buttons. (suggested by Tomaz)
 -3.56 - Added import and export support for BVH animations.
 -3.56 - Various additions/changes in plugin API land.
 -3.57 - Added software-resizing of image data before uploading non-power-of-2 textures on hardware where they aren't supported.
 -3.58 - Added base orientation change option to anim-only preview mode.
 -3.58 - Added an optional new flags parameter to imageDecodeRaw/imageDecodeRawPal in the Python API. See the DECODEFLAG_* values listed in __NPReadMe.txt.
 -3.58 - Added imageScaleRGBA32 to the Python API.
 -3.59 - Compiled CRT into Python library to circumvent a stupid Wine problem, and added/fixed a few other things.

Version 3.4 - 3.49:
 -Rebuilt plugins to force dependencies on older versions of the MSVC runtimes.
 -Added a "Making Plugins" section to the ReadMe.txt.
 -3.41 - Added stereoscopic rendering. Only works on hardware capable of creating a windowed stereo context. (like Quadro cards)
 -3.41 - Added a stereo option to the ultra-shot, to generate stereo renderings. This doesn't require stereo-capable hardware.
 -3.41 - Stereo rendering parameters (and other stuff, which will likely continue growing) can now be set in the "Persistent parameters" section of the data viewer. Some changes (such as enabling stereo) may require Noesis to be restarted to take effect.
 -3.42 - Fixed GL context going bad after using the "Reset all" option.
 -3.43 - Added NTEXFLAG_STEREO flag for textures.
 -3.43 - Added import+export support for JPS (stereo image) format.
 -3.43 - Added import+export support for MPO (stereo image) format. Now you can directly convert and transfer Noesis stereo renders for 3D viewing on your Nintendo 3DS.
 -3.43 - When previewing stereo images in active stereo mode, Noesis will now recognize this and display the correct image for each eye.
 -3.43 - Added a stereo texture offset option for stereo image display.
 -3.43 - Added a stereo eye swap option.
 -3.44 - Added -mpo3ds option, to force Nintendo 3DS header on MPO export. (allows you to use the offset slider when viewing the file on a 3DS - seems to only work on 640x480 images)
 -3.45 - Added -imgresz option, resizes all images to the specified dimensions.
 -3.45 - Added -imgmcut option, performs a median cut on all images.
 -3.46 - Added a new Python plugin. You can now write Python scripts to add support for new formats and other things. Special thanks to chrrox for helping test and provide feedback on Python stuff pre-release. Check out the plugins\python directory, or specifically plugins\python\__NPReadMe.txt for info on the Python implementation.
 -3.46 - Corrected the export dialog treating some image formats as non-image formats.
 -3.46 - Changed Quake PAK handler from memory streaming to disk streaming.
 -3.46 - Added support for extracting Duke3D .grp archives and viewing Duke3D .art tiles. (via Python script)
 -3.46 - Added import and export support for .m32 (Soldier of Fortune, possibly others) textures. (via Python script)
 -3.46 - Corrected a typo in one of the RichMat44 constructors.
 -3.46 - Added FF Type-0 model import. (note - the PKG extractor will try to detect .t0mdl files now and write them to a t0mdl folder, but it does get some false positives, so not all those t0mdl files are really models)
 -3.46 - Added Bullet Witch CPR model/texture import support, via Python script.
 -3.47 - Added Ofs variants for all of the rpgBind*/rpgFeed* Python functions, and changed the Bullet Witch script to use them.
 -3.47 - Added rpgConstructModelSlim, which omits various data types you probably won't need. (cuts BW load times in Python down by about 50%)
 -3.47 - Fixed some Bullet Witch models not getting their material names parsed.
 -3.48 - Small fix to array endian swap routine.
 -3.49 - Python math types can now operate with both tuples and lists. Changed the default type to tuple. (if you attempt to modify a tuple-based type, it will have to convert its internal storage to a list)

Version 3.3 - 3.39:
 -More DNF material additions/fixes, now correctly parsing most of the possible material parameters.
 -Added extraction of StaticMeshes for DNF.
 -Static DNF meshes can now be previewed/exported, but do not have material mappings. (due to the dependency order, this would have been a big pain in the ass)
 -3.31 - Added -mdlnobase option.
 -3.31 - Fixed a possible crash when resizing texture page for MDL output.
 -3.31 - Added Quake .spr import+export.
 -3.31 - Added .tspr import+export.
 -3.31 - Added Quake .lmp import+export.
 -3.31 - Fixed an alpha bug that occurred exporting RGB image data to RGBA PNG files.
 -3.32 - Updated the IQM plugin at the request of Randy. It now handles importing v1 and v2 files, and exports v2 instead of v1.
 -3.33 - Added new -vertbones option which creates a bone for each vertex. If the model has vertex anims, "skeletal" anims are generated for the per-vertex bones.
 -3.34 - Fixed crash in SMD importer with long bone names.
 -3.35 - Fixed BMP import/export not padding to 32-bit boundary for scanlines.
 -3.36 - Added support for extracting Record of Lodoss War (Dreamcast) data files, and exporting its model and texture files.
 -3.36 - Fixed a preview rendering bug with certain kinds of non-triangle geometry.
 -3.37 - Made PSK drop trailing spaces on bone names by default. Behavior can be changed back with -pskkeepspace.
 -3.38 - Various behind-the-scenes fixes and cleanup.
 -3.39 - Added Tales of VS .mgz support.
 -3.39 - Fixed possible GMO crash on line primitives.

Version 3.2 - 3.29:
 -Added MVC3 360 model/texture support. 360 .tex files must have a .360.tex extension to be handled correctly. Textures are not mapped properly, but materials are. Thanks to aluigi and chrrox for the 360 arc bms script.
 -Finally made DXT export handle non-power-of-2 images.
 -Other random changes/fixes.
 -3.21 - Fixed a bug that was causing .360.tex files to not be recognized as 360 .tex files.
 -3.22 - Added MDR import+export support.
 -3.22 - Re-sorted command line option print-out.
 -3.22 - Added NPAPI_AddTypeOption for plugin authors. This allows plugins to add new advanced/command-line options, and provide callbacks for those options.
 -3.22 - Properly preserving mesh names across various formats that weren't before, added mesh name redundancy checking.
 -3.22 - Fixed a bug with rotating/translating/scaling bones while exporting from files with multiple models.
 -3.23 - Added EF engine limit warnings to MDR plugin.
 -3.24 - Fixed a crash introduced by 3.22 for certain models with duplicate mesh names. (thanks to firsak for catching the crash)
 -3.25 - Made vertex culling routine a lot faster.
 -3.25 - Made IQM importer read mesh names.
 -3.25 - Fixed MDR crash when exporting without anims.
 -3.25 - Internal matrix->quaternion routine now does a better job at handling skewed matrix input.
 -3.25 - Redid mesh decimation functionality and changed command-line syntax.
 -3.26 - New DNF plugin, handles extracting 5 varieties of .dat files from the DNF demo.
 -3.26 - Small changes/fixes to the plugin API.
 -3.27 - Added DNF demo .msh support. Attempts to auto-load .skl and .def, as well as necessary resources from MegaPackage.dat and the texture directory. Most of the time attempts to auto-grab materials+textures will fail, however, as I still don't have the dmx/dtx files figured out well enough.
 -3.28 - Fixed DNF normal texture package handling - now handles bundled entries (e.g. normal+spec in a single file entry) and gets all the names right.
 -3.28 - Various new plugin API functions/features - check pluginshared.h.
 -3.29 - More DNF-related fixes/changes.

Version 3.1 - 3.19:
 -Added FF9 plugin. Supports extracting FF9.IMG and "ff9db" packages, as well as viewing resulting .ff9mdl and .ff9anm files. Only models/anims from dir07 (monsters) and dir10 (playable characters) are fully supported, though. Thanks to Satoh for sending along a lot of FF9 info, as well as Zidane2, Zande, Chev, and possibly others. (the docs I have don't contain any attributions)
 -Added "Image_LoadTIM1" extension for plugin authors.
 -Added a set of streaming file interface functions to the plugin API.
 -3.11 - Bone length fix for FF9.
 -3.12 - Made GMO anims load with no bone mappings, if there is only 1 bone and 1 anim track.
 -3.13 - Fixed some more GMO animation and bone scaling issues.
 -3.14 - Added Shadow Hearts .pack plugin, which reads the .pack files from chrrox's BMS script. Both models and anims are supported.
 -3.15 - Display UV coordinates for verts (when enabled) in data viewer.
 -3.15 - Added FX Fighter plugin, supports .dat models and autoloads .ani animations for character models.
 -3.15 - Added rpgSmoothNormals for plugin developers.
 -3.15 - Fixed a texture name export bug when using -texpre.
 -3.16 - Various things. Oh, and fixed a GMO negative scale bug.
 -3.17 - New console/command line mode, activated by ?cmode as the first command-line argument. Check the "Command Line Mode" section of this document for more info.
 -3.17 - A new Image_GetMedianCut function based on the work of Anton Kruger. Also made the .m8 exporter use this for better results from high-color images.
 -3.17 - More things that I haven't kept track of.
 -3.171 - Small addition to ?cmode functionality.
 -3.18 - Windows icon file import/export support. (I got sick of somehow never having a good icon exporter on hand) Doesn't do Vista/7-style PNG icons though, didn't have any on hand to test.
 -3.18 - More random fixes and crap.
 -3.19 - Replaced -loadrda with -loadanim, and made it work with any supported animation format. (including formats that are models+anims) -loadanim may also be specified more than once for anim concatenation.

Version 3.0:
 -Added support for Saint Seiya: The Hades GMI+TPL files. Plugin source is included. Thanks to fatduck for the file layout, and qslash for additional contributions.
 -Added support for DQ&FF in Itadaki Street Special JOB files. This is through the Saint Seiya plugin as the formats are very similar.
 -Added "Image_LoadTIM2" extension for plugin authors. See the ssthehades_gmi plugin for example usage.
 -Added a new option for SetPreviewOption - "noTextureLoad". Allows a plugin to disable auto-loading additional textures based on filenames for preview mode.
 -Added Noesis_AnimFromAnims and Noesis_AnimFromAnimsList functions for plugin authors. Combines multiple animations and sequences into a single animation with a sequence list.

Version 2.99:
 -Started writing a CPU emulator for the R5900. It can be invoked within Noesis to run native PS2 game code for specific tasks. The R5900 core will be exposed to plugin developers when it is more complete.
 -Added support for unpacking Bujingai's compressed .bin files. (the main AFS containers have already been supported by Noesis for a long time) This uses the R5900 core to decompress data, and find package index tables inside the game's ELF. I used symbol offsets in determining my points of code execution, so hopefully this will also work on different distributions of the game, but I make no guarantees.
 -Added import support for Bujingai models and textures. Praise be to Gackt! Materials will probably be messed up for most models, though, and level bits don't get snapped into place. And some stuff may just not work at all. Who knows. Animations are also loaded, but arm/leg bones are usually screwed up, because I'm not handling IK joints correctly.
 -Fixed COLLADA exporter bug where models that use multiple materials under the same name would only export a single material.
 -Fixed COLLADA vertex alphas not being imported.
 -Fixed problems with exporting to COLLADA with non-normalized vertex weights.
 -Added "No browse to target" option under the view menu. This prevents Noesis from browsing to the path of the loaded file in the shell folder view, as well as from browsing to the last selected folder on startup.
 -Added "Don't apply on drag" option under the view menu. This removes the prompt asking if you'd like to apply the model to the existing scene (if a scene is already open), and defaults to always loading the drag-and-dropped item as a new scene.
 -Now printing vertex indices next to individual triangles in data viewer.
 -Now printing bone indices, if applicable, next to individual vertices in data viewer.
 -Exposed Noesis_UntwiddlePS2 for plugin authors.

Version 2.9 - 2.982:
 -Added support for importing FFX models and animations. These would not be here without revelation, who provided a full spec for each. Thanks revelation!
 -Added support for FFX disc image extraction. Handles decompression and sorting files into folders. Thanks to revelation once again for the filesystem info!
 -Added support for The Bouncer's .tex, .fe. and .sk files. Thanks to shadowmoy for basic info on sk geometry!
 -Added support for The Bouncer's bouncer.bin, extracts .bin files recursively.
 -Added a "Create device image" option to the tools menu. Uses wnaspi32.dll to create a raw sector rip of the selected device. Will also continue reading beyond the device's reported size, if possible.
 -Added model/texture import support for TC:RS .ndp3 files. (skeleton+models+textures supported, but still a WIP)
 -Added extraction support for TC:RS .pac files.
 -Added T3B .pack model/texture import support. (note: not all .pack files contain model or texture data, and so some .pack files will not be recognized)
 -CommitTriangles can now be called with NULL data, which will automatically build an ordered list up to the number of indices given.
 -Made CPK extractor handle encrypted UTF data seen in Hyperdimensional Neptunia. Thanks to tpu for posting the decryption routine.
 -Added noesisExtTexRef_t with Noesis_AllocTexRefs for plugin developers. External texture reference objects can be attached to materials.
 -Added NMATFLAG_TWOSIDED and RPGEO_TRIANGLE_STRIP_FLIPPED for plugin developers.
 -Various new primitive types for plugin developers. Some of them aren't correctly implemented, though. If you use one and it doesn't work, let me know and I'll fix it for you.
 -This release marks over 100 unique file formats supported by Noesis. Truly, I have too much time on my hands.
 -2.92 - Still fixing various post-2.9 bugs.
 -2.95 - New functionality for materials in pluginshare.h.
 -2.95 - Made Noesis_AllocTexRefs automagically handle the "-texpre" option.
 -2.95 - Made COLLADA and obj exporters properly differentiate between material and external texture reference names.
 -2.95 - Fixed up unicode support a bit, allowing models on unicode paths to be previewed.
 -2.95 - Made some non-s3tc DDS files load. Thanks to Mirrorman95 for example files.
 -2.95 - Fixed relative-indexing in the obj loader. Thanks to Mirrorman95 for example files.
 -2.95 - Added SetPreviewOption for plugin authors.
 -2.96 - When Noesis_GetMatData/Noesis_GetMatDataFromLists is called, if materials do not have external texture references, external diffuse references are created based on provided texture filenames.
 -2.96 - Further unicode support. (fixed some modules not being able to load related files from unicode paths, and issues with exporting to unicode paths)
 -2.97 - Added Noesis_SetModelAnims and Noesis_SetModelMaterials calls for plugin developers, which allow setting anim/material data after a model has already been generated.
 -2.97 - Added NANIMFLAG_FORCENAMEMATCH and NANIMFLAG_INVALIDHIERARCHY flags for animations, see comments in pluginshare.h for their uses.
 -2.97 - Added wide-char versions of various path string query/manipulation functions.
 -2.97 - Fixed a bug in the paired file loading which was introduced by 2.96 unicode changes.
 -2.97 - Added unicode file read/write plugin API functions.
 -2.97 - Fixed a potential bug with extracting archives on a widechar path.
 -2.98 - Added Noesis_FindOrAddMaterial for plugin developers, see comment in pluginshare.h for usage.
 -2.98 - Fixed FF10 models having more meshes than necessary.
 -2.98 - Made triangle sort occur on ConstructModel, so that mesh generation is optimized even when the Optimize function has not been called.
 -2.98 - Added Noesis_SetModelTriSort for plugin developers, and exposed a "Sort triangles" value in the data viewer. A value of 1 means sort by mesh, and sort triangles on a sub-mesh basis. A value of 2 means sort triangles regardless of batching. However, setting the value to 2 can destroy performance. (as it can produce thousands of draw calls)
 -2.981 - Quick change to no longer sort by default on constructModel, and add rpgConstructModelAndSort to do default sort instead. (default sort interrupted natural draw order and upset blending for a few formats)

Version 2.8 - 2.85:
 -Added support for the Kinect via OpenNI, accessible from the Tools menu. Requires a Kinect device, with working drivers and OpenNI installed.
 -Added "Open file" to File menu. (directly opens and browses to a specific file with the standard file picker)
 -Made smooth/dampen factor modifiable in the Kinect dialog, improved error handling in skeletal tracking. (added in 2.81)
 -Fixed animation matrices not being stored properly for identity-based Kinect recording setups. (added in 2.82)
 -Integrated ODE+IK support for Kinect recordings. (added in 2.82)
 -Fixed a possible timing issue with Kinect recordings. (added in 2.82)
 -Added brot and bmoda commands. (2.83)
 -Various in-progress stuff. (2.85)

Version 2.76:
 -Added ActorX PSK (model) import+export. Plugin source is included.
 -Added ActorX PSA (animation) import+export. Plugin source is included.
 -Added md5anim export.
 -Added support for animation sequences. Sequences can be viewed in isolation by selecting them in the data viewer.
 -Added "export from preview" option, which exports data directly from the preview model, incorporating any changes made by the data viewer.
 -Added BNR+U8 container support.
 -Exposed generic un-lzss function, which accepts many different decompression parameters.
 -Added a "show memory leaks" option to the tools menu. It is recommended that plugin authors enable this option.
 -Fixed a stack overflow when loading large PSK models, and sped up smoothed normal calculation by a factor of 10 or so.
 -Changed default vertex normal calculation method.
 -Fixed procedural geometry generator breaking meshes up based on vertex weights, when it didn't need to.

Version 2.64:
 -New class-based math library for plugin authors. It's completely optional and works with the existing C-based math library.
 -Refined math classes a bit and cleaned up the implementations.
 -Made rpgOptimize account for varying numbers of vertex weights and different vertex component bits.
 -Added -combinemeshes option.
 -Made COLLADA importer support non-triangle polygon lists.

Version 2.54:
 -Exposed a variety of compression/decompression methods through the plugin interface.
 -Added Metroid Prime 1/2/3 .PAK support via plugin. (source is included) Thanks to revelation for providing the info for this format!
 -Added GameCube/Wii filesystem support to the .iso parser.
 -Added FF7CC archive extraction support, changed FF7CC model extension.
 -Added extra wireframe rendering functionality to the data viewer.
 -Added Evangelion: Jo .pkg extraction support.
 -Various other fixes and minor additions that I couldn't be bothered to keep track of.

Version 2.42:
 -Added "Batch process" to the tools menu. Allows you to export multiple files and issue other arbitary processing commands.
 -Fixed a crash when exporting UV-less models to SMD.
 -Fixed another crash when exporting UV-less or normal-less models to OBJ.
 -Fixed texture output type sometimes not being recognized.

Version 2.35/2.36/2.37/2.38:
 -Fixed Bayonetta support up, and added Vanqish support in the same plugin module. (the formats are similar)
 -Fixed broken path names for FPK extraction, made TTD's auto-load with GMO's. (when applicable)
 -Made GMO not default to grouping by material. Old functionality can be invoked by the new -gmogroup option.
 -Various changes and fixes for the plugin system.
 -And yet more changes and fixes for the plugin system! Added auto-normalization of weights, and triangles with different vertex component bits will not be merged into the same surface.
 -Added the ability to rotate/translate bones with offsets from within the data viewer.

Version 2.3:
 -Added proper display of normal maps where applicable, and some new light properties. (viewable/editable in the data viewer)
 -Bayonetta model import support. Source code is included in the plugin SDK.
 -Sped model preview load up slightly. Probably won't be noticeable, this was mainly a forward-looking optimization.
 -Added vertex morph frame items for the data viewer. Highlighting a frame will render the model in that frame in the active preview.
 -Now sorting the file type mask in alphabetical order.
 -Various new plugin API functions, including some useful procedural animation functionality. (use it to test your bone weights)
 -Fixed another container bug that was causing .iso and .afs to not be correctly recognized.
 -Added CPK container extraction support. Thanks to hcs for releasing source code that describes this format! This implementation should run around 10-20 times faster than cpk_unpack.exe.

Version 2.2:
 -Export support for Quake II MD2, with new -md2strips and -md2painskin command line options. MD2 exporter plugin source has been updated. This rounds out import+export support for MDL, MD2, MD3, and MD5.
 -Fixed a bug causing extra vertex weights to sometimes not be initialized with NMSHAREDFL_FLATWEIGHTS_FORCE4.
 -Unified the way that model-with-builtin-animation export is handled. (the IQM plugin code has been updated accordingly)
 -Over 15 new RAPI functions for plugin development, exposing lots of new functionality, from tokenized text parsing to image resampling and combining. (see pluginshare.h, >= 2.2 API functions are commented)
 -Added -mdlavoidfb command line option to avoid fullbright colors when exporting Quake MDL skins.
 -Added -mdlskinsize command line option to explicitly set output dimensions of Quake MDL skins.

Version 2.1:
 -Quake MDL export support. This automatically combines texture pages and dithers them all to the Quake palette. It also bakes all available skeletal and vertex animation into the MDL frames.
 -Fixed a general archive bug, which was causing quite a few archive file types to not be correctly recognized.
 -Added another RAPI interface function (for plugins) which performs all commandline-specified transforms on a set of animation matrices. (plugins previously had no way to obey -rotate, -posoffset, etc. command line options for anim data)
 -Fixed a variety of transform (rotate/scale/offset) bugs, as some transform behavior was still format-dependent and it no longer is.

Version 2.0:
 -New plugin system. Plugins can import/export any model, texture, and/or animation format, and allow seamless third-party integration of new file formats into Noesis.
 -Plugin SDK is now included in pluginsource.zip. Each plugin project compiles in MS Visual Studio 2005, and they probably compile fine with the free Express Edition.
 -Quake II MD2 import support added via plugin. Source code is included.
 -PCX image import and export support added via plugin. Source code is included.
 -Inter-Quake Model import and export support added via plugin. Source code is included.
 -Added new control over scene lights. Highlight them in the data viewer to rotate them with the left mouse in the model view. Their pivot point and distance to pivot can also be adjusted directly in the data viewer.
 -Added support for extracting LithTech REZ files. (thanks to aluigi's bms script for the spec)

Version 1.9:
 -Corrected a texture load path bug with .noesis files.
 -Added support for extracting GCF (Valve) files. Tested with format version 1.6, support for other versions is questionable.
 -Added import support for Valve VTF textures. Only supports a limited set of image types, and was only tested with v7.1 images.
 -Added import support for Source MDL models. Only tested with format version 44.
 -Added import support for Quake MDL.
 -Added import support for FF8 battle models/animations.
 -Made HL .map support actually work again. (loads halflife.wad if it's in the working directory, to generate proper texcoords)
 -Changed default coordinate system for Heretic 2, SiN, and Q3A models.

Version 1.8:
 -Made MD3 export path handle NULL UV's.
 -Added import and export support for Heretic 2 .m8 textures.
 -Added import support for Heretic 2 .fm models. Vertex animations are handled, but reference/node/skeletal data is not.
 -Added support for paletted images in PNG and TGA loaders.
 -Added support for SiN variant of Quake PAK format.
 -Added import support for SiN SBM/SAM model/frame data.
 -New support for ".noesis" scene files. This is a text-based format which allows custom scenes to be crafted with simulated physics, but functionality is still limited. Two scenes are included, one of which references an implementation of the ODE physics library.

Version 1.7:
 -Generic vertex morph handling. Only implemented so far for Sub Culture's DFF format, DOAX2/NG2, and MD3. Preserves vertex morphs on export (to some formats) and displays them in previewer as animations.
 -Quake 3 MD3 import and export. (useful for exporting those morph target meshes, though there is usually precision loss in the format)
 -Fixed a path bug, which might've shown up in situations where a file is processed in a working-directory-relative path.
 -Support for converting skeletal models+animations to pure vertex morph animations, via the MD3 path. Bone-based tags are also supported. (see -md3tbone advanced option)

Version 1.6:
 -New "Special Thanks" section in ReadMe, as I realized I was being a thankless bastard for all of the awesome people on XeNTaX.
 -Fixed a .glm import bug, which would cause some surfaces to be missed entirely. (thanks to AceWell for submitting this bug)
 -Added global JPEG reading/writing. (did this mainly to have auto-loading for JK2 model textures)
 -Fixed another .glm bug, where path to .gla would be treated as working-directory-relative instead of file-relative.
 -Made scene lighting not rotate with model when changing the base rotation axis.
 -Added read support for very old RenderWare (I think) DFF format. (used in Sub-Culture for Windows/PC)
 -Added limited BMP read/write support. (24bpp with no RLE)
 -Fixed bad interface state when drag-and-dropping anims to apply to open models.

Version 1.5:
 -Fixed crash on attempting to export non-power-of-two DXT-compressed images to non-DXT formats. (thanks to firsak for submitting this bug)
 -Fixed NMD texture output stomping sequential files in some instances.
 -Fixed a potential crash when opening screwy SMD files. (thanks to firsak for submitting this bug)
 -Added "advanced commands" button to export window, to list export options.
 -Other things which have been lost in the pages of history.

Versions 1.0-1.4:
 -It's a mystery!

==================
Release Milestones
==================
1.0 - 2010/06/09
2.0 - 2010/10/27
3.0 - 2011/04/08
3.5 - 2011/08/25
4.0 - 2012/12/15
4.1 - 2014/09/26
4.2 - 2016/09/23
4.39 - 2019/01/27

==============
Basic Controls
==============
In preview mode, the following controls are available:

1) Left Mouse: While held, moving the mouse will rotate your view around the focal point.

2) Left Mouse + CTRL: While held, moving the mouse up and down zooms your view in and out.

3) Right Mouse: While held, moving the mouse will move your focal point in the scene, relative to the direction you're looking. Your focal point is represented by a green/red box at the center of the screen.

4) Right Mouse + CTRL: While held, moving the mouse up and down moves your focal point "in" and "out" of the screen.

5) Middle Mouse: Clicking the middle mouse button re-centers your view on the model. Scrolling the mousewheel does what Left Mouse + CTRL does, with a larger step length.

6) The icons on the preview pane (and their corresponding F# keys) will change according to the data inside the file you are previewing. Remember to read the info text when the preview main is in focus for reference.

The red/green focal point in the center of the screen will only appear while you are holding down the right mouse button. If the box is green, it is not obstructed, but if it's red, that means it's "behind" the geometry you're looking at. This is helpful for determining the distance of your focal point when trying to center in on some geometry.

For certain touch pads, tablets, and other devices, you may want to prevent cursor locking when clicking and moving. There is an option to disable this under the data viewer. See "Tools->Data Viewer->Persistent settings->Other->Disable cursor locking".

Additionally, many features and options are available through the Noesis menus. Explore and enjoy.

=================
Command Line Mode
=================
Noesis can be activated on the command line by using ?cmode as the first command line argument. This allows you to quickly process files from external batch files or other automation tools. Syntax is Noesis.exe ?cmode infile.raw outfile.raw -options. An example batch file to convert one SMD model to RDM, rotating it 90 degrees, scaling it up to 2x the size, and prefixing texture names with the given string:

@echo off
Noesis.exe ?cmode "pl_male01_hi.smd" "pl_male01_hi.rdm" -rotate 90 0 0 -smdnorm -scale 2.0 -texpre "male01 tex_"
pause

Likewise, ?runtool can be used to execute tool plugins/scripts from the commandline. For tools that uses noesis.getSelectedFile, a third parameter can be supplied on the command-line to be returned as the selected file for that function. For example:

Noesis.exe ?runtool "&Get material info" "C:\Models\someninjaguy.gmd"

This command would execute the tool named "&Get material info" (the & is there because it's part of the tool's description string), and when that tool script calls noesis.getSelectedFile, it will receive the path for someninjaguy.gmd.

============
Kinect Notes
============
You're on your own when it comes to getting your Kinect set up and working with OpenNI, you'll just have to Google it. It's also possible that, by now, the Noesis OpenNI+Kinect implementation is broken. Probably not, but who knows!

That said, once you've got Noesis to recognize the device, you'll have to assume a "T-pose" with your arms sticking straight out, but also with your elbows bent so that your hands are pointing toward the ceiling. Consult the OpenNI/NITE documentation for more info, or go find my YouTube demo video and observe.

Setting models up to map to the generic NITE skeleton involves mapping bones. You can apply angle modifiers or flip specific axes, as needed. Most models will require you to tick the "global x flip" and "global y flip" options, but it depends on the coordinate system of the model you're working with.

Additionally, you can use the "Base cap" option to snap a pose of yourself attempting to mimic your model's base pose. This will then apply only base-relative matrices to the model's existing pose, rather than completely overriding. This option may mean less screwing around with angle offsets on certain models, but you shouldn't mess with it unless you've got a pretty good idea of what you're doing.

You can also record animation data directly into the preview model. After recording, you can export that animation data into any Noesis-exportable animation format, using the "Export from preview" option.

Oh, and you can save/load bone mappings in the form of .noekin files. If a .noekin file exists with the same name as your model file, it will be auto-loaded. Well, that about covers it. This is just crazy experimental functionality, so don't expect a lot from it.

================
MDL Export Notes
================
Noesis has some pretty in-depth functionality for exporting models to MDL/MD2/MD3/MD5, used by various id game engines. Here are some tips on using that functionality.

-For MD2, pay attention to the "Skin path:" printout at the end of your export. Skin paths need to be absolute to work in Quake II, so you may need to add something alone the lines of -texpre /models/monsters/infantry/ to your advanced options. (only as an example, you should replace the infantry path with wherever your skinpage.pcx will end up)
-For MDL, you will probably want to use -mdlavoidfb in the advanced options, if you want your model to look correct in software and you have not custom-crafted a Quake palette for it.
-The -mdlskinsize advanced option will work for both MDL and MD2 texture output.
-MD3 allows you to specify any bone in your import model as a tag on export - see the -md3tbone option.
-MDL, MD2, and MD3 are all generally interchangeable in terms of data they import/export. The main things to note are the potential loss of vertex/texture coordinate precision and MD3 tags.
-All MD* formats can also bake skeletal animation data out to their vertex frames. This happens automatically when you convert a model with skeletal animation data. You can also use -loadrda to load pre-generated RDA animation files and combine them with static skeletal meshes. (the results will be baked into the MDL/MD2/MD3)
-The MDL and MD2 exporters automatically generate a single texture page from all textures that the model being converted references, compensating the texture coordinates in the model. This can be incredibly handy, since MDL and MD2 only allow a single texture page to be referenced. Texture pages can be grabbed from within your source model, and on the local path in any image format that Noesis supports. Just remember to have your textures all in the same folder as the model being imported/exported.

This is all legacy code at this point, which is why it has various hardcoded tentacles running through Noesis instead of going through standard plugin routes.

==============
Special Thanks
==============
revelation:
 - Provided me with various specs and education on VIFcode and lots of other PS2-related stuff.
 - Provided spec for the FFX model/animation formats!
 - Continually put up with my dumb questions about FFX animations.
 - Provided info on the FFX filesystem.
 - Provided Metroid Prime .pak file info.
 - Also assisted in the Capcom .mod format and made many of his findings public, which assisted me in conjunction with Surveyor's efforts.
 - All around awesome guy that is always popping up wherever there's a technical challenge.

chrrox:
 - A longtime supporter of Noesis, with dozens of scripts under his belt.
 - The most useful Noesis bug reporter who ever lived.
 - A truly standup gentleman, who can routinely be seen writing importers for a variety of model formats.

Mr.Mouse:
 - Hosted Noesis and its site, once upon a time.
 - A founder of XeNTaX! (we're not worthy) XeNTaX once provided a great foundation for tools like Noesis to spring up.

flatz:
 - Played a very important role in facilitating FF15 support.

aluigi:
 - Cracked encryption on Ys: The Oath in Felghanna archives, which allowed me to get at the .ymo data with ease.
 - Provided spec on the LithTech .rez files.
 - Generally just does a lot of stuff. aluigi is a talented guy, and his site is constantly growing with new scripts and code.

Surveyor:
 - Made public most of the ground work for the Capcom .mod format, and saved me hours (maybe even days) of hex-editing!
 - Chipped in on a lot of other stuff during his tenure at XeNTaX.

Steve McCrea:
 - Contributed code for Sub-Culture BSP support, in addition to being an all-around excellent human being and a good friend.

Tomaz:
 - Hangs out in #qc and randomly shows interest in data decyphering. Helped with Sub-Culture stuff too.

The author of ffxitools:
 - The FF11 implementation uses MMB and MZB decryption code snippets, which I believe (but cannot confirm) were written by the author of ffxitools. I don't actually know who this is, but, thanks buddy!

=============
Rights of Use
=============
The author of this software, Rich Whitehouse, accepts no liability for any use (intended or otherwise) of this software, and expressly forbids the use of this software in violating any form of intellectual or copyright law.

Noesis is provided free of charge and as a NON-COMMERCIAL product, and may not be used or distributed in attachment to any other commercial or copyrighted product. Noesis also may not be distributed without this ReadMe.txt file included in completely unmodified form.

Many file formats supported by Noesis are also used in commercial products. When working with existing material, make sure you know your usage rights, and do not redistribute any copyrighted content that doesn't belong to you!

The author of this software does not in any way condone or support copyright violation/infringement.

Plugins for this program are not supported or guaranteed in any way, and the author of this software is not responsible for any aspect of third-party plugins. Use caution when using plugins, and please be responsible and adhere to legal practices when writing them.

Improper or uninformed use of Noesis could cause serious harm to you or your computer. The author of this software accepts no responsibility for any damages which result from the use of this software. You use this software entirely at your own risk.

Additionally, Noesis makes use of libjpeg for JPEG reading/writing, as well as zlib for... lots of things. Oh, and FCollada for COLLADA reading/writing. And libpng for PNG reading/writing, as well as GIFLIB for GIF reading/writing. And the crunch texture compression library by Rich Geldreich for crunch texture support. Noesis also implements Python through a plugin that links to the Python C library. As of version 3.75, a modified and slimmed down version of libcurl is also used for HTTP transfers. I think that covers all of the third-party libs.

============
Uninstalling
============
If you want to wipe all traces of Noesis from your system, first remember to use the association dialog under the Tools menu to remove all associations with file types on your system. Then delete the HKEY_CURRENT_USER\Software\Noesis key in your registry. You can then delete the actual folder in which you have extracted the Noesis files.
An automated installer/uninstaller may be supplied some day, when the author is less lazy.

========
Trouble!
========
If something goes wrong, first try removing all of your third-party plugins. If the problems go away after removing those plugins, try adding them back one at a time. Once you find the plugin causing the problem, contact the author of that plugin and tell him/her that his/her plugin is busted.

Additionally, if your problem appears to be on export to a specific format that doesn't appear right when imported into another tool, try importing it back into Noesis. If it looks right in Noesis, there's a pretty good chance the fault is actually in the other program's importer and not Noesis's exporter. In this case, you should contact the author(s) of that other program and/or its import plugin.

If you have trouble using a plugin, such as the plugin not seeming to load or add the given format to the format list, make sure you have the latest MSVC++ 2005 runtime package installed. Runtime links are provided near the top of this document.

If Noesis is crashing on startup, try running the program with ?compat_nomemmod as an argument on the commandline. If this prevents crashing, you may have a virus on your system (as was the case in the only known crash report), or perhaps an overly-zealous antivirus solution.

If none of the above circumvents your issue, make sure you're using the latest version of Noesis. If you are, you may be looking at a genuine Noesis bug. Feel free to report your issue to me, but take care to provide plenty of detail about the circumstances, your system, and the data/game(s) you're working with. Direct replies to bug reports are not guaranteed. If I sense that you're being intentionally vague with details or that you aren't being forthcoming with data required to reproduce your issue(s), you're likely to be ignored.

==============
Making Plugins
==============
For information on writing Python scripts, see "plugins\python\__NPReadMe.txt".

For native binary plugins, a file called pluginsource.zip is included in the Noesis distribution. The native API is fairly dated and in many ways terrifying, there's no formal documentation for any of it, and some of the included plugin source itself is really terrible. You can check the web site for some examples of more modern and less-grotesque plugin code, if you'd like. If you do set out to write a Noesis plugin and brave the wilderness, I'll generally be happy to hold your hand when you encounter issues.
