#!/bin/bash
#
# Die ersten vier Parameter sind vorgegeben durch die ResourcenGruppe in Azure
# 

# ID of your Azure subscription
subscription_id=""
# Name of the resource group
batch_rg=""
# Region
region="westeurope"
# Unique batch account name (e.g. batchwsaccount3245353)
batch_account_name=""
# Unique extension for the keyvault name (e.g. kv234)
# Maxc 24 Zeichen für  ${batch_account_name}${keyvault_extension} 
keyvault_extension="kv18"


# Die restlichen Parameter sind Variabel, sollten aber einer
# gewissen Logik folgen.
# Die Parameter sind Beispiele, wie ich sie verwendet habe

# Unique storage account name (e.g. batchwastorage3245353)
storage_account_name=""
# "batchwasest3245353"

# VNET name
batch_vnet_name=""
# "batch-sest-vnet"

# Compute subnet name
compute_subnet_name=""
# "compute"

# Unique storage account name for shared Azure Files NFS storage (e.g. batchwsnfsstorage3422435234)
nfs_storage_account_name="" 
# "batchsestnfsa37"

# Name of tha Azure Files fileshare
nfs_share="shared"

# Name des Pools
pool_id="batch-ws2-pool"
# Wuerde ich hier definieren

# Zip Datei mit allen Eingangsdaten:
# Unterstützt derzeit
# static driver
# dynamic driver
# p3d
# Dateien müssen zumindest die richtige Endung (p3d, static, dynamic ) haben
palm_zip_file = "test.zip"


BATCH_ACCOUNT_NAME = ''  # Your batch account name
BATCH_ACCOUNT_KEY = ''  # Your batch account key
BATCH_ACCOUNT_URL = ''  # Your batch account URL
STORAGE_ACCOUNT_NAME = ''
STORAGE_ACCOUNT_KEY = ''
STORAGE_ACCOUNT_DOMAIN = 'blob.core.windows.net' # Your storage account blob service domain

POOL_ID = 'PythonQuickstartPool'  # Your Pool ID
POOL_NODE_COUNT = 2  # Pool node count
POOL_VM_SIZE = 'STANDARD_DS1_V2'  # VM Type/Size
JOB_ID = 'PythonQuickstartJob'  # Job ID
STANDARD_OUT_FILE_NAME = 'stdout.txt'  # Standard Output file