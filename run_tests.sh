#!/bin/bash
################################################################################
# This is C3PO testing script
################################################################################
help()
{
echo "
This is C3PO testing script.

Options are :
    --help (or -h) : This help.
    --no-mpi (or -n) : To ignore tests with mpi.
    --cov (or -c) : To build a coverage report.
    --pylint (or -p) : To run pylint.
"
}

# Transform long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    "--help")   set -- "$@" "-h" ;;
    "--no-mpi") set -- "$@" "-n" ;;
    "--cov")    set -- "$@" "-c" ;;
    "--pylint") set -- "$@" "-p" ;;
    *)          set -- "$@" "$arg"
  esac
done

IGNOREMPI=""
PYTESTCOV=""
RUNPYLINT=false

while getopts hncp option
do
 case "${option}"
 in
  h) help ; exit 0;;
  n) IGNOREMPI="--ignore-glob="*mpi*"";;
  c) PYTESTCOV="--cov-report term --cov=c3po tests/";;
  p) RUNPYLINT=true;;
  "?") exit 1 ;;
 esac
done

pytest $IGNOREMPI $PYTESTCOV

if $RUNPYLINT ; then
  cd sources
  pylint c3po
fi
