# 🔐 Guia de Configuração HTTPS para Escalas

Este guia explica como configurar HTTPS com certificado SSL gratuito (Let's Encrypt) para o domínio escalas.click.

## 📋 Pré-requisitos

- ✅ Domínio escalas.click configurado no Route 53
- ✅ DNS apontando para o Elastic IP (98.86.53.112)
- ✅ Aplicação rodando na porta 8000
- ✅ Acesso SSH à instância EC2

## 🚀 Passo a Passo

### 1️⃣ Aplicar mudanças no Terraform (Abrir portas 80 e 443)

No seu computador Windows, execute:

```powershell
cd terraform
terraform apply
```

Confirme com `yes` quando solicitado. Isso abrirá as portas 80 (HTTP) e 443 (HTTPS) no Security Group.

### 2️⃣ Conectar na instância EC2 via SSM

```powershell
aws ssm start-session --target i-08b116a183890b384 --region us-east-1
```

### 3️⃣ Baixar o script de configuração

Na instância EC2:

```bash
cd /tmp
curl -O https://raw.githubusercontent.com/SR-Dionizio/Escalas/main/scripts/setup-nginx-ssl.sh
chmod +x setup-nginx-ssl.sh
```

### 4️⃣ Editar o email no script

```bash
nano setup-nginx-ssl.sh
```

Altere a linha:
```bash
EMAIL="seu-email@example.com"  # ALTERE ESTE EMAIL!
```

Para seu email real, por exemplo:
```bash
EMAIL="daniel@example.com"
```

Salve com `CTRL+O`, `ENTER`, `CTRL+X`

### 5️⃣ Executar o script

```bash
sudo ./setup-nginx-ssl.sh
```

O script irá:
1. ✅ Instalar Nginx e Certbot
2. ✅ Configurar Nginx como proxy reverso
3. ✅ Obter certificado SSL do Let's Encrypt
4. ✅ Configurar renovação automática
5. ✅ Redirecionar HTTP → HTTPS

### 6️⃣ Testar o acesso

Após a conclusão, acesse:
- 🌐 https://escalas.click
- 🌐 https://www.escalas.click

## 🔄 Renovação Automática

O certificado SSL é válido por 90 dias e será renovado automaticamente pelo Certbot.

Para verificar o status da renovação automática:
```bash
sudo systemctl status certbot.timer
```

Para renovar manualmente (se necessário):
```bash
sudo certbot renew
```

## 🛠️ Comandos Úteis

### Verificar status do Nginx
```bash
sudo systemctl status nginx
```

### Reiniciar Nginx
```bash
sudo systemctl restart nginx
```

### Ver logs do Nginx
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Verificar certificados SSL
```bash
sudo certbot certificates
```

### Testar configuração do Nginx
```bash
sudo nginx -t
```

## 🔧 Troubleshooting

### Erro: "DNS não aponta para este servidor"

Verifique se o DNS está correto:
```bash
nslookup escalas.click
```

Deve retornar: `98.86.53.112`

### Erro: "Porta 80/443 não acessível"

Verifique o Security Group:
```bash
aws ec2 describe-security-groups --group-ids $(terraform output -raw security_group_id) --region us-east-1
```

### Aplicação não responde

Verifique se o container está rodando:
```bash
sudo docker ps | grep escalas
sudo docker logs escalas
```

## 📝 Arquitetura Final

```
Internet
    ↓
Route 53 (DNS)
    ↓
Elastic IP (98.86.53.112)
    ↓
Security Group (portas 80, 443, 8000)
    ↓
EC2 Instance
    ↓
Nginx (porta 80/443) → Proxy Reverso
    ↓
Docker Container (porta 8000)
    ↓
FastAPI Application
```

## ✅ Resultado Esperado

- ✅ https://escalas.click → Funciona com SSL válido
- ✅ https://www.escalas.click → Funciona com SSL válido
- ✅ http://escalas.click → Redireciona para HTTPS
- ✅ http://www.escalas.click → Redireciona para HTTPS
- ✅ Certificado renovado automaticamente a cada 60 dias

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs do Nginx
2. Verifique se o container Docker está rodando
3. Verifique se as portas estão abertas no Security Group
4. Verifique se o DNS está apontando corretamente