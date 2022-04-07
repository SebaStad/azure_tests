#!/bin/bash
echo "Update sys"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y make cmake libfftw3-dev python3-pip python3-pyqt5 flex bison ncl-ncarg nmap libcurl4-openssl-dev

if [ -f /etc/profile.d/modules.sh ]; then
        . /etc/profile.d/modules.sh
fi

echo "Downloading palm"

export BASEDIR=/palmbase
mkdir $BASEDIR
cd $BASEDIR
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

wget -c http://www.mpich.org/static/downloads/3.3.2/mpich-3.3.2.tar.gz
wget -c https://www.zlib.net/zlib-1.2.11.tar.gz
wget -c https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.gz
wget -c https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.7.4.tar.gz
wget -c https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.5.2.tar.gz

module load mpi/hpcx

echo "All good"