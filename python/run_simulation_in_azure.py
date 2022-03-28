import datetime
import io
import os
from pickle import FALSE
import sys
import time

from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas,
    generate_container_sas
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

import azure_batch_functions as abf


#######################
# Preamble
#######################
upload_container_name = "statictest"
output_container_name = "output3"
output_file_name = "test.nc"

#######################
# Network Stuff
# (Not yet working)
#######################
compute_subnet_id = (
    f"/subscriptions/{config.subscription_id}/resourceGroups/"
    f"{config.batch_rg}/providers/Microsoft.Network/virtualNetworks/"
    f"{config.batch_vnet_name}/subnets/{config.compute_subnet_name}"
)

nfs_share_hostname = "${nfs_storage_account_name}.file.core.windows.net"
nfs_share_directory = "/${nfs_storage_account_name}/shared"

#######################
# Azure Batch
#######################
# https://stackoverflow.com/questions/46756780/azure-batch-pool-how-do-i-use-a-custom-vm-image-via-python
# Für netzwerk sachen sind die rechte heir nicht ausreichend!
#######################
credentials = SharedKeyCredentials(
    config.BATCH_ACCOUNT_NAME,
    config.BATCH_ACCOUNT_KEY
)
#######################
# https://docs.microsoft.com/en-us/python/api/azure.batch.batchserviceclient
#######################
batch_client = BatchServiceClient(
    credentials,
    batch_url=config.BATCH_ACCOUNT_URL
)

#######################
# Startup of Pool
#######################
try:
    abf.create_pool(batch_client, config.POOL_ID)
except Exception:
    print("pool already exists")

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

#######################
# Specify input files as zip
#######################

input_file_paths = [
    os.path.join(sys.path[0], config.palm_zip_file)
]
# Upload the data files.

blob_service_client = BlobServiceClient(
    account_url=(
        f"https://{config.STORAGE_ACCOUNT_NAME}."
        f"{config.STORAGE_ACCOUNT_DOMAIN}/"
    ),
    credential=config.STORAGE_ACCOUNT_KEY
)

try:
    input_files = [
        abf.upload_file_to_container(
            blob_service_client,
            upload_container_name,
            file_path
        )
        for file_path
        in input_file_paths
    ]
except Exception:
    print("Files already uploaded")

#######################
# Specify output container
#######################

try:
    blob_service_client.create_container(
        name=output_container_name
    )
except:
    print("Container already exists")
#######################
# https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob?view=azure-python#azure-storage-blob-generate-blob-sas
#######################
sas_container_token = generate_container_sas(
    account_name=config.STORAGE_ACCOUNT_NAME,
    container_name=output_container_name,
    account_key=config.STORAGE_ACCOUNT_KEY,
    permission=BlobSasPermissions(
        read=True,
        add=True,
        create=True,
        write=True,
        delete=True
    ),
    expiry=(
        datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    )
)

output_container_sas_url = abf.get_container_sas_url(
    output_container_name,
    sas_container_token
)

new_job = "test_palm0075"

try:
    abf.create_job(batch_client, new_job, config.POOL_ID)
    abf.add_tasks(batch_client, new_job, input_files, 1, output_container_sas_url)
except Exception:
    print("Job already exists, changed variable new_job")
