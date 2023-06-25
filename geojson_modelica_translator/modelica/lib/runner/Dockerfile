# Use the OpenModelica Docker image
# We only need this file for the copy command. The image can be/is loaded in the shell script instead of here.
FROM openmodelica/openmodelica:v1.20.0-gui

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

# Put the om.py CLI into the container
COPY ./om.py /mnt/lib/om.py
