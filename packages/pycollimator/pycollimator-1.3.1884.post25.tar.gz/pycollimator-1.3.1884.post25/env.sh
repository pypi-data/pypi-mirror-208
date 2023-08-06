#!/bin/bash

function do_exec() {
  >&2 echo "$ $@"
  "$@"
}

function do_echo() {
  echo -e "\033[1;32m$@\033[0m"
}

function die() {
  echo -e "\033[1;31m$@\033[0m"
  exit 1
}

NCPU=${NCPU:-`sysctl -n hw.ncpu || getconf _NPROCESSORS_ONLN || echo 1`}
ENV=${ENV:-dev}
