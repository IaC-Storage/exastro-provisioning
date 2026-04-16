# api-verification-environment/terraform/network_resource.tf
# 1. VNet
resource "azurerm_virtual_network" "eita_vnet" {
  name                = "vnet-eita"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.eita_rg.location
  resource_group_name = azurerm_resource_group.eita_rg.name
}

# 2. Subnet
resource "azurerm_subnet" "eita_subnet" {
  name                 = "snet-eita"
  resource_group_name  = azurerm_resource_group.eita_rg.name
  virtual_network_name = azurerm_virtual_network.eita_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# 3. Public IP
resource "azurerm_public_ip" "eita_pip" {
  name                = "pip-eita"
  location            = azurerm_resource_group.eita_rg.location
  resource_group_name = azurerm_resource_group.eita_rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# 4. NIC
resource "azurerm_network_interface" "eita_nic" {
  name                = "nic-eita"
  location            = azurerm_resource_group.eita_rg.location
  resource_group_name = azurerm_resource_group.eita_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.eita_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.eita_pip.id
  }
}

# 5. Associate Security Group with NIC
resource "azurerm_network_interface_security_group_association" "eita_nic_nsg" {
  network_interface_id      = azurerm_network_interface.eita_nic.id
  network_security_group_id = azurerm_network_security_group.eita_nsg.id
}