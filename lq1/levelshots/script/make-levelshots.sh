cd script/

echo 5041434b0c00000000000000 > pak0.pak

xxd -r -p pak0.pak pak0.pak

mv pak0.pak ../../

cd ../../../

ln -s -T lq1 id1

ironwail -condebug -nosound -nocdaudio +cl_startdemos 0 +exec levelshots/make-levelshots.cfg

