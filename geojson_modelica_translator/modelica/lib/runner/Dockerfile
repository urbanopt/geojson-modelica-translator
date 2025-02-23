FROM ubuntu:focal

# These libraries help compile and simulate separately.
# libgfortran4 is needed to load FMU for FMUZoneAdapterZones1.mo
RUN apt update && apt --no-install-recommends install -y \
    vim \
    gfortran \
    libpython3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Duplicating code from OM Dockerfile: https://github.com/OpenModelica/OpenModelicaDockerImages/blob/v1.23.1/Dockerfile
# This allows us to use a different Ubuntu version than the OM Dockerfile
# tests/GMT_Lib/test_gmt_lib_des.py fails with jammy, works with focal.
ARG OM_VERSION=1.24.0

RUN export DEBIAN_FRONTEND="noninteractive" && echo "OM VERSION: $OM_VERSION" && test ! -z "$OM_VERSION" && apt update && apt upgrade -qy && apt dist-upgrade -qy \
    && apt install -qy gnupg wget ca-certificates apt-transport-https \
    && echo "deb https://build.openmodelica.org/omc/builds/linux/releases/$OM_VERSION/ `cat /etc/lsb-release | grep CODENAME | cut -d= -f2` release" > /etc/apt/sources.list.d/openmodelica.list \
    && wget -q https://build.openmodelica.org/apt/openmodelica.asc \
    && apt-key add openmodelica.asc \
    && rm openmodelica.asc \
    && apt update && apt upgrade && apt dist-upgrade \
    && apt install --no-install-recommends -qy omc cmake \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Install MSL 4.0
RUN echo \
  "updatePackageIndex(); getErrorString(); installPackage(Modelica, \"4.0.0\", exactMatch=false); getErrorString();" >> /tmp/installMSL.mos && \
  omc /tmp/installMSL.mos && \
  rm /tmp/installMSL.mos

# Install MBL 11.0
# ALERT: Update the version in utils.py when updating the version here
RUN echo \
  "updatePackageIndex(); getErrorString(); installPackage(Buildings, \"11.0.0\", exactMatch=false); getErrorString();" >> /tmp/installMBL.mos && \
  omc /tmp/installMBL.mos && \
  rm /tmp/installMBL.mos
