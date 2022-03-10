#!/bin/bash
echo "Modules"
module avail

echo "amount of cores"
nproc
echo "nmap stuff"
export first_try=$(nmap -n -sn 10.0.0.0/24 -oG - | awk '/Up$/{print $2}'| paste -sd ,)
export second_try=$(echo "$first_try" | awk '{ gsub(",", ":1,") ; system( "echo "  $0) }')
export second_try+=$":1"

export command_option=$(echo "--host ")
export command_option+="$second_try"
echo "$command_option"

#echo "Adjusting palmrun"
# size=${#execute_command}
# sed -i "2142 i # added comment" /palmbase/palm/bin/palmrun
# sed -i "2143 i \ \ \ \ size=\${#execute_command}" /palmbase/palm/bin/palmrun
# sed -i "2144 i \ \ \ \ printf \"\n  \"$size\" \n\"" /palmbase/palm/bin/palmrun
# sed -i "2144 i \ \ \ \ execute_command=\$(echo \${execute_command:0:6} ${command_option}\${execute_command:7:\${size}})" /palmbase/palm/bin/palmrun
# sed -i "2146 i \ \ \ \ printf \"\n  \"$execute_command\" \n\"" /palmbase/palm/bin/palmrun

cd /mnt/batch/tasks/fsmounts/shared/palmbase/palm/

echo "Starting palm"
./bin/palmrun -a "d3#" -X 2 -T 1 -r example_cbl

echo "Simulation results"
filepath_results=$(ls /mnt/batch/tasks/fsmounts/shared/palmbase/palm/JOBS/example_cbl/OUTPUT)
echo $filepath_results


# Aus Sourcefile von Kai
# Determine hosts to run on
#src=$(tail -n1 $batch_hosts)
#dst=$(head -n1 $batch_hosts)
#echo "Src: $src"
#echo "Dst: $dst"

# Run two node MPI tests
#mpirun -np 2 --host $src,$dst --map-by node --mca btl tcp,vader,self --mca coll_hcoll_enable 0 --mca btl_tcp_if_include lo,eth0 --mca pml ^ucx ${AZ_BATCH_APP_PACKAGE_mpi_batch_1_0_0}/mpi_batch/mpi_hello_world
