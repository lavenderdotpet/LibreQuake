# Code written by ZungryWare

# This script copies the necessary files to build the different releases. The
# releases are specified in build_releases.json and they specify which
# components to use. Components are specified in build_components.json and each
# one is a big list of files that a release either wants all of or none of. Each
# component also specifies whether each file should end up in PAK0.PAK,
# PAK1.PAK, or just in the root folder without being packed. Files are copied to
# the 'working' directory, compiled, then copied over to a folder in the
# 'releases' directory. Before doing this, the script also compiles all of the
# wad and bsp/lit files so they can be copied over.

import sys
import subprocess
import os
import json
import shutil
import warnings
import runpy
import glob

# Builds a single file
def build_file(source_path, destination_path, source_if_missing):
    print(source_path)
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    try:
        shutil.copy(source_path, destination_path)
    except:
        if len(source_if_missing):
            shutil.copy(source_if_missing, destination_path)
        else:
            warnings.warn(f"Missing file with no substitute: {source_path}")

# Gets a source and dest path from a file entry File. Entries can be a string
# (where source and dest are the same) or a 2-long list (specifying the source
# and dest, respectively)
def extract_file(file):
    if type(file) is list:
        return file[0], file[1]
    else:
        return file, file

# Builds a single component from build_components.json
def build_component(component_data):
    # Determine the source if missing
    # This is the file to use as a substitute if the desired file is missing
    if component_data['source_if_missing']:
        source_if_missing = os.path.join('lq1/', component_data['source_if_missing'])
    else:
        source_if_missing = ""

    base_dir = component_data['base_dir']

    for file in component_data['files_pak0']:
        file_source, file_dest = extract_file(file)
        build_file(
            os.path.join(base_dir, file_source),
            os.path.join('working/pak0/', file_dest),
            source_if_missing,
        )
    for file in component_data['files_pak1']:
        file_source, file_dest = extract_file(file)
        build_file(
            os.path.join(base_dir, file_source),
            os.path.join('working/pak1/', file_dest),
            source_if_missing,
        )
    for file in component_data['files_unpacked']:
        file_source, file_dest = extract_file(file)
        build_file(
            os.path.join(base_dir, file_source),
            os.path.join('working/unpacked/', file_dest),
            source_if_missing,
        )

# Build a single release from build_releases.json
def build_release(name, data):
    # Print
    print(f"Building release {name}...")

    # Clear working and set up working directories
    clear_working()

    # Create release directory
    os.makedirs(f'releases', exist_ok=True)

    # Pull out base directory
    base_dir = data['base_dir']

    # Build components in release
    with open('build_components.json', 'r') as json_file:
        components = json.load(json_file)
        for component_name in data['components']:
            build_component(components[component_name])

    # Copy stuff over to release folder
    shutil.copytree('working/unpacked', os.path.join('releases', name, base_dir))

    # Build and copy pak0
    pak0_exists = len(os.listdir('working/pak0')) > 0
    if pak0_exists:
        os.chdir('working/pak0')
        filepaths = glob.glob('*')
        command = ['qpakman']
        command.extend(filepaths)
        command.extend(['-o', '../PAK0.PAK'])
        subprocess.call(command)
        os.chdir('../../')
        shutil.copy('working/PAK0.PAK', os.path.join('releases', name, base_dir, 'PAK0.PAK'))


    # Build and copy pak1
    pak1_exists = len(os.listdir('working/pak1')) > 0
    if pak1_exists:
        os.chdir('working/pak1')
        filepaths = glob.glob('*')
        command = ['qpakman']
        command.extend(filepaths)
        command.extend(['-o', '../PAK1.PAK'])
        subprocess.call(command)
        os.chdir('../../')
        shutil.copy('working/PAK1.PAK', os.path.join('releases', name, base_dir, 'PAK1.PAK'))

# Clears the working directory and sets up empty directories
def clear_working():
    # Remove working folder and its contents
    shutil.rmtree('./working', ignore_errors=True)

    # Create new empty directories
    os.makedirs(f'working', exist_ok=True)
    os.makedirs(f'working/pak0', exist_ok=True)
    os.makedirs(f'working/pak1', exist_ok=True)
    os.makedirs(f'working/unpacked', exist_ok=True)

def compile_wad():
    os.chdir('texture-wads')
    runpy.run_path('./compile_wads.py', run_name="__build__")
    os.chdir('../')

def compile_bsp():
    os.chdir('./lq1/maps')
    runpy.run_path('./compile_maps.py', run_name="__build__")
    os.chdir('../../')

def compile_progs():
    subprocess.call(['fteqcc', 'qcsrc/progs.src'])

def main():
    # First, compile wads
    if (len(sys.argv) > 1 and (sys.argv[1] == '-n' or sys.argv[1] == '--nocompile')):
        # Skip compile
        pass
    else:
        # Compile
        compile_wad()
        compile_bsp()
        compile_progs()

    # Delete existing releases
    shutil.rmtree('./releases', ignore_errors=True)

    # Build each release one by one
    with open('build_releases.json', 'r') as json_file:
        releases = json.load(json_file)
        for key, value in releases.items():
            build_release(key, value)

    # Confirmation
    print("Build complete!")

if __name__ == "__main__":
    main()
