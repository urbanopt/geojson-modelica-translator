ARG SEED_GMT_OM_RUNNER_IMAGE=nrel/gmt-om-runner:4.0.0
ARG OPENMODELICA_IMAGE=openmodelica/openmodelica:v1.27.0-minimal

FROM ${SEED_GMT_OM_RUNNER_IMAGE} AS seed-libraries

FROM ${OPENMODELICA_IMAGE}

# These libraries help compile and simulate separately.
# libgfortran4 is needed to load FMU for FMUZoneAdapterZones1.mo
RUN apt update && apt --no-install-recommends install -y \
    vim \
    gfortran \
    libpython3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Seed the OpenModelica-maintained Modelica, ModelicaServices, Complex, and
# Buildings libraries from the last released GMT runner so local and CI builds
# do not depend on libraries.openmodelica.org being reachable at build time.
COPY --from=seed-libraries /root/.openmodelica/libraries /root/.openmodelica/libraries
