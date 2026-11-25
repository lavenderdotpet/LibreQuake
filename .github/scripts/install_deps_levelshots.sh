#!/bin/bash

set -e

IRONWAIL_URL="https://github.com/andrei-drexler/ironwail/releases/download/v0.8.2/ironwail-0.8.2-linux-x64.tar.gz"

sudo apt-get update
sudo apt-get install -y wget zip unzip python3 imagemagick libmpg123-dev libsdl2-dev xvfb

repo_root=$(pwd)

# Install everything in /usr/local/bin to avoid path issues
cd /usr/local/bin

# Install IRONWAIL
wget -O ironwail.tar.gz "$IRONWAIL_URL"
tar --strip-components 1 -xf ironwail.tar.gz
rm ironwail.pak

# Done
cd "$repo_root"
