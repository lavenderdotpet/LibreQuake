#
# LibreQuake Map Builder Python Script
# v0.0.3
# ---
# MissLavander-LQ & cypress/MotoLegacy & ZungryWare/ZungrySoft
#
import os
import re
import subprocess
import sys
import shutil

# Map compiler paths
LQ_BSP_PATH = "qbsp"
LQ_VIS_PATH = "vis"
LQ_LIG_PATH = "light"

# Location of per-map compilation argument paths
LQ_MAP_CON_PATH = "src/-buildconfigs-"

# Default compilation flags
LQ_DEF_BSP_FLAGS = ""
LQ_DEF_VIS_FLAGS = ""
LQ_DEF_LIG_FLAGS = "-bounce -dirt"


# Check for compiler
def check_for_compiler():
    if not LQ_BSP_PATH:
        if not shutil.which('qbsp'):
            print("Couldn't find ericw-tools, required to build map content.")
            print("Please see https://github.com/ericwa/ericw-tools/ for info.")
            sys.exit()


def get_config_path(map_path):
    # We know that the config dir mirrors the map dir structure so we need to remove the common path.
    # whats left is the relative path to the map file.
    # Then we exchange the extension from .map to .conf
    map_abs_path = os.path.abspath(map_path)
    conf_abs_path = os.path.abspath(LQ_MAP_CON_PATH)
    common_path = os.path.commonpath([map_abs_path, conf_abs_path])
    map_rel_path = os.path.relpath(map_abs_path, common_path)
    map_rel_path_no_ext = os.path.splitext(map_rel_path)[0]
    return os.path.join(LQ_MAP_CON_PATH, f"{map_rel_path_no_ext}.conf")


def get_config(config_path):
    # Read the config file and return a dictionary of key-value pairs
    if not os.path.exists(config_path):
        print(f"No config file found at {config_path}. Using default values.")
        return {}

    config = {}
    with open(config_path, "r") as config_file:
        for line in config_file:
            # Strip whitespace and ignore empty lines or comments
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)  # Split on the first '=' only
                config[key.strip()] = value.strip('"').strip()
    return config


def get_compile_flags(map_path):
    config_path = get_config_path(map_path)
    config = get_config(config_path)

    LQ_BSP_FLAGS = config.get("LQ_BSP_FLAGS", LQ_DEF_BSP_FLAGS)
    LQ_VIS_FLAGS = config.get("LQ_VIS_FLAGS", LQ_DEF_VIS_FLAGS)
    LQ_LIG_FLAGS = config.get("LQ_LIG_FLAGS", LQ_DEF_LIG_FLAGS)

    return LQ_BSP_FLAGS, LQ_VIS_FLAGS, LQ_LIG_FLAGS


# Execute command
def execute_command(command, fail_on_regexes=[], **kwargs):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,  # Fail on non-zero exit code
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        print(f"!!! Command failed:\n{e.stdout.decode('utf-8')}")
        raise e

    stdout_str = result.stdout.decode("utf-8")
    for pattern in fail_on_regexes:
        if re.search(pattern, stdout_str):
            print(stdout_str)
            raise ValueError(f"!!! Command failed: `{pattern}` found in output")


# Find all files in directory with this extension
def find(directory, ext):
    result_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                result_list.append(os.path.join(root, file))
    return result_list


def move_file(src, dest_dir):
    # Get the base filename
    filename = os.path.basename(src)

    # Construct the full path for the destination file
    dest_file = os.path.join(dest_dir, filename)

    # Check if the destination file exists and remove it if it does
    if os.path.isfile(dest_file):
        os.remove(dest_file)

    # Move the source file to the destination directory
    shutil.move(src, dest_file)


# Command make
def command_make(specific_map=None, specific_dir=None):
    check_for_compiler()

    search_dir = specific_dir if specific_dir else './'

    for f in find(search_dir, '.map'):
        map_name = os.path.splitext(os.path.basename(f))[0]

        if specific_map and map_name != specific_map:
            continue

        if not specific_map:
            if "skip" in f:
                continue
            if "archive" in f:
                continue
            if "autosave" in f:
                continue

        LQ_BSP_FLAGS, LQ_VIS_FLAGS, LQ_LIG_FLAGS = get_compile_flags(f)

        print(f"Compiling {f}")

        unwanted_bsp_warnings = [
            r"WARNING: unable to (find|load) texture",
            r"WARNING: Couldn't locate texture",
        ]
        execute_command(
            [LQ_BSP_PATH] + LQ_BSP_FLAGS.split() + [f"{map_name}.map"], cwd=os.path.dirname(f),
            fail_on_regexes=unwanted_bsp_warnings,
        )

        if "LQ_SKIP" not in LQ_VIS_FLAGS:
            execute_command([LQ_VIS_PATH] + LQ_VIS_FLAGS.split() + [f"{map_name}.bsp"], cwd=os.path.dirname(f))

        if "LQ_SKIP" not in LQ_LIG_FLAGS:
            execute_command([LQ_LIG_PATH] + LQ_LIG_FLAGS.split() + [f"{map_name}.bsp"], cwd=os.path.dirname(f))

    # Move bsp and lit files into the /lq1/maps directory
    print("Moving files...")
    for ext in [".bsp", ".lit"]:
        for file in find('./src', ext):
            move_file(file, "./")

    print("* Build DONE")


# Command single
def command_single(map_name):
    if not map_name:
        print("Map name needed, e.g. 'lq_e1m1'")
        return
    command_make(specific_map=map_name)


# Command directory
def command_directory(directory):
    if not directory:
        print("Directory name needed, e.g. 'e1'")
        return
    command_make(specific_dir=directory)


# Command clean
def command_clean():
    for ext in [".bsp", ".lit", ".prt", ".texinfo", ".texinfo.json", ".pts", ".log"]:
        for file in find('./', ext):
            os.remove(file)
    print("* Clean DONE")


# Command help
def command_help():
    help_text = """
                 LibreQuake make.py Map Builder Script /// v0.0.3
    ==========================================================================
    This script requires ericw-tools (https://github.com/ericwa/ericw-tools/).
    --------------------------------------------------------------------------
    Usage: make.py [OPERATION] [FLAGS]

    OPERATIONS:
    -h, help            read this msg :3
    -c, clean           remove extra files that are left after build
    -m, make            compile all available map OR
    -s, single <MAP>    compile a specified single map
    -d, directory <DIR> compile all maps in a specified directory

    FLAGS:
    QBSP_FLAGS    override map-specific qbsp flags with a global setting
    QBSP_PATH     use a local path for qbsp instead of checking $PATH
    VIS_FLAGS     override map-specific vis flags with a global setting
    VIS_PATH     use a local path for qbsp instead of checking $PATH
    LIGHT_FLAGS   override map-specific light flags with a global setting
    LIGHT_PATH     use a local path for qbsp instead of checking $PATH

    Example: make.py -m LIGHT_FLAGS=\"-extra4 -bounce\" QBSP_PATH=\"~/qbsp\"
    Example: make.py -s e1/lq_e1m1
    ==========================================================================
    """
    print(help_text)


# Argument parsing
def parse_args(args):
    operations = {
        '-m': command_make,
        '-s': lambda: command_single(args[1] if len(args) > 1 else None),
        '-d': lambda: command_directory(args[1] if len(args) > 1 else None),
        '-c': command_clean,
        '-h': command_help,
    }

    operation = operations.get(args[0], command_help)
    operation()


# If being run from the command line
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        parse_args(sys.argv[1:])
    else:
        command_help()

# If being run from build.py
if __name__ == "__build__":
    command_make()
