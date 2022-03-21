#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
echo "Update sys"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y make cmake libfftw3-dev python3-pip python3-pyqt5 flex bison ncl-ncarg nmap libcurl4-openssl-dev

echo "Downloading palm"

if [ -f /etc/profile.d/modules.sh ]; then
        . /etc/profile.d/modules.sh
fi

export BASEDIR=/palmbase
mkdir $BASEDIR
cd $BASEDIR
sudo chmod -R 777 .
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz

wget -c http://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz
wget -c https://www.zlib.net/zlib-1.2.11.tar.gz
wget -c https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.gz
wget -c https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.7.4.tar.gz
wget -c https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.5.4.tar.gz

export BASEDIR=/palmbase
mkdir $BASEDIR
module load mpi/hpcx

sudo mkdir $BASEDIR/LIBRARIES
cd $BASEDIR
sudo chmod -R 777 .
export DIR=$BASEDIR/LIBRARIES

export LDFLAGS=-L$DIR/lib
export CPPFLAGS=-I$DIR/include

export CC=mpicc
export CXX=mpicxx
export FC=mpif90

cd $BASEDIR
sudo chmod -R 777 .
tar -xvzf zlib-1.2.11.tar.gz
sudo chmod -R 777 .
cd zlib-1.2.11/
./configure --prefix=$DIR
make
make install

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


cd $BASEDIR/palm_model_system-master
sudo chmod -R 777 .
bash install -p ../palm

echo "Copying basefile"
# cd $BASEDIR/palm && mkdir -p $BASEDIR/palm/JOBS/example_cbl/INPUT 
# cp $BASEDIR/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d $BASEDIR/palm/JOBS/example_cbl/INPUT/

cd ../palm && mkdir -p JOBS/example_cbl/INPUT 
cp ../palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d JOBS/example_cbl/INPUT/

cd $BASEDIR
sudo chmod -R 777 .