Tex-Mex 3.4
------------

Release : 16 October 2000
-------------------------

1. Fixed a crash bug when Shift-selecting with no other texture selected
2. Fixed pcx export (was upside down)
3. Added support for import of FAKK2 (.ftx) textures

Release : 06 July 2000
----------------------

Export has been broke for a while now, and this release
fixes that, all exporters work fine again. As well as a few
other minor enhancements.


Release : 21 June 2000
-----------------------

A minor upgrade that fixes tga,jpg & bmp single item export prom
and adds support for .m8 (heretic2) and .m32 (SOF) textures

Release : 20 June 2000
-----------------------

new for 3.2

1. Texmex can now save to BSP's. Modifying the size of the textures or the number of
   textures will disable it. So now you cab open a BSP, paste over a texture (in the 
   detail view) and save it back to disk. mapname.bak is created automatically.
2. The size of the wad & detail views is now persistant between sessions.
3. If the detail view gets lost behind the wad view, clicking the detail view icon
   or double clicking an item in the was will bring it bakc to the forefront.
4. Mip export has been fixed and should now be compatible with the Mip format
   of other Apps, such as Wally.
5. Jpg Batch export has now been fixed.
6. The folder browser (for batch exports) has been changed, and now allows the 
   creation of new folders while browsing.


Release : 6 March 2000
-----------------------

new for 3.1 :-

1. Texmex now supports the selection of more than 1 item
   and most operations are carried out on the currently selected items.
2. Much tidyed up interface and GUI layout using new IE flat toolbars.
3. Integrated RemipDLX code into texmex for improved mipping, courtesy of Neal White.


Release : 29 December 1999
  -------------------------

new for 3.0 :-

1. You can now search for textures by typing its name in the wad view
2. You can change the display brightness of all views using the new 'sun' icons on the toolbar
   or the slider in the preferences.
3. You can change the display size of textures in the wad view using + and -
4. You can change the default texture size in the preferences.
5. Added a log file feature. All texture import/renames are logged to a file.
6. Added support for the jpeg file format.
7. Added an automip option when loading images (under preferences)
8. Fixed a problem with empty wads crashing texmex.


  Release : 02 October 1999
  -------------------------

new for 2.9 :-

1. Added an undo option to texmex. The defaul is ten operations (you can change this in the options)
2. Added a cancel option to the resize dialog
3. Added a 'skip file' option to the console picture size dialog (wad reading)
4. Reduced max texture name length to 15 characters. This is to stop WorldCraft freaking out.
   (all wads loaded, now have their names truncated to 15 chars)
5. Fixed a regsitry problem whereby double clicking a wad in explorer didn't always work.
6. Ive now dropped the beta tag. Seems pretty stable now, so i think im safe with this one :)
7. Fixed a couple of custom texture bugs (automip was b0rked).


  Released : 07 September 1999
  ----------------------------

New for 2.8 :-

1. Texmex now supports Wads that use custom palettes (T/C's e.t.c.)
2. Palettes can be added, replaced or deleted with all color conversions if required
3. Added item on status bar for palette type (quake/custom).
4. Added support for importing Blood2/Shogo DTX files.
5. Submips can now be pasted and loaded individually if required
6. When loading a new image (detail view) the item is now only renamed if it was previously unnamed.
7. 'Out of Memory' errors are handled much better now.
8. Fixed problem when reading in some BSP files.
9. Fixed small bug in BMP save routine that could cause a memory leak.
10. Improved TGA load routine to include compressed 24&32 bit files (e.g. diamond2c.tga in Q3Test).
11. Fixed 'Export All' for TGA and BMP (images were flipped).
12. Fixed problem when loading help and tip's.

Known issues :-

1. Brighness Adjust is disabled when using a custom palette. Fixing this would involve a complete
   re-write of the adjustment algorithm.

----------------------------------------------------------------------------------

New for Beta 2.7 :-

1. Animated view now supports water/lava, sky and animated textures.
2. Multiple animated views can be opened at a time.
3. Tiling size in animated and detailed view can be adjusted using [ ]
4. Zoom in animated and tiling view can be adjusted using + -
5. Image save now supports PCX.
6. Export images function now supports TGA24 and PCX formats.
7. Resource leak in animated view fixed.

Known issues :- 

1. None as yet


------------------------------------------------------------


New for Beta 2.6 :-

1. Image pasting now supports 1,4,8 and 24 bit images
2. The WAL reader now supports Daiktana textures
3. Added a new view for animated textures
4. Removed the 100 file import limit

Known issues :-

1. None as yet


--------------------------------------------------------


New for Beta 2.5 :-

1. TexMex can now read and paste any size images (previous versions currupted with some sizes)
2. Reading 32 bit TGA images is now supported but the mask is ignored.
3. The first draft of a Help system is included with this release.

Known Issues :-

1. Still the 100 file import limit.
2. If the HTML-Help doesn't work for you then please let me know. Include you system details (OS, IE4 e.t.c.)


----------------------------------------------------


New for Beta2 :-

1.  Wad3 import/export now implemented.
2.  Quake2 Export Palette conversion fixed.
3.  Texture name section of status bar increased (long texture names were cut off previously)
4.  When importing multiple files no message box appears during the import
    but a list of ignored files is presented at the end.

Known Issues :-


1.  The file import dialog won't accept more than about 100 files at a time.
2.  You tell me :)


------------------------------------------------


Send any bug reports (and if possible any files that caused the bug) to me at

	mickey@planetquake.com

Check the website for Updates and news

	www.planetquake.com/texmex
