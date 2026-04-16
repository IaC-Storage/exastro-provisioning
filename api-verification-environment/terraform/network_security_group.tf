# terraform/network_security_group.tf
# Security Group (API用の443とSSHを開放)
resource "azurerm_network_security_group" "ita_nsg" {
  name                = "nsg-ita"
  location            = azurerm_resource_group.ita_rg.location
  resource_group_name = azurerm_resource_group.ita_rg.name

  # SSH許可 (22)
  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
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