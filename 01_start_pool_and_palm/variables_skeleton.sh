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