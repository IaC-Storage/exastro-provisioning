# terraform/main.tf
# 実行環境のパブリックIPを取得 (IPアドレスを実行環境に制限するため)
data "http" "myip" {
  url = "https://ifconfig.me"
}

# Resource Group
resource "azurerm_resource_group" "ita_rg" {
  name     = "rg-ita-verification"
  location = "Japan East"
}

# Network, Subnet, Public IP... (省略)


# VM Instance (Standard_B2s)
resource "azurerm_linux_virtual_machine" "ita_vm" {
  name                = "vm-ita"
  resource_group_name = azurerm_resource_group.ita_rg.name
  location            = azurerm_resource_group.ita_rg.location
  size                = "Standard_B2s"
  admin_username      = "azureuser"

  # 初期セットアップスクリプトの読み込み
  user_data = filebase64("../scripts/install_ita.sh")

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = 100
  }

  source_image_reference {
    publisher = "almalinux"
    offer     = "almalinux-9"
    sku       = "9_2-gen2"
    version   = "latest"
  }

  # AlmaLinux 9はマーケットプレイスのプラン情報が必要
  plan {
    name      = "9_2-gen2"
    product   = "almalinux-9"
    publisher = "almalinux"
  }

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub") # 開発環境の公開鍵パスを確認して記載してください
  }

  network_interface_ids = [
    azurerm_network_interface.ita_nic.id,
  ]
}