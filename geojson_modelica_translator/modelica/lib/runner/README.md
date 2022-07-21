# Modelica Runner

## Building and Pushing Docker Container

Building the container is only needed when the underlying Spawn executable or dependencies are updated. The license file is only needed to build the container, it will not be saved into the shared container. Each user will need to supply their own license file obtained from Modelon.

* Obtain a Modelon Optimica license
* Export a `MODELON_LICENSE_PATH` to the path of the license file. (e.g., `export MODELON_LICENSE_PATH=~/modelon` without the name of the file). Ideally add this to your environment configuration. For building and pushing, you can have this point to any file since no models are compiled in the building and pushing of the docker container.
    * Note that Optimica will look for a `license.lic` file in the `MODELON_LICENSE_PATH` directory.
* Export the license's assigned Mac address. This is requires since the system's mac address needs to match the mac address defined in the license. The mac address needs to be placed in a new environment variable named `MODELON_MAC_ADDRESS` and take the form of `AA:BB:CC:DD:EE:FF`, for example, `export MODELON_MAC_ADDRESS="12:34:56:78:9A:BC"`.


## Compiling Models

Compiling the models require the `MODELON_LICENSE_PATH` and `MODELON_MAC_ADDRESS` environments as described in the section above.

The compilation occurs through the Spawn Modelica Package.


## Running Models
