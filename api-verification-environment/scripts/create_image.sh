#!/bin/bash

# VMを停止
az vm deallocate --resource-group rg-eita-verification --name vm-eita
# 一般化 (Linuxのエージェント設定などをリセット)
az vm generalize --resource-group rg-eita-verification --name vm-eita
# イメージ作成
az image create --resource-group rg-eita-images --name eita-v2-golden-image --source vm-eita
