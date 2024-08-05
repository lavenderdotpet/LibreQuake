#!/bin/bash

set -e

QPAKMAN_URL="https://github.com/bunder/qpakman/archive/refs/tags/v0.67.tar.gz"
FTEQCC_URL="https://www.fteqcc.org/dl/fteqcc_linux64.zip"
ERICW_TOOL_URL="https://github.com/ericwa/ericw-tools/releases/download/2.0.0-alpha6/ericw-tools-2.0.0-alpha6-Linux.zip"

sudo apt-get update
sudo apt-get install -y wget zip unzip build-essential cmake libz-dev libpng-dev python3

repo_root=$(pwd)

# Install everything in /usr/local/bin to avoid path issues
cd /usr/local/bin

# Install QPAKMAN
wget -O qpakman.tar.gz "$QPAKMAN_URL"
tar --strip-components 1 -xf qpakman.tar.gz
cmake .
make

# Install FTEQCC
wget -O fteqcc.zip "$FTEQCC_URL"
unzip fteqcc.zip
ln -s fteqcc64 fteqcc

# Install ericw-tools
wget -O ericw-tools.zip "$ERICW_TOOL_URL"
unzip ericw-tools.zip

# Done
cd "$repo_root"
