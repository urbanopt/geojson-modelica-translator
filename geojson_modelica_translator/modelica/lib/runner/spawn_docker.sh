#!/bin/sh

# https://www.shellscript.sh/trap.html
# Addresses https://github.com/urbanopt/geojson-modelica-translator/issues/384
trap cleanup 1 2 3 6

cleanup()
{
  echo "Caught Signal ... cleaning up."
  rm -rf /tmp/temp_*.$$
  echo "Done cleanup ... quitting."
  exit 1
}
