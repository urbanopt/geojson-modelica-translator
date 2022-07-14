# Modelica Runner

## Building and Pushing Docker Container

Building the container is only needed when the underlying Spawn executable or dependencies are updated. The license file is only needed to build the container, it will not be saved into the shared container. Each user will need to supply their own license file obtained from Modelon.

* Obtain a Modelon Optimica license
* Export a `MODELON_LICENSE_PATH` to the path of the license file. (e.g., `export MODELON_LICENSE_PATH=~/modelon` without the name of the file). Ideally add this to your environment configuration. For building and pushing, you can have this point to any file since no models are compiled in the building and pushing of the docker container.
    * Note that Optimica will look for a `license.lic` file in the `MODELON_LICENSE_PATH` directory.


## Running Simulations

#FIXME -- this doesn't make sense below
If running with the GMT and the user specifies the `MODELON_LICENSE_PATH` and `MODELON_MAC`, then nothing needs to happen to simulate with Optimica.

* Note the Mac Address of the license, as that will be required for the docker container to run properly.
