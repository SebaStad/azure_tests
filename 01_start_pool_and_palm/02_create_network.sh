#!/bin/bash -x

source variables.sh

# Create a VNET
# Beim ersten Mal: "Microsoft.Network" not registered; passiert dann beim ersten Mal; dauert en Moment
az network vnet create \
    --name $batch_vnet_name \
    --location $region \
    --resource-group $batch_rg \
    --address-prefix 10.0.0.0/16 

# Create a network security group the subnet.
az network nsg create \
  --resource-group $batch_rg \
  --name compute-nsg \
  --location $region

# Create an NSG rule to allow SSH traffic from the Internet to the compute subnet.
# nsg = network securty group

# Netzwerk muss man sich dann spaeter genauer ueberlegen
# Bzgl public ip / zugriff von aussen

# 1. ssh zugriff
az network nsg rule create \
  --resource-group $batch_rg \
  --nsg-name compute-nsg \
  --name Allow-SSH-All \
  --access Allow \
  --protocol Tcp \
  --direction Inbound \
  --priority 200 \
  --source-address-prefix Internet \
  --source-port-range "*" \
  --destination-address-prefix "*" \
  --destination-port-range 22

# 2. batch darf auch drauf zugreifen
# sourceaddres preifx = service tag;
# 
az network nsg rule create \
  --resource-group $batch_rg \
  --nsg-name compute-nsg \
  --name Allow-Batch \
  --access Allow \
  --protocol Tcp \
  --direction Inbound \
  --priority 100 \
  --source-address-prefix "BatchNodeManagement" \
  --source-port-range "*" \
  --destination-address-prefix "*" \
  --destination-port-range "29876-29877"

# Verbietet zugriff für alle anderen auf den ports 29876...
# Die zwei Regeln fallen in zukunft evtl weg;
az network nsg rule create \
  --resource-group $batch_rg \
  --nsg-name compute-nsg \
  --name ModeAgentRule-DenyAll \
  --access Deny \
  --protocol Tcp \
  --direction Inbound \
  --priority 300 \
  --source-address-prefix "*" \
  --source-port-range "*" \
  --destination-address-prefix "*" \
  --destination-port-range "29876-29877"

# Create a subnet with service endpoints
# Subnetz auch erst danach zuweisen, damit des die gleichen Regeln hat
az network vnet subnet create \
  --name $compute_subnet_name \
  --resource-group $batch_rg \
  --vnet-name $batch_vnet_name \
  --address-prefix 10.0.0.0/24 \
  --network-security-group compute-nsg \
  --service-endpoints "Microsoft.Storage" "Microsoft.KeyVault"
