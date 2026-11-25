EXTENSION=jpg

./script/make-levelshots.sh && ./script/apply-overlay.sh && cd output/ && ../script/compress.sh

ls | grep \.$EXTENSION | while read LINE
do
	mv "$LINE" ../
done

cd ../

./script/clean-up.sh

