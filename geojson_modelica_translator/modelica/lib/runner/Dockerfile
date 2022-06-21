FROM ubuntu:18.04

ENV SPAWN=Spawn-0.3.0-8d93151657-Linux
ENV SPAWN_EXE=spawn-0.3.0-8d93151657

# Tried installing qemu to resolve spawn dependencies.
RUN apt update && apt install -y \
        # libncurses5 \
        # clang-8 \
        vim \
        wget \
        build-essential
        # qemu-kvm \
        # bridge-utils \
        # libvirt-clients \
        # libvirt-daemon-system

RUN wget https://spawn.s3.amazonaws.com/custom/$SPAWN.tar.gz \
    && tar -xzf $SPAWN.tar.gz \
    && ln -s /$SPAWN /spawn \
    && ln -s /spawn/bin/spawn /usr/local/bin/ \
    && ln -s /spawn/bin/$SPAWN_EXE /usr/local/bin/

COPY ./spawn.py /mnt/lib/spawn.py

WORKDIR /mnt
