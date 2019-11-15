
Doom-2-Brush README
===================

by Andrew Apted    April 2011


This program converts a DOOM map (inside a WAD file) to a
QUAKE .MAP file.  It is very basic and unpolished and not
very user friendly.  If it doesn't work properly or blows
your computer up, then tough luck.


USAGE:

1. edit the 'convdefs.txt' file in the doom2brush folder
   with a text editor (e.g. NOTEPAD).  This file tells
   doom2brush how to translate texture names and thing
   numbers.	

2. copy the wad file into the doom2brush folder and rename
   it to 'in.wad'.  Only the first map in the wad will be
   converted, so you may need to extract the level you want
   to convert first.

3. drag the 'in.wad' file onto glbsp.exe -- this will create
   a file called 'in.gwa'.  Don't forget this step if doing
   multiple maps!

4. run doom2brush.exe by double clicking on it -- this will
   convert the map and create a 'out.map' file.


NOTE: the map must be in DOOM format, this program does not
      handle Hexen or UDMF format which ZDoom projects
      sometimes use.

