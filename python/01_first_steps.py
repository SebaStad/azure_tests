
import datetime
import io
import os
import sys
import time

from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas
)
from azure.batch import BatchServiceClient
from azure.batch.batch_auth import SharedKeyCredentials
from azure.identity import UsernamePasswordCredential
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import ClientSecretCredential
import azure.batch.models as batchmodels
import azure.batch.operations as batchoperations
from azure.core.exceptions import ResourceExistsError

import config

import azure_functions as af
import batch_functions as bf

DEFAULT_ENCODING = "utf-8"

"""
Bash Scripts 01 - 03 must be carried out first!
These should be implemented in first start of simulation container!
However, e.g. storage is not need
so wee need the account (maybe hard set) and the network!
"""
#

# ----------------------------------------------------
# functions
# ----------------------------------------------------


def create_pool(batch_service_client: BatchServiceClient, pool_id: str):
    """
    Creates a pool of compute nodes with the specified OS settings.

    :param batch_service_client: A Batch service client.
    :param str pool_id: An ID for the new pool.
    :param str publisher: Marketplace image publisher
    :param str offer: Marketplace image offer
    :param str sku: Marketplace image sku
    """
    print(f'Creating pool [{pool_id}]...')
    # Create a new pool of Linux compute nodes using an Azure Virtual Machines
    # Marketplace image. For more information about creating pools of Linux
    # nodes, see:
    # https://azure.microsoft.com/documentation/articles/batch-linux-nodes/
    new_pool = batchmodels.PoolAddParameter(
        id=pool_id,
        vm_size=config.POOL_VM_SIZE,
        virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
            image_reference=batchmodels.ImageReference(
                publisher="microsoft-dsvm",
                offer="ubuntu-hpc",
                sku="2004",
                version="latest"
            ),
            node_agent_sku_id="batch.node.ubuntu 20.04"
        ),
        target_dedicated_nodes=config.POOL_NODE_COUNT,
        # target_dedicated_nodes=1,
        enable_inter_node_communication=False,
        # network_configuration=batchmodels.NetworkConfiguration(
        #     subnet_id=compute_subnet_id
        # ),
        task_slots_per_node=1,
        task_scheduling_policy=batchmodels.TaskSchedulingPolicy(
            node_fill_type=batchmodels.ComputeNodeFillType(
                "pack"
            )
        ),
        # mount_configuration=batchmodels.MountConfiguration(
        # )
        start_task=batchmodels.StartTask(
            command_line=(
                "bash -c \"wget -L https://raw.githubusercontent.com/"
                "SebaStad/azure_tests/main/startup_task_simple.sh;"
                "chmod u+x startup_task_simple.sh;"
                "./startup_task_simple.sh\""
            ),
            user_identity=batchmodels.UserIdentity(
                auto_user=batchmodels.AutoUserSpecification(
                    scope="pool",
                    elevation_level="admin"
                )
            ),
            max_task_retry_count=1,
            wait_for_success=True,
        )
    )
    batch_service_client.pool.add(new_pool)


def create_job(batch_service_client: BatchServiceClient, job_id: str, pool_id: str):
    """
    Creates a job with the specified ID, associated with the specified pool.

    :param batch_service_client: A Batch service client.
    :param str job_id: The ID for the job.
    :param str pool_id: The ID for the pool.
    """
    print(f'Creating job [{job_id}]...')
    job = batchmodels.JobAddParameter(
        id=job_id,
        pool_info=batchmodels.PoolInformation(
            pool_id=pool_id
        ),
        constraints=batchmodels.JobConstraints(
            max_wall_clock_time="P10675199DT2H48M5.477S",
            max_task_retry_count=2
        )
    )
    batch_service_client.job.add(job)


def add_tasks(
    batch_service_client: BatchServiceClient,
    job_id: str,
    ressource_file=[],
    idx=1
):
    """
    Adds a task for each input file in the collection to the specified job.

    :param batch_service_client: A Batch service client.
    :param str job_id: The ID of the job to which to add the tasks.
    :param list resource_input_files: A collection of input files.
     One task will becreated for each input file.
    """
    print(f'Adding tasks to job [{job_id}]...')
    display_name = f"palm-sim{config.JOB_ID}"
    tasks = []
    command = (
        "/bin/bash -c 'wget -L https://raw.githubusercontent.com/SebaStad/"
        "azure_tests/main/run_palm.sh;"
        "chmod u+x run_palm.sh;./run_palm.sh'"
    )
    tasks.append(batchmodels.TaskAddParameter(
        id=f'Task{idx}',
        display_name=display_name,
        command_line=command,
        resource_files=ressource_file,
        environment_settings=[
            batchmodels.EnvironmentSetting(
                name="NODES",
                value="1"
            ),
            batchmodels.EnvironmentSetting(
                name="PPN",
                value="20"
            )
        ],
        constraints=batchmodels.TaskConstraints(
            max_wall_clock_time="P10675199DT2H48M5.477S",
            max_task_retry_count=2,
            retention_time="P7D"
        ),
        multi_instance_settings=batchmodels.MultiInstanceSettings(
            coordination_command_line="/bin/bash -c env",
            number_of_instances=1,
            common_resource_files=[]
        ),
        user_identity=batchmodels.UserIdentity(
            auto_user=batchmodels.AutoUserSpecification(
                scope="pool",
                elevation_level="nonadmin"
            )
        )
    ))
    batch_service_client.task.add_collection(job_id, tasks)


def upload_file_to_container(
    blob_storage_service_client: BlobServiceClient,
    container_name: str, file_path: str
) -> batchmodels.ResourceFile:
    """
    Uploads a local file to an Azure Blob storage container.

    :param blob_storage_service_client: A blob service client.
    :param str container_name: The name of the Azure Blob storage container.
    :param str file_path: The local path to the file.
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    blob_name = os.path.basename(file_path)
    blob_client = blob_storage_service_client.get_blob_client(container_name, blob_name)
    print(f'Uploading file {file_path} to container [{container_name}]...')
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    sas_token = generate_blob_sas(
        config.STORAGE_ACCOUNT_NAME,
        container_name,
        blob_name,
        account_key=config.STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    )
    sas_url = generate_sas_url(
        config.STORAGE_ACCOUNT_NAME,
        config.STORAGE_ACCOUNT_DOMAIN,
        container_name,
        blob_name,
        sas_token
    )
    return batchmodels.ResourceFile(
        http_url=sas_url,
        file_path=blob_name
    )


def generate_sas_url(
    account_name: str,
    account_domain: str,
    container_name: str,
    blob_name: str,
    sas_token: str
) -> str:
    """
    Generates and returns a sas url for accessing blob storage
    """
    return f"https://{account_name}.{account_domain}/{container_name}/{blob_name}?{sas_token}"


# ----------------------------------------------------
# Create Pool!
# ----------------------------------------------------

compute_subnet_id = (
    f"/subscriptions/{config.subscription_id}/resourceGroups/"
    f"{config.batch_rg}/providers/Microsoft.Network/virtualNetworks/"
    f"{config.batch_vnet_name}/subnets/{config.compute_subnet_name}"
)
# pool_id="batch-ws-pool"
# pool_vm_size="STANDARD_F2s_v2"
nfs_share_hostname = "${nfs_storage_account_name}.file.core.windows.net"
nfs_share_directory = "/${nfs_storage_account_name}/shared"

# https://stackoverflow.com/questions/46756780/azure-batch-pool-how-do-i-use-a-custom-vm-image-via-python
# Für netzwerk sachen sind die rechte heir nicht ausreichend!
credentials = SharedKeyCredentials(
    config.BATCH_ACCOUNT_NAME,
    config.BATCH_ACCOUNT_KEY
)

# https://docs.microsoft.com/en-us/python/api/azure.batch.batchserviceclient
batch_client = BatchServiceClient(
    credentials,
    batch_url=config.BATCH_ACCOUNT_URL
)


bf.create_pool(batch_client, config.POOL_ID)

batch_client.pool.get( config.POOL_ID,).state.upper()
batch_client.pool.get( config.POOL_ID,).current_dedicated_nodes

while batch_client.pool.get(config.POOL_ID,).current_dedicated_nodes == 0:
    print("Pool is starting!")
    time.sleep(10)

time.sleep(10)

node_list = list(batch_client.compute_node.list(config.POOL_ID))
while any(node.state.lower()=="creating" for node in node_list):
    print("Nodes are being created")
    time.sleep(10)
    node_list = list(batch_client.compute_node.list(config.POOL_ID))

time.sleep(10)
node_list = list(batch_client.compute_node.list(config.POOL_ID))

while any(node.state.lower()=="waitingforstarttask" for node in node_list):
    print("Start task is running!")
    time.sleep(10)
    node_list = list(batch_client.compute_node.list(config.POOL_ID))


# here: checking whether pool is up or not!

full_id = f"palm-sim-task{config.JOB_ID}"
display_name = f"palm-sim{config.JOB_ID}"



# batch_client.pool.delete(config.POOL_ID)

input_file_paths = [
    os.path.join(sys.path[0], 'test.zip')
]
# Upload the data files.


blob_service_client = BlobServiceClient(
        account_url=(
            f"https://{config.STORAGE_ACCOUNT_NAME}."
            f"{config.STORAGE_ACCOUNT_DOMAIN}/"
        ),
        credential=config.STORAGE_ACCOUNT_KEY
    )

input_files = [
    af.upload_file_to_container(
        blob_service_client,
        "statictest",
        file_path
    )
    for file_path
    in input_file_paths
]

new_job = "test_palm0028"

create_job(batch_client, new_job, config.POOL_ID)
add_tasks(batch_client, new_job, input_files, 1)
