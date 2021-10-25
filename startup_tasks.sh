#!/bin/bash
echo "Update sys"
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y gfortran g++ make cmake libopenmpi-dev openmpi-bin libnetcdff-dev netcdf-bin libfftw3-dev python3-pip python3-pyqt5 flex bison ncl-ncarg nmap
echo "Downloading palm"
mkdir /palmbase
cd /palmbase
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

echo "Compiling palm"
mkdir /palmbase/palm && bash install -p /palmbase/palm
export PATH=/palmbase/palm/bin:${PATH}

echo "Copying basefile"
cd /palmbase/palm && mkdir -p /palmbase/palm/JOBS/example_cbl/INPUT 
cp /palmbase/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d /palmbase/palm/JOBS/example_cbl/INPUT/
