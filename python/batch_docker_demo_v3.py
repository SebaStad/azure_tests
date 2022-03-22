from __future__ import print_function
import datetime
import io
import os
import sys
import time
import config
try:
    input = raw_input
except NameError:
    pass

from azure.core.exceptions import ResourceExistsError

from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas,
    generate_container_sas
)

from azure.batch import BatchServiceClient
from azure.batch.batch_auth import SharedKeyCredentials
import azure.batch.models as batchmodels

## Added as needed for the User Subscription Mode
from azure.common.credentials import ServicePrincipalCredentials

# Update the Batch and Storage account credential strings in config.py with values
# unique to your accounts. These are used when constructing connection strings
# for the Batch and Storage client objects.

def query_yes_no(question, default="yes"):
    """
    Prompts the user for yes/no input, displaying the specified question text.

    :param str question: The text of the prompt for input.
    :param str default: The default if the user hits <ENTER>. Acceptable values
    are 'yes', 'no', and None.
    :rtype: str
    :return: 'yes' or 'no'
    """
    valid = {'y': 'yes', 'n': 'no'}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError("Invalid default answer: '{}'".format(default))

    while 1:
        choice = input(question + prompt).lower()
        if default and not choice:
            return default
        try:
            return valid[choice[0]]
        except (KeyError, IndexError):
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def print_batch_exception(batch_exception):
    """
    Prints the contents of the specified Batch exception.

    :param batch_exception:
    """
    print('-------------------------------------------')
    print('Exception encountered:')
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value:
        print(batch_exception.error.message.value)
        if batch_exception.error.values:
            print()
            for mesg in batch_exception.error.values:
                print('{}:\t{}'.format(mesg.key, mesg.value))
    print('-------------------------------------------')


def upload_file_to_container(blob_service_client, container_name, file_path):
    """
    Uploads a local file to an Azure Blob storage container.

    :param blob_service_client: A blob service client.
    :type blob_service_client: `azure.storage.blob.BlobServiceClient`
    :param str container_name: The name of the Azure Blob storage container.
    :param str file_path: The local path to the file.
    :rtype: `azure.batch.models.ResourceFile`
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    blob_name = os.path.basename(file_path)
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)

    print('Uploading file {} to container [{}]...'.format(file_path,
                                                          container_name))

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    sas_token = generate_blob_sas(
        config._STORAGE_ACCOUNT_NAME,
        container_name,
        blob_name,
        account_key=config._STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    )

    sas_url = generate_sas_url(
        config._STORAGE_ACCOUNT_NAME,
        config._STORAGE_ACCOUNT_DOMAIN,
        container_name,
        blob_name,
        sas_token
    )

    return batchmodels.ResourceFile(
        http_url=sas_url,
        file_path=blob_name
    )

## Added 

def get_container_sas_url(blob_service_client, container_name, blob_permissions):
    """
    Obtains a shared access signature URL that provides write access to the 
    ouput container to which the tasks will upload their output.

    :param block_blob_client: A blob service client.
    :type block_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param BlobPermissions blob_permissions:
    :rtype: str
    :return: A SAS URL granting the specified permissions to the container.
    """
    ###
    sas_token = generate_container_sas(
        config._STORAGE_ACCOUNT_NAME,
        container_name,
        account_key=config._STORAGE_ACCOUNT_KEY,
        permission=blob_permissions,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    )
    
    #Construct SAS URL for the container
    container_sas_url = "https://{}.blob.core.windows.net/{}?{}".format(
        config._STORAGE_ACCOUNT_NAME, container_name, sas_token)

    return container_sas_url

def generate_sas_url(
    account_name, account_domain, container_name, blob_name, sas_token
):
    return "https://{}.{}/{}/{}?{}".format(
        account_name,
        account_domain,
        container_name,
        blob_name,
        sas_token
    )

def create_pool(batch_service_client, pool_id):
    """
    Creates a pool of compute nodes with the specified OS settings.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str pool_id: An ID for the new pool.
    :param str publisher: Marketplace image publisher
    :param str offer: Marketplace image offer
    :param str sku: Marketplace image sku
    """
    print('Creating pool [{}]...'.format(pool_id))

    # Create a new pool of Linux compute nodes using an Azure Virtual Machines
    # Marketplace image. For more information about creating pools of Linux
    # nodes, see:
    # https://azure.microsoft.com/documentation/articles/batch-linux-nodes/

    ## Adding container configuration
    ## Specify a container registry
    container_registry = batchmodels.ContainerRegistry(
        registry_server=config._REGISTRY_SERVER,
        user_name=config._REGISTRY_USERNAME,
        password=config._REGISTRY_PASSWORD)

    ## Create container configuration, prefetching Docker images from the container registry
    container_conf = batchmodels.ContainerConfiguration(
        container_image_names=[config._CONTAINER_IMAGE_URL],
        container_registries =[container_registry])

    new_pool = batchmodels.PoolAddParameter(
        id=pool_id,
        virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
            image_reference=batchmodels.ImageReference(
                publisher="microsoft-azure-batch",
                offer="centos-container",
                sku="7-8",
                version="latest"
            ),
            container_configuration=container_conf,
            node_agent_sku_id="batch.node.centos 7"
        ),
        vm_size=config._POOL_VM_SIZE,
        target_dedicated_nodes=config._POOL_NODE_COUNT,
        ## Added network configuration
        network_configuration=batchmodels.NetworkConfiguration(
           subnet_id=config._COMPUTE_SUBNET_ID
        ),
        ## Added scheduling policy 
        task_scheduling_policy=batchmodels.TaskSchedulingPolicy(node_fill_type = 'Pack'),
        ## Added inter-node communication option
        enable_inter_node_communication=False,
        ## Added start task
        start_task=batchmodels.StartTask(
            command_line="/bin/bash -c \"#!/bin/bash\nhostname\nenv\npwd\ndocker image ls\"",
            max_task_retry_count=1,
            wait_for_success=True,
            user_identity=batchmodels.UserIdentity(
                auto_user=batchmodels.AutoUserSpecification(
                    scope=batchmodels.AutoUserScope.pool,
                    elevation_level=batchmodels.ElevationLevel.admin)),
        ),
        ## Added mount configuration
        ##mount_configuration = [batchmodels.MountConfiguration(nfs_mount_configuration=batchmodels.NFSMountConfiguration(
        ##        source="hpcnfsstorage.file.core.windows.net:/hpcnfsstorage/shared",
        ##        relative_mount_path="shared",
        ##        mount_options="-o rw,soft,noacl,vers=4,minorversion=1,sec=sys"
        ##))]
    )

    batch_service_client.pool.add(new_pool)


def create_job(batch_service_client, job_id, pool_id):
    """
    Creates a job with the specified ID, associated with the specified pool.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The ID for the job.
    :param str pool_id: The ID for the pool.
    """
    print('Creating job [{}]...'.format(job_id))

    job = batchmodels.JobAddParameter(
        id=job_id,
        pool_info=batchmodels.PoolInformation(pool_id=pool_id))

    batch_service_client.job.add(job)


def add_task(batch_service_client, job_id, input_files, output_container_sas_url):
    """
    Adds a task for each input file in the collection to the specified job.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The ID of the job to which to add the tasks.
    :param list input_files: A collection of input files. One task will be
     created for each input file.
    :param output_container_sas_token: A SAS token granting write access to
    the specified Azure Blob storage container.
    """

    print('Adding task to job [{}]...'.format(job_id))

    ##tasks = list()

    ## Adding container task
    task_id = 'container_task'

    task_container_settings = batchmodels.TaskContainerSettings(
        image_name=config._CONTAINER_IMAGE_URL,
        container_run_options='--rm --workdir /apphome -v $AZ_BATCH_TASK_WORKING_DIR:/apphome/output'
    )

    input_file = input_files[0]
    output_file_path = './output.txt'

    ## Added output_files upload to container
    task = batchmodels.TaskAddParameter(
        id=task_id,
        command_line='/bin/sh -c \"/usr/bin/mpirun -n 3 /apphome/my_exec.exe > /apphome/output/output.txt\"',
        container_settings=task_container_settings,
        resource_files=[input_file],
        output_files=[batchmodels.OutputFile(
            file_pattern=output_file_path,
            destination=batchmodels.OutputFileDestination(
                container=batchmodels.OutputFileBlobContainerDestination(
                    container_url=output_container_sas_url)),
            upload_options=batchmodels.OutputFileUploadOptions(
                upload_condition=batchmodels.OutputFileUploadCondition.task_success)
        )]
    )

    ## for idx, input_file in enumerate(input_files):
    ##
    ##    command = "/bin/bash -c \"cat {}\"".format(input_file.file_path)
    ##    tasks.append(batchmodels.TaskAddParameter(
    ##        id='Task{}'.format(idx),
    ##        command_line=command,
    ##        resource_files=[input_file]
    ##    )
    ##    )

    ##batch_service_client.task.add_collection(job_id, tasks)
    batch_service_client.task.add(job_id, task)


def wait_for_tasks_to_complete(batch_service_client, job_id, timeout):
    """
    Returns when all tasks in the specified job reach the Completed state.

    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The id of the job whose tasks should be to monitored.
    :param timedelta timeout: The duration to wait for task completion. If all
    tasks in the specified job do not reach Completed state within this time
    period, an exception will be raised.
    """
    timeout_expiration = datetime.datetime.now() + timeout

    print("Monitoring all tasks for 'Completed' state, timeout in {}..."
          .format(timeout), end='')

    while datetime.datetime.now() < timeout_expiration:
        print('.', end='')
        sys.stdout.flush()
        tasks = batch_service_client.task.list(job_id)

        incomplete_tasks = [task for task in tasks if
                            task.state != batchmodels.TaskState.completed]
        if not incomplete_tasks:
            print()
            return True
        else:
            time.sleep(1)

    print()
    raise RuntimeError("ERROR: Tasks did not reach 'Completed' state within "
                       "timeout period of " + str(timeout))


def print_task_output(batch_service_client, job_id, encoding=None):
    """
    Prints the stdout.txt file for each task in the job.

    :param batch_client: The batch client to use.
    :type batch_client: `batchserviceclient.BatchServiceClient`
    :param str job_id: The id of the job with task output files to print.
    """
    print('Printing task output...')

    tasks = batch_service_client.task.list(job_id)

    for task in tasks:

        node_id = batch_service_client.task.get(
            job_id, task.id).node_info.node_id
        print("Task: {}".format(task.id))
        print("Node: {}".format(node_id))

        stream = batch_service_client.file.get_from_task(
            job_id, task.id, config._STANDARD_OUT_FILE_NAME)

        file_text = _read_stream_as_string(
            stream,
            encoding)
        print("Standard output:")
        print(file_text)


def _read_stream_as_string(stream, encoding):
    """
    Read stream as string

    :param stream: input stream generator
    :param str encoding: The encoding of the file. The default is utf-8.
    :return: The file content.
    :rtype: str
    """
    output = io.BytesIO()
    try:
        for data in stream:
            output.write(data)
        if encoding is None:
            encoding = 'utf-8'
        return output.getvalue().decode(encoding)
    finally:
        output.close()


if __name__ == '__main__':

    start_time = datetime.datetime.now().replace(microsecond=0)
    print('Sample start: {}'.format(start_time))
    print()

    # Create the blob client, for use in obtaining references to
    # blob storage containers and uploading files to containers.
    blob_service_client = BlobServiceClient(
        account_url="https://{}.{}/".format(
            config._STORAGE_ACCOUNT_NAME,
            config._STORAGE_ACCOUNT_DOMAIN
        ),
        credential=config._STORAGE_ACCOUNT_KEY
    )

    # Use the blob client to create the containers in Azure Storage if they
    # don't yet exist.
    input_container_name = 'input'
    try:
        blob_service_client.create_container(input_container_name)
    except ResourceExistsError:
        pass

        # The collection of data files that are to be processed by the tasks.
    input_file_paths = [os.path.join(sys.path[0], 'inputdata.xlm')]

    # Upload the data files.
    input_files = [
        upload_file_to_container(blob_service_client, input_container_name, file_path)
        for file_path in input_file_paths]

    ## Use the blob client to create the containers in Azure Storage if they
    ## don't yet exist.
    output_container_name = 'output'
    try:
        blob_service_client.create_container(output_container_name)
    except ResourceExistsError:
        pass

    ## Retreive SAS URL for the output container
    
    output_blob_permissions=BlobSasPermissions(write=True)
    output_container_sas_url=get_container_sas_url(blob_service_client, output_container_name, output_blob_permissions)
  

    # Create a Batch service client. We'll now be interacting with the Batch
    # service in addition to Storage
    ## Removed shared key creadentials
    ##credentials = SharedKeyCredentials(config._BATCH_ACCOUNT_NAME,
    ##    config._BATCH_ACCOUNT_KEY)

    ## Added to have credetials for a user managed batch account
    credentials = ServicePrincipalCredentials(
        client_id=config._CLIENT_ID,
        secret=config._CLIENT_SECRET,
        tenant=config._TENANT_ID,
        resource="https://batch.core.windows.net/"
    )

    batch_client = BatchServiceClient(
        credentials,
        batch_url=config._BATCH_ACCOUNT_URL)

    try:
        # Create the pool that will contain the compute nodes that will execute the
        # tasks.
        create_pool(batch_client, config._POOL_ID)

        # Create the job that will run the tasks.
        create_job(batch_client, config._JOB_ID, config._POOL_ID)

        # Add the tasks to the job.
        add_task(batch_client, config._JOB_ID, input_files, output_container_sas_url)

        # Pause execution until tasks reach Completed state.
        wait_for_tasks_to_complete(batch_client,
                                   config._JOB_ID,
                                   datetime.timedelta(minutes=30))

        print("  Success! All tasks reached the 'Completed' state within the "
              "specified timeout period.")

        # Print the stdout.txt and stderr.txt files for each task to the console
        print_task_output(batch_client, config._JOB_ID)

    except batchmodels.BatchErrorException as err:
        print_batch_exception(err)
        raise

    # Clean up storage resources
    print('Deleting container [{}]...'.format(input_container_name))
    blob_service_client.delete_container(input_container_name)

    # Print out some timing info
    end_time = datetime.datetime.now().replace(microsecond=0)
    print()
    print('Sample end: {}'.format(end_time))
    print('Elapsed time: {}'.format(end_time - start_time))
    print()

    # Clean up Batch resources (if the user so chooses).
    if query_yes_no('Delete job?') == 'yes':
        batch_client.job.delete(config._JOB_ID)

    if query_yes_no('Delete pool?') == 'yes':
        batch_client.pool.delete(config._POOL_ID)

    print()
    input('Press ENTER to exit...')
