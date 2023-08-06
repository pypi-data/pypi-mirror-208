#!/bin/bash

set -e
cd `dirname $0`
source "env.sh"

VENVDIR="venv"
PYTHON="python3.8"

do_echo "Preparing environment for $PYTHON..."

if [ ! -d $VENVDIR ] ; then
  do_exec $PYTHON -m venv $VENVDIR
  source venv/bin/activate
  do_exec $PYTHON -m ensurepip
fi

source venv/bin/activate
do_exec $PYTHON -m pip install -U pip wheel black pylint flake8
do_exec $PYTHON -m pip install -e .

do_echo "Done. Now you can enter venv with:\n"
do_echo "  source $VENVDIR/bin/activate\n"
