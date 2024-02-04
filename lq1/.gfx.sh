#!/bin/bash
qpakman -pic gfx-wad/*.png -o gfx.wad
qpakman gfx/*.png -o name.pak
qpakman -f -r -e name.pak
qpakman -f -e name.pak
rm name.pak
