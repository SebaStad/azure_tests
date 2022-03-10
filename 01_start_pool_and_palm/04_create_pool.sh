#!/bin/bash

# Variables
source variables.sh

# Poolvm size; F2; siehe bezeichungen;

compute_subnet_id="/subscriptions/${subscription_id}/resourceGroups/${batch_rg}/providers/Microsoft.Network/virtualNetworks/${batch_vnet_name}/subnets/${compute_subnet_name}"
# pool_id="batch-ws-pool"
pool_vm_size="STANDARD_F2s_v2"
nfs_share_hostname="${nfs_storage_account_name}.file.core.windows.net"
nfs_share_directory="/${nfs_storage_account_name}/shared"


# Create the pool definition JSON file
# Define the batch pool

# Python: kann man des json file evtl hinlegen und dann einfach anpassen
# evtl gar nicht neue VM/ aufstellen für PALM, sondern PALM in den shared storage legen
cat << EOF >  ${pool_id}.json
{
  "id": "$pool_id",
  "vmSize": "$pool_vm_size",
  "virtualMachineConfiguration": {
    "imageReference": {
      "publisher": "microsoft-azure-batch",
      "offer": "ubuntu-server-container",
      "sku": "20-04-lts",
      "version": "latest"
    },
    "nodeAgentSKUId": "batch.node.ubuntu 20.04"
  },
  "targetDedicatedNodes": 2,
  "enableInterNodeCommunication": true,
  "networkConfiguration": {
    "subnetId": "$compute_subnet_id"
  },
  "maxTasksPerNode": 1,
  "taskSchedulingPolicy": {
    "nodeFillType": "Pack"
  },
  "mountConfiguration": [
      {
          "nfsMountConfiguration": {
              "source": "$nfs_share_hostname:/${nfs_share_directory}",
              "relativeMountPath": "shared",
              "mountOptions": "-o rw,hard,rsize=65536,wsize=65536,vers=4,minorversion=1,tcp,sec=sys"
          }
      }
  ],
  "startTask": {
    "commandLine": "bash -c \"wget -L https://raw.githubusercontent.com/SebaStad/azure_tests/main/startup_tasks.sh;chmod u+x startup_tasks.sh;./startup_tasks.sh\"",
    "userIdentity": {
      "autoUser": {
        "scope": "pool",
        "elevationLevel": "admin"
      }
    },
    "maxTaskRetryCount": 0,
    "waitForSuccess": true
  }
}
EOF

# Create a batch pool
az batch pool create --json-file ${pool_id}.json

# Look at the status of the batch pool
echo "az batch pool show --pool-id $pool_id --query \"state\""

# az batch pool show --pool-id $pool_id --query "state"

