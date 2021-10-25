#!/bin/bash
echo "Downloading palm"
wget https://gitlab.palm-model.org/releases/palm_model_system/-/archive/master/palm_model_system-master.tar.gz && tar -xf palm_model_system-master.tar.gz && cd palm_model_system-master/
echo "NodeListAzure"
echo "$AZ_BATCH_NODE_LIST"

echo "amount of cores"
nproc
echo "nmap stuff"
export first_try=$(nmap -n -sn 10.0.0.0/24 -oG - | awk '/Up$/{print $2}'| paste -sd ,)
export second_try=$(echo "$first_try" | awk '{ gsub(",", ":1,") ; system( "echo "  $0) }')
export second_try+=$":1"

export command_option=$(echo "-host ")
export command_option+="$second_try"
echo "$command_option"

echo "Compiling palm"
mkdir $HOME/palm && bash install -p $HOME/palm
export PATH=$HOME/palm/bin:${PATH}

echo "Copying basefile"
cd $HOME/palm && mkdir -p $HOME/palm/JOBS/example_cbl/INPUT 
cp $HOME/palm_model_system-master/packages/palm/model/tests/cases/example_cbl/INPUT/example_cbl_p3d $HOME/palm/JOBS/example_cbl/INPUT/

echo "Adjusting palmrun"
size=${#execute_command}
sed -i "2142 i # added comment" $HOME/palm/bin/palmrun
sed -i "2143 i # execute_command=(echo ${execute_command:0:6} ${command_option}${execute_command:7:${size}})" $HOME/palm/bin/palmrun

echo "Starting palm"
palmrun -a "d3#" -X 4 -r example_cbl

echo "Simulation results"
filepath_results=$(ls $HOME/palm/JOBS/example_cbl/OUTPUT)
echo $filepath_results


# Aus Sourcefile von Kai
# Determine hosts to run on
#src=$(tail -n1 $batch_hosts)
#dst=$(head -n1 $batch_hosts)
#echo "Src: $src"
#echo "Dst: $dst"

# Run two node MPI tests
#mpirun -np 2 --host $src,$dst --map-by node --mca btl tcp,vader,self --mca coll_hcoll_enable 0 --mca btl_tcp_if_include lo,eth0 --mca pml ^ucx ${AZ_BATCH_APP_PACKAGE_mpi_batch_1_0_0}/mpi_batch/mpi_hello_world
