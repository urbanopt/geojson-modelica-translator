# Modelica Runner

## Building and Pushing Docker Container

Building the container is only needed when the underlying Spawn executable or dependencies are updated. The license file is only needed to build the container, it will not be saved into the shared container. Each user will need to supply their own license file obtained from Modelon.

* Obtain a Modelon Optimica license
* Export a `MODELON_LICENSE_PATH` to the path of the license file. (e.g., `export MODELON_LICENSE_PATH=~/modelon` without the name of the file). Ideally add this to your environment configuration. For building and pushing, you can have this point to any file since no models are compiled in the building and pushing of the docker container.
    * Note that Optimica will look for a `license.lic` file in the `MODELON_LICENSE_PATH` directory.
* Export the license's assigned Mac address. This is requires since the system's mac address needs to match the mac address defined in the license. The mac address needs to be placed in a new environment variable named `MODELON_MAC_ADDRESS` and take the form of `AA:BB:CC:DD:EE:FF`, for example, `export MODELON_MAC_ADDRESS="12:34:56:78:9A:BC"`.

## Configuring GitHub Actions / CI

There are two secrets that are required for testing the models within GitHub Actions. The `MODELON_MAC_ADDRESS` and `MODELON_LICENSE_FILE` must be set. The `MODELON_MAC_ADDRESS` is simply the value of the mac address as shown above (e.g., 12:34:56:78:9A:BC, without the double quotes). However, the `MODELON_LICENSE_FILE` requires some escaping. Follow these steps:

* Do not copy the `#Please do not delete this comment line.`. This line is added by the CI system.
* Escape every double quote with a '\'.
* Copy from INCREMENT -> end of the SIGN block
* Paste that content into the `MODELON_LICENSE_FILE` GitHub secret.
* Make sure future PRs don't somehow expose these secrets to the logs.

The escaped `MODELON_LICENSE_FILE` that is copied into the secret should look something like below, also make sure that if you update the license file with a different mac address that the HOSTID in the license matches (without `:`'s though):

    ```bash
    INCREMENT OPTIMICA_BASE modelon 2023.0131 31-jan-2023 uncounted \
	    HOSTID=abcdef123456 ISSUER=\"Modelon AB\" ISSUED=29-apr-2022 \
	    NOTICE=\"Customer Some Customer \
	    OPTIMICA Compiler Toolkit Base\" \
	    SN=0000-0000-0000-0000-0000-0000-0000-0000 START=28-apr-2022 \
	    SIGN=\"0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
	    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
	    0000 0000 0000 0000 0000 0000 0000\"out
    ```

## Compiling Models

Compiling the models require the `MODELON_LICENSE_PATH` and `MODELON_MAC_ADDRESS` environments as described in the section above.

The compilation occurs through the Spawn Modelica Package.


## Running Models
