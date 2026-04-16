# api-verification-environment/terraform/network_security_group.tf
# Security Group (API用の443とSSHを開放)
resource "azurerm_network_security_group" "eita_nsg" {
  name                = "nsg-eita"
  location            = azurerm_resource_group.eita_rg.location
  resource_group_name = azurerm_resource_group.eita_rg.name

  # SSH許可 (22), variables.tfでtrueにすると許可される
  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = var.enable_ssh ? "Allow" : "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "${chomp(data.http.myip.response_body)}/32"
    destination_address_prefix = "*"
  }

  # HTTPS許可 (443) - ITA API/Web用
  security_rule {
    name                       = "HTTPS"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "${chomp(data.http.myip.response_body)}/32"
    destination_address_prefix = "*"
  }
}