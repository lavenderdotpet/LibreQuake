Program Name:   Wally 
Version:        1.55B
Date:           7/09/2001
Authors:        Ty Matthews (ty@wwa.com)
                Neal White III (neal_white_iii@hotmail.com)

Purpose:
		Program to manipulate game texture files and industry-standard image
		formats, including Quake, Quake2, Half-Life, SiN, Heretic2, BMP, PCX,
		JPG, and PNG.  Allows for enhanced editing, viewing, browsing, setting 
		of game texture flags & contents, filters, clipboard cut/copy/paste, and 
		much more.  Allows for new creation, and loading of existing textures.  
		For a more detailed list, check the revision history or the 
		FAQ page on our site.

Compiler:       Visual C++ 6.0

Where to Get:   http://www.telefragged.com/wally                

Misc:           Wally is freeware.  As always per the standard legal rhetoric, 
		this program is given AS-IS.  No fitness of merchantibility is 
		either given or implied.  If something disastrous happens to 
		your machine, I'd feel really bad, but I cannot be held liable.  
		By using this program, you agree to the terms set forth herein.
	
Usage:          Unzip into a directory, and run Wally.exe.  Everything is
                self-contained.  Registry settings are made into the
                following key:

                     "HKEY_CURRENT_USER\Software\Team BDP\Wally"

Files Included:
		Wally.exe    TheApp!
		Wally.txt    You're reading it :)
		Wally.hlp    Help File
		Wally.cnt    Another Help-related file

		Custom Palettes included:
		Standard.pal, rainbow.pal, pastels.pal, metalic.pal, max.pal,
		grays.pal, earth.pal, and blend.pal

		Custom Decal WADs included:
		Rivets, Patterns, BulletHoles, and Signs
               
Tutorial:       Check out the web sites given in "Where to get"
                
Credits and Acknowledgements:

		Id Software and Valve... duh.  To ADarcJedi, Ozric, and Talon:
		thanks for putting up with my crap during our all-nighter
		ICQ meetings.  Mosquito from Quake2.com, for painting the 
		awesome splash screen and art.  Tom Cleghorn for doing up the 
		Help file and tutorial stuff.  Aaron Stackpole for pointing 
		out the goofy Q2 palette file, beta testing, and the HL 
		WAD3 specs.  Jeff Lane, Jim Nobles, Stonehand, Adam Cooper,
		and Brian Martel: thanks for testing this baby, and giving the 
		excellent feedback you've provided.

		To anyone we might have missed:  sorry!

Revision History:

	0.1 (1/16/1998):
		Wally is born

	0.7 (2/2/1998):
		First public release of Wally

	0.8 (2/16/1998):
		New stuff:
			- Clipboard paste
			- PCX import
			- Support for JASC .pal files
			- Wally Options menu
			- Texture pop-up dialog
			- Persistent settings

		Bug Fixes:
		        - Fixed texture flags
			- Fixed explorer-type launching

	0.81 (2/23/1998):
		New/Improved:	
		        - ReMipDeluxe has been implemented :)
		        - Added Paste As New Texture
	        	- Added Drag-n-Drop support for Wally shortcut

	0.90 (3/14/1998):
	 	Bug Fixes:
			- Draw Tiled
			- Drawing coords bug when scrolled
			- Drawing tools draw connected lines

		New/Improved:
			- Undo/Redo up to 50 items
			- Paintbrush
			- Eraser
			- Darken
			- Lighten
			- Scratch
			- Bullet Holes
			- Brush width
			- Brush shape
			- Brush intensity
			- Texture browsing
			- 24bit BMP support
			- 24bit clipboard pasting
			- Quake1 MIP file support
			- Changed File...Import to File...Convert
			- View of all four sub-mips at once
			- Improved drawing code
			- Better drag-n-drop support to Wally icon/screen
			
                
	1.00 (4/13/1998):
	 	Bug Fixes:
			- Fixed always too dark scratch
			- Fixed lighten/darken/tint tools after Edit...Paste
			- Fixed browse for directory
			
		New/Improved:
			- Flood fill
			- Big cursor for drawing tools
			- Constraining tool (vertical/horizontal)
			- Pattern paint
			- Added some tool widths (4, 6, and 8)
			- Copy to clipboard, copy to clipboard tiled
			- Mirror, flip, and rotate (left/right, 90-180-270 degrees)
			- Three blend filters (light, medium, heavy)
			- Spray paint tool
			- Color palette toolbar
	            	- Color Replacer tool
        		- Spray Color Replacer
			- 24-bit PCX import
			- Added export of BMP and PCX format
			- Moved multiple options dialog boxes into one
        		- Preset texture directory option
	            
	1.01 (4/23/1998):
		Bug Fixes:
			- Fixed wrong sub-mip view bug
			- Fixed cancelling of Browse Directory

		New/Improved:
			- Added multiple-file selection for File|Convert

	1.09 (6/10/98):
		Bug Fixes:
			- Fixed Flood Fill missing areas
			- Fixed unnecessary flashing with Undo/Redo
			- Fixed longer than 32-character filename/directory bug
	
		New/Improved:
			- Line tool
			- Connected Lines tool (PolyLine)
			- Ray Lines tool
			- Added better support for non-Q2 palettes
			- Changed Browse Folder selection to include persistence

	1.10 (7/03/98):
		New/Improved:
			- Rectangle drawing tool
			- Add Noise Filter
			- Brightness/Contrast Filter
			- Improved Blend Filter
			- Improved Filter interfaces
			- User-settable maximum number of Undo levels
			- Auto-update of thumbnail image for Browse view

	1.20 (08/12/98):
		New/Improved:
			- Emboss filter
			- Edge Detect filter
			- Marble Procedural Texture Generator
			- Better PCX export routine
			- Better support for custom palettes, and a big collection of some nice ones

	1.29 (12/31/98):
		New/Improved:
			- Gamma-correction
			- Mirror tool
			- Tiled marble tool
			- Diffuse filter
			- Rivet tool
			- Much improved custom palette editing
			- Improved drag/drop support
			- Batch conversion
			- Texture shift
			- Improved GUI tools
			- User-definable number of undo levels
			- Export to 24-bit or 8-bit option
			- Half-Life support (WAD3 files)
			- Gaussian option for AddNoise filter
			- Auto-zoom the view
			- Much improved 24-bit to 8-bit palette reduction
			- Sharpen filter
			- Offset filter

		Bug Fixes:
			- Amount Combo bug
			- Bullet hole access violation bug
			- 24-bit BMP export bug
			- 8-bit BMP import bug with PhotoShop files

	1.30 (1/17/99):
		Bug Fixes:
			- PCX header bug with Corel PhotoPaint images

	1.31 (1/21/99):
		New/Improved:
			- Resize filter!
			- Enhanced Add Noise filter
			- Edit/Load/Save Palette options
			- Color translate feature

	1.32 (1/26/99):
		New/Improved:
			- Most filters converted to 24-bit internally
			- Selection tool!
			- Improved status bar display to include additional info
			- Undo/redo memory compression (conserves RAM)

	1.33 (1/28/99):
		Bug Fixes:
			- Memory compression bug
			- Flashing sub-mip bug
		
	1.34 (2/12/99):
		New/Improved:
			- Most recently used filters shortcut
			- Fine/coarse grid!
			- Reduce colors filter
			- Quake1 MIP and WAD2 full support

		Bug Fixes:
			- Undo/redo memory compression bug
			- Initial startup directory bug with custom palettes

	1.34C (2/17/99):
		Bug Fixes:
			- New Half-Life textures not saved properly to WAD
			- Export of images from WAD2 failing
			- Zooming/grid bug, and improved drawing code
			- Loading custom Q2 palette not taking effect properly
			- ReMip bug with multiple threads

	1.35B (2/23/99):
		New/Improved:
			- Cool new about box, with hotlinks to our web site
			- Updated tool subsystem
			- Filter for the list of images in a package file
			- Drag and drop between package files
			- TGA support
			- New Quake1/Quake2 palette options page; more robust support for 
			custom palettes.
			- Batch conversion now will allow you to create any supported image type						

		Bug Fixes:
			- Paste bug with "maintain indexes" palette option
			- Minor gamma status bar bug

	1.36B (3/23/99):
		New:
			- New Decal Tool - draws "picture tubes" when you choose a line-style drawing mode. 
			- More batch file features 
			- Cut, copy, copy tiled, paste, delete selections
			- Transparency amount for paste
			- Invisible background for paste 
			- Custom Rivet, Bullet Hole, Patterned Paint, and Decal images 
			- Above tools save their images and restore them when you run Wally again 
			- Colored Rivets 
			- Package view: right button menu has decal stuff 
			- 32 bit Targa file support (just discards alpha channel) 
			- ReMip all or selected items in a WAD 
			- Custom palettes for every image type			 
			- Mouse wheel zoom in / out (thanks to Jeff Lane for this idea!) 
			- More robust support for large textures - 1024x1024 seems fairly stable now 
			- Better error handling - Wally will now beep when resources or memory gets low.			
			- Preliminary support for Build (c) engine games (Duke Nukem 3D, Redneck 
			  Rampage, Shadow Warrior, et al) 
			
		Improved:
			- Flood Fill uses less stack space (hardly ever fails now) 
			- Rivet spacing can be set to 64 pixels 
			- Patterned Paint now supports transparency amount 
			- Copy Tiled now uses separate multiples of X and Y 
			- GetNearestColor function speed-up (It's used all over the place). 
			- Some operations that used to seem sluggish are now positively zippy! 

		Bug Fixes:
			- Fixed Undo compression bug 
			- Fixed Fine Grid resource leak / crash bug 
			- Fixed Bullet Hole edge wrap bug 
			- Package file - open second image copy, lose changes bug 
			- Package file - open image, resize, save, image size not updated bug 
			- Package file - load a wad, create a new H-L texture, save into same wad file, 						image lost bug 
			- Package file - Deleting items from a WAD via right-button menu would crash 
			- Saving a HL texture into a WAD that happens to already be open will establish 						a link between the two. 
			- Many other minor bug fixes 


	1.37B (3/30/99):
		New:
			- Middle-button double-click zooms to 100%

		Improved:
			- Internal 24-bit stuff
			- Minor speed up for drawing tools
			- Improved UI for picture tubes
			- Delete items in an .ART file

		Bug Fixes:
			- Flood fill bug that caused Wally to hang
			- Rivets undo bug

	1.38B (5/06/99):
		Bug Fixes:
			- Tiled Marble "grout doesn't get generated"
			- Minor Tiled Marble bugs
			- Flood fill while tiled "doesn't fill correctly"
			- Moving images from one WAD to another via drag-n-drop

		Improved:
			- Sped up the drawing code
			- Pixel access routines are compatible with 24-bit

	1.39B (5/25/99):
		New:
			- Zoom out (1/3, 1/4, 1/5, etc) with mouse wheel
			- Sound effect when reaching 100%

		Improved:
			- Status bar shows zoom as a percent value
			- Added ability to create new images directly in a WAD file
	
	1.40B (7/08/99):
		New:
			- Water drop tool 

		Bug Fixes:
			- Export to Quake1 MIP with greater height than width messed up the re-mip
			- Saving Quake1 MIP to a Quake1 WAD would not save the MIP's name

	1.41B (8/20/99):
		New:
			- Total rewrite of Image Browser.  Now browses all game types and supported
			  images.
		
		Improved:
			- Batch conversion option to recurse subdirectories
			- Batch conversion option to retain directory structure

	1.42B (9/21/99):
		New:
			- SiN support
			- Heretic2 support
			- Non-16 image size support
			- Image|Adjust Canvas Size

		Bug Fixes:		
			- Many internal fixes for 24-bit and non-16 size support
			- Copy to clipboard bug where width was DWORD aligned
			- MouseWheel in browser now works

		Improved:
			- Option to turn off sub-mip display
			- Browser now has multiple selection feature
			- Right-click popup menu for browser with copy, delete, paste, and information 
			  choices
			- Drag and drop between explorer/browser and package/browser
			- Option to delete older cache files
			- Palette blending on 24-bit conversion when numcolors is less than 256
			
			
	1.42C (9/28/99):
		Bug Fixes:
			- Incorrect header size for WAL textures (black line at top of image)
			
		New:
			- File Associations tab on View|Options

	1.43B (10/07/99):
		Bug Fixes:
			- Zoom-in pixel distortion fixed
			
		Improved:
			- WAD editor enhancements: browse mode, tile mode, animate, and random tile
			- Correct algorithm for calculating overall color image for SiN textures

	1.43C (10/16/99):
		Bug Fixes:
			- Non-mip images caused Wally to crash
			- Resizing image then saving in a WAD crash
			- Scrolling problem on really large WAD files

		Improved:
			- Thumbnails in WAD editor support drag-n-drop
			- Liquid texture animation

	1.48B (11/25/99):
		Bug Fixes:
			- Palette lookup bug when painting
			- PCX decode bug
			- WAD editor double-click in tiled mode opens up wrong item
			- Open a texture from a WAD doesn't update the palette bug.
			- Use an effects tool, filter, draw with the same tool doesn't update the effects buffer bug.

		New:
			- Clone tool
			- Rubber stamp tool
			- Pack editor (.PAK file support)

	1.49B (02/15/2000):
		New:
			- 24-bit editing (yay!)
			- TGA/BMP/PCX editing in 24-bit as actual image types
			- PNG support
			- JPG support
			- File association option for non-game types	
			- New registry handling code
			- Moved size, shape, and amount combo boxes to the ToolSettings Toolbar
			- Added color tolerance setting
			- Added quick-zoom to settings tab
			- Lots of internal bug fixes for 24-bit

	1.50B (03/17/2000):
		New:
			- Clickable color swatches
			- Improved status line

		Bug Fixes:
			- Tons!

	1.51B (04/25/2000)
		Bug Fixes:
			- Many

	1.52B (12/31/2000)
		New:
			- Half-Life color decal wizard

		Improved:
			- Color translator (now will actually swap indexes like you'd expect)
			- Includes new exception handling for trapping errors
			- Includes debugging option for serious problems (e-mail us for info)

		Miscellaneous:
			- This is the first version compiled with Visual C++ 6.0

		Bug Fixes:
			- Fixed Edit|Clear; background color is what you chose

	1.53B (1/12/2001)
		Bug Fixes:
			- Selecting tools that use decals and then tool settings caused unhandled exception errors

		Improved:
			- Added unchecking option for file assocations so it actually removes the association
			- Added saving of current assocation to Wally's key so that previous owner can be restored

	1.54B (6/19/2001)
		Bug Fixes:
			- Total re-write of batch conversion code to fix annoying problems (streaky images, missed images, etc.)
			- Fix for upside-down 16-bit TGA files
			- Fix for retail version of Counter-Strike for the Decal Wizard
			- Adding text files to a PAK at the root node will now appear in the list

		Improved:
			- Added ability to create a new WAD file when doing batch conversion
 			- Can now do a File|New and choose PAK as the type
			- Updated library for PNG files
			- Rewrite of I/O code for nearly all image loading routines, making them faster with more OS-level buffering

		New:
			- WAD Merge Tool

	1.54C (6/19/2001)
		Bug Fixes:
			- 24-Bit BMP problem on opening

	1.55B (7/9/2001)
		Bug Fixes:
			- Image|Blend filter was not blending properly
			- Attempting to save over a read-only file was causing unhandled exception

		Improved:
			- Added Blue-Shift to the Half-Life derivatives that the color decal wizard recognizes
			- Tweaked image-loading code to improve performance

		New:
			- Serious Sam TEX file support
