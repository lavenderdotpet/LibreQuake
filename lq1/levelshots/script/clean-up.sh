EXTENSION=png

mkdir -p ./output

ls | grep \.$EXTENSION | while read LINE
do
	mv "$LINE" "output/"
done

rm -r output/

cd ../

rm pak0.pak

cd ../

rm id1

