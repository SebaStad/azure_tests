#!/bin/bash

# Set directories
################################
# Hier Pfad anpassen
export DIR=/opt/PALM/LIBRARIES
################################

# Enter Libraries path
cd $DIR

# Download libraries
wget -c http://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz
wget -c https://www.zlib.net/zlib-1.2.11.tar.gz
wget -c https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.gz
wget -c https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.7.4.tar.gz
wget -c https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.5.4.tar.gz

################################
# MPI-Block
# START
# Auskommentieren, falls MPI bereits installiert ist!
# Ansonsten wird hier mpich mit GNU-Kompilern kompiliert
export CC=gcc
export CXX=g++
export FC=gfortran
export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include

# MPICH
tar -xvzf mpich-3.3.2.tar.gz
cd mpich-3.3.2/
./configure --prefix=$DIR
make
make install
# MPI-Block
# END
################################

export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include

export CC=mpicc
export CXX=mpicxx
export FC=mpif90

# ZLIP
cd $BASEDIR
sudo chmod -R 777 .
tar -xvzf zlib-1.2.11.tar.gz
sudo chmod -R 777 .
cd zlib-1.2.11/
./configure --prefix=$DIR
make
make install

################################
# HDF
# Die 40 zeigt hier die Anzahl der Processoren an,
# die fürs Kompilieren genutzt werden
# evtl anpassen
################################
cd $BASEDIR
sudo chmod -R 777 .
tar -xvzf hdf5-1.12.0.tar.gz
sudo chmod -R 777 .
cd hdf5-1.12.0
export FLAGS=-fPIC
./configure --prefix=$DIR --with-zlib=$DIR --enable-fortran --enable-parallel --enable-shared
make -j 40 && make -j 40 -i check
make -j 40 install


export HDF5=$DIR
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH


# netcdf-c
cd $BASEDIR
sudo chmod -R 777 .
tar -xvzf v4.7.4.tar.gz
sudo chmod -R 777 .
cd netcdf-c-4.7.4/

export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include
./configure --prefix=$DIR --enable-parallel-tests --enable-shared
make check
make install

export PATH=$DIR/bin:$PATH
export NETCDF=$DIR

################################
# netcdf-f
# Falls es hier Probleme gibt, bitte melden
# Bei uns lokal läuft netcdf-fortran-4.5.2
# Da gabs auf AZURE aber ein Problem,
# daher version 4.5.4
################################
cd $BASEDIR
sudo chmod -R 777 .
tar -xvzf v4.5.4.tar.gz
sudo chmod -R 777 .
cd netcdf-fortran-4.5.4/
# export LIBS="-lnetcdf -lhdf5_hl -lhdf5 -lz"
export LDFLAGS="-L$DIR/lib -fPIC"
export CPPFLAGS=-I$DIR/include
./configure --prefix=$DIR --enable-parallel-tests --enable-shared
make -i check
make install
