#!/bin/bash


# Set Bash options for safety
set -eu


# Make sure target directory exists
# TODO: If it does, warn the user
mkdir -p "${path}"


>&2 echo "Downloading R..."
cd "${tmp_dir}"
curl --silent "${url}" > "R-${version}.tar.gz" 2>>${stderr}


>&2 echo "Extracting R..."
tar xzf "R-${version}.tar.gz" >>${stdout} 2>>${stderr}
rm -f "R-${version}.tar.gz" >>${stdout} 2>>${stderr}


>&2 echo "Configuring R..."
cd R-*
./configure --prefix="${path}" >>${stdout} 2>>${stderr}


>&2 echo "Compiling R..."
make >>${stdout} 2>>${stderr}


>&2 echo "Installing R..."
make install >>${stdout} 2>>${stderr}
