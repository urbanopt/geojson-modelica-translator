# Modelica Runner

## Building and Pushing Docker Container

The OpenModelica docker container provides compilation and simulation capabilities without needing to install OpenModelica on a client computer. The container
includes Modelica Standards Library and a version of the Modelica Buildings Library. The table below shows the versions of the dependencies.

The GMT requires a locally built image or a version from Docker hub to run tests. The public use image is hosted on [Docker hub](https://hub.docker.com/r/nrel/gmt-om-runner).
CI builds this image once with `buildx` only when this `Dockerfile` changes (or when the published `nrel/gmt-om-runner` image is unavailable), shares the built image with the Linux and Windows/WSL2 Docker test jobs, and otherwise reuses the published image. That keeps runs fast because the image is never built when it has not changed, and never built twice.

To build the docker container locally, follow the below instructions:

1. If on the NLR network:
    - Disable Netskope temporarily
    - Disconnect from VPN
2. Then run the following from the GMT repository root:

```bash
docker build -t gmt-om-runner:local -f geojson_modelica_translator/modelica/lib/runner/Dockerfile .

# Optional: point GMT and pytest at the local image instead of Docker Hub
export GMT_OM_RUNNER_IMAGE=gmt-om-runner:local
```

The default tag is `nrel/gmt-om-runner:4.1.1`, which is the default version used in `modelica_runner.py`.
If `GMT_OM_RUNNER_IMAGE` is set, the runner uses that image instead.

If you run the image directly with a bind mount, note that the image runs as `root` so it can access the pre-installed Modelica libraries under `/root/.openmodelica`.

The GMT `ModelicaRunner` passes `HOST_UID`/`HOST_GID` into the container and `chown`s the mounted `/mnt/shared/<model_name>` directory at the end of the run so generated files are accessible on the host.

The image starts from the OpenModelica base image and installs the Modelica Standard Library and the Modelica Buildings Library with OpenModelica's package manager (`installPackage`) at build time, so `docker build` pulls those libraries from `libraries.openmodelica.org`.

### Versioning

In GMT Runner Version 2.0.0 we detached the OM version from the GMT Runner version.

| GTM Runner Version | OM Version | MSL Version | MBL Version |
| ------------------ | ---------- | ----------- | ----------- |
| 4.1.1              | 1.27.0     | 4.1.0       | 12.1.1      |
| 4.1.0              | 1.25.1     | 4.0.0       | 12.1.0      |
| 4.0.0              | 1.25.1     | 4.0.0       | 12.1.0      |
| 3.0.0              | 1.24.0     | 4.0.0       | 11.0.0      |
| 2.0.1              | 1.22.1     | 4.0.0       | 10.0.0      |
| 2.0.0              | 1.22.1     | 4.0.0       | 10.0.0      |
| 1.22.1             | 1.22.1     | 4.0.0       | 9.1.1       |
| 1.22.0             | 1.21.0     | 4.0.0       | 9.1.0       |
| 1.20.0             | 1.20.0     | 4.0.0       | 9.1.0       |

### Releasing a new container for users

Releasing is done through the **`Publish GMT runner image`** GitHub Actions workflow
(`.github/workflows/runner-image-release.yml`). It builds the multi-arch
(`linux/amd64` + `linux/arm64`) image from this `Dockerfile` and pushes it to
[Docker Hub](https://hub.docker.com/r/nrel/gmt-om-runner). To run it:

1. Make sure the runner changes are on the branch you want to release from (the
   workflow builds the current `Dockerfile` from the branch you pick when you run it).
2. In the repository on GitHub, open the **Actions** tab, select **Publish GMT
   runner image** from the left sidebar, and click the **Run workflow** button.
3. Choose the branch to build from, then fill in the inputs:
   - **`runner_tag`** – the tag to publish, e.g. `4.1.1`. Bump the **major**
     version for a new MBL (Buildings) version and the **minor** version for an
     OpenModelica update.
   - **`publish_latest`** – also tag the image as `latest` (default `false`). Set
     this to `true` when this release should become the new default `latest`.
   - **`force_push`** – overwrite the tag if it already exists on Docker Hub
     (default `false`). Leave it `false` for a normal release: the workflow skips
     the push when the tag already exists, so an unchanged version is never re-pushed.
4. Click **Run workflow** to start it.

The workflow needs the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository
secrets, set to Docker Hub credentials that can push `nrel/gmt-om-runner`. It logs
in, checks whether `runner_tag` already exists, and then either skips it (existing
tag with `force_push=false`) or builds and pushes the multi-arch image.

After the workflow succeeds, sign into
[Docker Hub](https://hub.docker.com/repository/docker/nrel/gmt-om-runner/general)
and update the version table in the Repository Overview section.

#### Publishing manually (fallback)

If you need to publish outside of CI, you can build and push the multi-arch image
yourself. This handles multiple platforms (arm64 as well as amd64); see
[docker's multi-platform images documentation](https://docs.docker.com/build/building/multi-platform/)
on how to configure buildx.

```bash
docker login

# Set up a buildx builder that can produce multiple platforms
docker buildx create --use

# Bump the major version of the GMT Runner for an MBL version,
# and bump the minor version for OM minor version updates.
docker buildx build --platform linux/amd64,linux/arm64 -t nrel/gmt-om-runner:4.1.1 --push -f geojson_modelica_translator/modelica/lib/runner/Dockerfile .
```

Then update the Docker Hub version table as described above.
