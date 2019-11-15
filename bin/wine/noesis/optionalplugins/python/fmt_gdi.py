#GDI extraction support

from inc_noesis import *
from inc_imgtools import NoeImgReader, NoeImgTrack
import shlex

MAX_REASONABLE_GDI_SIZE = 1024 * 1024

def registerNoesisTypes():
	handle = noesis.register("GD-ROM container", ".gdi")
	noesis.setHandlerExtractArc(handle, gdiExtractArc)
	return 1

def gdiExtractArc(fileName, fileLen, justChecking):
	if fileLen > MAX_REASONABLE_GDI_SIZE: #sanity check
		return 0
		
	gdiTracks = []
	try:
		with open(fileName, "r") as f:
			for line in f:
				values = shlex.split(line)
				if len(values) == 6:
					binPath = values[4]
					fullBinPath = os.path.join(rapi.getDirForFilePath(fileName), binPath)
					if os.path.exists(fullBinPath):
						baseLba = int(values[1])
						trackType = int(values[2])
						sectorSize = int(values[3])
						
						stream = None if justChecking else open(fullBinPath, "rb")
						#this would fall over for things like mode 2 xa with subheader, but we never expect that in a GD-ROM image
						sectorHeaderSize = 16 if sectorSize > 2048 else 0
						
						track = NoeImgTrack(stream, len(gdiTracks), baseLba, sectorSize, 2048, sectorHeaderSize)
						track.binPath = binPath
						track.fullBinPath = fullBinPath
						gdiTracks.append(track)
					else:
						return 0
	except:
		return 0

	if len(gdiTracks) == 0:
		return 0

	if justChecking:
		return 1

	print("Found", len(gdiTracks), "tracks, checking for volume data.")
	img = NoeImgReader(gdiTracks)
	for track in gdiTracks:
		if track.sectorSize != 2352:
			#we'll continue anyway, but there's a good chance something bad will happen
			print("Warning: GD-ROM image not in expected mode 1 form. Sector size:", track.sectorSize)
	
		imgVol = img.readFileSystemVolume(track.index)
		if imgVol:
			print("Read volume information from", track.fullBinPath)
			for imgFile in imgVol.files:
				writePath = track.binPath + "_vol/" + imgFile.path
				print("Writing", writePath)
				rapi.exportArchiveFile(writePath, img.readFileData(imgFile))
	img.close()

	return 1
