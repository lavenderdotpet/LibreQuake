Noesis Python Support
--
Noesis supports Python through a native binary module. In order to add format/functionality support, put .py scripts in this folder which implement a method named "registerNoesisTypes".

Take a look at __NPExample.txt for a complete model import+export sample module. You can rename the extension from .txt to .py if you want to be able import/export with it.

Alt+T,R is a quick shortcut for reloading plugins/Python scripts. You can also assign the reload plugins menu item to the shortcut of your choice, from the View->Interface->Customize dialog.

A trimmed down core 3.2.1 Python implementation is included. No modules (ctypes, sockets, etc.) are included - if you want support for them, you have to create a folder called "DLLs" under the Noesis folder and put them in it. DLLs not compiled for Python 3.2.1 may or may not work.

Your registerNoesisTypes method should register file handles, and define its own methods to act as file handlers. (see examples in existing scripts)

Noesis natively loads and makes the "noesis" and "rapi" modules available for import. However, the rapi module should only be accessed during file handler routines, because the entire underlying API is instanced.


The following methods are available for the "noesis" module:

	{"logOutput", Noesis_LogOutput, METH_VARARGS, "prints to log. (s)"}, //args=string
	{"logError", Noesis_LogOutput, METH_VARARGS, "logs error. (s)"}, //args=string
	{"logFlush", Noesis_LogFlush, METH_VARARGS, "flush log."}, //args=none
	{"logPopup", Noesis_LogPopup, METH_NOARGS, "pops up the debug log."}, //args=none
	{"allocBytes", Noesis_AllocByteArray, METH_VARARGS, "allocate byte array of predetermined size. (i)"}, //args=size
	{"allocType", Noesis_AllocType, METH_VARARGS, "allocate an internal noesis python type. (var) types: "
													//note that while stream objects will accept bytearrays, modifying the bytearray (resizing or reallocating) while the stream object is active can cause crashes
													"readStream (sO) "
													"writeStream (s) "
	}, //args=type name, others depending on type name
	{"deinterleaveBytes", Noesis_DeinterleaveBytes, METH_VARARGS, "pulls flat data out of an interleaved array. (Oiii)"}, //args=bytearray, offset in bytearray, size of element, stride between elements
	{"validateListType", NoePyMath_ValidateListType, METH_VARARGS, "validates list contains only a given type. does not throw an exception if the list is empty or None. (OO)"}, //args=list, desired type
	{"validateListTypes", NoePyMath_ValidateListTypes, METH_VARARGS, "validates list contains only types. does not throw an exception if the list is empty or None. (OO)"}, //args=list, list of desired types
	{"doException", Noesis_DoException, METH_VARARGS, "custom routine to raise an exception. (s)"}, //args=string
	{"getMainPath", Noesis_GetMainPath, METH_NOARGS, "returns string to main executable file."}, //args=none
	{"getScenesPath", Noesis_GetScenesPath, METH_NOARGS, "returns path string to scenes directory."}, //args=none
	{"getPluginsPath", Noesis_GetPluginsPath, METH_NOARGS, "returns path string to plugins directory."}, //args=none
	{"getSelectedFile", Noesis_GetSelectedFile, METH_NOARGS, "returns path string to selected file."}, //args=none
	{"getSelectedDirectory", Noesis_GetSelectedDirectory, METH_NOARGS, "returns path string to selected directory."}, //args=none
	{"getOpenPreviewFile", Noesis_GetOpenPreviewFile, METH_NOARGS, "returns path string to open preview file, or None if nothing is open."}, //args=none
	{"getAPIVersion", Noesis_GetAPIVersion, METH_NOARGS, "returns the api version."}, //args=none
	{"register", Noesis_Register, METH_VARARGS, "registers a file type. (ss)"}, //args=type name, type ext
	{"registerTool", Noesis_RegisterTool, METH_VARARGS, "registers a tool. returns a tool handle. (sO|s)"}, //args=tool name, tool method, tool help text (optional)
	{"registerCleanupFunction", Noesis_RegisterCleanupFunction, METH_VARARGS, "registers a cleanup function. (O)"}, //args=cleanup method
	{"disableFormatByDescription", Noesis_DisableFormatByDescription, METH_VARARGS, "disables a format by matching the full name string. (s)"}, //args=type name
	{"checkToolMenuItem", Noesis_CheckToolMenuItem, METH_VARARGS, "checks or unchecks a tool's menu item. (ii)"}, //args=tool handle, checked status
	{"setToolFlags", Noesis_SetToolFlags, METH_VARARGS, "sets a tool's flags. (ii)"}, //args=tool handle, flags
	{"getToolFlags", Noesis_GetToolFlags, METH_VARARGS, "returns a tool's flags. (i)"}, //args=tool handle
	{"setToolVisibleCallback", Noesis_SetToolVisibleCallback, METH_VARARGS, "sets visibility callback (is - toolHandle, selectedFile/None) for tool menu item. unlike most python callbacks, no special context cleanup is performed around this callback, so take care inside of it. (iO)"}, //args=tool handle, callback method

	{"addOption", Noesis_AddOption, METH_VARARGS, "adds an option for the registered type. (issi)"}, //args=handle, option name, option description, flags (e.g. OPTFLAG_WANTARG)
	{"optWasInvoked", Noesis_OptWasInvoked, METH_VARARGS, "returns non-0 if option has been invoked. (s)"}, //args=option name
	{"optGetArg", Noesis_OptGetArg, METH_VARARGS, "returns an argument string for the option. (s)"}, //args=option name

	{"userPrompt", Noesis_UserPrompt, METH_VARARGS, "displays a user input prompt. returns expected data type, or None on cancellation. (i|sssO)"}, //args=value type (a noesis.NOEUSERVAL_* constant), title string, prompt string, default value string, input validation handler
	{"messagePrompt", Noesis_MessagePrompt, METH_VARARGS, "displays a message box. (s)"}, //args=message string
	{"openFile", Noesis_OpenFile, METH_VARARGS, "opens a file in the main preview view. (s)"}, //args=file path
	{"openAndRemoveTempFile", Noesis_OpenAndRemoveTempFile, METH_VARARGS, "opens a file in the main preview view without browsing to it, and deletes it after opening. (s)"}, //args=file path
	{"fileIsLoadable", Noesis_FileIsLoadable, METH_VARARGS, "returns true if file is loadable. (s)"}, //args=file path

	{"loadImageRGBA", Noesis_LoadImageRGBA, METH_VARARGS, "loads the first image in a file and returns a NoeTexture. (s)"}, //args=file path
	{"saveImageRGBA", Noesis_SaveImageRGBA, METH_VARARGS, "saves a NoeTexture to a file. (sO)"}, //args=file path

	{"instantiateModule", Noesis_InstantiateModule, METH_NOARGS, "returns a handle to a new module. make sure you use freeModule when you're done!"}, //args=none
	{"freeModule", Noesis_FreeModule, METH_VARARGS, "frees a module. (i)"}, //args=module handle
	{"setModuleRAPI", Noesis_SetModuleRAPI, METH_VARARGS, "sets a module's rapi interface to the active rapi. pass -1 to clear the active rapi. (i)"}, //args=module handle
	{"setPreviewModuleRAPI", Noesis_SetPreviewModuleRAPI, METH_NOARGS, "sets the active preview module's rapi interface to the active rapi. throws an exception if there is no active preview module."}, //args=none
	{"isPreviewModuleRAPIValid", Noesis_IsPreviewModuleRAPIValid, METH_NOARGS, "returns > 0 if preview module rapi is valid."}, //args=none

	{"getCharSplineSet", Noesis_GetCharSplineSet, METH_VARARGS, "returns a NoeSplineSet for the given string character. (ord(c)) (i)"}, //args=character

	{"getWindowHandle", Noesis_GetWindowHandle, METH_NOARGS, "gets native platform window handle."}, //args=none

	{"getFormatExtensionFlags", Noesis_GetFormatExtensionFlags, METH_VARARGS, "returns a combination of noesis.NFORMATFLAG values for a file extension. (s)"}, //args=extension, including . at start

	{"usbOpenDevice", Noesis_UsbOpenDevice, METH_VARARGS, "returns a handle to the opened device. (uu)"}, //args=device interface GUID, device class GUID
	{"usbCloseDevice", Noesis_UsbCloseDevice, METH_VARARGS, "closes a handle opened by usbOpenDevice. (i)"}, //args=device handle
	{"usbSetAltInterface", Noesis_UsbSetAltInterface, METH_VARARGS, "sets an alternate interface. (ii)"}, //args=device handle, alt interface index
	{"usbGetEndpointCount", Noesis_UsbGetEndpointCount, METH_VARARGS, "get endpoint count for current interface. (i)"}, //args=device handle
	{"usbGetEndpointInfo", Noesis_UsbGetEndpointInfo, METH_VARARGS, "gets a tuple of parameters for specified ep in current interface. (ii)"}, //args=device handle, endpoint index
	{"usbWriteEndpoint", Noesis_UsbWriteEndpoint, METH_VARARGS, "writes data to endpoint. (iiO)"}, //args=device handle, endpoint index, data
	{"usbWriteEndpointId", Noesis_UsbWriteEndpointId, METH_VARARGS, "writes data to endpoint. (iiO)"}, //args=device handle, endpoint id, data
	{"usbReadEndpoint", Noesis_UsbReadEndpoint, METH_VARARGS, "reads data from endpoint. (iii)"}, //args=device handle, endpoint index, size
	{"usbReadEndpointId", Noesis_UsbReadEndpointId, METH_VARARGS, "reads data from endpoint. (iii)"}, //args=device handle, endpoint id, size
	{"usbControlTransfer", Noesis_UsbControlTransfer, METH_VARARGS, "reads data from endpoint. (iOiiii)"}, //args=device handle, data, request type, request, index, value
	{"usbSetEndpointTimeout", Noesis_UsbSetEndpointTimeout, METH_VARARGS, "sets timeout on endpoint. (iii)"}, //args=device handle, endpoint index, timeout value
	{"usbSetEndpointTimeoutId", Noesis_UsbSetEndpointTimeoutId, METH_VARARGS, "sets timeout on endpoint. (iii)"}, //args=device handle, endpoint id, timeout value

	//typecheck handler should be defined as def fmtCheckType(data), where data is a PyByteArray
	//should return 0 on fail (is not the format) or 1 on success (is the format)
	{"setHandlerTypeCheck", Noesis_SetHandlerTypeCheck, METH_VARARGS, "sets the type check handler. (iO)"}, //args=handle, function

	//loadmodel handler should be defined as def fmtLoadModel(data, mdlList), where data is a PyByteArray and mdlList is an empty list that should be filled with NoeModel objects
	//should return 0 on fail or 1 on success
	{"setHandlerLoadModel", Noesis_SetHandlerLoadModel, METH_VARARGS, "sets the model load handler. (iO)"}, //args=handle, function

	//writemodel handler should be defined as def fmtWriteModel(mdl, bsOut), where mdl is a NoeModel (the model being exported) and bsOut is a NoeBitStream that should have the resulting model binary written into it
	//should return 0 on fail or 1 on success
	{"setHandlerWriteModel", Noesis_SetHandlerWriteModel, METH_VARARGS, "sets the model write handler. (iO)"}, //args=handle, function

	//writeanim handler should be defined as def fmtWriteAnim(anims, bsOut), where anims is a list of NoeAnim and bsOut is a NoeBitStream that should have the resulting anim binary written into it
	//should return 0 on fail (or in the event that the NoeBitStream should not be written to disk) or 1 on success
	{"setHandlerWriteAnim", Noesis_SetHandlerWriteAnim, METH_VARARGS, "sets the animation write handler. (iO)"}, //args=handle, function

	//loadrgba handler should be defined as def fmtLoadRGBA(data, texList), where data is a PyByteArray and texList is an empty list that should be filled with NoeTexture objects
	//should return 0 on fail or 1 on success
	{"setHandlerLoadRGBA", Noesis_SetHandlerLoadRGBA, METH_VARARGS, "sets the image load handler. (iO)"}, //args=handle, function

	//writergba handler should be defined as def fmtWriteRGBA(data, width, height, bsOut), where data is a PyByteArray of 32bpp rgba, width/height are the image dimensions, and bsOut is a NoeBitStream that should have the resulting binary written into it
	//should return 0 on fail or 1 on success
	{"setHandlerWriteRGBA", Noesis_SetHandlerWriteRGBA, METH_VARARGS, "sets the image write handler. (iO)"}, //args=handle, function

	//extractarc handler should be defined as def fmtExtractArc(fileName, fileLen, justChecking), where fileName is a string (you should handle opening the file yourself in the handler), fileLen is an int/long, and justChecking (means you should return 1 as soon as you have determined the validity of the type) is an int
	//should return 0 on fail or 1 on success
	{"setHandlerExtractArc", Noesis_SetHandlerExtractArc, METH_VARARGS, "sets the archive handler. (iO)"}, //args=handle, function

	//when this format is the main export target, the provided string will be run through the advanced options parser
	{"setTypeExportOptions", Noesis_SetTypeExportOptions, METH_VARARGS, "sets the type's export options. (is)"}, //args=handle, function

	//math functions
	{"nextPow2", NoePyMath_NextPow2, METH_VARARGS, "returns next power of 2 value. (i)"}, //args=int
	{"getFloat16", NoePyMath_GetFloat16, METH_VARARGS, "returns float from half-float. (H)"}, //args=ushort
	{"encodeFloat16", NoePyMath_EncodeFloat16, METH_VARARGS, "returns half-float from float. (f)"}, //args=float
	{"getMFFP", NoePyMath_GetMFFP, METH_VARARGS, "returns float from motorola fast floating point format. (I)"}, //args=uint
	{"encodeMFFP", NoePyMath_EncodeMFFP, METH_VARARGS, "returns motorola FFP from float. (f)"}, //args=float
	{"morton2D", NoePyMath_Morton2D, METH_VARARGS, "returns morton index from x,y coordinates. (ii)"}, //args=x, y
	{"constLerp", NoePyMath_ConstLerp, METH_VARARGS, "constant lerp. (fff)"}, //args=float 1, float 2, fraction
	{"linLerp", NoePyMath_LinLerp, METH_VARARGS, "linear lerp. (fff)"}, //args=float 1, float 2, fraction
	{"bilinLerp", NoePyMath_BilinLerp, METH_VARARGS, "bilinear lerp. (ffffff)"}, //args=x, y, z, w, frac1, frac2
	{"triLerp", NoePyMath_TriLerp, METH_VARARGS, "tri lerp. (ffffff)"}, //args=x, y, z, frac1, frac2, frac3
	{"cubicLerp", NoePyMath_CubicLerp, METH_VARARGS, "cubic lerp. (fffff)"}, //args=y0, y1, y2, y3, frac
	{"hermiteLerp", NoePyMath_HermiteLerp, METH_VARARGS, "cubic lerp. (fffffff)"}, //args=y0, y1, y2, y3, frac, tension, bias
	{"bezier3D", NoePyMath_Bezier3D, METH_VARARGS, "returns point on bezier spline. (Of)"}, //args=list of points, fraction
	{"bezierTangent3D", NoePyMath_BezierTangent3D, METH_VARARGS, "returns tangent on a bezier spline. (Of)"}, //args=list of 4 points, fraction
	{"cubicBezier3D", NoePyMath_CubicBezier3D, METH_VARARGS, "returns point on cubic bezier spline. (Of)"}, //args=list of 4 points, fraction
	{"planeFromPoints", NoePyMath_PlaneFromPoints, METH_VARARGS, "returns a plane(NoeVec4) from 3 points. (OOO)"}, //args=NoeVec3, NoeVec3, NoeVec3

Various other math and streaming functions are also exposed, but it's best to use the Noe* types (see inc_noesis.py) instead of accessing those methods directly.

The following constants are also exposed:

	PYNOECONSTN(NOESIS_PLUGIN_VERSION),
	PYNOECONSTN(NOESIS_PLUGINAPI_VERSION),
	PYNOECONSTN(MAX_NOESIS_PATH),

	PYNOECONSTN(NOESISTEX_UNKNOWN),
	PYNOECONSTN(NOESISTEX_RGBA32),
	PYNOECONSTN(NOESISTEX_RGB24),
	PYNOECONSTN(NOESISTEX_DXT1),
	PYNOECONSTN(NOESISTEX_DXT3),
	PYNOECONSTN(NOESISTEX_DXT5),

	PYNOECONSTN(FOURCC_DXT1),
	PYNOECONSTN(FOURCC_DXT3),
	PYNOECONSTN(FOURCC_DXT5),
	PYNOECONSTN(FOURCC_DXT1NORMAL),
	PYNOECONSTN(FOURCC_ATI1),
	PYNOECONSTN(FOURCC_ATI2),
	PYNOECONSTN(FOURCC_DX10),
	PYNOECONSTN(FOURCC_BC1),
	PYNOECONSTN(FOURCC_BC2),
	PYNOECONSTN(FOURCC_BC3),
	PYNOECONSTN(FOURCC_BC4),
	PYNOECONSTN(FOURCC_BC5),
	PYNOECONSTN(FOURCC_BC6H),
	PYNOECONSTN(FOURCC_BC6S),
	PYNOECONSTN(FOURCC_BC7),

	PYNOECONSTN(NOEFSMODE_READBINARY),
	PYNOECONSTN(NOEFSMODE_WRITEBINARY),
	PYNOECONSTN(NOEFSMODE_READWRITEBINARY),

	PYNOECONSTN(NTOOLFLAG_CONTEXTITEM),
	PYNOECONSTN(NTOOLFLAG_USERBITS),

	PYNOECONSTN(NFORMATFLAG_ARCREAD),
	PYNOECONSTN(NFORMATFLAG_IMGREAD),
	PYNOECONSTN(NFORMATFLAG_IMGWRITE),
	PYNOECONSTN(NFORMATFLAG_MODELREAD),
	PYNOECONSTN(NFORMATFLAG_MODELWRITE),
	PYNOECONSTN(NFORMATFLAG_ANIMWRITE),

	PYNOECONSTN(NTEXFLAG_WRAP_REPEAT),
	PYNOECONSTN(NTEXFLAG_ISNORMALMAP),
	PYNOECONSTN(NTEXFLAG_SEGMENTED),
	PYNOECONSTN(NTEXFLAG_STEREO),
	PYNOECONSTN(NTEXFLAG_STEREO_SWAP),
	PYNOECONSTN(NTEXFLAG_FILTER_NEAREST),
	PYNOECONSTN(NTEXFLAG_WRAP_CLAMP),
	PYNOECONSTN(NTEXFLAG_PREVIEWLOAD),
	PYNOECONSTN(NTEXFLAG_CUBEMAP),
	PYNOECONSTN(NTEXFLAG_ISLINEAR),
	PYNOECONSTN(NTEXFLAG_HDRISLINEAR),
	PYNOECONSTN(NTEXFLAG_WANTSEAMLESS),
	PYNOECONSTN(NTEXFLAG_WRAP_MIRROR_REPEAT),
	PYNOECONSTN(NTEXFLAG_WRAP_MIRROR_CLAMP),

	PYNOECONSTN(NMATFLAG_NMAPSWAPRA),
	PYNOECONSTN(NMATFLAG_TWOSIDED),
	PYNOECONSTN(NMATFLAG_PREVIEWLOAD),
	PYNOECONSTN(NMATFLAG_USELMUVS),
	PYNOECONSTN(NMATFLAG_BLENDEDNORMALS),
	PYNOECONSTN(NMATFLAG_KAJIYAKAY),
	PYNOECONSTN(NMATFLAG_SORT01),
	PYNOECONSTN(NMATFLAG_GAMMACORRECT),
	PYNOECONSTN(NMATFLAG_VCOLORSUBTRACT),
	PYNOECONSTN(NMATFLAG_PBR_SPEC),
	PYNOECONSTN(NMATFLAG_PBR_METAL),
	PYNOECONSTN(NMATFLAG_NORMALMAP_FLIPY),
	PYNOECONSTN(NMATFLAG_NORMALMAP_NODERZ),
	PYNOECONSTN(NMATFLAG_PBR_SPEC_IR_RG),
	PYNOECONSTN(NMATFLAG_ENV_FLIP),
	PYNOECONSTN(NMATFLAG_PBR_ALBEDOENERGYCON),
	PYNOECONSTN(NMATFLAG_PBR_COMPENERGYCON),
	PYNOECONSTN(NMATFLAG_SPRITE_FACINGXY),
	PYNOECONSTN(NMATFLAG_NORMAL_UV1),
	PYNOECONSTN(NMATFLAG_SPEC_UV1),

	PYNOECONSTN(NSEQFLAG_NONLOOPING),
	PYNOECONSTN(NSEQFLAG_REVERSE),

	PYNOECONSTN(NANIMFLAG_FORCENAMEMATCH),
	PYNOECONSTN(NANIMFLAG_INVALIDHIERARCHY),

	PYNOECONSTN(RPGEO_NONE),
	PYNOECONSTN(RPGEO_POINTS),
	PYNOECONSTN(RPGEO_TRIANGLE),
	PYNOECONSTN(RPGEO_TRIANGLE_STRIP),
	PYNOECONSTN(RPGEO_QUAD), //ABC_DCB
	PYNOECONSTN(RPGEO_POLYGON),
	PYNOECONSTN(RPGEO_TRIANGLE_FAN),
	PYNOECONSTN(RPGEO_QUAD_STRIP),
	PYNOECONSTN(RPGEO_TRIANGLE_STRIP_FLIPPED),
	PYNOECONSTN(NUM_RPGEO_TYPES),
	PYNOECONSTN(RPGEO_QUAD_ABC_BCD),
	PYNOECONSTN(RPGEO_QUAD_ABC_ACD),
	PYNOECONSTN(RPGEO_QUAD_ABC_DCA),

	PYNOECONSTN(RPGEODATA_FLOAT),
	PYNOECONSTN(RPGEODATA_INT),
	PYNOECONSTN(RPGEODATA_UINT),
	PYNOECONSTN(RPGEODATA_SHORT),
	PYNOECONSTN(RPGEODATA_USHORT),
	PYNOECONSTN(RPGEODATA_HALFFLOAT),
	PYNOECONSTN(RPGEODATA_DOUBLE),
	PYNOECONSTN(RPGEODATA_BYTE),
	PYNOECONSTN(RPGEODATA_UBYTE),
	PYNOECONSTN(NUM_RPGEO_DATATYPES),

	PYNOECONSTN(NMSHAREDFL_WANTNEIGHBORS),
	PYNOECONSTN(NMSHAREDFL_WANTGLOBALARRAY),
	PYNOECONSTN(NMSHAREDFL_WANTTANGENTS),
	PYNOECONSTN(NMSHAREDFL_FLATWEIGHTS),
	PYNOECONSTN(NMSHAREDFL_FLATWEIGHTS_FORCE4),
	PYNOECONSTN(NMSHAREDFL_REVERSEWINDING),
	PYNOECONSTN(NMSHAREDFL_WANTTANGENTS4),
	PYNOECONSTN(NMSHAREDFL_WANTTANGENTS4R),
	PYNOECONSTN(NMSHAREDFL_UNIQUEVERTS),
	PYNOECONSTN(NMSHAREDFL_BONEPALETTE),

	PYNOECONSTN(SHAREDSTRIP_LIST),
	PYNOECONSTN(SHAREDSTRIP_STRIP),

	PYNOECONSTN(RPGOPT_BIGENDIAN),
	PYNOECONSTN(RPGOPT_TRIWINDBACKWARD),
	PYNOECONSTN(RPGOPT_TANMATROTATE),
	PYNOECONSTN(RPGOPT_DERIVEBONEORIS),
	PYNOECONSTN(RPGOPT_FILLINWEIGHTS),
	PYNOECONSTN(RPGOPT_SWAPHANDEDNESS),
	PYNOECONSTN(RPGOPT_UNSAFE),
	PYNOECONSTN(RPGOPT_MORPH_RELATIVEPOSITIONS),
	PYNOECONSTN(RPGOPT_MORPH_RELATIVENORMALS),

	PYNOECONSTN(RPGVUFLAG_PERINSTANCE),
	PYNOECONSTN(RPGVUFLAG_NOREUSE),

	PYNOECONSTN(OPTFLAG_WANTARG),

	PYNOECONSTN(DECODEFLAG_PS2SHIFT),

	PYNOECONSTN(BLITFLAG_ALPHABLEND),

	PYNOECONSTN(NOEUSERVAL_NONE),
	PYNOECONSTN(NOEUSERVAL_STRING),
	PYNOECONSTN(NOEUSERVAL_FLOAT),
	PYNOECONSTN(NOEUSERVAL_INT),
	PYNOECONSTN(NOEUSERVAL_BOOL),
	PYNOECONSTN(NOEUSERVAL_FILEPATH),
	PYNOECONSTN(NOEUSERVAL_FOLDERPATH),
	PYNOECONSTN(NOEUSERVAL_SAVEFILEPATH),

	PYNOECONSTN(NOEBLEND_NONE),
	PYNOECONSTN(NOEBLEND_ZERO),
	PYNOECONSTN(NOEBLEND_ONE),
	PYNOECONSTN(NOEBLEND_SRC_COLOR),
	PYNOECONSTN(NOEBLEND_ONE_MINUS_SRC_COLOR),
	PYNOECONSTN(NOEBLEND_SRC_ALPHA),
	PYNOECONSTN(NOEBLEND_ONE_MINUS_SRC_ALPHA),
	PYNOECONSTN(NOEBLEND_DST_ALPHA),
	PYNOECONSTN(NOEBLEND_ONE_MINUS_DST_ALPHA),
	PYNOECONSTN(NOEBLEND_DST_COLOR),
	PYNOECONSTN(NOEBLEND_ONE_MINUS_DST_COLOR),
	PYNOECONSTN(NOEBLEND_SRC_ALPHA_SATURATE),
	PYNOECONSTN(NUM_NOE_BLENDS),

	PYNOECONSTN(NOESPLINEFLAG_CLOSED),

	PYNOECONSTF(g_flPI),
	PYNOECONSTF(g_flDegToRad),
	PYNOECONSTF(g_flRadToDeg),

	PYNOECONSTN(PS2_VIFCODE_NOP),
	PYNOECONSTN(PS2_VIFCODE_STCYCL),
	PYNOECONSTN(PS2_VIFCODE_OFFSET),
	PYNOECONSTN(PS2_VIFCODE_BASE),
	PYNOECONSTN(PS2_VIFCODE_ITOP),
	PYNOECONSTN(PS2_VIFCODE_STMOD),
	PYNOECONSTN(PS2_VIFCODE_MSKPATH3),
	PYNOECONSTN(PS2_VIFCODE_MARK),
	PYNOECONSTN(PS2_VIFCODE_FLUSHE),
	PYNOECONSTN(PS2_VIFCODE_FLUSH),
	PYNOECONSTN(PS2_VIFCODE_FLUSHA),
	PYNOECONSTN(PS2_VIFCODE_MSCAL),
	PYNOECONSTN(PS2_VIFCODE_MSCNT),
	PYNOECONSTN(PS2_VIFCODE_MSCALF),
	PYNOECONSTN(PS2_VIFCODE_STMASK),
	PYNOECONSTN(PS2_VIFCODE_STROW),
	PYNOECONSTN(PS2_VIFCODE_STCOL),
	PYNOECONSTN(PS2_VIFCODE_MPG),
	PYNOECONSTN(PS2_VIFCODE_DIRECT),
	PYNOECONSTN(PS2_VIFCODE_DIRECTHL),

	PYNOECONSTN(BONEFLAG_ORTHOLERP),
	PYNOECONSTN(BONEFLAG_DIRECTLERP),
	PYNOECONSTN(BONEFLAG_NOLERP),
	PYNOECONSTN(BONEFLAG_DECOMPLERP),

	PYNOECONSTN(BITSTREAMFL_BIGENDIAN),
	PYNOECONSTN(BITSTREAMFL_DESCENDINGBITS),
	PYNOECONSTN(BITSTREAMFL_USERFLAG1),
	PYNOECONSTN(BITSTREAMFL_USERFLAG2),
	PYNOECONSTN(BITSTREAMFL_USERFLAG3),
	PYNOECONSTN(BITSTREAMFL_USERFLAG4),
	PYNOECONSTN(BITSTREAMFL_USERFLAG5),
	PYNOECONSTN(BITSTREAMFL_USERFLAG6),
	PYNOECONSTN(BITSTREAMFL_USERFLAG7),
	PYNOECONSTN(BITSTREAMFL_USERFLAG8),

	PYNOECONSTN(NOEKF_ROTATION_QUATERNION_4),
	PYNOECONSTN(NUM_NOEKF_ROTATION_TYPES),
	PYNOECONSTN(NOEKF_TRANSLATION_VECTOR_3),
	PYNOECONSTN(NOEKF_TRANSLATION_SINGLE),
	PYNOECONSTN(NUM_NOEKF_TRANSLATION_TYPES),
	PYNOECONSTN(NOEKF_SCALE_SCALAR_1),
	PYNOECONSTN(NOEKF_SCALE_SINGLE),
	PYNOECONSTN(NOEKF_SCALE_VECTOR_3),
	PYNOECONSTN(NOEKF_SCALE_TRANSPOSED_VECTOR_3),
	PYNOECONSTN(NUM_NOEKF_SCALE_TYPES),
	PYNOECONSTN(NOEKF_INTERPOLATE_LINEAR),
	PYNOECONSTN(NOEKF_INTERPOLATE_NEAREST),
	PYNOECONSTN(NUM_NOEKF_INTERPOLATION_TYPES),

	PYNOECONSTN(PVRTC_DECODE_PVRTC2),
	PYNOECONSTN(PVRTC_DECODE_LINEARORDER),
	PYNOECONSTN(PVRTC_DECODE_BICUBIC),
	PYNOECONSTN(PVRTC_DECODE_PVRTC2_ROTATE_BLOCK_PAL),
	PYNOECONSTN(PVRTC_DECODE_PVRTC2_NO_OR_WITH_0_ALPHA),

	PYNOECONSTN(NOE_ENCODEDXT_BC1),
	PYNOECONSTN(NOE_ENCODEDXT_BC3),
	PYNOECONSTN(NOE_ENCODEDXT_BC4),

The "rapi" module exposes the following methods:

	//core functionality
	//--
	{"getOutputName", Noesis_GetOutputName, METH_NOARGS, "returns destination filename."}, //args=none
	{"getInputName", Noesis_GetInputName, METH_NOARGS, "returns source filename."}, //args=none
	{"getLastCheckedName", Noesis_GetLastCheckedName, METH_NOARGS, "returns last checked/parsed filename."}, //args=none
	{"checkFileExt", Noesis_CheckFileExt, METH_VARARGS, "non-0 if filename contains extension. (uu)"}, //args=filename, extension
	{"getLocalFileName", Noesis_GetLocalFileName, METH_VARARGS, "returns local filename string. (u)"}, //args=full file path
	{"getExtensionlessName", Noesis_GetExtensionlessName, METH_VARARGS, "returns extensionless filename string. (u)"}, //args=filename
	{"getDirForFilePath", Noesis_GetDirForFilePath, METH_VARARGS, "returns directory string for filename. (u)"}, //args=filename
	{"checkFileExists", Noesis_CheckFileExists, METH_VARARGS, "returns non-0 if file exists. (u)"}, //args=filename
	{"noesisIsExporting", Noesis_IsExporting, METH_NOARGS, "returns non-0 if the handler is invoked for an export target instead of a preview or instanced module data load."}, //args=none
	{"loadIntoByteArray", Noesis_LoadIntoByteArray, METH_VARARGS, "returns PyByteArray with file. (u)"}, //args=filename
	{"loadPairedFile", Noesis_LoadPairedFile, METH_VARARGS, "returns PyByteArray with file. (ss)"}, //args=file description, file extension
	{"loadPairedFileOptional", Noesis_LoadPairedFileOptional, METH_VARARGS, "same as loadPairedFile, but returns None on cancel/fail instead of raising an exception. (ss)"}, //args=file description, file extension
	{"loadPairedFileGetPath", Noesis_LoadPairedFileGetPath, METH_VARARGS, "same as loadPairedFile, but returns None on cancel/fail instead of raising an exception, and returns a tuple of (data, loadPath). (ss)"}, //args=file description, file extension
	{"loadFileOnTexturePaths", Noesis_LoadFileOnTexturePaths, METH_VARARGS, "checks all texture paths for files, and returns None or bytearray of loaded data. (s)"}, //args=file name
	{"simulateDragAndDrop", Noesis_SimulateDragAndDrop, METH_VARARGS, "simulates drag and drop using specified file. (s)"}, //args=file name
	{"processCommands", Noesis_ParseCommands, METH_VARARGS, "processes given commands in the active rapi module. (s)"}, //args=commands

	{"exportArchiveFile", Noesis_ExportArchiveFile, METH_VARARGS, "exports an archive file. (sO)"}, //args=filename, data (PyBytes or PyByteArray)
	{"exportArchiveFileCheck", Noesis_ExportArchiveFileCheck, METH_VARARGS, "returns non-0 if calling exportArchiveFile on this path would overwrite. (s)"}, //args=filename

	//image/array utility
	//--
	//swapEndianArray can be useful for things like 360 dxt data (swap count of 2)
	{"swapEndianArray", Noesis_SwapEndianArray, METH_VARARGS, "returns the entire array endian-swapped at x bytes. (Oi|ii)"}, //args=source array, swap count, (optional) offset (in bytes, into array), stride
	{"imageResample", Noesis_ImageResample, METH_VARARGS, "returns a resampled rgba/32bpp image in a bytearray. (Oiiii)"}, //args=source image array (must be rgba32), source width, source height, dest width, dest height
	{"imageResampleBox", Noesis_ImageResampleBox, METH_VARARGS, "returns a resampled rgba/32bpp image in a bytearray. (Oiiii)"}, //args=source image array (must be rgba32), source width, source height, dest width, dest height
	//imageMedianCut - pixel stride is expected to be 3 for rgb888 or 4 for rgba8888 data. desiredColors can be any number. if useAlpha is true (and pixStride is 4), the alpha channel will be considered in the process.
	//returned bytearray is in rgba32 form.
	{"imageMedianCut", Noesis_ImageMedianCut, METH_VARARGS, "returns a median-cut rgba/32bpp image in a bytearray. (Oiiiii)"}, //args=source image array (must be rgba32), pixel stride, width, height, dest width, dest height, desiredColors, alpha flag
	//imageGetPalette - source image must be rgba32. if clear flag is non-0, the first entry of the palette will be made black/clear. if alpha flag is 0, alpha will be ignored.
	{"imageGetPalette", Noesis_ImageGetPalette, METH_VARARGS, "returns a rgba/32bpp X-entry palette in a bytearray. (Oiiiii)"}, //args=source image array (must be rgba32), width, height, number of colors, clear flag, alpha flag
	//imageApplyPalette source image must be rgba32, as must palette.
	{"imageApplyPalette", Noesis_ImageApplyPalette, METH_VARARGS, "returns an indexed/8bpp image in a bytearray. (OiiOi)"}, //args=source image array (must be rgba32), width, height, rgba32 palette, number of palette entries
	//example python code to generate a 8bpp image with 256-color palette and convert it back to rgba32:
	//(the 256 in each call could also be replaced with 16 to generate 4bpp data)
	/*
	imgPal = rapi.imageGetPalette(imgPix, imgWidth, imgHeight, 256, 0, 1)
	idxPix = rapi.imageApplyPalette(imgPix, imgWidth, imgHeight, imgPal, 256)
	#the following takes the provided palette and 8bpp pixel array, and combines it back into a rgba32 pixel array
	for i in range(0, imgWidth*imgHeight):
		imgPix[i*4 + 0] = imgPal[idxPix[i]*4 + 0]
		imgPix[i*4 + 1] = imgPal[idxPix[i]*4 + 1]
		imgPix[i*4 + 2] = imgPal[idxPix[i]*4 + 2]
		imgPix[i*4 + 3] = imgPal[idxPix[i]*4 + 3]
	*/
	//imageEncodeRaw/imageDecodeRaw - format string is in the format of "rx gx bx ax", where x is the number of bits taken by that component. does not automatically pad to byte boundaries between pixels. (use p if padding is desired)
	//omitting a component from the format string will mean the component is 0 (or in the case of alpha, 255) in the destination buffer.
	//component ordering also dictates the source order, so a1r5b5g5 would be formatted as "a1 r5 g5 b5" (spaces optional)
	//you may also use p to denote padding. p may be used numerous times in the format string, so if you wanted only 7 bits of each component on a rgba32 image, you'd use: "p1r7p1g7p1b7p1a7"
	{"imageEncodeRaw", Noesis_ImageEncodeRaw, METH_VARARGS, "returns encoded image from rgba32. (Oiis)"}, //args=source image array, width, height, format string
	{"imageDecodeRaw", Noesis_ImageDecodeRaw, METH_VARARGS, "returns rgba32 image from decoded raw pixels. (Oiis|i)"}, //args=source image array, width, height, format string, optional flags
	{"imageDecodeRawPal", Noesis_ImageDecodeRawPal, METH_VARARGS, "returns rgba32 image from decoded raw pixels+palette. (OOiiis|i)"}, //args=source image array, source palette, width, height, bits per pixel, format string (for palette colors), optional flags (noesis.DECODEFLAG_* flags)
	{"imageScaleRGBA32", Noesis_ImageScaleRGBA32, METH_VARARGS, "returns scaled rgba32 data. (OOii|i)"}, //args=source image array, list/tuple/vec4 for rgba scale, image width, image height, optype (0=normal, 1=renormalize rgba instead of clipping each component, 2=pow instead of scale)
	{"imageFlipRGBA32", Noesis_ImageFlipRGBA32, METH_VARARGS, "returns flipped rgba32 data. (Oiiii)"}, //args=source image array, width, height, horizontal flip flag, vertical flip flag
	{"imageGaussianBlur", Noesis_ImageGaussianBlur, METH_VARARGS, "returns gaussian-blurred rgba32 data from rgba32 source. (Oiif)"}, //args=source image array, width, height, sigma
	{"imageNormalMapFromHeightMap", Noesis_ImageNormalMapFromHeightMap, METH_VARARGS, "returns normal map rgba32 data from rgba32 source. (Oiiff)"}, //args=image array, width, height, height scale, texel scale
	{"imageInterpolatedSample", Noesis_ImageInterpolatedSample, METH_VARARGS, "returns a rgba tuple (in 0.0-1.0 range) of the interpolated sample from a rgba32 image (Oiiff)"}, //args=image array, width, height, x fraction, y fraction
	//example python code convert to r5g5b5a1 from rgba32, then go back to rgba32 from r5g5b5a1
	//imgPix = rapi.imageEncodeRaw(imgPix, imgWidth, imgHeight, "r5g5b5a1")
	//imgPix = rapi.imageDecodeRaw(imgPix, imgWidth, imgHeight, "r5g5b5a1")
	{"imageDecodeDXT", Noesis_ImageDecodeDXT, METH_VARARGS, "returns rgba32 image from decoded dxt. (Oiii)"}, //args=source image array, width, height, dxt format (may be one of the noesis.NOESISTEX_DXT* constants or a FOURCC code)
	{"imageDecodePVRTC", Noesis_ImageDecodePVRTC, METH_VARARGS, "returns rgba32 image from decoded pvrtc. (Oiii)"}, //args=source image array, width, height, bits per pixel
	{"imageUntile360Raw", Noesis_ImageUntile360Raw, METH_VARARGS, "returns untiled raw pixel data. (Oiii)"}, //args=source image array, width, height, bytes per pixel
	{"imageUntile360DXT", Noesis_ImageUntile360DXT, METH_VARARGS, "returns untiled dxt pixel data. (Oiii)"}, //args=source image array, width, height, block size (e.g. 8 for dxt1, 16 for dxt5)
	{"imageNormalSwizzle", Noesis_ImageNormalSwizzle, METH_VARARGS, "returns rgba32 image with various pixel processing. also auto-normalizes pixels. (Oiiiii)"}, //args=source image array (must be rgba32), width, height, swap alpha-red flag (0 or 1), derive b/z flag (0 or 1), signed flag (0 or 1)
	{"imageGetDDSFromDXT", Noesis_ImageGetDDSFromDXT, METH_VARARGS, "returns a dds file in a bytearray, from dxt data and supplied parameters. (Oiiii)"}, //args=source image array, width, height, number of mipmaps, dxt format (may be one of the noesis.NOESISTEX_DXT* constants or a FOURCC code)
	{"imageGetTGAFromRGBA32", Noesis_ImageGetTGAFromRGBA32, METH_VARARGS, "returns a tga file in a bytearray, from rgba32 data and supplied parameters. (Oii)"}, //args=source image array, width, height
	{"imageUntwiddlePSP", Noesis_ImageUntwiddlePSP, METH_VARARGS, "returns untwiddled (psp hardware) texture data. (Oiii)"}, //args=source image array, width, height, bits (not bytes) per pixel
	{"imageUntwiddlePS2", Noesis_ImageUntwiddlePS2, METH_VARARGS, "returns untwiddled (ps2 hardware) texture data. (Oiii)"}, //args=source image array, width, height, bits (not bytes) per pixel. bpp must be 4 or 8.
	{"imageTwiddlePS2", Noesis_ImageTwiddlePS2, METH_VARARGS, "returns twiddled (ps2 hardware) texture data. (Oiii)"}, //args=source image array, width, height, bits (not bytes) per pixel. bpp must be 4 or 8.
	{"imageToMortonOrder", Noesis_ImageFromMortonOrder, METH_VARARGS, "returns morton ordered image data data. (Oii|ii)"}, //args=source image array, width, height, (optional) bytes per pixel, inferred from array size if not specified, (optional) additional flags
	{"imageFromMortonOrder", Noesis_ImageToMortonOrder, METH_VARARGS, "returns morton ordered image data data. (Oii|ii)"}, //args=source image array, width, height, (optional) bytes per pixel, inferred from array size if not specified, (optional) additional flags
	{"imageGetTexRGBA", Noesis_ImageGetTexRGBA, METH_VARARGS, "gets rgba32 pixel data for a texture object. (O)"}, //args=NoeTexture
	{"imageBlit32", Noesis_ImageBlit32, METH_VARARGS, "image blit between 2 32-bit images. (OiiiiOiiii|ii)"}, //args=destination image, destination width, destination height, destination x offset, destination y offset, source image, source width, source height, source x offset, source y offset, (optional) dest stride, source stride (if not provided, assumed to be width*4)
	{"imageKernelProcess", Noesis_ImageKernelProcess, METH_VARARGS, "returns a processed image, processed by invoking a provided kernel method which operates on a bytearray containing data for the active pixel. (OiiiO|O)"}, //args=destination image, width, height, bytes per pixel, kernel method (should be implemented as def kernelMethod(imageData (original image), offset (current processing offset into image), kernelData (bytes of data to operate on), userData), (optional) user data
	{"imageDXTRemoveFlatFractionBlocks", Noesis_ImageRemoveFlatFractionBlocks, METH_VARARGS, "performs processing to turn dxt fraction-only blocks into direct color reference blocks for shitty hardware. (Oi)"}, //args=dxt data, texture format (must be one of the noesis.NOESISTEX_DXT* constants)
	{"imageEncodeDXT", Noesis_ImageEncodeDXT, METH_VARARGS, "returns encoded dxt from rgba image. (Oiiii)"}, //args=source image array, source pixel stride in bytes, width, height, dxt format (may be one of the noesis.NOE_ENCODEDXT_* constants)

	//data compression/decompression
	//--
	{"decompInflate", Noesis_DecompInflate, METH_VARARGS, "returns decompressed bytearray. (Oi|i)"}, //args=source bytes, destination size, (optional) window size
	{"decompPuff", Noesis_DecompPuff, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompBlast", Noesis_DecompBlast, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompLZS01", Noesis_DecompLZS01, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompFPK", Noesis_DecompFPK, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompLZO", Noesis_DecompLZO, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompLZO2", Noesis_DecompLZO2, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompLZHMelt", Noesis_DecompLZHMelt, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompXMemLZX", Noesis_DecompXMemLZX, METH_VARARGS, "returns decompressed bytearray. (Oi|iii)"}, //args=source bytes, destination size. optional: window bits (default 17), reset interval (default -1), frame size (default -1)
	{"decompPRS", Noesis_DecompPRS, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size.
	{"decompLZ4", Noesis_DecompLZ4, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size.
	{"decompLZMA", Noesis_DecompLZMA, METH_VARARGS, "returns decompressed bytearray. (OiO)"}, //args=source bytes, destination size, props bytes.
	{"getInflatedSize", Noesis_GetInflatedSize, METH_VARARGS, "walks through deflate stream to return final decompressed size. (O|i)"}, //args=source bytes, (optional) window bits
	{"getLZHMeltSize", Noesis_GetLZHMeltSize, METH_VARARGS, "walks through lzh stream to return final decompressed size. (O)"}, //args=source bytes
	{"getPRSSize", Noesis_GetPRSSize, METH_VARARGS, "walks through prs stream to return final decompressed size. (O)"}, //args=source bytes

	{"compressDeflate", Noesis_CompressDeflate, METH_VARARGS, "returns compressed bytearray. (O|i)"}, //args=source bytes, (optional) window size

	{"compressHuffmanCanonical", Noesis_CompressHuffmanCanonical, METH_VARARGS, "returns compressed bytearray. (O)"}, //args=source bytes
	{"decompHuffmanCanonical", Noesis_DecompHuffmanCanonical, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size
	{"decompRNC", Noesis_DecompRNC, METH_VARARGS, "returns decompressed bytearray. (Oi)"}, //args=source bytes, destination size

	//geometry/misc utility
	//--
	//getFlatWeights - e.g. wbytes = getFlatWeights(vertWeights, 4)
	{"getFlatWeights", Noesis_GetFlatWeights, METH_VARARGS, "returns byte array of flattened weights. (in the form of int bone indices for each vert, float weights for each vert) (Oi)"}, //args=list of NoeVertWeight, max weights (0 to use the max from the list)
	{"multiplyBones", Noesis_MultiplyBones, METH_VARARGS, "returns a list of NoeBones multiplied according to hierarchy. (O)"}, //args=list of NoeBone objects
	{"createTriStrip", Noesis_CreateTriStrip, METH_VARARGS, "returns a list of triangle strip indices. (O|i)"}, //args=list of triangle list indices, optional WORD specifying a strip termination value (if provided, strips are terminated with this value instead of degenerate faces)
	{"createBoneMap", Noesis_CreateBoneMap, METH_VARARGS, "returns a list of mapped bone indices and remaps the provided weights. (O)"}, //args=list of NoeVertWeights
	{"dataToIntList", Noesis_DataToIntList, METH_VARARGS, "returns a list of ints interpreted from raw data. (Oiii)"}, //args=bytearray, number of elements, RPGEODATA_ type, NOE_LITTLEENDIAN or NOE_BIGENDIAN
	{"dataToFloatList", Noesis_DataToFloatList, METH_VARARGS, "returns a list of floats interpreted from raw data. (Oiii|i)"}, //args=bytearray, number of elements, RPGEODATA_ type, NOE_LITTLEENDIAN or NOE_BIGENDIAN, (optional) scale and bias unsigned values into -1 to 1 range if 1
	{"decodeNormals32", Noesis_DecodeNormals32, METH_VARARGS, "returns a bytearray of decoded floating point normals. (Oiiiii)"}, //args=original buffer of 32-bit normals, stride, x bits, y bits, z bits, source endianness. x/y/z bit values can be negative to indicate a signed component.
	{"decodeTangents32", Noesis_DecodeTangents32, METH_VARARGS, "returns a bytearray of decoded floating point tangents. (Oiiiii)"}, //args=original buffer of 32-bit normals, stride, x bits, y bits, z bits, w bits, source endianness. x/y/z/w bit values can be negative to indicate a signed component.
	{"decompressEdgeIndices", Noesis_DecompressEdgeIndices, METH_VARARGS, "returns a bytearray of decompressed little-endian short indices. (Oi|i)"}, //args=compressed data, number of indices to be decompressed, (optional) source endianness (NOE_LITTLEENDIAN or NOE_BIGENDIAN)
	{"isGeometryTarget", Noesis_IsGeometryTarget, METH_NOARGS, "returns 1 if the active format is a geometry target, otherwise 0."}, //args=none
	{"setDeferredAnims", Noesis_SetDeferredAnims, METH_VARARGS, "sets deferred anim data for a list of NoeAnim objects."}, //args=list of NoeAnim
	{"getDeferredAnims", Noesis_GetDeferredAnims, METH_NOARGS, "returns a list of NoeAnim objects. (or an empty list, if no deferred data is available)"}, //args=none
	{"loadExternalTex", Noesis_LoadExternalTex, METH_VARARGS, "returns a NoeTexture, or None if the texture could not be found. (s)"}, //args=name/path of texture, without extension
	{"loadTexByHandler", Noesis_LoadTexByHandler, METH_VARARGS, "returns a NoeTexture, or None if the texture could not be found. (Os)"}, //args=source bytes, desired extension
	{"loadMdlTextures", Noesis_LoadMdlTextures, METH_VARARGS, "returns a tuple of NoeTextures, where all textures have already been converted to raw RGBA32. Sets the texRefIndex member of every NoeMesh in the model to the index of its texture in the returned tuple. (O)"}, //args=NoeModel, desired extension
	{"unpackPS2VIF", Noesis_UnpackPS2VIF, METH_VARARGS, "returns a tuple of NoePS2VIFUnpacks (O)"}, //args=vifcode data in byte form
	{"decodePSPVert", Noesis_DecodePSPVert, METH_VARARGS, "returns a NoePSPVertInfo (I)"}, //args=32-bit vertex tag
	{"splineToMeshBuffers", Noesis_SplineToMeshBuffers, METH_VARARGS, "returns a tuple of vertex and index data bytearrays. (OOiffi)"}, //args=spline, transform matrix, reverse triangle winding if 1, step size, size, subdivisions
	{"mergeKeyFramedFloats", Noesis_MergeKeyFramedFloats, METH_VARARGS, "returns a list of keyframes with n-element values given a list of keyframe floats, using linear interpolation to match keyframe times. (O)"}, //args=list of keyframed floats

	{"decodeADPCMBlock", Noesis_DecodeADPCMBlock, METH_VARARGS, "decodes an adpcm block. (OiiiiOOO|iid)"}, //args=data, bits per sample, num samples to decode, lshift, filter, filter table 0 (old sample) list, filter table 1 (older sample) list, list of 2 previous samples (will be modified), (optional) bit offset, bit stride, sample scale
	{"writePCMWaveFile", Noesis_WritePCMWaveFile, METH_VARARGS, "writes pcm wave file with provided data. (uOiii)"}, //args=filename, data, bitrate, samplerate, channelcount
	{"createPCMWaveHeader", Noesis_CreatePCMWaveHeader, METH_VARARGS, "returns a bytearray of pcm wave header data. (iiii)"}, //args=data size, bitrate, samplerate, channelcount

	//setPreviewOption - allows the following options (list may or may not be outdated at any given time)
	//"drawAllModels"						"0"/"1" (toggles drawing all models at once in preview mode by default)
	//"noTextureLoad"						"0"/"1" (toggles auto-loading of textures for previewed model based on tex/mat names)
	//"setAnimPlay"							"0"/"1" (if 1, auto-starts animation in preview)
	//"setAnimSpeed"						"<val>" (set frames per second for preview animation playback to <val>)
	//"setAngOfs"							"x y z" (set default preview angle offset to x y z)
	{"setPreviewOption", Noesis_SetPreviewOption, METH_VARARGS, "sets various preview options. (ss)"}, //args=optName, optVal
	{"callExtensionMethod", Noesis_CallExtensionMethod, METH_VARARGS, "calls an extension method. (s|)"}, //args=optName, ... (other arguments depend on extension being called)
	{"createProceduralAnim", Noesis_CreateProceduralAnim, METH_VARARGS, "generates a procedural animation. (OOi)"}, //args=NoeBone list, NoeProceduralAnim list, numFrames

	{"toolLoadGData", Noesis_ToolLoadGData, METH_VARARGS, "sets the module into global data mode and loads a file. this should only be invoked by tools, do not invoke it in format handlers or you will probably crash noesis. returns True on success. (s)"}, //args=filename
	{"toolFreeGData", Noesis_ToolFreeGData, METH_NOARGS, "frees global data, must be used after toolLoadGData."}, //args=none
	{"toolSetGData", Noesis_ToolSetGData, METH_VARARGS, "same as toolLoadGData, but allows you to set the gdata from a model list. (O)"}, //args=list of NoeModel
	{"toolExportGData", Noesis_ToolExportGData, METH_VARARGS, "exports loaded gdata to given file. returns true on success. (ss)"}, //args=filename, options
	{"toolGetLoadedModelCount", Noesis_ToolGetLoadedModelCount, METH_NOARGS, "returns number of loaded models in gdata."}, //args=none
	{"toolGetLoadedModel", Noesis_ToolGetLoadedModel, METH_VARARGS, "returns NoeModel from gdata (i)."}, //args=model index

	//rpg (Rich Procedural Geometry) interface
	//--
	//creates a rpg context. does not need to be explicitly freed in python, but make sure you don't grab any references to it and keep them outside of the method you created them in
	{"rpgCreateContext", RPGCreateContext, METH_NOARGS, "returns rpgeo context handle."}, //args=none
	//sets the active context
	{"rpgSetActiveContext", RPGSetActiveContext, METH_VARARGS, "sets the active context. (O)"}, //args=handle created by rpgCreateContext
	//All following rpg*/imm* functions operate on the active context and require no context handle to be passed in

	{"rpgReset", RPGReset, METH_NOARGS, "resets the active context."}, //args=none
	{"rpgSetMaterial", RPGSetMaterial, METH_VARARGS, "sets the material name. (s)"}, //args=string
	{"rpgSetLightmap", RPGSetLightmap, METH_VARARGS, "sets the lightmap/secondpass material name. (s)"}, //args=string
	{"rpgSetName", RPGSetName, METH_VARARGS, "sets the mesh name. (s)"}, //args=string
	{"rpgClearMaterials", RPGClearMaterials, METH_NOARGS, "clears all internal materials."}, //args=none
	{"rpgClearNames", RPGClearNames, METH_NOARGS, "clears all internal names."}, //args=none
	{"rpgClearMorphs", RPGClearMorphs, METH_NOARGS, "clears all internal morph buffers."}, //args=none
	{"rpgSetTransform", RPGSetTransform, METH_VARARGS, "sets geometry transform matrix. pass None to disable. (O)"}, //args=NoeMat43 or None
	{"rpgSetPosScaleBias", RPGSetPosScaleBias, METH_VARARGS, "sets geometry scale and bias - pass None, None to disable. (O)"}, //args=NoeVec3 (scale), NoeVec3 (bias) - or None, None
	{"rpgSetUVScaleBias", RPGSetUVScaleBias, METH_VARARGS, "sets uv coordinate scale and bias - pass None, None to disable. (O)"}, //args=NoeVec3 (scale), NoeVec3 (bias) - or None, None
	{"rpgSetBoneMap", RPGSetBoneMap, METH_VARARGS, "provides an index map for vertex weight references to bone indices. (O)"}, //args=list of ints
	{"rpgSetOption", RPGSetOption, METH_VARARGS, "sets rpgeo option. (ii)"}, //args=option flag (one of the noesis.RPGOPT_ constants), option status (1=enabled, 0=disabled)
	{"rpgGetOption", RPGGetOption, METH_VARARGS, "returns 1 if option is enabled, otherwise 0. (i)"}, //args=option flag
	//rpgSetEndian/rpgSetTriWinding are now deprecated, use rpgSetOption instead
	{"rpgSetEndian", RPGSetEndian, METH_VARARGS, "sets endian mode for reading raw buffers. (i)"}, //args=0 - little endian or 1 - big endian
	{"rpgSetTriWinding", RPGSetTriWinding, METH_VARARGS, "sets triangle winding mode. (i)"}, //args=0 - normal or 1 - reverse winding
	{"rpgSetStripEnder", RPGSetStripEnder, METH_VARARGS, "sets the strip-reset value. (i)"}, //args=value
	{"rpgGetStripEnder", RPGGetStripEnder, METH_NOARGS, "returns the strip-reset value."}, //args=none

	//immediate-mode drawing in python works by feeding variable-sized component lists and/or tuples.
	//keep in mind that these values will not be normalized for you, even if they are provided as fixed-point.
	{"immBegin", IMMBegin, METH_VARARGS, "begin immediate-mode drawing. (i)"}, //args=primitive type
	{"immEnd", IMMEnd, METH_NOARGS, "end immediate-mode drawing."}, //args=none
	{"immVertex3", IMMVertex3, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (O)"}, //args=3-component list
	{"immNormal3", IMMNormal3, METH_VARARGS, "feeds a vertex normal. (O)"}, //args=3-component list
	{"immTangent4", IMMTangent4, METH_VARARGS, "feeds a tangent vector. (O)"}, //args=4-component list, where 4th component is sign (-1 or 1) for bitangent
	{"immUV2", IMMUV2, METH_VARARGS, "feeds a vertex uv. (O)"}, //args=2-component list
	{"immLMUV2", IMMLMUV2, METH_VARARGS, "feeds a vertex lmuv. (O)"}, //args=2-component list
	{"immColor3", IMMColor3, METH_VARARGS, "feeds a vertex color. (O)"}, //args=3-component list
	{"immColor4", IMMColor4, METH_VARARGS, "feeds a vertex color. (O)"}, //args=4-component list
	{"immBoneIndex", IMMBoneIndex, METH_VARARGS, "feeds a vertex bone index. (O)"}, //args=x-component list
	{"immBoneWeight", IMMBoneWeight, METH_VARARGS, "feeds a vertex bone weight. (O)"}, //args=x-component list
	{"immVertMorphIndex", IMMVertMorphIndex, METH_VARARGS, "feeds a vertex morph index. (i)"}, //args=int
	//The following functions take raw bytes and decode them appropriately. Naming convention is #<type>, where # is number of elements and <type> is:
	//f - float
	//hf - half-float
	//b - byte
	//ub - unsigned byte
	//s - short
	//us - unsigned short
	//i - 32-bit int
	//ui - unsigned 32-bit int
	//X - arbitrary, you provide the RPGEODATA_ type and the number of elements.
	//All of these functions can also take an additional argument to specify an offset into the provided array of bytes.
	//For example, rapi.immVertex3f(positions[idx*12:idx*12+12]) could instead be rapi.immVertex3f(positions, idx*12), which is significantly less eye-raping and more efficient (as it requires no construction of a separate object for the slice)
	DEFINE_IMM_EX(immVertexX, IMMVertexX, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immVertex3f, IMMVertex3f, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immVertex3us, IMMVertex3us, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immVertex3s, IMMVertex3s, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immVertex3hf, IMMVertex3hf, METH_VARARGS, "feeds a vertex position. (must be called last for each primitive) (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immNormalX, IMMNormalX, METH_VARARGS, "feeds a vertex normal. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immNormal3f, IMMNormal3f, METH_VARARGS, "feeds a vertex normal. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immNormal3us, IMMNormal3us, METH_VARARGS, "feeds a vertex normal. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immNormal3s, IMMNormal3s, METH_VARARGS, "feeds a vertex normal. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immNormal3hf, IMMNormal3hf, METH_VARARGS, "feeds a vertex normal. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immTangentX, IMMTangentX, METH_VARARGS, "feeds a tangent vector. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immTangent4f, IMMTangent4f, METH_VARARGS, "feeds a tangent vector. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immTangent4us, IMMTangent4us, METH_VARARGS, "feeds a tangent vector. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immTangent4s, IMMTangent4s, METH_VARARGS, "feeds a tangent vector. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immTangent4hf, IMMTangent4hf, METH_VARARGS, "feeds a tangent vector. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immUVX, IMMUVX, METH_VARARGS, "feeds a vertex uv. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immUV2f, IMMUV2f, METH_VARARGS, "feeds a vertex uv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immUV2us, IMMUV2us, METH_VARARGS, "feeds a vertex uv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immUV2s, IMMUV2s, METH_VARARGS, "feeds a vertex uv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immUV2hf, IMMUV2hf, METH_VARARGS, "feeds a vertex uv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immLMUVX, IMMLMUVX, METH_VARARGS, "feeds a vertex lmuv. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immLMUV2f, IMMLMUV2f, METH_VARARGS, "feeds a vertex lmuv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immLMUV2us, IMMLMUV2us, METH_VARARGS, "feeds a vertex lmuv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immLMUV2s, IMMLMUV2s, METH_VARARGS, "feeds a vertex lmuv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immLMUV2hf, IMMLMUV2hf, METH_VARARGS, "feeds a vertex lmuv. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColorX, IMMColorX, METH_VARARGS, "feeds a vertex color. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immColor3f, IMMColor3f, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor3us, IMMColor3us, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor3s, IMMColor3s, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor3hf, IMMColor3hf, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor4f, IMMColor4f, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor4us, IMMColor4us, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor4s, IMMColor4s, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immColor4hf, IMMColor4hf, METH_VARARGS, "feeds a vertex color. (O)"), //args=bytes/bytearray of raw data
	DEFINE_IMM_EX(immBoneIndexX, IMMBoneIndexX, METH_VARARGS, "feeds a vertex bone index. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immBoneIndexub, IMMBoneIndexub, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneIndexb, IMMBoneIndexb, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneIndexus, IMMBoneIndexus, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneIndexs, IMMBoneIndexs, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneIndexui, IMMBoneIndexui, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneIndexi, IMMBoneIndexi, METH_VARARGS, "feeds a vertex bone index. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneWeightX, IMMBoneWeightX, METH_VARARGS, "feeds a vertex bone weight. (Oii)"), //args=bytes/bytearray of raw data, data type, number of elements
	DEFINE_IMM_EX(immBoneWeightf, IMMBoneWeightf, METH_VARARGS, "feeds a vertex bone weight. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneWeightus, IMMBoneWeightus, METH_VARARGS, "feeds a vertex bone weight. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneWeightub, IMMBoneWeightub, METH_VARARGS, "feeds a vertex bone weight. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	DEFINE_IMM_EX(immBoneWeighthf, IMMBoneWeighthf, METH_VARARGS, "feeds a vertex bone weight. (Oi)"), //args=bytes/bytearray of raw data, number of elements
	{"immUserData", IMMUserData, METH_VARARGS, "feeds vertex user data. (sO|i)"}, //args=name, data, (optional) flags

	//all buffer binding calls will keep a reference to the object passed in, until after the handler has exited.
	//each bind function also accepts None for the first bytes parameter, to indicate that the buffer type should be unbound.
	{"rpgBindPositionBuffer", RPGBindPositionBuffer, METH_VARARGS, "binds position buffer. (Oii)"}, //args=bytes for positions, dataType, stride
	{"rpgBindNormalBuffer", RPGBindNormalBuffer, METH_VARARGS, "binds normal buffer. (Oii)"}, //args=bytes for normals, dataType, stride
	{"rpgBindTangentBuffer", RPGBindTangentBuffer, METH_VARARGS, "binds tangent buffer. (Oii)"}, //args=bytes for tangents, dataType, stride
	{"rpgBindUV1Buffer", RPGBindUV1Buffer, METH_VARARGS, "binds uv1 buffer. (Oii)"}, //args=bytes for uv1's, dataType, stride
	{"rpgBindUV2Buffer", RPGBindUV2Buffer, METH_VARARGS, "binds uv2 buffer. (Oii)"}, //args=bytes for uv2's, dataType, stride
	{"rpgBindUVXBuffer", RPGBindUVXBuffer, METH_VARARGS, "binds uvx buffer. (Oiiii)"}, //args=bytes for uv2's, dataType, stride, uv index, uv elem count
	{"rpgBindColorBuffer", RPGBindColorBuffer, METH_VARARGS, "binds color buffer. (Oiii)"}, //args=bytes for colors, dataType, stride, num colors (3=rgb, 4=rgba)
	{"rpgBindBoneIndexBuffer", RPGBindBoneIndexBuffer, METH_VARARGS, "binds bone index buffer. (Oiii)"}, //args=bytes for bone indices, dataType, stride, number of indices per vert
	{"rpgBindBoneWeightBuffer", RPGBindBoneWeightBuffer, METH_VARARGS, "binds bone weight buffer. (Oiii)"}, //args=bytes for bone weights, dataType, stride, number of weights per vert
	{"rpgFeedMorphTargetPositions", RPGFeedMorphTargetPositions, METH_VARARGS, "feed vmorph position buffer. (Oii)"}, //args=bytes for positions, dataType, stride
	{"rpgFeedMorphTargetNormals", RPGFeedMorphTargetNormals, METH_VARARGS, "feed vmorph normal buffer. (Oii)"}, //args=bytes for positions, dataType, stride
	{"rpgCommitMorphFrame", RPGCommitMorphFrame, METH_VARARGS, "commits a frame of bound vertex morph data. (i)"}, //args=numverts for the morph frame
	{"rpgCommitMorphFrameSet", RPGCommitMorphFrameSet, METH_NOARGS, "commits all frames of bound vertex morph data."}, //args=none
	{"rpgGetMorphBase", RPGGetMorphBase, METH_NOARGS, "returns current morph frame base index."}, //args=none
	{"rpgSetMorphBase", RPGSetMorphBase, METH_VARARGS, "sets current morph frame base index. (i)"}, //args=morph frame base index, use -1 to invalidate current base
	{"rpgClearBufferBinds", RPGClearBufferBinds, METH_NOARGS, "clears all bound buffers."}, //args=none
	{"rpgCommitTriangles", RPGCommitTriangles, METH_VARARGS, "commit triangle buffer as bytes. (Oiii|i)"}, //args=bytes for index buffer, dataType, numIdx, primType, usePlotMap (1 or 0)
	{"rpgBindUserDataBuffer", RPGBindUserDataBuffer, METH_VARARGS, "binds user data buffer. (sOii|i)"}, //args=name, data bytes, element size, stride (may be 0 to specify per-instance instead of per-vertex), (optional) offset

	//all rpgBind*/rpgFeed* functions also have Ofs variants (e.g. rpgBindPositionBufferOfs) which accept an offset parameter after the stride parameter.
	//this can be useful in order to avoid making multiple slices of your vertex buffer, especially when you don't know how much vertex buffer you will need beforehand.

	{"rpgOptimize", RPGOptimize, METH_NOARGS, "optimizes lists to remove duplicate vertices, sorts triangles by material, etc."}, //args=none
	{"rpgSmoothNormals", RPGSmoothNormals, METH_NOARGS, "generates smoothed normals."}, //args=none
	{"rpgFlatNormals", RPGFlatNormals, METH_NOARGS, "generates flat normals."}, //args=none
	{"rpgSmoothTangents", RPGSmoothTangents, METH_NOARGS, "generates smoothed tangents."}, //args=none
	{"rpgUnifyBinormals", RPGUnifyBinormals, METH_VARARGS, "unifies tangent binormals. (i)"}, //args=flip (flips binormals if 1)
	{"rpgCreatePlaneSpaceUVs", RPGCreatePlaneSpaceUVs, METH_NOARGS, "generates plane-space uv's."}, //args=none
	{"rpgSkinPreconstructedVertsToBones", RPGSkinPreconstructedVertsToBones, METH_VARARGS, "skins all relevant committed (via immEnd/rpgCommitTriangles) vertex components using the provided bone list. must be performed prior to rpgConstructModel. (O|ii)"}, //args=bone list, (optional) vertex start index, (optional) vertex count
	{"rpgGetVertexCount", RPGGetVertexCount, METH_NOARGS, "returns number of vertices for current rpgeo context."}, //args=none
	{"rpgGetTriangleCount", RPGGetTriangleCount, METH_NOARGS, "returns number of triangles for current rpgeo context."}, //args=none
	{"rpgConstructModel", RPGConstructModel, METH_NOARGS, "returns a NoeModel constructed from the rpgeo."}, //args=none
	{"rpgConstructModelSlim", RPGConstructModelSlim, METH_NOARGS, "same as rpgConstructModel but omits various data types."}, //args=none
