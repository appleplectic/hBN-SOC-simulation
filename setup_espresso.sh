# nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04 or similar

export QE_VERSION="7.4"

apt update -y && apt upgrade -y

apt install -y \
    build-essential \
    wget \
    git \
    python3 \
    python3-pip \
    gfortran \
    openmpi-bin \
    libopenmpi-dev \
    libfftw3-dev \
    libfftw3-mpi-dev \
    libscalapack-openmpi-dev \
    pkg-config \
    make \
    cmake

wget https://github.com/QEF/q-e/archive/qe-${QE_VERSION}.tar.gz \
    && tar -xzf qe-${QE_VERSION}.tar.gz \
    && rm qe-${QE_VERSION}.tar.gz

cd q-e-qe-${QE_VERSION}

# change cc version and CUDA depending on GPU
./configure \
    --enable-openmp \
    --enable-parallel \
    --with-scalapack=yes \
    --with-cuda=yes \
    --with-cuda-cc=90 \
    --with-cuda-runtime=12.8 \
    --with-cuda-mpi=yes \
    && make pw -j$(nproc) \
    && make cp -j$(nproc) \
    && make ph -j$(nproc) \
    && make pp -j$(nproc) \
    && make install