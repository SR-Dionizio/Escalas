#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Configurando Nginx + SSL para Escalas"
echo "=========================================="

# Variáveis
DOMAIN="escalas.click"
EMAIL="seu-email@example.com"  # ALTERE ESTE EMAIL!
APP_PORT=8000

echo ""
echo "📦 [1/6] Instalando Nginx e Certbot..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

echo ""
echo "🔧 [2/6] Configurando Nginx (HTTP temporário)..."
sudo tee /etc/nginx/sites-available/escalas > /dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo ""
echo "🔗 [3/6] Ativando configuração do Nginx..."
sudo ln -sf /etc/nginx/sites-available/escalas /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo ""
echo "✅ [4/6] Testando configuração do Nginx..."
sudo nginx -t

echo ""
echo "🔄 [5/6] Reiniciando Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "🔐 [6/6] Obtendo certificado SSL (Let's Encrypt)..."
echo "⚠️  IMPORTANTE: Certifique-se de que o DNS está apontando para este servidor!"
echo "⚠️  Pressione CTRL+C para cancelar se o DNS não estiver configurado."
echo ""
read -p "Continuar com a obtenção do certificado SSL? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect
    
    echo ""
    echo "✅ Configurando renovação automática..."
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer
    
    echo ""
    echo "=========================================="
    echo "✅ HTTPS configurado com sucesso!"
    echo "=========================================="
    echo ""
    echo "🌐 Acesse: https://$DOMAIN"
    echo "🌐 Acesse: https://www.$DOMAIN"
    echo ""
    echo "📝 Certificado será renovado automaticamente"
    echo "📝 Para renovar manualmente: sudo certbot renew"
else
    echo ""
    echo "⚠️  Certificado SSL não foi configurado."
    echo "📝 Para configurar depois, execute:"
    echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

echo ""
echo "=========================================="
echo "✅ Configuração concluída!"
echo "=========================================="

# Made with Bob
