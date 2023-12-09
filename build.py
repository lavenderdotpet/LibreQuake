# Code written by ZungryWare

import subprocess
import os
import json
import shutil
import warnings

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

def extract_file(file):
    if type(file) is list:
        return file[0], file[1]
    else:
        return file, file

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
        subprocess.call('qpakman * -o ../PAK0.PAK', cwd='working/pak0')
        shutil.copy('working/PAK0.PAK', os.path.join('releases', name, base_dir, 'PAK0.PAK'))
    
    # Build and copy pak1
    pak1_exists = len(os.listdir('working/pak1')) > 0
    if pak1_exists:
        subprocess.call('qpakman * -o ../PAK1.PAK', cwd='working/pak1')
        shutil.copy('working/PAK1.PAK', os.path.join('releases', name, base_dir, 'PAK1.PAK'))

def clear_working():
    # Remove working folder and its contents
    shutil.rmtree('./working', ignore_errors=True)

    # Create new empty directories
    os.makedirs(f'working', exist_ok=True)
    os.makedirs(f'working/pak0', exist_ok=True)
    os.makedirs(f'working/pak1', exist_ok=True)
    os.makedirs(f'working/unpacked', exist_ok=True)

def main():
    # Delete existing releases
    shutil.rmtree('./releases', ignore_errors=True)

    # Build each release one by one
    with open('build_releases.json', 'r') as json_file:
        releases = json.load(json_file)
        for key, value in releases.items():
            build_release(key, value)

main()
