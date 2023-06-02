# Modelica Runner

## Building and Pushing Docker Container

The OpenModelica docker container needs to be built locally or pushed to Docker hub for wide-spread use.

The public use image is hosted on Docker hub under https://hub.docker.com/r/nrel/gmt-om-runner.

To build the docker container locally and push, the instructions are as follows:

```bash
cd geojson_modelica_translator/modelica/lib/runner

# have you computer setup for linux/amd64 and linux/arm64
docker build -t nrel/gmt-om-runner:latest .
```

The default tag will be `nrel/gmt-om-runner:latest`, which is the default version used in the om_docker.sh file.

### Releasing a new container for users

Build the container as described in the above section, then tag and push to the remote location. This
only is available to individuals with write access to the NREL org.

```bash
# Build for more platforms on release.
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t nrel/gmt-om-runner:latest --push .
```
