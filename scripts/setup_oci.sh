#!/bin/bash

# Script de Configuração Maricá Cidadão - Oracle Cloud (Ubuntu)
echo "🚀 Iniciando configuração da Oracle Cloud..."

# 1. Atualizar o sistema
sudo apt-get update -y

# 2. Instalar Docker
echo "🐳 Instalando Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 3. Instalar Docker Compose
echo "🐙 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Abrir Firewall Interno (Porta 8000)
echo "🔥 Abrindo porta 8000 no firewall interno..."
sudo ufw allow 8000/tcp
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save

echo "✅ Configuração concluída! Agora você pode clonar o repositório e rodar o docker-compose."
