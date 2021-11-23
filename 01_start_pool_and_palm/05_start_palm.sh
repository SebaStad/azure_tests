#!/bin/bash

# Variables
source variables.sh

run_id="04"

# Create job to create the application packahe
az batch job create --id palm-sim${run_id} --pool-id ${pool_id}

# Create task to create the application zip file
full_id="palm-sim-task${run_id}"
display_name="palm-sim${run_id}"


cat << EOF >  palm_run.json
{
    "id": "$full_id",
    "displayName": "$display_name",
    "commandLine": "/bin/bash -c 'wget -L https://raw.githubusercontent.com/SebaStad/azure_tests/main/palm_tests_palm_installed.sh;chmod u+x palm_tests_palm_installed.sh;./palm_tests_palm_installed.sh'",
    "resourceFiles": [],
    "environmentSettings": [
      {
        "name": "NODES",
        "value": "2"
      },
      {
        "name": "PPN",
        "value": "2"
      }
    ],
    "constraints": {
      "maxWallClockTime": "P10675199DT2H48M5.477S",
      "maxTaskRetryCount": 2,
      "retentionTime": "P7D"
    },
    "userIdentity": {
      "autoUser": {
        "scope": "pool",
        "elevationLevel": "nonadmin"
      }
    },
    "multiInstanceSettings": {
      "coordinationCommandLine": "/bin/bash -c env",
      "numberOfInstances": 2,
      "commonResourceFiles": []
    }
  }
EOF

az batch task create --task-id palm-sim-task${run_id} --job-id palm-sim${run_id} --json-file palm_run.json
    # --command-line "/bin/bash -c 'wget -L https://raw.githubusercontent.com/SebaStad/azure_tests/main/palm_tests_palm_installed.sh;chmod u+x palm_tests_palm_installed.sh;./palm_tests_palm_installed.sh'"
    # --command-line "/bin/bash -c 'wget -L https://raw.githubusercontent.com/SebaStad/azure_tests/main/palm_tests_palm_installed.sh;chmod u+x palm_tests_palm_installed.sh;./palm_tests_palm_installed.sh'"
    #    --command-line "/bin/bash -c 'wget -L https://raw.githubusercontent.com/kaneuffe/azure-batch-workshop/main/create_palm.sh;chmod u+x create_app_zip.sh;./create_app_zip.sh'"

# Wait for the task to finish
state=$(az batch task show --job-id palm-sim${run_id} --task-id palm-sim-task${run_id} --query 'state')
echo "Job task status"
echo $state
while [[ $state != *"completed"* ]]
do
    state=$(az batch task show --job-id palm-sim${run_id} --task-id palm-sim-task${run_id} --query 'state')
    echo $state
    sleep 10
done


