#!/bin/sh
#C3PO
export C3PODIR=$PWD/../..
export C3POSOURCES=${C3PODIR}/sources
export PYTHONPATH=${PYTHONPATH}:${C3POSOURCES}

#MED / MEDCOUPLING
export LD_LIBRARY_PATH=/home/apollo3/product/hdf5-1.10.3/lin-x86-64-cen7/lib/:/home/apollo3/product/SALOME-9.4.0/med-4.0.0/lin-x86-64-cen7/lib/:/home/apollo3/product/SALOME-9.4.0/MEDCOUPLING/lin-x86-64-cen7/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/home/apollo3/product/SALOME-9.4.0/MEDCOUPLING/lin-x86-64-cen7/lib/python3.6/site-packages:$PYTHONPATH
