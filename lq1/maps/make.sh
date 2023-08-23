#
# LibreQuake Map Builder Shell Script
# v0.0.2
# ---
# MissLavander-LQ & cypress/MotoLegacy
#

# Map compiler paths
LQ_QBSP_PATH="qbsp"
LQ_VIS_PATH="vis"
LQ_LIG_PATH="light"

# Location of per-map compilation argument paths
LQ_MAP_CON_PATH="buildconfigs"

# Location of .map source files
LQ_MAP_SRC_PATH="src-compile"

#
# DEFAULT COMPILATION FLAGS
# Always set before config execution to avoid
# "leaking" into another build.
#
LQ_DEF_BSP_FLAGS=""
LQ_DEF_VIS_FLAGS="-fast"
LQ_DEF_LIG_FLAGS="-extra4 -bounce -dirt"

#
# ericw-tools qbsp check
#
function check_for_compiler {
    if [ -z ${LQ_BSP_PATH+x} ]; then
        # No local path set, is it in $PATH?
        if ! command -v qbsp &> /dev/null
        then
            echo "Couldn't find ericw-tools, required to build map content."
            echo "Please see https://github.com/ericwa/ericw-tools/ for info."
            exit
        fi
    fi
}

#
# MAKE
#

function setup_compile_args {
    # Reset our compilation flags
    LQ_BSP_FLAGS=$LQ_DEF_BSP_FLAGS
    LQ_VIS_FLAGS=$LQ_DEF_VIS_FLAGS
    LQ_LIG_FLAGS=$LQ_DEF_LIG_FLAGS

    # Try to source a configuration file
    source "$LQ_MAP_CON_PATH/$map_name.conf" > /dev/null 2>&1

    # Set force-flags if provided by the user
    if [ $LQ_FORCED_BSP_FLAGS ]; then
        LQ_BSP_FLAGS=$LQ_FORCED_BSP_FLAGS
    fi
    if [ $LQ_FORCED_VIS_FLAGS ]; then
        LQ_BSP_FLAGS=$LQ_FORCED_VIS_FLAGS
    fi
    if [ $LQ_FORCED_LIG_FLAGS ]; then
        LQ_BSP_FLAGS=$LQ_FORCED_LIG_FLAGS
    fi
}

function command_make {
    # Don't bother doing anything if we can't find the compiler
    check_for_compiler;

    cd "$LQ_MAP_SRC_PATH/"

    # Iterate through every map in our source directory
    for f in $(find . -name '*.map') ; do
        # Clean up the string a bit
        map_name=${f:2:-4}
        # Get compilation flags ready
        setup_compile_args;
        # Perform build operation, silence non-errors
        echo "- $map_name"
        $LQ_BSP_PATH "$LQ_BSP_FLAGS $map_name.map" 1> /dev/null
        $LQ_VIS_PATH "$LQ_VIS_FLAGS $map_name.map" 1> /dev/null
        $LQ_LIG_PATH "$LQ_LIG_FLAGS $map_name.map" 1> /dev/null
    done

    cp *.bsp ..
    cp *.log logs/
    cp *.lit ..
    rm -f *.log *.bsp *.lit
    echo -e "* Build DONE"
}

#
# CLEAN
#

function command_clean {
    cd "$LQ_MAP_SRC_PATH/"
    rm -f *.prt *.texinfo *.pts
    echo -e "* Clean DONE"
}

#
# HELP
#

function command_help {
    echo -e "
                 LibreQuake make.sh Map Builder Script /// v0.0.2
    ==========================================================================
    This script requires ericw-tools (https://github.com/ericwa/ericw-tools/).
    --------------------------------------------------------------------------
    Usage: make.sh [OPERATION] [FLAGS]

    OPERATIONS:
    -h, help      read this msg :3
    -c, clean     remove extra files that are left after build
    -m, make      compile all available maps

    FLAGS:
    QBSP_FLAGS    override map-specific qbsp flags with a global setting
    QBSP_PATH     use a local path for qbsp instead of checking \$PATH
    VIS_FLAGS     override map-specific vis flags with a global setting
    VIS_PATH     use a local path for qbsp instead of checking \$PATH
    LIGHT_FLAGS   override map-specific light flags with a global setting
    LIGHT_PATH     use a local path for qbsp instead of checking \$PATH

    Example: make.sh -m LIGHT_FLAGS=\"-extra4 -bounce\" QBSP_PATH=\"~/qbsp\"
    =========================================================================="
}

#
# FLAG PARSER
#
OIFS=$IFS
IFS='='
for arg in "$@"; do
    # Split argument into flag=val
    read -r -a flagarg <<< "$arg"
    flag=${flagarg[0]}
    val=${flagarg[1]}

    # Parse and store flags.
    if [ $flag = "QBSP_FLAGS" ]; then
        LQ_FORCED_BSP_FLAGS=$val
    elif [ $flag = "QBSP_PATH" ]; then
        LQ_BSP_PATH=$val
    elif [ $flag = "VIS_FLAGS" ]; then
        LQ_FORCED_VIS_FLAGS=$val
    elif [ $flag = "VIS_PATH" ]; then
        LQ_VIS_PATH=$val
    elif [ $flag = "LIGHT_FLAGS" ]; then
        LQ_FORCED_LIG_FLAGS=$val
    elif [ $flag = "LIGHT_PATH" ]; then
        LQ_LIG_PATH=$val
    fi
done
IFS=$OIFS

#
# OPERATIONS PARSER
#

case $1 in
    # make/-m : command_make
    make)command_make;;
    -m)command_make;;
    # clean/-c : command_clean
    clean)command_clean;;
    -c)command_clean;;
    # help/-h : command_help
    help)command_help;;
    -h)command_help;;
    # if no command is specified just run help, otherwise
    # this would be a little annoying.
    *)command_help;;
esac
