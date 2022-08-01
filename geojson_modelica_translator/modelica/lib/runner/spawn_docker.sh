#!/bin/bash

DOCKER_USERNAME=nrel
IMG_NAME=spawn_modelica_docker

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
# Split path somehow. Replace double-slashes with single-slashes, to ensure compatibility with
# Windows paths.
{
   local pat="$1"
   # Each entry in pat will be a mounted read-only volume
   local mnt_cmd=""
   for ele in ${pat//:/ }; do
      mnt_cmd="${mnt_cmd} -v ${ele}:/mnt${ele}:ro"
   done

   # On Darwin, the exported temporary folder needs to be /private/var/folders, not /var/folders
   # see https://askubuntu.com/questions/600018/how-to-display-the-paths-in-path-separately
   if [ `uname` == "Darwin" ]; then
       mnt_cmd=`echo ${mnt_cmd} | sed -e 's| /var/folders/| /private/var/folders/|g'`
   fi
   echo "${mnt_cmd}"
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

# Create the mac address for the container, which is needed by the
# Optimica compiler
if [ -z ${MODELON_MAC_ADDRESS+x} ]; then
    # set the mac address to empty string, so that the docker will generate a new one
    MODELON_MAC_ADDRESS=""
else
    # Prepend the docker command line option to the MAC address from the env var
    MODELON_MAC_ADDRESS="--mac-address=${MODELON_MAC_ADDRESS}"
fi

# Create the command to mount all directories in read-only mode
# a) for MODELICAPATH
MOD_MOUNT=`create_mount_command ${MODELICAPATH}`
# b) for PYTHONPATH
PYT_MOUNT=`create_mount_command ${PYTHONPATH}`
# c) for MODELON_LICENSE_PATH
LIC_MOUNT=`create_mount_command ${MODELON_LICENSE_PATH}`

# Prepend /mnt/ in front of each entry, which will then be used as the MODELICAPATH
DOCKER_MODELICAPATH=`update_path_variable ${MODELICAPATH}`
DOCKER_PYTHONPATH=`update_path_variable ${PYTHONPATH}`
DOCKER_MODELON_LICENSE_PATH=`update_path_variable ${MODELON_LICENSE_PATH}`

# If the current directory is part of the argument list,
# replace it with . as the container may have a different file structure
cur_dir=`pwd`
bas_nam=`basename ${cur_dir}`

# Set variable for shared directory
sha_dir=`dirname ${cur_dir}`

docker run \
  ${MOD_MOUNT} \
  ${PYT_MOUNT} \
  ${LIC_MOUNT} \
  ${MODELON_MAC_ADDRESS} \
  -e DISPLAY=${DISPLAY} \
  -e MODELICAPATH=${DOCKER_MODELICAPATH} \
  -e PYTHONPATH=${DOCKER_PYTHONPATH} \
  -e MODELON_LICENSE_PATH=${DOCKER_MODELON_LICENSE_PATH} \
  -v ${sha_dir}:/mnt/shared \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --rm \
  ${DOCKER_USERNAME}/${IMG_NAME} /bin/bash -c \
  "cd /mnt/shared/${bas_nam} && \
  python /mnt/lib/spawn.py '$1' '$2' '$3' '$4'"
exit $?
