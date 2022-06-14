FROM ubuntu:20.04

ENV MODELON_LICENSE_PATH ~/Documents/projects/gmt/
ENV SPAWN=Spawn-0.3.0-8d93151657-Linux
ENV SPAWN_EXE=spawn-0.3.0-8d93151657

RUN wget https://spawn.s3.amazonaws.com/custom/$SPAWN.tar.gz \
    && tar -xzf $SPAWN.tar.gz \
    && ln -s /$SPAWN /spawn \
    && ln -s /spawn/bin/spawn /usr/local/bin/ \
    && ln -s /spawn/bin/$SPAWN_EXE /usr/local/bin/

COPY modelica-buildings /sim/modelica-buildings

# copy the examples into the container, these are also used in the tests
# COPY examples /sim/examples

# If using Optimica, then copy license file here. The license must match
# the mac address that is configured when launching this container
RUN mkdir /home/simulator
COPY README.md license.l* /home/simulator/

WORKDIR /sim
