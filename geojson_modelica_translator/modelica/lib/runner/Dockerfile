FROM openmodelica/openmodelica:v1.22.0-gui

# libgfortran4 is needed to load FMU for FMUZoneAdapterZones1.mo
RUN apt update && apt --no-install-recommends install -y \
    vim \
    gfortran \
    libpython3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install MSL 4.0.0
RUN echo \
  "updatePackageIndex(); getErrorString(); installPackage(Modelica, \"4.0.0\", exactMatch=false); getErrorString();" >> /tmp/installMSL.mos && \
  omc /tmp/installMSL.mos && \
  rm /tmp/installMSL.mos

# Download MBL into the container. Ideally we just point MODELICAPATH to the MBL on the host (required for GMT to build models).
# https://docs.docker.com/engine/reference/builder/#add
# https://docs.docker.com/develop/develop-images/instructions/#add-or-copy
ADD https://github.com/lbl-srg/modelica-buildings/releases/download/v9.1.0/Buildings-v9.1.0.zip ./Buildings-v9.1.0.tar.gz
RUN unzip ./Buildings-v9.1.0
ENV MODELICAPATH=./Buildings-v9.1.0
