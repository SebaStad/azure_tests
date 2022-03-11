
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
        )
    )
    batch_service_client.job.add(job)


def add_tasks(
    batch_service_client: BatchServiceClient,
    job_id: str,
    input_files: list = [],
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
        "/bin/bash -c 'wget -L https://raw.githubusercontent.com/"
        "SebaStad/azure_tests/main/test_modules.sh;"
        "chmod u+x test_modules.sh;./test_modules.sh'"
    )
    tasks.append(batchmodels.TaskAddParameter(
        id=f'Task{idx}',
        display_name=display_name,
        command_line=command,
        resource_files=input_files,
        environment_settings=[
            batchmodels.EnvironmentSetting(
                name="NODES",
                value="2"
            ),
            batchmodels.EnvironmentSetting(
                name="PPN",
                value="44"
            )
        ],
        constraints=batchmodels.TaskConstraints(
            max_wall_clock_time="P10675199DT2H48M5.477S",
            max_task_retry_count=2,
            retention_time="P7D"
        ),
        multi_instance_settings=batchmodels.MultiInstanceSettings(
            coordination_command_line="/bin/bash -c env",
            number_of_instances=2,
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
