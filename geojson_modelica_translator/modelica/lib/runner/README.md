# Modelica Runner

## Building and Pushing Docker Container

The OpenModelica docker container provides compilation and simulation capabilities without needing to install OpenModelica on a client computer. The container
includes Modelica Standards Library and a version of the Modelica Buildings Library. The table below shows the versions of the dependencies.

The GMT requires a locally built image or a version from Docker hub to run tests. The public use image is hosted on [Docker hub](https://hub.docker.com/r/nrel/gmt-om-runner).
CI now builds the runner image from this Dockerfile and runs the Docker-based test suite against that freshly built image.

To build the docker container locally, follow the below instructions:

1. If on the NREL network:
    - Disable Netskope temporarily
    - Disconnect from VPN
2. Then run the following from the GMT repository root:

```bash
# <from gmt root directory>
docker build -t gmt-om-runner:local -f geojson_modelica_translator/modelica/lib/runner/Dockerfile .

# Optional: point GMT and pytest at the local image instead of Docker Hub
export GMT_OM_RUNNER_IMAGE=gmt-om-runner:local
```

The default tag is `nrel/gmt-om-runner:4.1.0`, which is the default version used in `modelica_runner.py`.
If `GMT_OM_RUNNER_IMAGE` is set, the runner uses that image instead.

If you run the image directly with a bind mount, note that the image runs as `root` so it can access the pre-installed Modelica libraries under `/root/.openmodelica`.

The GMT `ModelicaRunner` passes `HOST_UID`/`HOST_GID` into the container and `chown`s the mounted `/mnt/shared/<model_name>` directory at the end of the run so generated files are accessible on the host.

The image now starts from the latest OpenModelica base image and copies the known-good OpenModelica-maintained Modelica, ModelicaServices, Complex, and Buildings libraries from the previous GMT runner release. That keeps local and CI builds deterministic even when `libraries.openmodelica.org` is unavailable during `docker build`.

### Versioning

In GMT Runner Version 2.0.0 we detached the OM version from the GMT Runner version.

| GTM Runner Version | OM Version | MSL Version | MBL Version |
| ------------------ | ---------- | ----------- | ----------- |
| 4.1.0              | 1.27.0     | 4.1.0       | 12.1.0      |
| 4.0.0              | 1.25.1     | 4.0.0       | 12.1.0      |
| 3.0.0              | 1.24.0     | 4.0.0       | 11.0.0      |
| 2.0.1              | 1.22.1     | 4.0.0       | 10.0.0      |
| 2.0.0              | 1.22.1     | 4.0.0       | 10.0.0      |
| 1.22.1             | 1.22.1     | 4.0.0       | 9.1.1       |
| 1.22.0             | 1.21.0     | 4.0.0       | 9.1.0       |
| 1.20.0             | 1.20.0     | 4.0.0       | 9.1.0       |

### Releasing a new container for users

Releasing is available through the GitHub Actions workflow `Publish GMT runner image`, which accepts the image tag to push to Docker Hub. The workflow still requires Docker Hub credentials with permission to push `nrel/gmt-om-runner`.

Building for release is a bit different than development since you will need to handle multiple platforms (that is adding support for armhf to
support OpenModelica as well as AMD64). See
[docker's multi-platform images documentation](https://docs.docker.com/build/building/multi-platform/) on how to configure.

```bash
docker login

# Build for more platforms on release due to newer macos, etc., etc.
docker buildx create --use

# update version of OMC and determine if the latest should be updated. Bump the major version of the GMT Runner for an MBL version,
# and bump the minor version for OM minor version updates.
docker buildx build --platform linux/amd64,linux/arm64 -t nrel/gmt-om-runner:4.1.0 --push -f geojson_modelica_translator/modelica/lib/runner/Dockerfile .
```

Sign into [Docker Hub](https://hub.docker.com/repository/docker/nrel/gmt-om-runner/general) and update the version
table in the Repository Overview section
