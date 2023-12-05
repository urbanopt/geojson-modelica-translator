# Modelica Runner

## Building and Pushing Docker Container

The OpenModelica docker container needs to be built locally or pushed to Docker hub for wide-spread use.

The public use image is hosted on Docker hub under https://hub.docker.com/r/nrel/gmt-om-runner.

To build the docker container locally, follow the below instructions:

```bash
cd geojson_modelica_translator/modelica/lib/runner

docker build -t nrel/gmt-om-runner:latest .
```

The default tag will be `nrel/gmt-om-runner:latest`, which is the default version used in the om_docker.sh file.

### Releasing a new container for users

Releasing is only available to individuals with write access to the NREL org. Unfortunately, the NREL org is still
under a free plan resulting in a maximum of 3 users for the entire org, which have already been allocated.

Building for release is a bit different than development since you will need to handle multiple platforms. See
[docker's multi-platform images documentation](https://docs.docker.com/build/building/multi-platform/) on how to configure.

```bash
docker login

# Build for more platforms on release due to newer macos, etc., etc.
docker buildx create --use

# update version of OMC and determine if the latest should be updated. Ideally, the latest should be updated
# only if the new OMC release is needed to fix previous issues.
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nrel/gmt-om-runner:v1.22.0 --push .
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nrel/gmt-om-runner:latest --push .

```
