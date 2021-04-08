import os
import pathlib
import subprocess
import sys


# Function declarations
def create_mount_command(pat):
    # Each entry in pat will be a mounted read-only volume
    mnt_cmd = []
    for ele in pat.split(':'):
        if not ele:
            continue

        # On Darwin, the exported temporary folder needs to be /private/var/folders, not /var/folders
        # see https://askubuntu.com/questions/600018/how-to-display-the-paths-in-path-separately
        if sys.version == 'Darwin':
            ele = ele.replace('/var/folders/', '/private/var/folders/')
        mnt_cmd += [f'--volume={ele}:/mnt{ele}:ro']

    return mnt_cmd


def update_path_variable(pat):
    # Prepend /mnt/ in front of each entry of a PATH variable in which the arguments are
    # separated by a colon ":"
    # This allows for example to create the new MODELICAPATH
    new_pat = []
    for ele in pat.split(':'):
        if not ele:
            continue

        new_pat.append(f'/mnt{ele}')

    return ':'.join(new_pat)


def main():
    IMG_NAME = 'ubuntu-1804_jmodelica_trunk'
    DOCKER_USERNAME = 'michaelwetter'
    MODELICAPATH = os.environ.get('MODELICAPATH', '')
    PYTHONPATH = os.environ.get('PYTHONPATH', '')

    # Export the MODELICAPATH
    if not MODELICAPATH:
        MODELICAPATH = os.getcwd()
    else:
        # Add the current directory to the front of the Modelica path.
        # This will export the directory to the docker, and also set
        # it in the MODELICAPATH so that JModelica finds it.
        MODELICAPATH = f'{os.getcwd()}:{MODELICAPATH}'

    # Create the command to mount all directories in read-only mode
    # a) for MODELICAPATH
    MOD_MOUNT = create_mount_command(MODELICAPATH)
    # b) for PYTHONPATH
    PYT_MOUNT = create_mount_command(PYTHONPATH)

    # Prepend /mnt/ in front of each entry, which will then be used as the MODELICAPATH
    DOCKER_MODELICAPATH = update_path_variable(MODELICAPATH)
    DOCKER_PYTHONPATH = update_path_variable(PYTHONPATH)

    # If the current directory is part of the argument list,
    # replace it with . as the docker may have a different file structure
    cur_dir = pathlib.Path.cwd()
    bas_nam = cur_dir.name
    arg_lis = ' '.join([arg.replace(str(cur_dir), '.') for arg in sys.argv[1:]])

    # Set variable for shared directory
    sha_dir = cur_dir.parent

    container_cmd = f'''export MODELICAPATH={DOCKER_MODELICAPATH}:/usr/local/JModelica/ThirdParty/MSL && \
    export PYTHONPATH={DOCKER_PYTHONPATH} && \
    cd /mnt/shared/{bas_nam} && \
    /usr/local/JModelica/bin/jm_ipython.sh {arg_lis}'''

    docker_run_cmd = [
        'docker', 'run',
        # f'--user={os.environ.get("UID", 0)}',
        '-i',
        '--detach=false',
        *MOD_MOUNT,
        *PYT_MOUNT,
        f'--volume={sha_dir}:/mnt/shared',
        '-e', f'DISPLAY={os.environ.get("DISPLAY", "")}',
        '--volume=/tmp/.X11-unix:/tmp/.X11-unix',
        '--rm',
        f'{DOCKER_USERNAME}/{IMG_NAME}',
        '/bin/bash', '-c', container_cmd
    ]

    res = subprocess.run(docker_run_cmd, capture_output=True)
    print(res.stderr.decode(), file=sys.stderr)
    print(res.stdout.decode())
    sys.exit(res.returncode)


if __name__ == '__main__':
    main()
