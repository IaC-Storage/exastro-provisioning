# api-verification-environment/terraform/outputs.tf
output "eita_public_ip" {
  value = azurerm_public_ip.eita_pip.ip_address
}
