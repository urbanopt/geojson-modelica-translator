#!/bin/bash

# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

DOCKER_USERNAME=nrel
IMG_NAME=gmt-om-runner

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

function create_mbl_mount()
# Only grab the modelica-buildings path of the MODELICAPATH env var.
{
  # Path variable
  local pat="$1"
  local mnt_cmd=""

  # Remove the first character of the pat variable if it is a colon
  if [[ ${pat:0:1} == ":" ]]; then
      pat="${pat:1}"
  else
      pat="$pat"
  fi

  # ModelicaPath will be a mounted read-only volume
  if [[ $(tr ':' '\n' <<< "${pat}" | wc -l) -eq 1 ]]; then
    # Check if the path variable has only one element
    mnt_cmd="${mnt_cmd} -v ${pat}:/mnt/lib/mbl:ro"
  else
    # Iterate over the elements of the path variable
    read -ra path_elements <<< "${pat}"
    for ele in "${path_elements[@]}"; do
      # Check if the element matches the specific string
      if [[ $ele == *"modelica-buildings"* || $ele == *"Buildings"* ]]; then
        mnt_cmd="${mnt_cmd} -v ${ele}:/mnt/lib/mbl:ro"
        break
      fi
    done
  fi

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

# Create the command to mount all directories in read-only mode
# a) Check for MODELICAPATH and then create the mount command
if [[ -z ${MODELICAPATH+x} ]]; then
  echo "MODELICAPATH is required to include the MBL and the envvar is not set"
  exit 1
fi
if [[ ${MODELICAPATH} == *" "* ]]; then
  echo "MODELICAPATH contains a space, which are not allowed. Please remove and try again."
  exit 1
fi
MOD_MOUNT=`create_mbl_mount ${MODELICAPATH}`
echo "Mounting MBL in read-only mode: ${MOD_MOUNT}"

# b) for PYTHONPATH
PYT_MOUNT=`create_mount_command ${PYTHONPATH}`

# Prepend /mnt/ in front of each entry, which will then be used as the MODELICAPATH
DOCKER_MODELICAPATH=`update_path_variable ${MODELICAPATH}`
DOCKER_PYTHONPATH=`update_path_variable ${PYTHONPATH}`

# If the current directory is part of the argument list,
# replace it with . as the container may have a different file structure
cur_dir=`pwd`
bas_nam=`basename ${cur_dir}`

# Set variable for shared directory
sha_dir=`dirname ${cur_dir}`
mbl_dir=`dirname ${MODELICAPATH}`

docker run \
  ${MOD_MOUNT} \
  ${PYT_MOUNT} \
  -e DISPLAY=${DISPLAY} \
  -e PYTHONPATH=${DOCKER_PYTHONPATH} \
  -v ${sha_dir}:/mnt/shared \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --rm \
  ${DOCKER_USERNAME}/${IMG_NAME} /bin/bash -c \
  "cd /mnt/shared/${bas_nam} && \
  python3 /mnt/lib/om.py '$1' '$2' '$3'"

exit $?
