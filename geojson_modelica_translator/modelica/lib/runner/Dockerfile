FROM openmodelica/openmodelica:v1.25.1-minimal

# These libraries help compile and simulate separately.
# libgfortran4 is needed to load FMU for FMUZoneAdapterZones1.mo
RUN apt update && apt --no-install-recommends install -y \
    vim \
    gfortran \
    libpython3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install MSL 4.0
RUN echo \
  "updatePackageIndex(); getErrorString(); installPackage(Modelica, \"4.0.0\", exactMatch=false); getErrorString();" >> /tmp/installMSL.mos && \
  omc /tmp/installMSL.mos && \
  rm /tmp/installMSL.mos

# Install MBL 12.1
# ALERT: Update the version in utils.py when updating the version here
RUN echo \
  "updatePackageIndex(); getErrorString(); installPackage(Buildings, \"12.1.0\", exactMatch=false); getErrorString();" >> /tmp/installMBL.mos && \
  omc /tmp/installMBL.mos && \
  rm /tmp/installMBL.mos
