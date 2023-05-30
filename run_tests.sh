#!/bin/bash
set -euo pipefail
unalias -a
current_script_dir="$( cd "$( dirname "${0}" )" &> /dev/null && pwd )"
################################################################################
# This is C3PO testing script
################################################################################
help()
{
echo "
This is C3PO testing script.

Options are :
    --help (or -h) : This help.
    --no-mpi (or -n) : To ignore tests with mpi (including medmpi).
    --no-medmpi (or -m) : To ignore tests using mpi features of medcoupling.
    --html (or -l) : To generate html reports.
    --cov (or -c) : To build a coverage report.
    --pylint (or -p) : To run pylint.
"
}

# Transform long options to short ones
for arg in "$@"; do
  shift
  case "$arg" in
    "--help")      set -- "$@" "-h" ;;
    "--no-mpi")    set -- "$@" "-n" ;;
    "--no-medmpi") set -- "$@" "-m" ;;
    "--html")      set -- "$@" "-l" ;;
    "--cov")       set -- "$@" "-c" ;;
    "--pylint")    set -- "$@" "-p" ;;
    *)             set -- "$@" "$arg"
  esac
done

IGNOREMPI=""
IGNOREMEDMPI=""
PYTESTCOV=""
ISCOV=false
RUNPYLINT=false
COVREPORT="term"
HTMLREPORT=""

while getopts hnmlcp option
do
 case "${option}"
 in
  h) help ; exit 0;;
  n) IGNOREMPI="--ignore-glob="*mpi*"";;
  m) IGNOREMEDMPI="--ignore-glob="*medmpi*"";;
  l) COVREPORT="html"
     HTMLREPORT="--html=report.html --self-contained-html";;
  c) ISCOV=true;;
  p) RUNPYLINT=true;;
  "?") exit 1 ;;
 esac
done

if $ISCOV ; then
  export COVERAGE_PROCESS_START=$PWD/.coveragerc
  PYTESTCOV="--cov-report ${COVREPORT} --cov=c3po tests/"
fi

command_failed=()
cd ${current_script_dir}
export PYTHONPATH="${current_script_dir}:${PYTHONPATH}"
set +eu
pytest $IGNOREMPI $IGNOREMEDMPI $PYTESTCOV $HTMLREPORT
set -eu
if (( $? > 0 )); then
  echo "pytest failed!"
  command_failed+=("pytest")
fi


if $RUNPYLINT ; then
  cd ${current_script_dir}/sources
  set +eu
  pylint c3po
  set -eu
  if (( $? > 0 )); then
    echo "pylint failed!"
    command_failed+=("pylint")
  fi
fi

exit ${#command_failed[@]}
