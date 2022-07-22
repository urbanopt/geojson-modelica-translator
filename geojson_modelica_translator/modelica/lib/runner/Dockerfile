FROM ubuntu:18.04

# New version no worky with Bouncing Ball nor DES Models
# ENV SPAWN=Spawn-0.3.0-69040695f9-Linux
# ENV SPAWN_EXE=spawn-0.3.0-69040695f9

# Version below works with bouncing ball but not DES
ENV SPAWN=Spawn-0.3.0-8d93151657-Linux
ENV SPAWN_EXE=spawn-0.3.0-8d93151657

# Tried installing qemu to resolve spawn dependencies.
# gfortran can be removed after Spawn is updated.
RUN apt update && apt install -y \
        # libncurses5 \
        # clang-8 \
        # qemu-kvm \
        # bridge-utils \
        # libvirt-clients \
        # libvirt-daemon-system
        gfortran \
        vim \
        wget \
        build-essential && \
    apt install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    rm -rf /var/lib/apt/lists/*

# Install spawn from S3.
RUN wget https://spawn.s3.amazonaws.com/custom/$SPAWN.tar.gz \
    && tar -xzf $SPAWN.tar.gz \
    && ln -s /$SPAWN /spawn \
    && ln -s /spawn/bin/spawn /usr/local/bin/ \
    && ln -s /spawn/bin/$SPAWN_EXE /usr/local/bin/

COPY ./spawn.py /mnt/lib/spawn.py

WORKDIR /mnt
