# Modelica Runner

## Building and Pushing Docker Container

The OpenModelica docker container provides compilation and simulation capabilities without needing to install OpenModelica on a client computer. The container
includes Modelica Standards Library and a version of the Modelica Buildings Library. The table below shows the versions of the dependencies.

The GMT requires a locally built image or a version from Docker hub to run tests. The public use image is hosted on [Docker hub](https://hub.docker.com/r/nrel/gmt-om-runner).

To build the docker container locally, follow the below instructions:

1. If on the NREL network:
    - Disable Netskope temporarily
    - Disconnect from VPN
2. Then:

```bash
# <from gmt root directory>
cd geojson_modelica_translator/modelica/lib/runner

docker build -t nrel/gmt-om-runner:<tag> .
```

The default tag will be `nrel/gmt-om-runner:3.0.0`, which is the default version used in the modelica_runner.py file.

### Versioning

In GMT Runner Version 2.0.0 we detached the OM version from the GMT Runner version.

| GTM Runner Version | OM Version | MSL Version | MBL Version |
| ------------------ | ---------- | ----------- | ----------- |
| 3.0.0              | 1.24.0     | 4.0.0       | 11.0.0      |
| 2.0.1              | 1.22.1     | 4.0.0       | 10.0.0      |
| 2.0.0              | 1.22.1     | 4.0.0       | 10.0.0      |
| 1.22.1             | 1.22.1     | 4.0.0       | 9.1.1       |
| 1.22.0             | 1.21.0     | 4.0.0       | 9.1.0       |
| 1.20.0             | 1.20.0     | 4.0.0       | 9.1.0       |

### Releasing a new container for users

Releasing is only available to individuals with write access to the NREL org. Unfortunately, the NREL org is still
under a free plan resulting in a maximum of 3 users for the entire org, which have already been allocated.

Building for release is a bit different than development since you will need to handle multiple platforms (that is adding support for armhf to
support OpenModelica as well as AMD64). See
[docker's multi-platform images documentation](https://docs.docker.com/build/building/multi-platform/) on how to configure.

```bash
docker login

# Build for more platforms on release due to newer macos, etc., etc.
docker buildx create --use

# update version of OMC and determine if the latest should be updated. Bump the major version of the GMT Runner for an MBL version,
# and bump the minor version for OM minor version updates.
docker buildx build --platform linux/amd64,linux/arm64 -t nrel/gmt-om-runner:3.0.0 --push .
```

Sign into [Docker Hub](https://hub.docker.com/repository/docker/nrel/gmt-om-runner/general) and update the version
table in the Repository Overview section
