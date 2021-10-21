import os
import subprocess

bash_command = "nmap -n -sn 10.0.0.0/24 -oG - | awk '/Up$/{print $2}'"
ip_addresses = subprocess.check_output(["bash", "-c", bash_command])

cores_per_node = 2
ip_list = ip_addresses.decode("utf-8").split("\n")
ip_list_ne = [item for item in ip_list if len(item)!=0]

ip_plus_cpn = [item + f":{cores_per_node}" for item in ip_list_ne]
mpi_host_settings = ",".join(ip_plus_cpn)

os.environ["MPI_HOST_SETTINGS"] = mpi_host_settings
