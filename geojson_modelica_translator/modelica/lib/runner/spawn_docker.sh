#!/bin/bash

# Catch signals to kill the container if it is interrupted
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

# Function declarations
function create_mount_command()
'''
Split path somehow. Replace double-slashes with single-slashes, to ensure compatibility with Windows paths.
'''
{
   local pat="$1"
   # Each entry in pat will be a mounted read-only volume
   local mnt_cmd=""
   for ele in ${pat//:/ }; do
      mnt_cmd="${mnt_cmd} -v ${ele}:/mnt${ele}:ro"
   done
}

function update_path_variable()
{
  # Prepend /mnt/ in front of each entry of a PATH variable in which the arguments are
  # separated by a colon ":"
  # This allows for example to create the new MODELICAPATH
  local pat="$1"
  local new_pat=`(set -f; IFS=:; printf "/mnt%s:" ${pat})`
  # Cut the trailing ':'
  new_pat=${new_pat%?}
  echo "${new_pat}"
}

# Export the MODELICAPATH
if [ -z ${MODELICAPATH+x} ]; then
    MODELICAPATH=`pwd`
else
    # Add the current directory to the front of the Modelica path.
    # This will export the directory to the docker, and also set
    # it in the MODELICAPATH so that JModelica finds it.
    MODELICAPATH=`pwd`:${MODELICAPATH}
fi

# Create the command to mount all directories in read-only mode
# a) for MODELICAPATH
MOD_MOUNT=`create_mount_command ${MODELICAPATH}`
# b) for PYTHONPATH
PYT_MOUNT=`create_mount_command ${PYTHONPATH}`

# Prepend /mnt/ in front of each entry, which will then be used as the MODELICAPATH
DOCKER_MODELICAPATH=`update_path_variable ${MODELICAPATH}`
DOCKER_PYTHONPATH=`update_path_variable ${PYTHONPATH}`

# If the current directory is part of the argument list,
# replace it with . as the docker may have a different file structure
cur_dir=`pwd`
bas_nam=`basename ${cur_dir}`
arg_lis=`echo $@ | sed -e "s|${cur_dir}|.|g"`

# Set variable for shared directory
sha_dir=`dirname ${cur_dir}`
