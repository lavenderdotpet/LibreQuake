#!/bin/bash
DATE=`date +'%Y%m%d'`
ARCHIVE=/tmp/LibreQuake$DATE.zip
ENTRY=librequake
rm $ARCHIVE
7z a -tzip $ARCHIVE *.sh *.wad $ENTRY.bsp $ENTRY.lit $ENTRY.map $ENTRY.txt ./screenshots/*.jpg
