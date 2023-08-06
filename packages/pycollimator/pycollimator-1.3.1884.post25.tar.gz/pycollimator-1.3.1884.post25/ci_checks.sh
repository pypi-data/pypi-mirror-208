#!/bin/bash

set -e
cd `dirname $0`
source "env.sh"

do_echo "Running CI checks for collimator package in ENV=${ENV}..."

source venv/bin/activate
do_exec black --check .
do_exec pylint -E pycollimator
do_exec flake8 pycollimator

do_echo "Running pytest..."
# FIXME: disabled compile_pip_requirements_test because there is some unknown discrepancy between
# local and CI.
do_exec bazel test -- //src/lib/pycollimator:all -//src/lib/pycollimator:compile_pip_requirements_test

do_echo "All good! You can now merge this PR."
