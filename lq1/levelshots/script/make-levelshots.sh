cd script/

echo 5041434b0c00000000000000 > pak0.pak

xxd -r -p pak0.pak pak0.pak

mv pak0.pak ../../

cd ../../../

ln -d -s -T lq1 id1

ironwail -nosound -nocdaudio +exec levelshots/make-levelshots.cfg

