cd script/

echo 5041434b0c00000000000000 > pak0.pak

xxd -r -p pak0.pak pak0.pak

mv pak0.pak ../../

cd ../../

rm ironwail.cfg

#echo alias make-levelshots "exec levelshots/make-levelshots.cfg" > autoexec.cfg
#echo make-levelshots >> autoexec.cfg

cd ../

rm id1

ln -s lq1 id1

ironwail +exec levelshots/make-levelshots.cfg

