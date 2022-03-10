#!/bin/bash
echo "Update sys"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y make cmake libfftw3-dev python3-pip python3-pyqt5 flex bison ncl-ncarg nmap libcurl4-openssl-dev

echo "Downloading palm"
mkdir /palmbase
cd /palmbase
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

wget -c http://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz
wget -c https://www.zlib.net/zlib-1.2.11.tar.gz
wget -c https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.gz
wget -c https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.7.4.tar.gz
wget -c https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.5.2.tar.gz

module load mpi/hpcx

sudo mkdir /palmbase/LIBRARIES
cd /palmbase
sudo chmod -R 777 .
export DIR=/palmbase/LIBRARIES

export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include

export CC=mpicc
export CXX=mpicxx
export FC=mpif90

cd /palmbase


tar -xvzf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure --prefix=$DIR
make
make install

cd /palmbase
tar -xvzf hdf5-1.12.0.tar.gz
cd hdf5-1.12.0
export FLAGS=-fPIC
./configure --prefix=$DIR --with-zlib=$DIR --enable-fortran --enable-parallel --enable-shared
make -j 40 && make -j 40 -i check
make -j 40 install


export HDF5=$DIR
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH


cd /palmbase
tar -xf netcdf-c-4.7.4.tar.gz
cd netcdf-c-4.7.4/

tar -xvzf v4.7.4.tar.gz
cd netcdf-c-4.7.4/

export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include
./configure --prefix=$DIR --enable-parallel-tests --enable-shared
make check
make install

export PATH=$DIR/bin:$PATH
export NETCDF=$DIR


cd /palmbase
tar -xvzf v4.5.2.tar.gz
cd netcdf-fortran-4.5.2/
# export LIBS="-lnetcdf -lhdf5_hl -lhdf5 -lz"
export LDFLAGS="-L$DIR/lib -fPIC"
export CPPFLAGS=-I$DIR/include
./configure --prefix=$DIR --enable-parallel-tests --enable-shared
make -i check
make install


cd /palmbase/palm_model_system-master
bash install -p ../palm

echo "Copying basefile"
# cd /palmbase/palm && mkdir -p /palmbase/palm/JOBS/example_cbl/INPUT 
# cp /palmbase/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d /palmbase/palm/JOBS/example_cbl/INPUT/

cd ../palm && mkdir -p JOBS/example_cbl/INPUT 
cp ../palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d JOBS/example_cbl/INPUT/