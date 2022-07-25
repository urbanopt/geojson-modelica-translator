FROM ubuntu:20.04

# New version no worky with Bouncing Ball nor DES Models
# ENV SPAWN=Spawn-0.3.0-69040695f9-Linux
# ENV SPAWN_EXE=spawn-0.3.0-69040695f9

# Version below works with bouncing ball but not DES
ENV SPAWN=Spawn-0.3.0-8d93151657-Linux
ENV SPAWN_EXE=spawn-0.3.0-8d93151657

# Settings for building dependencies such as PyFMI
ENV BUILD_DIR $HOME/build
ENV ROOT_DIR /usr/local
ENV DEBIAN_FRONTEND noninteractive

# gfortran can be removed after Spawn is updated.
# The following package(s) are needed to run Spawn on 20.04: libtinfo5
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
        build-essential \
        libtinfo5 \
        # Below are dependencies for install PyFMI
        ca-certificates \
        curl \
        vim \
        wget \
        git \
        openjdk-8-jdk-headless \
        liblapack-dev \
        gfortran \
        libgfortran4 \
        cmake \
        libblas-dev \
        python3 \
        python3-pip && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    rm -rf /var/lib/apt/lists/*

# Install spawn from S3.
RUN wget https://spawn.s3.amazonaws.com/custom/$SPAWN.tar.gz \
    && tar -xzf $SPAWN.tar.gz \
    && ln -s /$SPAWN /spawn \
    && ln -s /spawn/bin/spawn /usr/local/bin/ \
    && ln -s /spawn/bin/$SPAWN_EXE /usr/local/bin/

# PyFMI installation instructions
WORKDIR $BUILD_DIR

# Use set in update-alternatives instead of config to
# provide non-interactive input.
RUN update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java \
    && update-alternatives --set javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac \
    && curl -SLO http://openstudio-resources.s3.amazonaws.com/bcvtb-linux.tar.gz \
    && tar -xzf bcvtb-linux.tar.gz \
    && rm bcvtb-linux.tar.gz

ENV FMIL_TAG 2.4
ENV FMIL_HOME $ROOT_DIR/fmil

ENV SUNDIALS_HOME $ROOT_DIR
ENV SUNDIALS_TAG v4.1.0

ENV ASSIMULO_TAG Assimulo-3.2.9

ENV PYFMI_TAG PyFMI-2.9.5

ENV SUPERLU_HOME $ROOT_DIR/SuperLU_MT_3.1

# Modelica requires libgfortran3 which is not in apt for 20.04
RUN wget http://archive.ubuntu.com/ubuntu/pool/universe/g/gcc-6/gcc-6-base_6.4.0-17ubuntu1_amd64.deb \
    && wget http://archive.ubuntu.com/ubuntu/pool/universe/g/gcc-6/libgfortran3_6.4.0-17ubuntu1_amd64.deb \
    && dpkg -i gcc-6-base_6.4.0-17ubuntu1_amd64.deb \
    && dpkg -i libgfortran3_6.4.0-17ubuntu1_amd64.deb \
    && ln -s /usr/lib/x86_64-linux-gnu/libffi.so.7 /usr/lib/x86_64-linux-gnu/libffi.so.6 \
    && rm *.deb

# Build FMI Library (for PyFMI)
RUN git clone --branch $FMIL_TAG --depth 1 https://github.com/modelon-community/fmi-library.git \
    && mkdir $FMIL_HOME \
    && mkdir fmil_build \
    && cd fmil_build \
    && cmake -DFMILIB_INSTALL_PREFIX=$FMIL_HOME ../fmi-library \
    && make install \
    && cd .. && rm -rf fmi-library fmil_build

# Build SuperLU (groan)
COPY make.inc $BUILD_DIR

RUN cd $ROOT_DIR \
    && curl -SLO http://crd-legacy.lbl.gov/~xiaoye/SuperLU/superlu_mt_3.1.tar.gz \
    && tar -xzf superlu_mt_3.1.tar.gz \
    && cd SuperLU_MT_3.1 \
    && rm make.inc \
    && cp $BUILD_DIR/make.inc make.inc \
    && make lib

ENV LD_LIBRARY_PATH $ROOT_DIR/lib:$SUPERLU_HOME/lib:$LD_LIBRARY_PATH

# Build Sundials with SuperLU(for Assimulo)
RUN git clone --branch $SUNDIALS_TAG --depth 1 https://github.com/LLNL/sundials.git \
    && mkdir sundials_build \
    && cd sundials_build \
    && cmake ../sundials \
    -DPTHREAD_ENABLE=1 \
    -DBLAS_ENABLE=1 \
    -DLAPACK_LIBRARIES='-llapack -lblas' \
    -DLAPACK_ENABLE=1 \
    -DSUPERLUMT_ENABLE=1 \
    -DSUNDIALS_INDEX_SIZE=32 \
    -DSUPERLUMT_INCLUDE_DIR=$SUPERLU_HOME/SRC \
    -DSUPERLUMT_LIBRARY_DIR=$SUPERLU_HOME/lib \
    -DSUPERLUMT_LIBRARIES='-lblas' \
    && make \
    && make install \
    && cd .. && rm -rf sundials sundials_build

# This is required for Assimulo to build correctly with setuptools 60+
ENV SETUPTOOLS_USE_DISTUTILS stdlib

# Install Numpy to allow for installation of Assimulo
RUN pip install numpy==1.21.6 Cython==0.29.28 scipy==1.7.3

RUN git clone --branch $ASSIMULO_TAG --depth 1 https://github.com/modelon-community/Assimulo.git \
     && cd Assimulo \
     && python setup.py install \
     --sundials-home=$SUNDIALS_HOME \
     --blas-home=/usr/lib/x86_64-linux-gnu \
     --lapack-home=/usr/lib/x86_64-linux-gnu/lapack/ \
     --superlu-home=$SUPERLU_HOME \
     && cd .. && rm -rf Assimulo

# Install PyFMI
RUN git clone --branch $PYFMI_TAG --depth 1 https://github.com/modelon-community/PyFMI.git \
    && cd PyFMI \
    && python setup.py install \
    && cd .. && rm -rf PyFMI

# Copy the Python helper files, CLI and FMU runner
COPY ./spawn.py /mnt/lib/spawn.py
COPY ./fmu_runner.py /mnt/lib/fmu_runner.py

WORKDIR /mnt
