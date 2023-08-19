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

function -h {
    echo -n "";
    echo "
========================================================================
    run ./make.sh to compile all maps
    run ./make.sh clean to remove extra files that are left after build
    run ./make.sh help or -h to read this msg :3
========================================================================
    ";
    echo -n "";
}

function help {
    echo -n "";
    echo "
========================================================================
    run ./make.sh to compile all maps
    run ./make.sh clean to remove extra files that are left after build
    run ./make.sh help or -h to read this msg :3
========================================================================
    ";
    echo -n "";
}

case $1 in
    clean)
    clean
    ;;

    help)
    help
    ;;

    -h)
    -h
    ;;

    *)
    make
    ;;
    
esac