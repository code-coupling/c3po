#!/bin/sh
#C3PO
export C3PODIR=$PWD/../../..
export C3POSOURCES=${C3PODIR}/sources
export PYTHONPATH=${PYTHONPATH}:${C3POSOURCES}

#tests
export PYTHONPATH=${PYTHONPATH}:${C3PODIR}
