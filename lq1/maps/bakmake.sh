### make commands ###
function make {
    cd src-compile/ ;
    for f in $(find . -name '*.map') ; do qbsp "$f" ; done ;
    for f in $(find . -name '*.map') ; do vis "$f" ; done ;
    for f in $(find . -name '*.map') ; do light -extra4 -bounce -dirt "$f" ; done ;
    cp *.bsp .. ; 
    cp *.log logs/ ;
    cp *.lit .. ;
    rm -f *.log *.bsp *.lit;
    echo -e "=====Build done=====";
}

function -m {
    cd src-compile/ ;
    for f in $(find . -name '*.map') ; do qbsp "$f" ; done ;
    for f in $(find . -name '*.map') ; do vis "$f" ; done ;
    for f in $(find . -name '*.map') ; do light -extra4 -bounce -dirt "$f" ; done ;
    cp *.bsp .. ; 
    cp *.log logs/ ;
    cp *.lit .. ;
    rm -f *.log *.bsp *.lit;
    echo -e "=====Build done=====";
}

function -f {
    cd src-compile/ ;
    for f in $(find . -name '*.map') ; do qbsp "$f" ; done ;
    for f in $(find . -name '*.map') ; do vis -fast "$f" ; done ;
    for f in $(find . -name '*.map') ; do light "$f" ; done ;
    cp *.bsp .. ;
    cp *.log logs/ ;
    cp *.lit .. ;
    rm -f *.log *.bsp *.lit;
    echo -e "=====Build done=====";
}

### clean commands ###
function clean {
    cd src-compile/ ;   
    rm -f *.prt *.texinfo *.pts;
    echo -e "=====Cleaning done=====";
}

function -c {
    cd src-compile/ ;   
    rm -f *.prt *.texinfo *.pts;
    echo -e "=====Cleaning done=====";
}

### help commands ###
function help {
    echo -e "
    ==========================================================================
    Dependencies [ericw-tools][https://github.com/ericwa/ericw-tools/]
    run ./make.sh make or -m to compile all maps
    run ./make.sh clean or -c to remove extra files that are left after build
    run ./make.sh help or -h to read this msg :3
    ==========================================================================
    ";
}

function -h {
    echo -e "
    ==========================================================================
    Dependencies [ericw-tools][https://github.com/ericwa/ericw-tools/]
    run ./make.sh make or -m to compile all maps
    run ./make.sh clean or -c to remove extra files that are left after build
    run ./make.sh help or -h to read this msg :3
    ==========================================================================
    ";
}


### command list ###
case $1 in
    make)
    make
    ;;

    -m)
    -m
    ;;

    -f)
    -f
    ;;

    clean)
    clean
    ;;
    
    -c)
    -c
    ;;

    help)
    help
    ;;

    -h)
    -h
    ;;

    *)
    echo -e "
    ====================================
     run ./make.sh help or ./make.sh -h
    ====================================
    "
    ;;
    
esac
