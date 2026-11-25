WIDTH=1600
HEIGHT=1200
EXTENSION=png

mkdir -p ./output

ls | grep \.$EXTENSION | while read LINE
do
	magick -define colorspace:auto-grayscale=off  -type truecolor "$LINE" -interpolate Integer -filter point -resize ${WIDTH}x${HEIGHT}! script/overlay -compose Hard_Light -composite "output/$LINE"
done
