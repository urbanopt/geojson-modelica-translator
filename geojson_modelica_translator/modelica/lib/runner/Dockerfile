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

WORKDIR /sim
