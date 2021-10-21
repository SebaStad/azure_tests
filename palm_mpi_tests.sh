#!/bin/bash
echo "Downloading palm"
printenv AZ_BATCH_HOST_LIST
echo "python variable"
echo $MPI_HOST_SETTINGS

echo "amount of cores"
nproc
echo "ifconfig stats"
ifconfig
echo "bold assumption of ip addresses"
nmap -sn 10.0.0.0/24

#wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/

#echo "Compiling palm"
#mkdir $HOME/palm && bash install -p $HOME/palm
#export PATH=$HOME/palm/bin:${PATH}

#echo "Copying basefile"
#cd $HOME/palm && mkdir -p $HOME/palm/JOBS/example_cbl/INPUT 
#cp $HOME/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d $HOME/palm/JOBS/example_cbl/INPUT/

#echo "Starting palm"
#palmrun -a "d3#" -X 4 -r example_cbl

#echo "Simulation results"
#filepath_results=$(ls $HOME/palm/JOBS/example_cbl/OUTPUT)
#echo $filepath_results
