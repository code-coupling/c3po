#!/bin/bash

cp Doxyfile_version.in Doxyfile.in 
VERSION=$(cat ../sources/c3po/VERSION) 
sed -i "s/C3PO_VERSION_NUMBER/$VERSION/" Doxyfile.in
doxygen Doxyfile.in
rm -f Doxyfile.in
