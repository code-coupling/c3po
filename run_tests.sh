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
    --html (or -l) : To generate html reports.
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
    "--html")   set -- "$@" "-l" ;;
    "--cov")    set -- "$@" "-c" ;;
    "--pylint") set -- "$@" "-p" ;;
    *)          set -- "$@" "$arg"
  esac
done

IGNOREMPI=""
PYTESTCOV=""
ISCOV=false
RUNPYLINT=false
COVREPORT="term"
HTMLREPORT=""

while getopts hnlcp option
do
 case "${option}"
 in
  h) help ; exit 0;;
  n) IGNOREMPI="--ignore-glob="*mpi*"";;
  l) COVREPORT="html"
     HTMLREPORT="--html=report.html --self-contained-html";;
  c) ISCOV=true;;
  p) RUNPYLINT=true;;
  "?") exit 1 ;;
 esac
done

if $ISCOV ; then
  PYTESTCOV="--cov-report ${COVREPORT} --cov=c3po tests/"
fi

pytest $IGNOREMPI $PYTESTCOV $HTMLREPORT

if $RUNPYLINT ; then
  cd sources
  pylint c3po
fi
