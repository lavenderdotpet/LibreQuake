function make {
    cd src/ ;
    for f in $(find . -name '*.map') ; do qbsp "$f" ; done ; 
    for f in $(find . -name '*.map') ; do vis "$f" ; done ; 
    for f in $(find . -name '*.map') ; do light -extra "$f" ; done ;
    cp *.bsp .. ; 
    cp *.log logs/ ;
    cp *.lit .. ;
    rm -f *.log *.bsp *.lit;
    echo -n "";
    echo -n "=====Build done=====";
    echo -n "";
}

function clean {
    cd src/ ;   
    rm -f *.prt *.texinfo *.pts;
    echo -n "";
    echo "=====Cleaning done=====";
    echo -n "";
}

case $1 in
    clean)
    clean
    ;;

    *)
    make
    ;;
    
esac