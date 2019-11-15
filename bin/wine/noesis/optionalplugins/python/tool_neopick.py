from inc_noesis import *
import os
from fmt_atari_st import NeochromeImage, NEOCHROME_ENDIAN, NEOCHROME_BLOCKWIDTH
from ctypes import *
import noewin
from noewin import user32, gdi32, kernel32

"""
Controls:
 - CTRL + Left Click: Toggle byte-clip segment.
 - Hold Shift: Show all active byte-clip segments.
 - Right Click: Save file.
"""

def registerNoesisTypes():
	handle = noesis.registerTool("NEOpicker", neoPickToolMethod, "Tool to remove extraneous bytes behind pixel groups.")
	noesis.setToolFlags(handle, noesis.NTOOLFLAG_CONTEXTITEM)
	noesis.setToolVisibleCallback(handle, neoPickContextVisible)
	return 1

def neoPickContextVisible(toolIndex, selectedFile):
	if (selectedFile is None or
		os.path.splitext(selectedFile)[1].lower() != ".neo" or
		(noesis.getFormatExtensionFlags(os.path.splitext(selectedFile)[1]) & noesis.NFORMATFLAG_IMGREAD) == 0):
		return 0
	return 1

def neoPickAttachNeoToNoeWnd(noeWnd, data):
	neo = NeochromeImage(NoeBitStream(data, NEOCHROME_ENDIAN))
	if neo.parseImageHeader() == 0:
		noeWnd.neoData = data
		noeWnd.neoObject = neo
		flippedImage = rapi.imageFlipRGBA32(neo.rasterizeData(), neo.getWidth(), neo.getHeight(), 0, 1)
		noeWnd.neoDIB = bytes(rapi.imageEncodeRaw(flippedImage, neo.getWidth(), neo.getHeight(), "b8g8r8"))
		
		bmi = noewin.BITMAPINFO()
		bmi.bmiHeader.biBitCount = 24
		bmi.bmiHeader.biWidth = neo.getWidth()
		bmi.bmiHeader.biHeight = neo.getHeight()
		bmi.bmiHeader.biPlanes = 1
		bmi.bmiHeader.biSize = sizeof(noewin.BITMAPINFOHEADER)
		bmi.bmiHeader.biSizeImage = neo.getWidth() * neo.getHeight() * 3
		bmi.bmiHeader.biCompression = 0
		
		noeWnd.neoBMI = bmi
		return True
	return False
			
def neoPickToolMethod(toolIndex):
	filePath = noesis.getSelectedFile()
	nameNoExt, ext = os.path.splitext(filePath)
	neoPickPath = nameNoExt + "_neoPick" + ext

	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	
	with open(filePath, "rb") as f:
		data = f.read()

	noeWndWidth = 1280
	noeWndHeight = 800
	noeWndPad = 64
	noeWnd = noewin.NoeUserWindow("NEOpicker", "NeoPickerWindowClass", noeWndWidth + noeWndPad, noeWndHeight + noeWndPad, neoPickWindowProc)
	noeWnd.showClipped = False
	noeWnd.drawWidth = noeWndWidth
	noeWnd.drawHeight = noeWndHeight
	noeWnd.imgCoordX = 0
	noeWnd.imgCoordY = 0
	noeWnd.clipAddrs = set([])
	noeWnd.pickPath = neoPickPath
	
	if neoPickAttachNeoToNoeWnd(noeWnd, data):
		noeWnd.originalData = data
		#offset a bit into the noesis window
		noeWindowRect = noewin.getNoesisWindowRect()
		if noeWindowRect:
			windowMargin = 64
			noeWnd.x = noeWindowRect[0] + windowMargin
			noeWnd.y = noeWindowRect[1] + windowMargin
		if noeWnd.createWindow():
			noeWnd.doModal()
						
	noesis.freeModule(noeMod)

	return 0

def neoPickWindowProc(hWnd, message, wParam, lParam):
	if message == noewin.WM_PAINT:
		noeWnd = noewin.getNoeWndForHWnd(hWnd)
		ps = noewin.PAINTSTRUCT()
		rect = noewin.RECT()
		hBlitDC = user32.BeginPaint(hWnd, byref(ps))
		user32.GetClientRect(hWnd, byref(rect))	
		hDC = gdi32.CreateCompatibleDC(hBlitDC)
		bpp = gdi32.GetDeviceCaps(hBlitDC, 12)	
		width = rect.right - rect.left
		height = rect.bottom - rect.top
		hBmp = gdi32.CreateBitmap(width, height, 1, bpp, 0)
		gdi32.SelectObject(hDC, hBmp)
		if noeWnd.hFont:
			gdi32.SelectObject(hDC, noeWnd.hFont)

		hBc = gdi32.CreateSolidBrush(noewin.RGB(255, 0, 0))
		hBcHighlight = gdi32.CreateSolidBrush(noewin.RGB(255, 127, 0))
			
		if noeWnd.neoDIB:
			bmi = noeWnd.neoBMI
			neo = noeWnd.neoObject
			gdi32.StretchDIBits(hDC, 0, 0, noeWnd.drawWidth, noeWnd.drawHeight, 0, 0, bmi.bmiHeader.biWidth, bmi.bmiHeader.biHeight, cast(noeWnd.neoDIB, POINTER(c_ubyte * len(noeWnd.neoDIB))), byref(bmi), noewin.DIB_RGB_COLORS, noewin.SRCCOPY)
			
			blockOffset = neo.blockOffsetForPixelCoordinate(noeWnd.imgCoordX, noeWnd.imgCoordY)
			blockX, blockY = neo.pixelCoordinateForBlockOffset(blockOffset)
			absAddr = neo.dataOffset + blockOffset + neo.getBlockSize()
			
			toDrawWidth = noeWnd.drawWidth / neo.getWidth()
			toDrawHeight = noeWnd.drawHeight / neo.getHeight()
			drawX = min(max(int(blockX * toDrawWidth), 0), noeWnd.drawWidth - 1)
			drawY = min(max(int(blockY * toDrawHeight), 0), noeWnd.drawHeight - 1)

			if noeWnd.showClipped:
				gdi32.SelectObject(hDC, hBcHighlight)
				for hAddr in noeWnd.clipAddrs:
					hX, hY = neo.pixelCoordinateForBlockOffset(hAddr - neo.dataOffset - neo.getBlockSize())
					dHX = min(max(int(hX * toDrawWidth), 0), noeWnd.drawWidth - 1)
					dHY = min(max(int(hY * toDrawHeight), 0), noeWnd.drawHeight - 1)
					gdi32.Rectangle(hDC, dHX, dHY, int(dHX + NEOCHROME_BLOCKWIDTH * toDrawWidth), int(dHY + 1 * toDrawHeight))
			
			gdi32.SelectObject(hDC, hBc)
			gdi32.Rectangle(hDC, drawX, drawY, int(drawX + NEOCHROME_BLOCKWIDTH * toDrawWidth), int(drawY + 1 * toDrawHeight))

			gdi32.SetTextColor(hDC, noewin.RGB(255, 127, 0))
			gdi32.SetBkMode(hDC, noewin.TRANSPARENT)
			clippedText = "(clipped)" if absAddr in noeWnd.clipAddrs else "(unclipped)"
			noewin.user32.DrawTextW(hDC, "%i, %i / %i "%(blockX, blockY, blockOffset) + clippedText, -1, byref(rect), noewin.DT_SINGLELINE | noewin.DT_CENTER)
			
		gdi32.BitBlt(hBlitDC, 0, 0, width, height, hDC, 0, 0, 0x00CC0020)
		gdi32.DeleteDC(hDC)
		gdi32.DeleteObject(hBmp)
		gdi32.DeleteObject(hBc)
		gdi32.DeleteObject(hBcHighlight)
		user32.EndPaint(hWnd, byref(ps))
				
		return 0
	elif message == noewin.WM_ERASEBKGND:
		return 0
	elif message == noewin.WM_MOUSEMOVE:
		noeWnd = noewin.getNoeWndForHWnd(hWnd)
		neo = noeWnd.neoObject
		x = noeUnpack("h", noePack("H", lParam & 0xFFFF))[0]
		y = noeUnpack("h", noePack("H", (lParam >> 16) & 0xFFFF))[0]
		noeWnd.imgCoordX = min(max(int((x / noeWnd.drawWidth) * neo.getWidth()), 0), neo.getWidth() - 1)
		noeWnd.imgCoordY = min(max(int((y / noeWnd.drawHeight) * neo.getHeight()), 0), neo.getHeight() - 1)
		user32.InvalidateRect(noeWnd.hWnd, 0, False)
	elif message == noewin.WM_LBUTTONUP:
		if (wParam & noewin.MK_CONTROL):
			noeWnd = noewin.getNoeWndForHWnd(hWnd)
			neo = noeWnd.neoObject
			blockSize = neo.getBlockSize()
			blockOffset = neo.blockOffsetForPixelCoordinate(noeWnd.imgCoordX, noeWnd.imgCoordY)
			absAddr = neo.dataOffset + blockOffset + blockSize
			if absAddr in noeWnd.clipAddrs:
				noeWnd.clipAddrs.remove(absAddr)
			else:
				noeWnd.clipAddrs.add(absAddr)
			bs = NoeBitStream(noeWnd.originalData)
			dst = NoeBitStream()
			while not bs.checkEOF():
				if dst.tell() in noeWnd.clipAddrs:
					bs.readUByte()
				if (bs.getSize() - bs.tell()) < blockSize:
					break
				dst.writeBytes(bs.readBytes(blockSize))
			neoPickAttachNeoToNoeWnd(noeWnd, dst.getBuffer())
			user32.InvalidateRect(noeWnd.hWnd, 0, False)
	elif message == noewin.WM_RBUTTONUP:
		noeWnd = noewin.getNoeWndForHWnd(hWnd)
		wantWrite = True
		if os.path.exists(noeWnd.pickPath):
			wantWrite = (user32.MessageBoxW(hWnd, noeWnd.pickPath + " already exists. Do you want to overwrite it?", "NEOpicker", noewin.MB_YESNO) == noewin.IDYES)
		if wantWrite:
			with open(noeWnd.pickPath, "wb") as f:
				f.write(noeWnd.neoData)
			user32.MessageBoxW(hWnd, "Saved to " + noeWnd.pickPath, "NEOpicker", noewin.MB_OK)
	elif message == noewin.WM_KEYDOWN:
		if wParam == noewin.VK_SHIFT:
			noeWnd = noewin.getNoeWndForHWnd(hWnd)
			noeWnd.showClipped = True
			user32.InvalidateRect(noeWnd.hWnd, 0, False)
	elif message == noewin.WM_KEYUP:
		if wParam == noewin.VK_SHIFT:
			noeWnd = noewin.getNoeWndForHWnd(hWnd)
			noeWnd.showClipped = False
			user32.InvalidateRect(noeWnd.hWnd, 0, False)
	
	return noewin.defaultWindowProc(hWnd, message, wParam, lParam)
